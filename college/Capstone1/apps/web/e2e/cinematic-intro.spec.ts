import { expect, test } from "@playwright/test";

const BASE = "http://localhost:3000";

/** Smoke-test the scroll-driven cinematic image-sequence intro. */
test.describe("cinematic intro", () => {
  test("renders and responds to scroll on desktop", async ({ page }) => {
    test.setTimeout(30_000);
    await page.goto(BASE);

    // Hero: the AutoInspect-X brand must be visible.
    await expect(page.getByText("AutoInspect-X").first()).toBeVisible();

    // The canvas must be present and attached.
    const canvas = page.locator("canvas");
    await expect(canvas).toBeAttached();

    // Scroll hint shows on load.
    await expect(page.getByText("Scroll", { exact: true })).toBeVisible();

    // Scroll to midpoint: the frame counter should show a value between 1 and TOTAL.
    // The counter is styled `hidden sm:block`, so only assert it on ≥640px viewports.
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight * 0.5));
    await page.waitForTimeout(600); // allow rAF to settle
    if ((page.viewportSize()?.width ?? 0) >= 640) {
      const counter = page.locator("text=/frame \\d+ \\/ 913/");
      await expect(counter).toBeVisible({ timeout: 5_000 });
    }

    // Scroll to the very bottom: the CTA must appear.
    await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
    await page.waitForTimeout(800);
    await expect(page.getByText("Talk to AutoInspect-X")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByRole("link", { name: "Start Inspection" })).toBeVisible();
  });

  test("canvas exists on mobile viewport", async ({ page }) => {
    test.setTimeout(20_000);
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto(BASE);
    await expect(page.locator("canvas")).toBeAttached();
  });
});
