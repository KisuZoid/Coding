import { expect, test } from "@playwright/test";

import { COMPOSER_PLACEHOLDER, expectConnectionOnline, openDemo } from "./helpers";

/**
 * Lightweight responsiveness checks on all viewport projects: the intro and
 * the demo shell render correctly and the API badge reflects real connectivity.
 */
test.describe("responsive shell", () => {
  test("landing and demo shell render on every viewport", async ({ page }) => {
    await openDemo(page);
    await expect(page.getByPlaceholder(COMPOSER_PLACEHOLDER)).toBeVisible();
    await expect(page.getByRole("button", { name: "New inspection" })).toBeVisible();
    await expectConnectionOnline(page);
  });
});