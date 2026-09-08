import { existsSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "@playwright/test";

import { openDemo, reachPhotoStage, uploadFile } from "./helpers";
import { blurryImage, validImage } from "./png";

// The committed demo checkpoint is git-ignored (ml/experiments/), exactly like
// the pytest engine test that skips when it is absent. These journeys need the
// real engine, so they only run where the checkpoint is present.
const CHECKPOINT = resolve("../../ml/experiments/cardd_baseline_ce/best_checkpoint.pt");
const hasCheckpoint = existsSync(CHECKPOINT);

/**
 * Full browser journey against the real backend engine. Asserts the honesty
 * contract in the UI: no fabricated quote, explicit provenance chips, retake
 * guidance on a rejected photo, consent, finish.
 */
test.describe("inspection journey", () => {
  test("full happy path with honest labels", async ({ page }, testInfo) => {
    test.setTimeout(300_000);
    test.skip(testInfo.project.name !== "desktop", "engine journey runs once on desktop");
    test.skip(!hasCheckpoint, "committed demo checkpoint not present");

    await openDemo(page);
    await reachPhotoStage(page);

    await uploadFile(page, validImage(), "car.png");

    // The engine runs: model findings, cost honesty, repair rule, context.
    await expect(page.getByRole("heading", { name: "What the model found" })).toBeVisible({
      timeout: 120_000,
    });
    await expect(page.getByText("No real quote is available.")).toBeVisible();
    await expect(page.getByText("Demo rule").first()).toBeVisible();
    await expect(page.getByText("What you told us")).toBeVisible();
    await expect(page.getByText(/Provenance: user/i)).toBeVisible();

    // Optional consent.
    await expect(page.getByRole("heading", { name: "Help improve the model?" })).toBeVisible();
    await page.getByRole("button", { name: "Yes, keep it for training" }).click();

    // Finish closes the session.
    await expect(page.getByRole("button", { name: "Finish and show summary" })).toBeVisible();
    await page.getByRole("button", { name: "Finish and show summary" }).click();
    await expect(page.getByRole("heading", { name: "Inspection complete" })).toBeVisible();
  });

  test("poor-quality photo is rejected with retake guidance, then succeeds", async ({ page }, testInfo) => {
    test.setTimeout(300_000);
    test.skip(testInfo.project.name !== "desktop", "engine journey runs once on desktop");
    test.skip(!hasCheckpoint, "committed demo checkpoint not present");

    await openDemo(page);
    await reachPhotoStage(page);

    await uploadFile(page, blurryImage(), "car-blurry.png");
    await expect(
      page.getByText("Your photo looks blurry. Hold the phone steady and retake close up."),
    ).toBeVisible({ timeout: 60_000 });

    // Retake with a valid photo proceeds.
    await uploadFile(page, validImage(), "car.png");
    await expect(page.getByRole("heading", { name: "What the model found" })).toBeVisible({
      timeout: 120_000,
    });
  });
});