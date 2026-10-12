import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { Audience } from './Audience';
import {
  type AudienceState, caseLabels, clock, reasonText, stateCopy, statusText,
} from './copy';
import type { ContractSchema } from './generated/contracts';
import './style.css';

type Snapshot = ContractSchema['snapshot'];
type Event = ContractSchema['event'];
type Feedback = ContractSchema['feedback'];
type Fixture = { name: string; description: string; session_count: number };
type Health = { live_integrated: boolean };
type EngagementEvent = Extract<Event, { type: 'engagement.state' }>;

const LIVE = '__live__';

function Icon({ name }: { name: 'spark' | 'play' | 'stop' | 'camera' | 'shield' }) {
  const paths = {
    spark: <><path d="m12 3 2.5 6.5L21 12l-6.5 2.5L12 21l-2.5-6.5L3 12l6.5-2.5Z" /><path d="m20 2 .6 1.4L22 4l-1.4.6L20 6l-.6-1.4L18 4l1.4-.6Z" /></>,
    play: <path d="m9 5 10 7-10 7Z" />,
    stop: <rect x="6" y="6" width="12" height="12" rx="2" />,
    camera: <><rect x="3" y="6" width="13" height="12" rx="3" /><path d="m16 10 5-3v10l-5-3" /></>,
    shield: <><path d="M12 3 4 6v6c0 4 4 7 8 9 4-2 8-5 8-9V6Z" /><path d="m8.5 12 2.5 2.5 4.5-5" /></>,
  };
  return <svg className={`icon icon-${name}`} width="20" height="20" viewBox="0 0 24 24"
    fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"
    aria-hidden="true">{paths[name]}</svg>;
}

async function api<T>(path: string, body?: object): Promise<T> {
  const response = await fetch(path, body === undefined ? undefined : {
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
  });
  const result = await response.json();
  if (!response.ok) {
    const detail = typeof result.detail === 'string' ? result.detail : 'Please try again.';
    throw new Error(detail.replaceAll('_', ' '));
  }
  return result as T;
}

type Source = 'speech' | 'vision';

// A source's displayed status: a status event wins a capture-time tie, and a later
// non-available metrics window keeps the specific outage reason instead of a generic one.
function inputState(snapshot: Snapshot, source: Source) {
  const status = snapshot.latest_events[`signal.status:${source}`];
  const metrics = snapshot.latest_events[`${source}.metrics`];
  const st = status?.type === 'signal.status' ? status : undefined;
  const mt = metrics?.type === 'speech.metrics' || metrics?.type === 'vision.metrics' ? metrics : undefined;
  if (st && (!mt || st.timestamp_s >= mt.timestamp_s)) return { ...st.payload };
  if (mt?.payload.availability === 'available') {
    return { availability: 'available', reason: 'observation_available' };
  }
  if (mt) {
    return { availability: mt.payload.availability,
      reason: st && st.payload.availability !== 'available' ? st.payload.reason : 'observation_unavailable' };
  }
  return snapshot.input_status[source] ?? { availability: 'unavailable', reason: 'not_started' };
}

// Values are current only when captured after the source's latest status event, so
// neither an outage nor a later recovery status brings back a pre-outage value.
function freshMetrics<S extends Source>(snapshot: Snapshot | null, source: S) {
  const metrics = snapshot?.latest_events[`${source}.metrics`];
  const status = snapshot?.latest_events[`signal.status:${source}`];
  if (!metrics || (metrics.type !== 'speech.metrics' && metrics.type !== 'vision.metrics')) return null;
  if (metrics.payload.availability !== 'available') return null;
  if (status && metrics.timestamp_s <= status.timestamp_s) return null;
  return metrics.payload as Extract<Event, { type: `${S}.metrics` }>['payload'];
}

