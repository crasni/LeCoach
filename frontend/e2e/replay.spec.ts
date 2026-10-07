import { expect, test } from '@playwright/test';

test('replay shows authored reactions and coaching and keeps all requests local', async ({ page }) => {
  const remoteRequests: string[] = [];
  const browserErrors: string[] = [];
  page.on('request', request => {
    if (!request.url().startsWith('http://127.0.0.1:8000')) remoteRequests.push(request.url());
  });
  page.on('pageerror', error => browserErrors.push(error.message));
  await page.goto('/');
  await expect(page.getByText('Synthetic replay', { exact: true })).toBeVisible();
  await page.getByRole('button', { name: 'Start replay' }).click();
  await expect(page.getByTestId('audience-state')).toHaveText('CONFUSED', { timeout: 12000 });
  await expect(page.getByTestId('audience-state')).toHaveText('BORED', { timeout: 5000 });
  await expect(page.getByTestId('audience-state')).toHaveText('ENGAGED', { timeout: 5000 });
  await expect(page.getByRole('region', { name: 'Example coaching' })).toBeVisible();
  await expect(page.getByText('Keep doing this', { exact: true })).toBeVisible();
  await expect(page.getByText('Try next time', { exact: true })).toHaveCount(2);
  await expect(page.getByRole('button', { name: 'Start replay' })).toBeEnabled();
  expect(remoteRequests).toEqual([]);
  expect(browserErrors).toEqual([]);
});

test('stop, repeat and delayed transcript remain isolated', async ({ page }) => {
  await page.goto('/');
  await page.getByRole('button', { name: 'Start replay' }).click();
  await expect(page.getByRole('button', { name: 'Stop', exact: true })).toBeEnabled();
  await page.getByRole('button', { name: 'Stop', exact: true }).click();
  await expect(page.getByText('Replay stopped early. The authored example summary is unavailable.')).toBeVisible();
  await page.getByLabel('Example', { exact: true }).selectOption('late_final_and_duplicates');
  await page.getByRole('button', { name: 'Start replay' }).click();
  await expect(page.getByRole('region', { name: 'Example coaching' })).toBeVisible({ timeout: 10000 });
  await expect(page.locator('.transcript')).toHaveText('Our synthetic example is ready.');
  await expect(page.locator('.transcript')).not.toContainText('foreign');
  await expect(page.getByText('No supported coaching moments in this example.')).toBeVisible();
});

test('empty session completes and narrow layout fits', async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto('/');
  await page.getByLabel('Example', { exact: true }).selectOption('empty_session');
  await page.getByRole('button', { name: 'Start replay' }).click();
  await expect(page.getByRole('region', { name: 'Example coaching' })).toBeVisible();
  await expect(page.getByRole('button', { name: 'Start replay' })).toBeEnabled();
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
});

test('a connection interruption resynchronizes without restarting playback', async ({ page }) => {
  let startRequests = 0;
  page.on('request', request => {
    if (request.url().endsWith('/start')) startRequests += 1;
  });
  await page.addInitScript(() => {
    const OriginalWebSocket = window.WebSocket;
    window.WebSocket = class extends OriginalWebSocket {
      constructor(url: string, protocols?: string | string[]) {
        super(url, protocols);
        (window as unknown as { lastSocket: WebSocket }).lastSocket = this;
      }
    };
  });
  await page.goto('/');
  await page.getByRole('button', { name: 'Start replay' }).click();
  await expect(page.getByRole('button', { name: 'Stop', exact: true })).toBeEnabled();
  await page.evaluate(() => {
    (window as unknown as { lastSocket: WebSocket }).lastSocket.close(4000, 'test interruption');
  });
  await expect(page.getByText('Connected locally', { exact: true })).toBeVisible();
  await expect(page.getByRole('region', { name: 'Example coaching' })).toBeVisible({ timeout: 15000 });
  expect(startRequests).toBe(1);
});
