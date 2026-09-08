import { type Page, expect } from "@playwright/test";

/**
 * Shared navigation for the demo suite. The chat preamble mirrors the backend
 * E2E journey (tests/test_e2e_integration.py): incident -> repair location ->
 * insurance -> photo capture.
 *
 * `sendTurn` is race-tolerant: the very first send can arrive before the demo
 * has created its session (runTurn silently drops it without adding a bubble).
 * We detect that by counting the user's amber bubbles and retry the message.
 */

const USER_BUBBLE = "div.bg-amber-400";

export async function openDemo(page: Page): Promise<void> {
  await page.goto("/");
  await expect(page.getByText("AutoInspect-X").first()).toBeVisible();
  await page.getByRole("link", { name: "Skip to demo" }).click();
  await expect(page.getByText("API online")).toBeVisible();
  await expect(page.getByPlaceholder("Type your reply")).toBeVisible();
}

export async function sendTurn(page: Page, text: string): Promise<void> {
  const input = page.getByPlaceholder("Type your reply");
  const bubbles = page.locator(USER_BUBBLE);
  for (let attempt = 0; attempt < 3; attempt++) {
    const before = await bubbles.count();
    await expect(input).toBeEnabled();
    await input.fill(text);
    await input.press("Enter");
    try {
      await expect(bubbles).toHaveCount(before + 1, { timeout: 5_000 });
      await expect(input).toBeEnabled();
      return;
    } catch {
      // Run dropped (session was still being created) — resend once ready.
      await page.waitForTimeout(1_000);
    }
  }
  throw new Error(`failed to deliver chat turn: ${text}`);
}

/** Advances the conversation to the photo-capture stage. */
export async function reachPhotoStage(page: Page): Promise<void> {
  for (const turn of ["I hit a pothole and scraped the front bumper", "not sure yet", "no insurance claim"]) {
    await sendTurn(page, turn);
  }
  await expect(page.getByRole("heading", { name: "Photo of the damage" })).toBeVisible();
}

export async function uploadFile(page: Page, buffer: Buffer, name: string): Promise<void> {
  await page.setInputFiles("input[type=file]", { name, mimeType: "image/png", buffer });
}