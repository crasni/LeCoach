// Plain-language wording for engine reason codes, audience states and input status.
// The engine decides; the UI only explains.

export const STATES = ['ENGAGED', 'INTERESTED', 'NEUTRAL', 'CONFUSED', 'BORED'] as const;
export type AudienceState = typeof STATES[number];

export const stateCopy: Record<AudienceState, { label: string; detail: string }> = {
  ENGAGED: { label: 'Leaning in', detail: 'Delivery has been steady for a while.' },
  INTERESTED: { label: 'Perking up', detail: 'Recent delivery is landing well.' },
  NEUTRAL: { label: 'Listening', detail: 'Nothing notable yet.' },
  CONFUSED: { label: 'Losing the thread', detail: 'Something is making you harder to follow.' },
  BORED: { label: 'Drifting off', detail: 'Attention is slipping.' },
};

export const reasonCopy: Record<string, string> = {
  pace_high: 'Pace has stayed fast',
  pace_low: 'Pace has stayed slow',
  fillers_frequent: 'Frequent filler words',
  silence_prolonged: 'A long silence',
  facing_away_sustained: 'Turned away from the audience for a while',
  pace_steady: 'Comfortable pace',
  facing_audience: 'Facing the audience',
};

export function reasonText(code: string) {
  return reasonCopy[code] || code.replaceAll('_', ' ');
}

const statusCopy: Record<string, string> = {
  not_started: 'Not started',
  observation_available: 'Receiving',
  observation_unavailable: 'No usable observation',
  adapter_not_integrated: 'Not connected in this build',
  adapter_start_failed: 'Could not start',
  camera_permission_denied: 'Camera permission denied',
  microphone_permission_denied: 'Microphone permission denied',
  camera_disconnected: 'Camera disconnected',
  microphone_disconnected: 'Microphone disconnected',
  // Vision adapter (src/lecoach/vision/README.md).
  capture_started: 'Starting',
  camera_unavailable: 'Camera unavailable (missing, busy or permission denied)',
  camera_start_failed: 'Camera could not start',
  camera_read_failed: 'Camera stopped sending frames',
  vision_capture_failed: 'Camera processing failed',
  pose_model_missing: 'Pose model not installed',
  pose_runtime_missing: 'Pose software not installed',
  // Speech adapter (src/lecoach/speech/README.md, "Failure reasons").
  microphone_not_found: 'No microphone found',
  microphone_no_signal: 'No sound from the microphone (muted or access denied)',
  speech_vad_unavailable: 'Speech detection not installed',
  microphone_unavailable: 'Microphone unavailable',
  audio_queue_overflow: 'Audio processing fell behind',
  speech_model_unavailable: 'Speech model unavailable',
  speech_segmentation_failed: 'Speech detection failed',
  transcription_failed: 'Transcription failed',
};

export function statusText(reason: string) {
  return statusCopy[reason] || reason.replaceAll('_', ' ');
}

export const caseLabels: Record<string, string> = {
  weak_to_improved: 'Finding your rhythm', camera_unavailable: 'Speech with camera unavailable',
  no_usable_signals: 'Unavailable inputs', empty_session: 'An empty rehearsal',
  insufficient_window: 'A short rehearsal', late_final_and_duplicates: 'Delayed transcript',
  drain_timeout: 'Incomplete speech processing', adjacent_incidents: 'One repeated incident',
};

export function clock(seconds: number) {
  const whole = Math.max(0, Math.floor(seconds));
  return `${Math.floor(whole / 60).toString().padStart(2, '0')}:${(whole % 60).toString().padStart(2, '0')}`;
}