function Track({ transitions, end }: { transitions: EngagementEvent[]; end: number }) {
  const span = Math.max(end, transitions.at(-1)?.timestamp_s ?? 0, 1);
  return <div className="track" aria-label="Audience timeline">{transitions.map((event, index) => {
    const from = event.timestamp_s;
    const to = index + 1 < transitions.length ? transitions[index + 1].timestamp_s : span;
    return <span key={event.event_id} className={`segment state-${event.payload.state.toLowerCase()}`}
      style={{ left: `${(from / span) * 100}%`, width: `${Math.max(0, (to - from) / span) * 100}%` }}
      title={`${clock(from)} ${stateCopy[event.payload.state].label}`} />;
  })}</div>;
}

function Transitions({ transitions }: { transitions: EngagementEvent[] }) {
  return <ol className="transitions" aria-label="Audience transitions">
    {transitions.map(event => <li key={event.event_id}>
      <time>{clock(event.timestamp_s)}</time>
      <strong className={`dot state-${event.payload.state.toLowerCase()}`}>
        {stateCopy[event.payload.state].label}</strong>
      <span>{event.payload.reasons.length
        ? event.payload.reasons.map(r => reasonText(r.code)).join(' · ')
        : event.payload.usable_sources.length ? 'No specific reason' : 'Waiting for usable input'}</span>
    </li>)}
  </ol>;
}

const reducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

// Eases a displayed number toward its latest value so readings glide instead of jumping.
function useEased(target: number | null, ms = 450) {
  const [value, setValue] = useState(target);
  const shown = useRef(target);
  useEffect(() => {
    const from = shown.current;
    if (target == null || from == null || reducedMotion()) {
      shown.current = target; setValue(target); return;
    }
    const begin = performance.now();
    let frame = requestAnimationFrame(function step(now) {
      const t = Math.min(1, (now - begin) / ms);
      shown.current = from + (target - from) * (1 - (1 - t) ** 3);
      setValue(t < 1 ? shown.current : target);
      if (t < 1) frame = requestAnimationFrame(step);
    });
    return () => cancelAnimationFrame(frame);
  }, [target, ms]);
  return value;
}

const STEPS = [['ready', 'Set up'], ['running', 'Rehearse'], ['review', 'Review']] as const;

