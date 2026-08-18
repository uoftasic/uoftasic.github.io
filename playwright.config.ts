import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: 0,
  workers: 1,
  reporter: "list",
  use: {
    baseURL: "http://127.0.0.1:4000",
    trace: "off",
    screenshot: "off",
  },
  projects: [
    {
      name: "desktop",
      use: { ...devices["Desktop Chrome"], viewport: { width: 1440, height: 900 } },
    },
    {
      name: "mobile",
      use: {
        ...devices["Desktop Chrome"],
        viewport: { width: 390, height: 844 },
        isMobile: true,
        hasTouch: true,
      },
    },
  ],
  // Serves the already-built site rather than invoking Jekyll, so the suite runs
  // the same way whether the build came from a local Ruby install or Docker.
  // Build first: `npm run build`.
  webServer: {
    command: "python3 -m http.server 4000 --bind 127.0.0.1 --directory _site",
    url: "http://127.0.0.1:4000",
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
