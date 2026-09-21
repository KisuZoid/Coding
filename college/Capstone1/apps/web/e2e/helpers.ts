import { type Page, expect } from "@playwright/test";

/**
 * Shared navigation for the demo suite (photo-first flow, ADR 0011): open the
 * demo, send chat turns, and attach+send photos from the composer. There is no
 * questionnaire to reach first.
 *
 * `sendTurn` is race-tolerant: the very first send can arrive before the demo
 * has created its session (the composer only submits when a session exists, so
 * mostly this matters on slow CI). We detect delivery by counting the user's
 * amber bubbles and retry the message.
 */

const USER_BUBBLE = "div.bg-amber-400";
export const COMPOSER_PLACEHOLDER = "Ask or attach a photo of the damage";

export async function openDemo(page: Page): Promise<void> {
  await page.goto("/");
  await expect(page.getByText("AutoInspect-X").first()).toBeVisible();
  await page.getByRole("link", { name: "Skip to demo" }).click();
  await expect(page.getByText("API online")).toBeVisible();
  await expect(page.getByPlaceholder(COMPOSER_PLACEHOLDER)).toBeVisible();
}

export async function sendTurn(page: Page, text: string): Promise<void> {
  const input = page.getByPlaceholder(COMPOSER_PLACEHOLDER);
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

/**
 * Attaches a photo and presses Send. Asserts the user bubble grew by one and
 * the composer returned to an idle, enabled state (analysis runs server-side).
 */
export async function sendPhoto(page: Page, buffer: Buffer, name: string): Promise<void> {
  const input = page.getByPlaceholder(COMPOSER_PLACEHOLDER);
  const bubbles = page.locator(USER_BUBBLE);
  const before = await bubbles.count();
  await page.setInputFiles("input[type=file]", { name, mimeType: "image/png", buffer });
  await expect(page.getByAltText("Attached photo preview")).toBeVisible();
  await page.getByRole("button", { name: "Send" }).click();
  await expect(bubbles).toHaveCount(before + 1, { timeout: 10_000 });
  await expect(input).toBeEnabled();
}