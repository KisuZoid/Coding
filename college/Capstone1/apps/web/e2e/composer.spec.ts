import { expect, test } from "@playwright/test";

import { COMPOSER_PLACEHOLDER, openDemo, sendTurn } from "./helpers";
import { validImage } from "./png";

/**
 * Composer interactions that need no engine checkpoint: text chat turns, the
 * attach preview + remove gesture, and send enablement. These run on every
 * project (desktop/tablet/mobile) so the offline/slow network path is covered.
 */
test.describe("demo composer", () => {
  test("text turn renders user and assistant bubbles", async ({ page }) => {
    await openDemo(page);

    await sendTurn(page, "Hello, what can you tell me about damage?");
    await expect(page.locator('div[data-message-role="user"]').first()).toBeVisible();
    await expect(page.locator('div[data-message-role="assistant"]').first()).toBeVisible();
  });

  test("attach preview appears and can be removed without sending", async ({ page }) => {
    await openDemo(page);

    const send = page.getByRole("button", { name: "Send" });
    await expect(send).toBeDisabled();

    await page.setInputFiles("input[type=file]", {
      name: "preview.png",
      mimeType: "image/png",
      buffer: validImage(),
    });
    await expect(page.getByAltText("Attached photo preview")).toBeVisible();
    await expect(send).toBeEnabled();

    await page.getByRole("button", { name: "Remove attached photo" }).click();
    await expect(page.getByAltText("Attached photo preview")).toHaveCount(0);
    await expect(send).toBeDisabled();
    await expect(page.getByPlaceholder(COMPOSER_PLACEHOLDER)).toBeEnabled();
  });
});