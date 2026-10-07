/* Generated from contracts/schema.json. Run npm run types; do not edit. */

export type Event =
  | StartedEvent
  | StoppingEvent
  | CompletedEvent
  | StatusEvent
  | TranscriptEvent
  | SpeechMetricsEvent
  | VisionMetricsEvent
  | EngagementEvent;
export type SchemaVersion = 0;
export type SessionId = string;
export type EventId = string;
export type TimestampS = number;
export type Source = "session";
export type Type = "session.started";
export type SchemaVersion1 = 0;
export type SessionId1 = string;
export type EventId1 = string;
export type TimestampS1 = number;
export type Source1 = "session";
export type Type1 = "session.stopping";
export type SchemaVersion2 = 0;
export type SessionId2 = string;
export type EventId2 = string;
export type TimestampS2 = number;
export type Source2 = "session";
export type Type2 = "session.completed";
export type DurationS = number;
export type IncompleteSources = ("speech" | "vision")[];
export type SchemaVersion3 = 0;
export type SessionId3 = string;
export type EventId3 = string;
export type TimestampS3 = number;
export type Source3 = "speech" | "vision";
export type Type3 = "signal.status";
export type Availability = "available" | "unavailable" | "error";
export type Reason = string;
export type SchemaVersion4 = 0;
export type SessionId4 = string;
export type EventId4 = string;
export type TimestampS4 = number;
export type Source4 = "speech";
export type Type4 = "speech.transcript";
export type UtteranceId = string;
export type Revision = number;
export type IsFinal = boolean;
export type StartS = number;
export type EndS = number;
export type Text = string;
export type SchemaVersion5 = 0;
export type SessionId5 = string;
export type EventId5 = string;
export type TimestampS5 = number;
export type Source5 = "speech";
export type Type5 = "speech.metrics";
export type WindowStartS = number;
export type WindowEndS = number;
export type Availability1 = "available" | "unavailable" | "error";
export type Wpm = number | null;
export type FillerCount = number | null;
export type FillerRatePerMin = number | null;
export type State = "none" | "active" | "completed" | "unknown";
export type DurationS1 = number | null;
export type StartS1 = number | null;
export type EndS1 = number | null;
export type SchemaVersion6 = 0;
export type SessionId6 = string;
export type EventId6 = string;
export type TimestampS6 = number;
export type Source6 = "vision";
export type Type6 = "vision.metrics";
export type WindowStartS1 = number;
export type WindowEndS1 = number;
export type Availability2 = "available" | "unavailable" | "error";
export type PersonPresent = boolean | null;
export type PoseAvailable = boolean | null;
export type FacingScore = number | null;
export type ActivityScore = number | null;
export type SchemaVersion7 = 0;
export type SessionId7 = string;
export type EventId7 = string;
export type TimestampS7 = number;
export type Source7 = "engagement";
export type Type7 = "engagement.state";
export type State1 = "ENGAGED" | "NEUTRAL" | "CONFUSED" | "BORED" | "INTERESTED";
export type PreviousState = "ENGAGED" | "NEUTRAL" | "CONFUSED" | "BORED" | "INTERESTED";
export type Code = string;
/**
 * @minItems 1
 */
export type SourceEventIds = [string, ...string[]];
export type Reasons = Reason1[];
export type UsableSources = ("speech" | "vision")[];
export type Mode = "fixture" | "live";
export type FixtureCase = string;
export type ReplaySpeed = number;
export type StartupTimeoutS = number;
export type DrainTimeoutS = number;
export type FeedbackTimeoutS = number;
export type SessionId8 = string;
export type Mode1 = "fixture" | "live";
export type Phase = "prepared" | "running" | "stopping" | "completed";
export type ElapsedS = number;
export type DurationS2 = number | null;
export type IncompleteSources1 = ("speech" | "vision")[];
export type Transcript = (
  | StartedEvent
  | StoppingEvent
  | CompletedEvent
  | StatusEvent
  | TranscriptEvent
  | SpeechMetricsEvent
  | VisionMetricsEvent
  | EngagementEvent
)[];
export type FeedbackStatus = "pending" | "ready" | "unavailable";
export type OutputProvenance = "hand_authored" | "computed";
export type Error = string | null;
export type DurationS3 = number;
export type IncompleteSources2 = ("speech" | "vision")[];
export type SessionId9 = string;
export type Events = (
  | StartedEvent
  | StoppingEvent
  | CompletedEvent
  | StatusEvent
  | TranscriptEvent
  | SpeechMetricsEvent
  | VisionMetricsEvent
  | EngagementEvent
)[];
export type SessionId10 = string;
export type DurationS4 = number;
/**
 * @maxItems 4
 */
export type Moments = [] | [Moment] | [Moment, Moment] | [Moment, Moment, Moment] | [Moment, Moment, Moment, Moment];
export type TimestampS8 = number;
export type Kind = "strength" | "improvement";
export type Observation = string;
export type Suggestion = string;
/**
 * @minItems 1
 */
export type EvidenceEventIds = [string, ...string[]];
export type Limitations = string[];

