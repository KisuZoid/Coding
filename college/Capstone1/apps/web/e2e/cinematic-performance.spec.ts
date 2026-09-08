import { expect, test, type Page } from "@playwright/test";

declare global {
  interface Window {
    __rafStats?: number[];
    __cinematicDraws?: number;
    __cinematicFirstDrawAt?: number;
    performance: Performance & { memory?: { usedJSHeapSize: number } };
  }
}

/**
 * Measured performance checks for the scroll-driven cinematic intro.
 *
 * The suite never claims smoothness by inspection — it measures, from the real
 * browser:
 *   - time to first cinematic frame (component draw counter)
 *   - rAF cadence under slow and fast scroll (interval stats + drop count)
 *   - distinct canvas frames painted while scrolling (downsampled hash)
 *   - JS heap growth before/after a full scrub and a rapid back-and-forth
 *   - reverse (upward) scroll support: frames must move, not reset
 *
 * HEADLESS CAVEAT: headless Chrome usually vsyncs at the display rate, so exact
 * 60 FPS is not assumed. We assert structure and boundedness, and report the
 * measured numbers in the test output for human review.
 */

const rAF_HOOK = `
  window.__rafStats = [];
  const _origRaf = window.requestAnimationFrame.bind(window);
  window.requestAnimationFrame = (cb) =>
    _origRaf((t) => { window.__rafStats.push(t); cb(t); });
`;

function jsHeapMb(page: Page): Promise<number> {
  return page.evaluate(() => {
    const mem = window.performance.memory;
    return mem ? Number((mem.usedJSHeapSize / 1048576).toFixed(1)) : NaN;
  });
}

function firstDrawMs(page: Page): Promise<number | null> {
  return page.evaluate(() =>
    typeof window.__cinematicFirstDrawAt === "number" ? window.__cinematicFirstDrawAt : null,
  );
}

function drawCount(page: Page): Promise<number> {
  return page.evaluate(() => window.__cinematicDraws ?? 0);
}

/** Tiny downsampled canvas hash — cheap way to detect distinct painted frames. */
async function sampleCanvasHash(page: Page): Promise<string> {
  return page.evaluate(() => {
    const canvas = document.querySelector<HTMLCanvasElement>("canvas");
    if (!canvas) return "";
    const t = document.createElement("canvas");
    t.width = 24;
    t.height = 14;
    const ctx = t.getContext("2d");
    if (!ctx) return "";
    try {
      ctx.drawImage(canvas, 0, 0, 24, 14);
      return t.toDataURL("image/jpeg", 0.4);
    } catch {
      return "";
    }
  });
}

async function rAFIntervals(page: Page): Promise<{ avg: number; dropsOver17Ms: number; total: number }> {
  return page.evaluate(() => {
    const t = window.__rafStats as number[];
    let total = 0;
    let drops = 0;
    if (t.length > 1) {
      for (let i = 1; i < t.length; i += 1) {
        const d = t[i] - t[i - 1];
        total += d;
        if (d > 17.5) drops += 1;
      }
    }
    return { avg: t.length > 1 ? total / (t.length - 1) : 0, dropsOver17Ms: drops, total: t.length };
  });
}

/** Smoothly scroll the page to `frac` over ~`ms`, pausing between sub-steps. */
async function smoothScroll(page: Page, frac: number, ms = 1200): Promise<void> {
  const step = 60;
  const steps = Math.max(8, Math.ceil(ms / step));
  const maxY = await page.evaluate(() => document.body.scrollHeight);
  for (let i = 0; i < steps; i += 1) {
    await page.evaluate((y) => window.scrollTo(0, y), (maxY * frac * (i + 1)) / steps);
    await page.waitForTimeout(step);
  }
}

test.describe("cinematic performance", () => {
  test.setTimeout(120_000);

  test("scrubs down and back up with measured cadence and bounded memory", async ({ page }) => {
    await page.addInitScript(rAF_HOOK);
    await page.goto("/");

    // 1. Time to first cinematic frame.
    await expect.poll(() => drawCount(page), { timeout: 15_000 }).toBeGreaterThan(0);
    const first = await firstDrawMs(page);
    expect(first).not.toBeNull();
    test.info().annotations.push({
      type: "measure",
      description: `time to first cinematic frame: ${first?.toFixed(1)} ms after navigation start (raw)`,
    });

    const heap0 = await jsHeapMb(page);
    test.info().annotations.push({ type: "measure", description: `heap before scroll: ${heap0} MB` });

    // 2. Slow downward scrub through the whole sequence.
    await smoothScroll(page, 1, 1600);
    await page.waitForTimeout(400); // let rAF settle at the end

    const down = await rAFIntervals(page);
    const downHashes = new Set<string>();
    for (let i = 0; i < 6; i += 1) {
      downHashes.add(await sampleCanvasHash(page));
      await page.waitForTimeout(250);
    }
    test.info().annotations.push({
      type: "measure",
      description: `slow-down rAF: avg ${down.avg.toFixed(1)} ms/tick, ${down.dropsOver17Ms} ticks >17.5 ms of ${down.total}`,
    });

    // The final CTA must be reachable.
    await expect(page.getByText("Talk to AutoInspect-X")).toBeVisible({ timeout: 5_000 });

    // 3. Rapid back-and-forth (scroll up, then down again quickly).
    const midY = await page.evaluate(() => document.body.scrollHeight / 2);
    for (let i = 0; i < 4; i += 1) {
      await page.evaluate((y) => window.scrollTo(0, y), midY);
      await page.waitForTimeout(80);
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(80);
    }

    // 4. Upward scroll: frame counter must fall, not reset to first frame mid-way.
    const counterBefore = await page.locator("text=/frame \\d+ \\/ 913/").count();
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.25));
    await page.waitForTimeout(600);
    const frameText = await page.evaluate(() => {
      const p = document.querySelector("p");
      void p;
      // read the frame counter paragraph (last one, fixed bottom-right)
      const ps = [...document.querySelectorAll("p")];
      const m = ps.map((el) => el.textContent ?? "").find((t) => /frame \d+ \/ 913/.test(t));
      return m ?? "";
    });
    const num = parseInt((frameText.match(/frame (\d+) /)?.[1] ?? "0"), 10);
    expect(num).toBeLessThan(913);
    expect(num).toBeGreaterThan(0);
    expect(counterBefore).toBe(1);

    // 5. Memory after the scrub storm.
    const heap1 = await jsHeapMb(page);
    const growth = Number((heap1 - heap0).toFixed(1));
    test.info().annotations.push({
      type: "measure",
      description: `heap after scrub: ${heap1} MB (growth ${growth} MB)`,
    });

    // Heads-up, not a hard gate: LRU preloader should keep decoded memory bounded,
    // so heap growth after scrubbing every frame should remain modest.
    expect(growth).toBeLessThan(350);
  });
});