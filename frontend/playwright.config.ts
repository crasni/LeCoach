import { resolve } from 'node:path';
import { defineConfig } from '@playwright/test';

const lecoach = process.platform === 'win32'
  ? `"${resolve('..', '.venv', 'Scripts', 'lecoach.exe')}"` : '../.venv/bin/lecoach';

export default defineConfig({
  testDir: './e2e',
  timeout: 30000,
  workers: 1,
  use: {
    baseURL: 'http://127.0.0.1:8000',
    launchOptions: process.env.LECOACH_CHROMIUM_PATH
      ? { executablePath: process.env.LECOACH_CHROMIUM_PATH } : {},
  },
  webServer: {
    command: `${lecoach} serve`,
    url: 'http://127.0.0.1:8000/api/health',
    timeout: 15000,
    reuseExistingServer: false,
  },
});