function App() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [health, setHealth] = useState<Health | null>(null);
  const [selected, setSelected] = useState('weak_to_improved');
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [transitions, setTransitions] = useState<EngagementEvent[]>([]);
  const [previewOk, setPreviewOk] = useState(true);
  const [previewAttempt, setPreviewAttempt] = useState(0);
  const [previewLoaded, setPreviewLoaded] = useState(false);
  const previewImage = useRef<HTMLImageElement | null>(null);
  const [busy, setBusy] = useState(false);
  const [connection, setConnection] = useState('Ready when you are');
  const [error, setError] = useState('');
  const socket = useRef<WebSocket | null>(null);
  const activeId = useRef<string | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    api<Fixture[]>('/api/fixtures').then(setFixtures).catch(() => {
      setError('The local service is unavailable. Reopen LeCoach after starting it.');
    });
    api<Health>('/api/health').then(setHealth).catch(() => {});
    return () => {
      mounted.current = false;
      activeId.current = null;
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
      socket.current?.close();
    };
  }, []);

  useEffect(() => {
    if (snapshot?.feedback_status !== 'ready') return;
    const id = snapshot.session_id;
    api<Feedback>(`/api/sessions/${id}/feedback`).then(value => {
      if (activeId.current === id) setFeedback(value);
    }).catch(() => setError('The rehearsal summary could not be loaded.'));
  }, [snapshot?.session_id, snapshot?.feedback_status]);

  function applyEvent(event: Event) {
    if (event.session_id !== activeId.current) return;
    if (event.type === 'engagement.state') {
      setTransitions(current => current.some(e => e.event_id === event.event_id)
        ? current : [...current, event]);
    }
    setSnapshot(current => {
      if (!current || current.session_id !== event.session_id) return current;
      const next = { ...current, latest_events: { ...current.latest_events },
        input_status: { ...current.input_status }, transcript: [...current.transcript] };
      const key = event.type === 'signal.status' ? `signal.status:${event.source}` : event.type;
      const previous = next.latest_events[key];
      // Like the backend, a source's input status follows its newest status or metrics
      // event by capture time, whichever type it is.
      const statusTime = (source: string) => Math.max(-1,
        ...[`signal.status:${source}`, `${source}.metrics`].map(k => next.latest_events[k]?.timestamp_s ?? -1));
      const sourceTime = event.source === 'speech' || event.source === 'vision'
        ? statusTime(event.source) : -1;
      if (!previous || event.timestamp_s >= previous.timestamp_s) {
        next.latest_events[key] = event;
        const current = event.timestamp_s >= sourceTime;
        if (event.type === 'signal.status' && current) {
          next.input_status[event.source] = { ...event.payload };
        }
        if ((event.type === 'speech.metrics' || event.type === 'vision.metrics') && current) {
          next.input_status[event.source] = { availability: event.payload.availability,
            reason: event.payload.availability === 'available'
              ? 'observation_available' : 'observation_unavailable' };
        }
      }
      if (event.type === 'speech.transcript') {
        const index = next.transcript.findIndex(e => e.type === 'speech.transcript'
          && e.payload.utterance_id === event.payload.utterance_id);
        const old = next.transcript[index];
        if (index < 0) next.transcript.push(event);
        else if (old.type === 'speech.transcript' && !old.payload.is_final
          && event.payload.revision > old.payload.revision) next.transcript[index] = event;
        next.transcript.sort((a, b) => a.type === 'speech.transcript' && b.type === 'speech.transcript'
          ? a.payload.start_s - b.payload.start_s : 0);
      }
      if (next.phase !== 'stopping' && next.phase !== 'completed') {
        next.elapsed_s = Math.max(next.elapsed_s, event.timestamp_s);
      }
      if (event.type === 'session.stopping') {
        next.phase = 'stopping'; next.duration_s = event.timestamp_s;
      }
      if (event.type === 'session.completed') {
        next.phase = 'completed'; next.duration_s = event.payload.duration_s;
        next.incomplete_sources = event.payload.incomplete_sources;
      }
      return next;
    });
  }

  function connect(id: string, attempt = 0): Promise<void> {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`${location.protocol === 'https:' ? 'wss' : 'ws'}://${location.host}/api/sessions/${id}/events`);
      socket.current = ws;
      let ready = false;
      const timeout = setTimeout(() => {
        if (!ready) { ws.close(); reject(new Error('The audience connection timed out.')); }
      }, 5000);
      ws.onmessage = message => {
        if (!mounted.current || activeId.current !== id) return;
        try {
          const value = JSON.parse(message.data);
          if (value.kind === 'snapshot') {
            const snap = value.snapshot as Snapshot;
            setSnapshot(snap);
            const latest = snap.latest_events['engagement.state'];
            if (latest?.type === 'engagement.state') {
              setTransitions(current => current.some(e => e.event_id === latest.event_id)
                ? current : [...current, latest].sort((a, b) => a.timestamp_s - b.timestamp_s));
            }
            setConnection('Connected locally');
            if (!ready) { ready = true; clearTimeout(timeout); resolve(); }
          } else if (value.kind === 'event') applyEvent(value.event as Event);
        } catch { setError('The local service sent an unreadable update.'); }
      };
      ws.onerror = () => {
        if (!ready) { clearTimeout(timeout); reject(new Error('Could not connect to the local audience.')); }
      };
      ws.onclose = event => {
        clearTimeout(timeout);
        if (!ready) reject(new Error('The audience connection closed.'));
        if (!mounted.current || activeId.current !== id || !ready) return;
        if (event.code === 1000) { setConnection('Session closed'); return; }
        if (attempt < 3) {
          setConnection('Connection interrupted. Reconnecting…');
          reconnectTimer.current = setTimeout(() => {
            if (activeId.current === id) connect(id, attempt + 1).catch(() => {
              setError('Connection interrupted. Select Reconnect to restore this rehearsal.');
            });
          }, 300);
        } else setError('Connection interrupted. Select Reconnect to restore this rehearsal.');
      };
    });
  }

  async function start() {
    if (busy) return;
    setBusy(true); setError(''); setFeedback(null); setTransitions([]); setPreviewOk(true);
    setPreviewLoaded(false);
    activeId.current = null;
    if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    socket.current?.close();
    try {
      const config = selected === LIVE ? { mode: 'live' } : { mode: 'fixture', fixture_case: selected };
      const prepared = await api<Snapshot>('/api/sessions', config);
      activeId.current = prepared.session_id;
      setSnapshot(prepared);
      await connect(prepared.session_id);
      await api<Snapshot>(`/api/sessions/${prepared.session_id}/start`, {});
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not start the rehearsal.');
      if (activeId.current) {
        await api(`/api/sessions/${activeId.current}/stop`, {}).catch(() => {});
      }
    } finally { setBusy(false); }
  }

  async function stop() {
    if (!activeId.current || busy) return;
    setBusy(true); setError('');
    try { setSnapshot(await api<Snapshot>(`/api/sessions/${activeId.current}/stop`, {})); }
    catch { setError('Could not stop this rehearsal. Try again.'); }
    finally { setBusy(false); }
  }

  const live = snapshot ? snapshot.mode === 'live' : selected === LIVE;
  const running = snapshot?.phase === 'running' || snapshot?.phase === 'stopping';
  const audience = snapshot?.latest_events['engagement.state'];
  const engagement = audience?.type === 'engagement.state' ? audience : null;
  const state: AudienceState = engagement?.payload.state ?? 'NEUTRAL';
  const transcript = snapshot?.transcript.filter(e => e.type === 'speech.transcript') ?? [];
  const sources = Object.keys(snapshot?.input_status || {}) as Source[];
  const speech = freshMetrics(snapshot, 'speech');
  const vision = freshMetrics(snapshot, 'vision');
  const facing = vision?.facing_score ?? null;
  const pause = speech?.pause.state === 'active' && speech.pause.duration_s != null
    ? `Pausing · ${speech.pause.duration_s.toFixed(1)} s` : null;
  const end = snapshot?.duration_s ?? snapshot?.elapsed_s ?? 0;
  const inputs = sources.map(source => [source, inputState(snapshot!, source)] as const);
  const anyInput = inputs.some(([, value]) => value.availability === 'available');
  const cameraOk = !!snapshot && inputState(snapshot, 'vision').availability === 'available';
  const showPreview = live && running && cameraOk;
  const previewVisible = showPreview && previewOk && previewLoaded;

  // When the preview is hidden (camera failed or session ended), prepare a fresh request
  // for next time; a stream left from before a camera failure would show a frozen frame.
  useEffect(() => {
    if (showPreview) return;
    setPreviewLoaded(false); setPreviewOk(true); setPreviewAttempt(n => n + 1);
  }, [showPreview]);

  // The camera may still be opening: retry the backend preview instead of giving up.
  useEffect(() => {
    if (previewOk || !showPreview) return;
    const timer = setTimeout(() => { setPreviewAttempt(n => n + 1); setPreviewOk(true); }, 2000);
    return () => clearTimeout(timer);
  }, [previewOk, showPreview]);

  // Show the stream only once a frame has arrived, so failed probes never flash an empty box.
  useEffect(() => {
    if (!showPreview || !previewOk || previewLoaded) return;
    const timer = setInterval(() => {
      if ((previewImage.current?.naturalWidth ?? 0) > 0) setPreviewLoaded(true);
    }, 200);
    return () => clearInterval(timer);
  }, [showPreview, previewOk, previewLoaded, previewAttempt]);

  // One primary view per phase: set up, perform in front of the room, then review.
  const view = running || (busy && snapshot?.phase === 'prepared') ? 'running'
    : snapshot?.phase === 'completed' ? 'review' : 'ready';
  const tone = `tone-${state.toLowerCase()}`;
  const modeName = live ? 'Live rehearsal' : 'Synthetic replay';
  const modeDetail = live
    ? 'Microphone and camera are processed on this device. No audio or video is recorded.'
    : 'Speech and camera observations are authored examples; the engagement engine computes the audience from them. Coaching is an authored example. Microphone and camera are off.';
  const modeChip = <span className={`chip mode-chip${live ? ' live' : ''}`} title={modeDetail}>{modeName}</span>;
  const reasons = engagement?.payload.reasons.length
    ? engagement.payload.reasons.map(r => reasonText(r.code)).join(' · ')
    : running && !anyInput ? 'Waiting for usable speech or camera input.' : stateCopy[state].detail;
  const wpm = useEased(speech?.wpm ?? null);
  const fillers = useEased(speech?.filler_rate_per_min ?? null);
  const actionRef = useRef<HTMLButtonElement | null>(null);

  // A short on-stage cue when the rehearsal begins, so the switch into the room is explained.
  const [cue, setCue] = useState(false);
  const wasRunning = useRef(false);
  useEffect(() => {
    const now = snapshot?.phase === 'running';
    if (now && !wasRunning.current) {
      setCue(true);
      const timer = setTimeout(() => setCue(false), 3200);
      wasRunning.current = now;
      return () => clearTimeout(timer);
    }
    if (!now) setCue(false);
    wasRunning.current = now;
  }, [snapshot?.phase]);

  // When a view swap removes the focused control, hand focus to the new view's main action.
  useEffect(() => {
    if (document.activeElement === document.body) actionRef.current?.focus({ preventScroll: true });
  }, [view, running]);

  // Space starts or stops a rehearsal when no control has focus.
  const shortcut = useRef<() => void>(() => {});
  shortcut.current = () => { if (running) void stop(); else if (view !== 'running') void start(); };
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.code !== 'Space' || event.repeat || event.target !== document.body) return;
      event.preventDefault(); shortcut.current();
    };
    addEventListener('keydown', onKey);
    return () => removeEventListener('keydown', onKey);
  }, []);

  const modeSelect = <label className="field">Practice mode
    <select aria-label="Practice mode" value={selected} onChange={e => setSelected(e.target.value)} disabled={busy}>
      <option value={LIVE} disabled={!health?.live_integrated}>
        Live microphone and camera{health?.live_integrated ? '' : ' (not connected yet)'}</option>
      {fixtures.filter(f => f.session_count === 1).map(f => <option key={f.name} value={f.name}>
        {caseLabels[f.name] || f.name}</option>)}
    </select></label>;
  const action = running
    ? <button ref={actionRef} className="secondary" onClick={stop} disabled={busy || snapshot?.phase === 'stopping'}>
      <Icon name="stop" />Stop</button>
    : <button ref={actionRef} className={`primary${busy ? ' is-busy' : ''}`} onClick={start}
      disabled={busy || (!fixtures.length && selected !== LIVE)}>
      {busy ? <span className="spinner" aria-hidden="true" /> : <Icon name="play" />}
      {busy ? 'Connecting…' : selected === LIVE ? 'Start rehearsal' : 'Start replay'}</button>;
  const transcriptBlock = <div className="transcript-block"><h3>Transcript</h3>
    <p className="transcript">{transcript.length
      ? transcript.map((e, i) => e.type === 'speech.transcript'
        ? <span key={e.event_id} className={e.payload.is_final ? undefined : 'partial'}>
          {i ? ' ' : ''}{e.payload.text}</span> : null)
      : 'Listening for speech…'}</p></div>;
  const audienceNote = <p className="audience-note">Simulated audience states from deterministic rules,
    not measured emotions or judgments of you.</p>;
  const hint = <span className="hint"><kbd>Space</kbd> {running ? 'to stop' : 'to start'}</span>;

  return <main className={`studio is-${view}`}>
    <header><a className="brand" href="/"><span className="brand-mark"><Icon name="spark" /></span>
      <span className="brand-name">LeCoach</span></a>
      <ol className="steps" aria-label="Rehearsal steps">{STEPS.map(([key, label], index) =>
        <li key={key} className={key === view ? 'is-current'
          : STEPS.findIndex(([k]) => k === view) > index ? 'is-done' : undefined}
          aria-current={key === view ? 'step' : undefined}><span className="step-num">{index + 1}</span>
          <span className="step-label">{label}</span></li>)}</ol>
      <div className="header-status">
        <span className="local"><Icon name="shield" /> Runs on this device</span>
        <span className={`connection${connection === 'Connected locally' ? ' is-live' : ''}`}><i /> {connection}</span></div></header>
    {error && <div className="error" role="alert">{error}
      {activeId.current && <button onClick={() => {
        if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
        socket.current?.close(); setError('');
        connect(activeId.current!).catch(() => setError('The local connection is unavailable.'));
      }}>Reconnect</button>}</div>}

    {view === 'ready' && <div className="view view-ready" key="ready">
      <section className="stage">
        <div className="intro"><h1>Find your rhythm. <span>Feel the audience.</span></h1>
          <p>Rehearse in front of a private audience that reacts to your pace, filler words and where you face.</p></div>
        <Audience state={state} label={live ? 'Audience' : 'Example audience'} />
        {audienceNote}
      </section>
      <aside className="setup card" aria-label="Rehearsal controls">
        <h2>Start a rehearsal</h2>
        <ol className="how">
          <li><span>1</span>Pick live practice or an example replay.</li>
          <li><span>2</span>Start, then speak to the room. It reacts as you go.</li>
          <li><span>3</span>Stop or finish to get coaching on key moments.</li>
        </ol>
        {modeSelect}
        <div className="mode-note">{modeChip}<p>{modeDetail}</p></div>
        <div className="action-row">{action}{hint}</div>
      </aside>
    </div>}

    {view === 'running' && <div className="view view-running" key="running">
      <section className="session-bar" aria-label="Rehearsal controls">
        {modeChip}
        <div className="timer" aria-label="Elapsed time">{clock(snapshot?.elapsed_s || 0)}
          <small>{snapshot?.phase === 'stopping' ? 'Wrapping up…' : running ? 'Rehearsing' : 'Getting ready'}</small></div>
        {running && hint}
        {action}
      </section>
      <section className="live-grid">
        <article className={`stage ${tone}`}>
          <div className="stage-room">
            <Audience state={state} label={live ? 'Audience' : 'Example audience'} />
            {!running && <div className="overlay"><span className="spinner" aria-hidden="true" />
              Setting up the room…</div>}
            {cue && <div className="cue" role="status"><strong>You're on.</strong>
              {live ? 'Face the camera and start speaking. The room reacts to your pace, filler words and where you face.'
                : 'Watch the room react to the example speaker’s pace, filler words and where they face.'}</div>}
          </div>
          <div className="reaction" aria-live="polite">
            <strong key={state}>{stateCopy[state].label}</strong>
            <span className="state" data-testid="audience-state">{state}</span>
            <p key={reasons}>{reasons}</p>
          </div>
          <Track transitions={transitions} end={end} />
        </article>
        <aside className="rail" aria-label={live ? 'Your delivery' : 'Example inputs'}>
          {/* Live self-view leads the rail so framing is checkable without covering the room. */}
          {live && <div className="self-view">
            {showPreview && previewOk && <img className="camera" alt="Camera preview" key={previewAttempt}
              ref={previewImage} hidden={!previewLoaded}
              src={`/api/sessions/${snapshot!.session_id}/preview?attempt=${previewAttempt}`}
              onLoad={() => setPreviewLoaded(true)}
              onError={() => { setPreviewLoaded(false); setPreviewOk(false); }} />}
            {!previewVisible && <div className="preview"><Icon name="camera" />
              <p>{showPreview && previewOk ? 'Waiting for the camera preview' : 'Camera preview unavailable'}</p></div>}
            <small className="caption">Preview only. No video is recorded.</small>
          </div>}
          <div className="metrics">
            <div><strong>{wpm != null ? <>{Math.round(wpm)}<span> WPM</span></> : '—'}</strong>
              <small>Pace</small></div>
            <div><strong>{fillers != null ? <>{fillers.toFixed(0)}<span>/min</span></> : '—'}</strong>
              <small>Fillers</small></div>
            <div><strong>{facing != null ? <meter min={0} max={1} low={0.4} high={0.6} optimum={1} value={facing}
              aria-label="Facing the audience" /> : '—'}</strong><small>Facing (approx.)</small></div>
          </div>
          {pause && <p className="pause">{pause}</p>}
          <div className="inputs">{inputs.map(([name, value]) => <span key={name}
            className={`input input-${value.availability}`}><i />
            {name === 'speech' ? 'Microphone' : 'Camera'}: {statusText(value.reason)}</span>)}</div>
          {(transcript.length > 0 || live) && transcriptBlock}
          {transitions.length > 0 && <div className="log"><h3>How the room responded</h3>
            <Transitions transitions={transitions} /></div>}
          <div className="footnote">{!live && <p>{modeDetail}</p>}{audienceNote}</div>
        </aside>
      </section>
    </div>}

    {view === 'review' && <div className="view view-review" key="review">
      <section className="session-bar" aria-label="Rehearsal controls">
        {modeChip}
        <div className="timer" aria-label="Elapsed time">{clock(end)}<small>Complete</small></div>
        {modeSelect}
        {action}
      </section>
      <div className="review-body">
        <section className="review-head">
          <div><h1>{feedback ? 'A few moments to learn from.' : 'Rehearsal complete.'}</h1>
            <p>{live ? 'Coaching' : 'Authored example coaching'} · {clock(end)} rehearsal ·
              Run it again or pick another mode above.</p></div>
          <div className={`final ${tone}`}><small>The room ended</small>
            <strong>{stateCopy[state].label}</strong>
            <span className="state" data-testid="audience-state">{state}</span></div>
        </section>
        {feedback && <section className="summary" aria-label={live ? 'Rehearsal coaching' : 'Example coaching'}>
          <div className="moments">{feedback.moments.map((moment, index) =>
            <article className={`card moment moment-${moment.kind}`} key={index}
              style={{ ['--i' as string]: index }}>
              <div className="moment-top"><strong>{moment.kind === 'strength' ? 'Keep doing this' : 'Try next time'}</strong>
                <time>{clock(moment.timestamp_s)}</time></div>
              <p className="suggestion">{moment.suggestion}</p>
              <p className="observation">{moment.observation}</p>
            </article>)}</div>
          {!feedback.moments.length && <p className="notice">No supported coaching moments in this example.</p>}
          {feedback.limitations.map((limitation, index) => <p className="notice" key={index}>{limitation}</p>)}
        </section>}
        {snapshot?.feedback_status === 'pending' && <p className="notice loading">
          <span className="spinner" aria-hidden="true" />Preparing the rehearsal summary…</p>}
        {snapshot?.feedback_status === 'unavailable'
          && <p className="notice">{live ? 'The rehearsal summary is unavailable.'
            : 'Replay stopped early. The authored example summary is unavailable.'}</p>}
        <div className="review-foot">
          {transitions.length > 0 && <section className="timeline">
            <div className="timeline-top"><h2>How the room responded</h2><span>{clock(end)}</span></div>
            <Track transitions={transitions} end={end} />
            <Transitions transitions={transitions} />
          </section>}
          {transcript.length > 0 && transcriptBlock}
        </div>
        <div className="footnote">{!live && <p>{modeDetail}</p>}{audienceNote}</div>
      </div>
    </div>}
  </main>;
}

createRoot(document.getElementById('root')!).render(<App />);