export interface ContractSchema {
  event: Event;
  config: SessionConfig;
  snapshot: SessionSnapshot;
  completed_session: CompletedSession;
  feedback: Feedback;
}
export interface StartedEvent {
  schema_version: SchemaVersion;
  session_id: SessionId;
  event_id: EventId;
  timestamp_s: TimestampS;
  source: Source;
  type: Type;
  payload: EmptyPayload;
}
export interface EmptyPayload {}
export interface StoppingEvent {
  schema_version: SchemaVersion1;
  session_id: SessionId1;
  event_id: EventId1;
  timestamp_s: TimestampS1;
  source: Source1;
  type: Type1;
  payload: EmptyPayload;
}
export interface CompletedEvent {
  schema_version: SchemaVersion2;
  session_id: SessionId2;
  event_id: EventId2;
  timestamp_s: TimestampS2;
  source: Source2;
  type: Type2;
  payload: CompletionPayload;
}
export interface CompletionPayload {
  duration_s: DurationS;
  incomplete_sources: IncompleteSources;
}
export interface StatusEvent {
  schema_version: SchemaVersion3;
  session_id: SessionId3;
  event_id: EventId3;
  timestamp_s: TimestampS3;
  source: Source3;
  type: Type3;
  payload: StatusPayload;
}
export interface StatusPayload {
  availability: Availability;
  reason: Reason;
}
export interface TranscriptEvent {
  schema_version: SchemaVersion4;
  session_id: SessionId4;
  event_id: EventId4;
  timestamp_s: TimestampS4;
  source: Source4;
  type: Type4;
  payload: TranscriptPayload;
}
export interface TranscriptPayload {
  utterance_id: UtteranceId;
  revision: Revision;
  is_final: IsFinal;
  start_s: StartS;
  end_s: EndS;
  text: Text;
}
export interface SpeechMetricsEvent {
  schema_version: SchemaVersion5;
  session_id: SessionId5;
  event_id: EventId5;
  timestamp_s: TimestampS5;
  source: Source5;
  type: Type5;
  payload: SpeechMetricsPayload;
}
export interface SpeechMetricsPayload {
  window_start_s: WindowStartS;
  window_end_s: WindowEndS;
  availability: Availability1;
  wpm: Wpm;
  filler_count: FillerCount;
  filler_rate_per_min: FillerRatePerMin;
  pause: Pause;
}
export interface Pause {
  state: State;
  duration_s: DurationS1;
  start_s: StartS1;
  end_s: EndS1;
}
export interface VisionMetricsEvent {
  schema_version: SchemaVersion6;
  session_id: SessionId6;
  event_id: EventId6;
  timestamp_s: TimestampS6;
  source: Source6;
  type: Type6;
  payload: VisionMetricsPayload;
}
export interface VisionMetricsPayload {
  window_start_s: WindowStartS1;
  window_end_s: WindowEndS1;
  availability: Availability2;
  person_present: PersonPresent;
  pose_available: PoseAvailable;
  facing_score: FacingScore;
  activity_score: ActivityScore;
}
export interface EngagementEvent {
  schema_version: SchemaVersion7;
  session_id: SessionId7;
  event_id: EventId7;
  timestamp_s: TimestampS7;
  source: Source7;
  type: Type7;
  payload: EngagementPayload;
}
export interface EngagementPayload {
  state: State1;
  previous_state: PreviousState;
  reasons: Reasons;
  usable_sources: UsableSources;
}
export interface Reason1 {
  code: Code;
  source_event_ids: SourceEventIds;
}
export interface SessionConfig {
  mode?: Mode;
  fixture_case?: FixtureCase;
  replay_speed?: ReplaySpeed;
  startup_timeout_s?: StartupTimeoutS;
  drain_timeout_s?: DrainTimeoutS;
  feedback_timeout_s?: FeedbackTimeoutS;
}
export interface SessionSnapshot {
  session_id: SessionId8;
  mode: Mode1;
  phase: Phase;
  elapsed_s: ElapsedS;
  duration_s: DurationS2;
  incomplete_sources: IncompleteSources1;
  input_status: InputStatus;
  latest_events: LatestEvents;
  transcript: Transcript;
  feedback_status: FeedbackStatus;
  output_provenance: OutputProvenance;
  error: Error;
}
export interface InputStatus {
  [k: string]: {
    [k: string]: string;
  };
}
export interface LatestEvents {
  [k: string]:
    | StartedEvent
    | StoppingEvent
    | CompletedEvent
    | StatusEvent
    | TranscriptEvent
    | SpeechMetricsEvent
    | VisionMetricsEvent
    | EngagementEvent;
}
export interface CompletedSession {
  duration_s: DurationS3;
  incomplete_sources: IncompleteSources2;
  session_id: SessionId9;
  events: Events;
}
export interface Feedback {
  session_id: SessionId10;
  duration_s: DurationS4;
  moments: Moments;
  limitations: Limitations;
}
export interface Moment {
  timestamp_s: TimestampS8;
  kind: Kind;
  observation: Observation;
  suggestion: Suggestion;
  evidence_event_ids: EvidenceEventIds;
}
