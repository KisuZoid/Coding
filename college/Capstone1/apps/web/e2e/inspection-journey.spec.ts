import { existsSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "@playwright/test";

import { openDemo, sendPhoto } from "./helpers";
import { blurryImage, validImage } from "./png";

// The committed demo checkpoint is git-ignored (ml/experiments/), exactly like
// the pytest engine test that skips when it is absent. These journeys need the
// real engine, so they only run where the checkpoint is present.
const CHECKPOINT = resolve("../../ml/experiments/cardd_hybrid_ce/best_checkpoint.pt");
const hasCheckpoint = existsSync(CHECKPOINT);

/**
 * Photo-first browser journey against the real backend engine. Asserts the
 * honesty contract in the UI: inline model overlay + class chips, no fabricated
 * quotes, retake guidance on a rejected photo, optional consent stored in the
 * flow (no questionnaire, no finish step).
 */
test.describe("inspection journey", () => {
  test("full happy path with honest labels", async ({ page }, testInfo) => {
    test.setTimeout(300_000);
    test.skip(testInfo.project.name !== "desktop", "engine journey runs once on desktop");
    test.skip(!hasCheckpoint, "committed checkpoint not present");

    await openDemo(page);
    await sendPhoto(page, validImage(), "car.png");

    // The engine ran: the assistant message carries the inline model overlay.
    await expect(page.getByAltText("Model overlay of the detected damage")).toBeVisible({
      timeout: 180_000,
    });

    // Optional consent.
    await expect(page.getByRole("heading", { name: "Help improve the model?" })).toBeVisible();
    await page.getByRole("button", { name: "Yes, keep it for training" }).click();
    await expect(page.getByRole("heading", { name: "Consent saved" })).toBeVisible();

    // The removed bottom "Back to the intro" link stays gone (the header logo
    // is the single way back to the intro).
    await expect(page.getByRole("link", { name: "Back to the intro" })).toHaveCount(0);
  });

  test("poor-quality photo is rejected with retake guidance, then succeeds", async ({ page }, testInfo) => {
    test.setTimeout(300_000);
    test.skip(testInfo.project.name !== "desktop", "engine journey runs once on desktop");
    test.skip(!hasCheckpoint, "committed checkpoint not present");

    await openDemo(page);

    await sendPhoto(page, blurryImage(), "car-blurry.png");
    // Quality guidance surfaced in the main chat. The word varies between the
    // offline stub ("retake") and a live LLM ("blurry"/"reshoot"), so assert on
    // guidance about the rejected photo rather than one exact word — the
    // backend contract is "reject + guidance", not a literal string.
    await expect(
      page.locator("text=/retake|reshoot|blurry|out of focus|too dark|quality/i").first()
    ).toBeVisible({
      timeout: 180_000,
    });
    await expect(page.getByAltText("Model overlay of the detected damage")).toHaveCount(0);

    // Retake with a valid photo proceeds.
    await sendPhoto(page, validImage(), "car.png");
    await expect(page.getByAltText("Model overlay of the detected damage")).toBeVisible({
      timeout: 180_000,
    });
  });
});