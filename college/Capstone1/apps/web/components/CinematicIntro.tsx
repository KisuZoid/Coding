"use client";

import Link from "next/link";
import { useCallback, useEffect, useRef, useState } from "react";

import { coverRect } from "@/lib/cinematic/canvas";
import { CinematicPreloader } from "@/lib/cinematic/preload";
import { SCENES, TOTAL_FRAMES, frameForProgress, sceneUrl, segmentAt } from "@/lib/cinematic/sequence";

const BASE_URL = (scene: number, frame: number) => sceneUrl(scene, frame);
const COUNTS = SCENES.map((s) => s.frameCount);

/** Frames of scroll travel assigned to the cinematic section. */
const SCROLL_VH = 380;

/** Settled smoothing factor for progress interpolation. */
const SMOOTHING = 0.16;

/**
 * Scroll-driven cinematic intro rendered from the 30 FPS image sequences in
 * /videos/{1..4}. One continuous timeline: scroll progress -> normalized
 * progress -> global frame -> scene + local frame -> canvas draw.
 *
 * Scroll events only set a *target* progress; a requestAnimationFrame loop
 * lerps the *current* progress toward it so motion is smooth in both
 * directions and responsive to quick scrolls. Frames are decoded on demand by
 * a bounded preloader and drawn to a single high-DPI canvas (no DOM explosion).
 *
 * prefers-reduced-motion: the fixed scenes collapse to a static, reduced
 * sequence — copy still advances but no continuous frame scrubbing occurs.
 */
