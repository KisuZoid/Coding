import { defineConfig, devices } from "@playwright/test";

const port = 3000;
const baseURL = `http://localhost:${port}`;

// Hermetic by default: the backend webServer starts its OWN key-blanked
// StubAssistant-backed API on :8000 and never silently reuses a running one,
// so browser tests can't accidentally hit a live Groq server. To deliberately
// run against an already-running backend (e.g. the fixed dev API), set
// REUSE_BACKEND=1 and optionally BACKEND_URL / BACKEND_CMD.
const backendUrl = process.env.BACKEND_URL ?? "http://localhost:8000";

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
      // Backend on :8000 (ai conda env). The Groq key is blanked so the suite
      // runs hermetic against the offline StubAssistant (same rule as the
      // pytest conftest). Set BACKEND_CMD / BACKEND_URL to override for CI or a
      // live test, and REUSE_BACKEND=1 to target an already-running API.
      command:
        process.env.BACKEND_CMD ??
        "bash -lc 'source ~/miniconda3/etc/profile.d/conda.sh && conda activate ai && exec env GROQ_AUTO_INSPECT_API_KEY= uvicorn apps.api.main:app --port 8000 --log-level warning'",
      cwd: "../..",
      url: `${backendUrl}/health`,
      reuseExistingServer: process.env.REUSE_BACKEND === "1",
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