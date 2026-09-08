import { defineConfig, devices } from "@playwright/test";

const port = 3000;
const baseURL = `http://localhost:${port}`;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  workers: 1,
  retries: 1,
  timeout: 90_000,
  expect: { timeout: 15_000 },
  reporter: [["list"]],
  use: {
    baseURL,
    channel: "chrome",
    headless: true,
    trace: "retain-on-failure",
  },
  projects: [
    { name: "desktop", use: { viewport: { width: 1280, height: 900 } } },
    { name: "tablet", use: { viewport: { width: 768, height: 1024 }, hasTouch: true } },
    {
      name: "mobile",
      use: {
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
        userAgent: devices["iPhone 13"].userAgent,
      },
    },
  ],
  webServer: [
    {
      // Backend on :8000 (ai conda env). With the prod checkpoints removed the
      // suite should still pass for every test outside the real-engine happy
      // path; set BACKEND_CMD to override for CI.
      command:
        process.env.BACKEND_CMD ??
        "bash -lc 'source ~/miniconda3/etc/profile.d/conda.sh && conda activate ai && exec uvicorn apps.api.main:app --port 8000 --log-level warning'",
      cwd: "../..",
      url: "http://localhost:8000/health",
      reuseExistingServer: true,
      timeout: 90_000,
    },
    {
      command: "npm run start -- -p 3000",
      cwd: ".",
      url: baseURL,
      reuseExistingServer: true,
      timeout: 90_000,
    },
  ],
});