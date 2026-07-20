import { defineConfig, devices } from '@playwright/test';

/**
 * E2E configuration for the SPA happy path (import -> read -> test -> cert).
 *
 * IMPORTANT — this suite is OPT-IN and SKIPS gracefully when not enabled:
 *   - Playwright and its browsers are NOT installed by default.
 *   - Without RUN_E2E=1 (and a reachable backend + built SPA) every spec
 *     calls test.skip() so a local `npm run build` / `npm run test:e2e`
 *     exits cleanly (no failure on machines without a browser).
 *
 * To run it for real:
 *   npm install
 *   npm install -D @playwright/test
 *   npx playwright install chromium
 *   RUN_E2E=1 npx playwright test        # or: npm run test:e2e
 *
 * The backend must be running (see README) and the SPA built/served.
 */
export default defineConfig({
  testDir: './e2e',
  timeout: 60_000,
  expect: { timeout: 10_000 },
  retries: 0,
  use: {
    baseURL: process.env.FRONTEND_BASE_URL || 'http://localhost:5173',
    headless: true,
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
  ],
});
