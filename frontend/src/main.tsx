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

function Timeline({ transitions, end }: { transitions: EngagementEvent[]; end: number }) {
  if (!transitions.length) return null;
  const span = Math.max(end, transitions[transitions.length - 1].timestamp_s, 1);
  return <div className="timeline" aria-label="Audience timeline">
    <div className="track">{transitions.map((event, index) => {
      const from = event.timestamp_s;
      const to = index + 1 < transitions.length ? transitions[index + 1].timestamp_s : span;
      return <span key={event.event_id} className={`segment state-${event.payload.state.toLowerCase()}`}
        style={{ left: `${(from / span) * 100}%`, width: `${Math.max(0, (to - from) / span) * 100}%` }}
        title={`${clock(from)} ${stateCopy[event.payload.state].label}`} />;
    })}</div>
    <ol className="transitions" aria-label="Audience transitions">
      {transitions.map(event => <li key={event.event_id}>
        <time>{clock(event.timestamp_s)}</time>
        <strong className={`dot state-${event.payload.state.toLowerCase()}`}>
          {stateCopy[event.payload.state].label}</strong>
        <span>{event.payload.reasons.length
          ? event.payload.reasons.map(r => reasonText(r.code)).join(' · ')
          : event.payload.usable_sources.length ? 'No specific reason' : 'Waiting for usable input'}</span>
      </li>)}
    </ol>
  </div>;
}

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

  return <main>
    <header><a className="brand" href="/">LeCoach<span>Your Private AI Audience.</span></a>
      <span className="local"><i /> Runs on this device</span></header>
    <section className="intro"><div className="eyebrow">A SPACE TO PRACTICE</div>
      <h1>Find your rhythm.<br /><span>Feel the audience.</span></h1>
      <p>Rehearse and watch a simulated audience respond to your pace, fillers, pauses and
        whether you face the room. Reactions come from fixed rules, not from reading emotions.</p>
    </section>
    {live
      ? <aside className="mode live"><strong>Live rehearsal</strong>
        <span>Microphone and camera are processed on this device. No audio or video is recorded.</span></aside>
      : <aside className="mode"><strong>Synthetic replay</strong>
        <span>Speech and camera observations are authored examples; the audience is computed from
          them by the engagement engine. Coaching is an authored example. Microphone and camera are off.</span></aside>}
    <section className="controls" aria-label="Rehearsal controls">
      <label>Example<select aria-label="Example" value={selected} onChange={e => setSelected(e.target.value)} disabled={!!running || busy}>
        <option value={LIVE} disabled={!health?.live_integrated}>
          Live microphone and camera{health?.live_integrated ? '' : ' (not connected yet)'}</option>
        {fixtures.filter(f => f.session_count === 1).map(f => <option key={f.name} value={f.name}>
          {caseLabels[f.name] || f.name}</option>)}
      </select></label>
      <button className="primary" onClick={start} disabled={!!running || busy || (!fixtures.length && selected !== LIVE)}>
        {busy && !running ? 'Connecting…' : selected === LIVE ? 'Start rehearsal' : 'Start replay'}</button>
      <button className="secondary" onClick={stop} disabled={!running || busy}>Stop</button>
      <div className="timer" aria-label="Elapsed time">{clock(snapshot?.elapsed_s || 0)}
        <small>{snapshot?.phase || 'Ready'}</small></div>
    </section>
    {error && <div className="error" role="alert">{error}
      {activeId.current && <button onClick={() => {
        if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
        socket.current?.close(); setError('');
        connect(activeId.current!).catch(() => setError('The local connection is unavailable.'));
      }}>Reconnect</button>}</div>}
    <section className="grid">
      <article className="audience card"><div className="card-top"><h2>Your audience</h2>
        <span className={`state state-${state.toLowerCase()}`} data-testid="audience-state">{state}</span></div>
        <Audience state={state} label={live ? 'Audience' : 'Example audience'} />
        <div className="reaction" aria-live="polite">
          <strong>{stateCopy[state].label}</strong>
          <span>{engagement?.payload.reasons.length
            ? engagement.payload.reasons.map(r => reasonText(r.code)).join(' · ')
            : running && !anyInput
              ? 'Waiting for usable speech or camera input.' : stateCopy[state].detail}</span>
        </div>
        <p className="muted">Simulated audience states from deterministic rules. They are not measured
          emotions or judgments of you.</p>
        <Timeline transitions={transitions} end={end} />
      </article>
      <article className="card observations"><div className="card-top"><h2>Rehearsal input</h2>
        <span className="muted">{live ? 'On this device' : 'Example data'}</span></div>
        {showPreview && previewOk && <img className="camera" alt="Camera preview" key={previewAttempt}
          ref={previewImage} hidden={!previewLoaded}
          src={`/api/sessions/${snapshot!.session_id}/preview?attempt=${previewAttempt}`}
          onLoad={() => setPreviewLoaded(true)}
          onError={() => { setPreviewLoaded(false); setPreviewOk(false); }} />}
        {!previewVisible && <div className="preview"><span aria-hidden="true">◉</span>
          <p>{!live ? 'Camera is off during replay' : !running ? 'Camera starts with the rehearsal'
            : showPreview && previewOk ? 'Waiting for the camera preview' : 'Camera preview unavailable'}</p>
          <small>No video is recorded.</small></div>}
        <div className="inputs">{inputs.map(([name, value]) => <span key={name}
          className={`input input-${value.availability}`}>
          {name === 'speech' ? 'Microphone' : 'Camera'}: {statusText(value.reason)}</span>)}</div>
        <div className="metrics">
          <div><small>{live ? 'Pace' : 'Example pace'}</small><strong>
            {speech?.wpm != null ? `${Math.round(speech.wpm)} WPM` : '—'}</strong></div>
          <div><small>Fillers</small><strong>
            {speech?.filler_rate_per_min != null ? `${speech.filler_rate_per_min.toFixed(0)}/min` : '—'}</strong></div>
          <div><small>Facing (approx.)</small><strong>
            {facing != null ? <meter min={0} max={1} low={0.4} high={0.6} optimum={1} value={facing}
              aria-label="Facing the audience" /> : '—'}</strong></div>
        </div>
        {pause && <p className="pause">{pause}</p>}
        <h3>Transcript</h3><p className="transcript">{transcript.length
          ? transcript.map((e, i) => e.type === 'speech.transcript'
            ? <span key={e.event_id} className={e.payload.is_final ? undefined : 'partial'}>
              {i ? ' ' : ''}{e.payload.text}</span> : null)
          : 'No transcript yet.'}</p>
      </article>
    </section>
    {feedback && <section className="summary" aria-label={live ? 'Rehearsal coaching' : 'Example coaching'}>
      <div className="eyebrow">AFTER THE REHEARSAL</div><h2>A few moments to learn from.</h2>
      <p className="muted">{live ? 'Coaching' : 'Authored example coaching'} · {clock(feedback.duration_s)} rehearsal</p>
      <div className="moments">{feedback.moments.map((moment, index) => <article className="card" key={index}>
        <div className="moment-top"><span>{clock(moment.timestamp_s)}</span>
          <strong>{moment.kind === 'strength' ? 'Keep doing this' : 'Try next time'}</strong></div>
        <p>{moment.observation}</p><p className="suggestion">{moment.suggestion}</p>
      </article>)}</div>
      {feedback.limitations.map((limitation, index) => <p className="notice" key={index}>{limitation}</p>)}
      {!feedback.moments.length && <p>No supported coaching moments in this example.</p>}
    </section>}
    {snapshot?.phase === 'completed' && snapshot.feedback_status === 'unavailable'
      && <p className="notice">{live ? 'The rehearsal summary is unavailable.'
        : 'Replay stopped early. The authored example summary is unavailable.'}</p>}
    <footer><span><i /> {connection}</span><span>Private practice, one rehearsal at a time.</span></footer>
  </main>;
}

createRoot(document.getElementById('root')!).render(<App />);
