import { defineConfig, devices } from '@playwright/test'

/** Must match `PUBLIC_API_URL` baked into the booking page script (dev server env below). */
const mockApiOrigin = 'http://127.0.0.1:3001'

/** Dedicated port so `bun run test:e2e` does not fight `astro dev` on 4321. */
const e2eSitePort = 4329

export default defineConfig({
  testDir: './e2e',
  /** Bun also runs `*.spec.ts` / `*.test.ts`; keep Playwright files named `*.e2e.ts`. */
  testMatch: '**/*.e2e.ts',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  reporter: [['list']],
  use: {
    baseURL: `http://127.0.0.1:${e2eSitePort}`,
    trace: 'on-first-retry',
  },
  projects: [{ name: 'chromium', use: { ...devices['Desktop Chrome'] } }],
  webServer: {
    command: `bun run dev -- --host 127.0.0.1 --port ${e2eSitePort}`,
    url: `http://127.0.0.1:${e2eSitePort}/booking`,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
    env: {
      ...process.env,
      PUBLIC_API_URL: mockApiOrigin,
    },
  },
})
