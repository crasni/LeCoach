import { expect, test, type WebSocketRoute } from '@playwright/test';

// Failure-state checks with a scripted local backend: the page's HTTP and WebSocket
// traffic is answered in the browser, so exact event sequences can be replayed.

const SESSION = 'ui-state-session';

function snapshot(phase: string, extra: object = {}) {
  return {
    session_id: SESSION, mode: 'fixture', phase, elapsed_s: 0, duration_s: null,
    incomplete_sources: [],
    input_status: {
      speech: { availability: 'unavailable', reason: 'not_started' },
      vision: { availability: 'unavailable', reason: 'not_started' },
    },
    latest_events: {}, transcript: [], feedback_status: 'pending',
    output_provenance: 'computed', error: null, ...extra,
  };
}

function envelope(event_id: string, source: string, type: string, timestamp_s: number, payload: object) {
  return { kind: 'event', event: {
    schema_version: 0, session_id: SESSION, event_id, source, type, timestamp_s, payload } };
}

const speechMetrics = (id: string, end: number, wpm: number) => envelope(id, 'speech', 'speech.metrics', end, {
  window_start_s: Math.max(0, end - 10), window_end_s: end, availability: 'available', wpm,
  filler_count: 0, filler_rate_per_min: 0,
  pause: { state: 'none', duration_s: 0, start_s: null, end_s: null },
});
const status = (id: string, source: string, at: number, availability: string, reason: string) =>
  envelope(id, source, 'signal.status', at, { availability, reason });
const neutral = (id: string, at: number, usable: string[]) => envelope(id, 'engagement', 'engagement.state', at, {
  state: 'NEUTRAL', previous_state: 'NEUTRAL', reasons: [], usable_sources: usable });
const utterance = (id: string, start: number, end: number, text: string) =>
  envelope(id, 'speech', 'speech.transcript', end, {
    utterance_id: id, revision: 0, is_final: true, start_s: start, end_s: end, text });

test('mid-session outages blank stale values and statuses read plainly', async ({ page }) => {
  let socket: WebSocketRoute | undefined;
  await page.route('**/api/health', route => route.fulfill({ json: { live_integrated: false } }));
  await page.route('**/api/fixtures', route => route.fulfill({
    json: [{ name: 'weak_to_improved', description: 'scripted', session_count: 1 }] }));
  await page.route('**/api/sessions', route => route.fulfill({ status: 201, json: snapshot('prepared') }));
  await page.route(`**/api/sessions/${SESSION}/start`, route => route.fulfill({ json: snapshot('running') }));
  await page.routeWebSocket(/\/api\/sessions\/.*\/events/, ws => {
    socket = ws;
    ws.send(JSON.stringify({ kind: 'snapshot', snapshot: snapshot('prepared') }));
  });
  const send = (message: object) => socket!.send(JSON.stringify(message));

  await page.goto('/');
  await page.getByRole('button', { name: 'Start replay' }).click();
  await expect.poll(() => socket).toBeTruthy();
  send({ kind: 'snapshot', snapshot: snapshot('running') });
  send(neutral('engagement-0', 0, []));
  const reaction = page.locator('.reaction');
  await expect(reaction).toContainText('Waiting for usable speech or camera input.');

  // Input arrives without an audience transition: the waiting message must clear.
  send(speechMetrics('metrics-5', 5, 150));
  await expect(page.getByText('Microphone: Receiving')).toBeVisible();
  await expect(page.locator('.metrics')).toContainText('150 WPM');
  await expect(reaction).not.toContainText('Waiting for usable');

  // The microphone drops mid-session: its last value must not stay on screen.
  send(status('mic-lost', 'speech', 6, 'error', 'microphone_disconnected'));
  await expect(page.getByText('Microphone: Microphone disconnected')).toBeVisible();
  await expect(page.locator('.metrics')).not.toContainText('WPM');
  await expect(reaction).toContainText('Waiting for usable speech or camera input.');

  // A late observation captured before the outage does not revive the old value. The
  // pose status is sent after it, so once that is visible the late event was applied.
  send(speechMetrics('metrics-5.5', 5.5, 160));
  send(status('pose', 'vision', 6.5, 'unavailable', 'pose_runtime_missing'));
  await expect(page.getByText('Camera: Pose software not installed')).toBeVisible();
  await expect(page.getByText('Microphone: Microphone disconnected')).toBeVisible();
  await expect(page.locator('.metrics')).not.toContainText('WPM');

  // Later unavailable windows keep the specific reason, and a recovery status alone
  // does not bring back the pre-outage pace.
  send(envelope('metrics-7', 'speech', 'speech.metrics', 7, {
    window_start_s: 0, window_end_s: 7, availability: 'error', wpm: null, filler_count: null,
    filler_rate_per_min: null, pause: { state: 'unknown', duration_s: null, start_s: null, end_s: null } }));
  send(status('mic-back', 'speech', 8, 'available', 'capture_started'));
  await expect(page.getByText('Microphone: Starting')).toBeVisible();
  await expect(page.locator('.metrics')).not.toContainText('WPM');
  send(speechMetrics('metrics-9', 9, 140));
  await expect(page.locator('.metrics')).toContainText('140 WPM');

  // Utterances delivered out of order still read in capture order.
  send(utterance('u2', 3, 4, 'second'));
  send(utterance('u1', 1, 2, 'first'));
  await expect(page.locator('.transcript')).toHaveText('first second');
});

const PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==',
  'base64');

test('live preview waits for the camera, retries, and hides a failed camera', async ({ page }) => {
  let socket: WebSocketRoute | undefined;
  let previewRequests = 0;
  const live = (phase: string) => ({ ...snapshot(phase), mode: 'live' });
  await page.route('**/api/health', route => route.fulfill({ json: { live_integrated: true } }));
  await page.route('**/api/fixtures', route => route.fulfill({ json: [] }));
  await page.route('**/api/sessions', route => route.fulfill({ status: 201, json: live('prepared') }));
  await page.route(`**/api/sessions/${SESSION}/start`, route => route.fulfill({ json: live('running') }));
  await page.route(`**/api/sessions/${SESSION}/preview*`, route => {
    previewRequests += 1;
    return previewRequests === 1
      ? route.fulfill({ status: 503, json: { detail: 'preview_unavailable' } })
      : route.fulfill({ status: 200, contentType: 'image/png', body: PNG });
  });
  await page.routeWebSocket(/\/api\/sessions\/.*\/events/, ws => {
    socket = ws;
    ws.send(JSON.stringify({ kind: 'snapshot', snapshot: live('prepared') }));
  });
  const send = (message: object) => socket!.send(JSON.stringify(message));

  await page.goto('/');
  await page.getByLabel('Example', { exact: true }).selectOption({ label: 'Live microphone and camera' });
  await page.getByRole('button', { name: 'Start rehearsal' }).click();
  await expect.poll(() => socket).toBeTruthy();
  send({ kind: 'snapshot', snapshot: live('running') });
  await expect(page.getByText('Live rehearsal', { exact: true })).toBeVisible();
  await expect(page.getByText('Camera preview unavailable')).toBeVisible();
  expect(previewRequests).toBe(0);  // No camera yet, so no preview request.

  // The camera opens: the first request fails (still starting) without flashing an
  // empty preview box, then a retry succeeds.
  send(status('cam-start', 'vision', 0.5, 'available', 'capture_started'));
  await expect.poll(() => previewRequests).toBe(1);
  await expect(page.getByText('Camera preview unavailable')).toBeVisible();
  await expect(page.getByRole('img', { name: 'Camera preview' })).toBeHidden();
  await expect(page.getByRole('img', { name: 'Camera preview' })).toBeVisible({ timeout: 6000 });
  expect(previewRequests).toBe(2);  // One failed attempt, then one retry.

  // A camera failure removes the (possibly frozen) stream and explains why.
  send(status('cam-fail', 'vision', 3, 'error', 'camera_read_failed'));
  await expect(page.getByText('Camera: Camera stopped sending frames')).toBeVisible();
  await expect(page.getByRole('img', { name: 'Camera preview' })).toHaveCount(0);
  await expect(page.getByText('Camera preview unavailable')).toBeVisible();
});
