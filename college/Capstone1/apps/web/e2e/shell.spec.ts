import { existsSync } from "node:fs";
import { resolve } from "node:path";

import { expect, test } from "@playwright/test";

import { COMPOSER_PLACEHOLDER, openDemo, sendPhoto, sendTurn } from "./helpers";
import { validImage } from "./png";

// Engine-gated journeys need the committed (but git-ignored) demo checkpoint,
// like tests/test_e2e_integration.py and the inspection journey.
const CHECKPOINT = resolve("../../ml/experiments/cardd_hybrid_ce/best_checkpoint.pt");
const hasCheckpoint = existsSync(CHECKPOINT);

/**
 * The chat/workspace shell (ADR 0011 photo-first UI): full-viewport app shell,
 * clickable top-left brand, bottom-anchored composer, inline photo attachment,
 * and chat that continues inside the same conversation after an analysis.
 */
test.describe("application shell", () => {
  test("brand lockup navigates /demo → / → /demo", async ({ page }) => {
    await openDemo(page);

    // Brand lockup in the demo header returns to the cinematic intro.
    await page.getByRole("link", { name: /AutoInspect-X/ }).click();
    await expect(page).toHaveURL("/");
    await expect(page.getByText("Scroll")).toBeVisible();

    // Existing intro CTA returns to the inspection workspace.
    await page.getByRole("link", { name: "Skip to demo" }).click();
    await expect(page.getByRole("button", { name: "New inspection" })).toBeVisible();
    await expect(page.getByPlaceholder(COMPOSER_PLACEHOLDER)).toBeVisible();
  });

  test("shell fills the viewport without a page-level scrollbar", async ({ page }) => {
    await openDemo(page);
    const shell = page.locator("[data-shell]");
    const box = await shell.boundingBox();
    expect(box).not.toBeNull();
    const vh = await page.evaluate(() => window.innerHeight);
    expect(box!.height).toBeGreaterThanOrEqual(vh - 2);

    const pageScrollOverflow = await page.evaluate(
      () => document.documentElement.scrollHeight - document.documentElement.clientHeight,
    );
    expect(pageScrollOverflow).toBeLessThanOrEqual(1);
  });

  test("composer stays anchored near the viewport bottom", async ({ page }) => {
    await openDemo(page);
    const input = page.getByPlaceholder(COMPOSER_PLACEHOLDER);
    await expect(input).toBeVisible();
    const box = await input.boundingBox();
    expect(box).not.toBeNull();
    const vh = await page.evaluate(() => window.innerHeight);
    expect(vh - (box!.y + box!.height)).toBeLessThan(160);
  });

  test("photo attaches inline with a ready-to-analyze state and can be removed", async ({ page }, testInfo) => {
    test.skip(testInfo.project.name !== "desktop", "attachment workflow exercised on desktop");
    await openDemo(page);
    await page.setInputFiles("input[type=file]", {
      name: "damage.png",
      mimeType: "image/png",
      buffer: validImage(),
    });
    await expect(page.getByAltText("Attached photo preview")).toBeVisible();
    await expect(page.getByText("Photo attached — ready to analyze")).toBeVisible();

    await page.getByRole("button", { name: "Remove attached photo" }).click();
    await expect(page.getByAltText("Attached photo preview")).toHaveCount(0);
  });

  test("text chat turns continue inside the same conversation", async ({ page }) => {
    await openDemo(page);
    const assistantRows = page.locator('[data-message-role="assistant"]');
    await sendTurn(page, "Hello, can you help me inspect my car?");
    await sendTurn(page, "What do I need to upload?");
    await expect(assistantRows).not.toHaveCount(0);
  });
});

test.describe("post-analysis chat", () => {
  test("follow-up chat after an analysis stays in the main chat", async ({ page }, testInfo) => {
    test.setTimeout(300_000);
    test.skip(testInfo.project.name !== "desktop", "engine journey runs once on desktop");
    test.skip(!hasCheckpoint, "committed checkpoint not present");

    await openDemo(page);
    await sendPhoto(page, validImage(), "car.png");
    const overlay = page.getByAltText("Model overlay of the detected damage");
    await expect(overlay).toBeVisible({ timeout: 180_000 });

    const assistantRows = page.locator('[data-message-role="assistant"]');
    const before = await assistantRows.count();
    await sendTurn(page, "Is the glass damage severe?");
    await expect(assistantRows).toHaveCount(before + 1, { timeout: 30_000 });
    await expect(overlay).toBeVisible();
  });
});