export default function CinematicIntro() {
  const holderRef = useRef<HTMLDivElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const preloadRef = useRef<CinematicPreloader | null>(null);
  const currentProgressRef = useRef(0);
  const targetProgressRef = useRef(0);
  const rafRef = useRef(0);
  const lastDrawnRef = useRef<string>("");
  const reduceMotionRef = useRef(false);

  const [progress, setProgress] = useState(0);

  const initPreloader = useCallback(() => {
    if (!preloadRef.current) preloadRef.current = new CinematicPreloader(BASE_URL, COUNTS);
  }, []);

  // Draw one frame to the canvas.
  const draw = useCallback((img: ImageBitmap | HTMLImageElement) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Lightweight counters for the browser performance suite (harmless, prod-safe).
    const g = window as unknown as { __cinematicDraws?: number; __cinematicFirstDrawAt?: number };
    g.__cinematicDraws = (g.__cinematicDraws ?? 0) + 1;
    if (g.__cinematicDraws === 1) g.__cinematicFirstDrawAt = performance.now();

    const cssW = canvas.clientWidth || canvas.width;
    const cssH = canvas.clientHeight || canvas.height;
    const rect = coverRect(
      { width: img.width, height: img.height },
      { width: cssW, height: cssH },
      canvas.width / cssW,
      canvas.height / cssH,
    );
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.drawImage(img as CanvasImageSource, rect.dx, rect.dy, rect.dw, rect.dh);
  }, []);

  const renderFrame = useCallback(
    (p: number): boolean => {
      const pos = frameForProgress(p);
      const preloader = preloadRef.current;
      if (!preloader) return false;
      const img = preloader.getFrame(pos.scene.id, pos.localFrame);
      if (!img) return false; // frame not decoded yet; keep last frame (no flash) and retry next tick
      draw(img);
      return true;
    },
    [draw],
  );

  // Scroll -> target progress.
  useEffect(() => {
    const onScroll = () => {
      const el = holderRef.current;
      if (!el) return;
      const rect = el.getBoundingClientRect();
      const span = rect.height - window.innerHeight;
      if (span <= 0) return;
      const p = Math.min(1, Math.max(0, -rect.top / span));
      targetProgressRef.current = p;
      setProgress(p);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("resize", onScroll);
    onScroll();
    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("resize", onScroll);
    };
  }, []);

  // Reduced motion detection (read before the rAF loop wires up).
  useEffect(() => {
    try {
      reduceMotionRef.current = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    } catch {
      reduceMotionRef.current = false;
    }
  }, []);

  // rAF smoothing loop.
  useEffect(() => {
    initPreloader();

    if (reduceMotionRef.current) {
      // Reduced motion: park on the final scene's last frame; no scrubbing.
      preloadRef.current?.update(4, SCENES[3].frameCount);
      renderFrame(1); // last frame of the sequence
      return () => {
        preloadRef.current?.clear();
      };
    }

    let last = performance.now();
    const tick = (now: number) => {
      const dt = Math.min(64, now - last);
      last = now;
      const cp = currentProgressRef.current;
      const tp = targetProgressRef.current;
      const k = 1 - Math.pow(1 - SMOOTHING, dt / 16.7);
      currentProgressRef.current = cp + (tp - cp) * k;

      const pos = frameForProgress(currentProgressRef.current);
      const preloader = preloadRef.current;
      if (preloader) {
        preloader.update(pos.scene.id, pos.localFrame);
      }

      const frameKey = `${pos.scene.id}/${pos.localFrame}`;
      if (frameKey !== lastDrawnRef.current && renderFrame(currentProgressRef.current)) {
        lastDrawnRef.current = frameKey;
      }
      rafRef.current = requestAnimationFrame(tick);
    };
    rafRef.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(rafRef.current);
  }, [initPreloader, renderFrame]);

  // DPR-aware canvas sizing.
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const recompute = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2); // cap at 2x
      const rect = canvas.getBoundingClientRect();
      if (rect.width === 0 || rect.height === 0) return;
      canvas.width = Math.round(rect.width * dpr);
      canvas.height = Math.round(rect.height * dpr);
      preloadRef.current?.onResize();
    };
    recompute();
    window.addEventListener("resize", recompute);
    return () => window.removeEventListener("resize", recompute);
  }, []);

  const segment = segmentAt(progress);
  const active = SCENES[segment]?.text ?? SCENES[0].text;
  const atEnd = progress > 0.93;
  const decade = Math.round(progress * 10) / 10;

  return (
    <div
      ref={holderRef}
      className="relative cinematic-scroll"
      style={{ height: `${SCROLL_VH}vh` }}
      aria-label="AutoInspect-X introduction"
    >
      <div className="sticky top-0 h-screen w-full overflow-hidden bg-black">
        <canvas
          ref={canvasRef}
          className="absolute inset-0 h-full w-full"
          aria-hidden
        />
        {/* Subtle vignette to keep text legible without killing the image. */}
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-black/60 via-black/10 to-black/30" />

        {/* Narrative overlay — fades in/out per scene region. */}
        <div
          className="absolute inset-x-0 bottom-24 px-6 text-center text-white transition-opacity duration-500 sm:bottom-28 sm:px-12"
          style={{
            opacity:
              progress >= (SCENES[segment]?.textStart ?? 0) && progress <= (SCENES[segment]?.textEnd ?? 1)
                ? 1
                : 0,
          }}
        >
          <p className="text-xs font-semibold tracking-[0.3em] text-amber-300/90 uppercase sm:text-sm">
            {active.eyebrow}
          </p>
          <h2 className="mx-auto mt-3 max-w-3xl text-3xl font-semibold leading-tight text-white sm:text-5xl">
            {active.title}
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-sm leading-relaxed text-slate-200/90 sm:text-base">
            {active.body}
          </p>
        </div>

        {/* Scroll progress bar */}
        <div className="absolute inset-x-0 bottom-0 h-1 bg-white/10">
          <div
            className="h-full bg-amber-400"
            style={{ width: `${Math.round(decade * 100)}%` }}
          />
        </div>

        {/* Scroll hint, hidden near the end */}
        {!atEnd && (
          <div className="absolute bottom-6 left-1/2 -translate-x-1/2 text-[11px] tracking-widest text-white/60 uppercase">
            Scroll
          </div>
        )}

        {/* Call to action at the end */}
        <div
          className={`absolute inset-0 z-10 flex flex-col items-center justify-center gap-6 transition-opacity duration-700 ${
            atEnd ? "opacity-100" : "pointer-events-none opacity-0"
          }`}
        >
          <h2 className="max-w-xl px-6 text-center text-3xl font-semibold text-white sm:text-4xl">
            Talk to AutoInspect-X
          </h2>
          <Link
            href="/demo"
            className="rounded-full bg-amber-400 px-8 py-4 text-base font-semibold text-black shadow-lg shadow-amber-400/30 transition hover:bg-amber-300"
          >
            Start Inspection
          </Link>
        </div>

        {/* Total frame counter (subtle, informational) */}
        <p className="absolute right-4 bottom-6 hidden text-[10px] tracking-widest text-white/40 uppercase sm:block">
          frame {Math.round(progress * (TOTAL_FRAMES - 1)) + 1} / {TOTAL_FRAMES}
        </p>
      </div>
    </div>
  );
}
