/// Bounded, staged frame preloader for the cinematic sequence.
///
/// Strategy:
///   - Scene 1 is brought in first (it appears immediately on scroll-down).
///   - Scenes 2..4 are preloaded progressively as the user approaches them.
///   - The decoded-image cache is LRU-bounded (see `budget`) so thousands of
///     decoded frames never accumulate in memory. Undecoded source files stay in
///     the browser HTTP cache; decoded `ImageBitmap` memory is what we bound.
///   - Mobile gets a smaller budget than desktop/tablet (adaptive loading).

export interface PreloadOptions {
  /** Rough decoded-frame budget we are willing to hold. */
  budget: number;
  /** How many frames ahead of the current one to fetch. */
  lookahead: number;
}

function defaultOptions(): PreloadOptions {
  const dpr = typeof window !== "undefined" ? (window.devicePixelRatio || 1) : 1;
  const width = typeof window !== "undefined" ? (window.innerWidth || 1280) : 1280;
  // Mobile / narrow viewport => lower memory pressure.
  if (width < 640 && dpr <= 1) return { budget: 28, lookahead: 24 };
  if (width < 1024) return { budget: 60, lookahead: 48 };
  return { budget: 90, lookahead: 72 };
}

/** LRU-bounded cache of decoded images for one scene. */
export class SceneCache {
  private map = new Map<string, ImageBitmap | HTMLImageElement>();
  private order: string[] = [];
  budget: number;

  constructor(budget: number) {
    this.budget = budget;
  }

  has(src: string): boolean {
    return this.map.has(src);
  }

  get(src: string): ImageBitmap | HTMLImageElement | undefined {
    const img = this.map.get(src);
    if (img) {
      this.order.splice(this.order.indexOf(src), 1);
      this.order.push(src); // most recently used
    }
    return img;
  }

  set(src: string, img: ImageBitmap | HTMLImageElement): void {
    if (this.map.has(src)) return;
    this.map.set(src, img);
    this.order.push(src);
    this.evict();
  }

  /** Drop every decoded entry except the given keep-list. */
  prune(keep: string[]): void {
    const keepSet = new Set(keep);
    for (const src of [...this.order]) {
      if (!keepSet.has(src)) this.delete(src);
    }
  }

  clear(): void {
    for (const src of [...this.order]) this.delete(src);
  }

  private delete(src: string): void {
    const img = this.map.get(src);
    if (img && typeof (img as ImageBitmap).close === "function") {
      try {
        (img as ImageBitmap).close();
      } catch {
        /* already closed */
      }
    }
    this.map.delete(src);
    const i = this.order.indexOf(src);
    if (i !== -1) this.order.splice(i, 1);
  }

  private evict(): void {
    while (this.order.length > this.budget) {
      const oldest = this.order[0];
      if (!oldest) break;
      this.delete(oldest);
    }
  }
}

type Decoded = ImageBitmap | HTMLImageElement;

/**
 * Preloader for one scene. Fetches frames and stores them as decoded
 * `ImageBitmap` (when supported) so the canvas can draw without an extra
 * decode hop per frame. Falls back to `HTMLImageElement` where `createImageBitmap`
 * is unavailable.
 */
export class ScenePreloader {
  readonly scene: number;
  readonly count: number;
  private cache: SceneCache;
  private inFlight = new Set<string>();
  private baseUrl: (scene: number, frame: number) => string;

  constructor(scene: number, count: number, baseUrl: (s: number, f: number) => string, budget: number) {
    this.scene = scene;
    this.count = count;
    this.baseUrl = baseUrl;
    this.cache = new SceneCache(budget);
  }

  setBudget(budget: number): void {
    this.cache.budget = budget;
  }

  /** Ensure frames around `frame` are requested/decoded, pruning far frames. */
  prefetch(frame: number, windowSize: number): void {
    const lo = Math.max(1, frame - windowSize);
    const hi = Math.min(this.count, frame + windowSize);
    for (let f = lo; f <= hi; f += 1) this.request(f);
    const keep = new Set<string>();
    for (let f = lo; f <= hi; f += 1) keep.add(this.baseUrl(this.scene, f));
    this.cache.prune([...keep]);
  }

  private request(frame: number): void {
    const src = this.baseUrl(this.scene, frame);
    if (this.cache.has(src) || this.inFlight.has(src)) return;
    this.inFlight.add(src);
    const finish = (img: Decoded) => {
      this.inFlight.delete(src);
      this.cache.set(src, img);
    };
    const fail = () => {
      this.inFlight.delete(src);
    };

    if (typeof createImageBitmap === "function") {
      fetch(src)
        .then((r) => {
          if (!r.ok) throw new Error(`HTTP ${r.status}`);
          return r.blob();
        })
        .then((blob) => createImageBitmap(blob))
        .then((bitmap) => finish(bitmap))
        .catch(fail);
    } else {
      const img = new Image();
      img.onload = () => finish(img);
      img.onerror = fail;
      img.src = src;
    }
  }

  /** The decoded frame for `frame`, or undefined if not ready. */
  getFrame(frame: number): Decoded | undefined {
    return this.cache.get(this.baseUrl(this.scene, frame));
  }

  /** The nearest already-decoded frame at or before `frame`. */
  nearest(frame: number): { img: Decoded; frame: number } | undefined {
    for (let f = frame; f >= 1; f -= 1) {
      const img = this.cache.get(this.baseUrl(this.scene, f));
      if (img) return { img, frame: f };
    }
    return undefined;
  }

  clear(): void {
    for (const src of [...this.inFlight]) this.inFlight.delete(src);
    this.cache.clear();
  }
}

/**
 * Manages staged loading across all four scenes. Scene 1 is keyst warm;
 * later scenes load progressively on approach.
 */
export class CinematicPreloader {
  private preloaders: ScenePreloader[];
  private options: PreloadOptions;

  constructor(baseUrl: (s: number, f: number) => string, counts: number[], options?: PreloadOptions) {
    this.options = options ?? defaultOptions();
    this.preloaders = counts.map(
      (count, i) => new ScenePreloader(i + 1, count, baseUrl, this.options.budget),
    );
  }

  onResize(): void {
    this.options = defaultOptions();
    for (const p of this.preloaders) p.setBudget(this.options.budget);
  }

  /**
   * Drive loading from the current frame. Scene 1 stays warm; the scene that
   * follows the current one is prefetched aggressively near its boundary.
   */
  update(currentScene: number, localFrame: number): void {
    const current = this.preloaders[currentScene - 1];
    if (current) current.prefetch(localFrame, this.options.lookahead);

    if (currentScene > 1) {
      // Keep scene 1 warm but lightweight throughout.
      this.preloaders[0].prefetch(1, 12);
    }

    const next = this.preloaders[currentScene]; // 0-indexed, next scene
    if (next && localFrame > next.count * 0.5) {
      next.prefetch(1, this.options.lookahead);
    }
  }

  /** Decoded frame for a position, or the nearest available. */
  getFrame(scene: number, localFrame: number): Decoded | undefined {
    const p = this.preloaders[scene - 1];
    if (!p) return undefined;
    return p.getFrame(localFrame) ?? p.nearest(localFrame)?.img;
  }

  clear(): void {
    for (const p of this.preloaders) p.clear();
  }
}
