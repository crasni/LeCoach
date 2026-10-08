import { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import type { ContractSchema } from './generated/contracts';
import './style.css';

type Snapshot = ContractSchema['snapshot'];
type Event = ContractSchema['event'];
type Feedback = ContractSchema['feedback'];
type Fixture = { name: string; description: string; session_count: number };

const labels: Record<string, string> = {
  weak_to_improved: 'Finding your rhythm', camera_unavailable: 'Speech with camera unavailable',
  no_usable_signals: 'Unavailable inputs', empty_session: 'An empty rehearsal',
  insufficient_window: 'A short rehearsal', late_final_and_duplicates: 'Delayed transcript',
  drain_timeout: 'Incomplete speech processing', adjacent_incidents: 'One repeated incident',
};
const faces: Record<string, string> = {
  ENGAGED: '🙂', NEUTRAL: '😐', CONFUSED: '🤔', BORED: '😴', INTERESTED: '👀',
};

function time(seconds: number) {
  return `${Math.floor(seconds / 60).toString().padStart(2, '0')}:${Math.floor(seconds % 60).toString().padStart(2, '0')}`;
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

function App() {
  const [fixtures, setFixtures] = useState<Fixture[]>([]);
  const [selected, setSelected] = useState('weak_to_improved');
  const [snapshot, setSnapshot] = useState<Snapshot | null>(null);
  const [feedback, setFeedback] = useState<Feedback | null>(null);
  const [transitions, setTransitions] = useState<Event[]>([]);
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
    }).catch(() => setError('The example summary could not be loaded.'));
  }, [snapshot?.session_id, snapshot?.feedback_status]);

  function applyEvent(event: Event) {
    if (event.session_id !== activeId.current) return;
    if (event.type === 'engagement.state') {
      setTransitions(current => [...current, event].slice(-20));
    }
    setSnapshot(current => {
      if (!current || current.session_id !== event.session_id) return current;
      const next = { ...current, latest_events: { ...current.latest_events },
        input_status: { ...current.input_status }, transcript: [...current.transcript] };
      const key = event.type === 'signal.status' ? `signal.status:${event.source}` : event.type;
      const previous = next.latest_events[key];
      if (!previous || event.timestamp_s >= previous.timestamp_s) {
        next.latest_events[key] = event;
        if (event.type === 'signal.status') next.input_status[event.source] = { ...event.payload };
        if (event.type === 'speech.metrics' || event.type === 'vision.metrics') {
          next.input_status[event.source] = { availability: event.payload.availability,
            reason: 'Observation received' };
        }
      }
      if (event.type === 'speech.transcript') {
        const index = next.transcript.findIndex(e => e.type === 'speech.transcript'
          && e.payload.utterance_id === event.payload.utterance_id);
        const old = next.transcript[index];
        if (index < 0) next.transcript.push(event);
        else if (old.type === 'speech.transcript' && !old.payload.is_final
          && event.payload.revision > old.payload.revision) next.transcript[index] = event;
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
            setSnapshot(value.snapshot as Snapshot);
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
    setBusy(true); setError(''); setFeedback(null); setTransitions([]);
    activeId.current = null;
    if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    socket.current?.close();
    try {
      const prepared = await api<Snapshot>('/api/sessions', { mode: 'fixture', fixture_case: selected });
      activeId.current = prepared.session_id;
      setSnapshot(prepared);
      await connect(prepared.session_id);
      await api<Snapshot>(`/api/sessions/${prepared.session_id}/start`, {});
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : 'Could not start the example.');
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

  const running = snapshot?.phase === 'running' || snapshot?.phase === 'stopping';
  const audience = snapshot?.latest_events['engagement.state'];
  const state = audience?.type === 'engagement.state' ? audience.payload.state : 'NEUTRAL';
  const transcript = snapshot?.transcript.filter(e => e.type === 'speech.transcript');
  const speech = snapshot?.latest_events['speech.metrics'];

  return <main>
    <header><a className="brand" href="/">LeCoach<span>Your Private AI Audience.</span></a>
      <span className="local"><i /> Runs on this device</span></header>
    <section className="intro"><div className="eyebrow">A SPACE TO PRACTICE</div>
      <h1>Find your rhythm.<br /><span>Feel the audience.</span></h1>
      <p>Try an example rehearsal and see how delivery can shape an audience’s response.</p>
    </section>
    <aside className="mode"><strong>Synthetic replay</strong>
      <span>Speech, audience reactions, and coaching are authored examples. Microphone and camera are off.</span></aside>
    <section className="controls" aria-label="Rehearsal controls">
      <label>Example<select aria-label="Example" value={selected} onChange={e => setSelected(e.target.value)} disabled={!!running || busy}>
        {fixtures.filter(f => f.session_count === 1).map(f => <option key={f.name} value={f.name}>
          {labels[f.name] || f.name}</option>)}
      </select></label>
      <button className="primary" onClick={start} disabled={!!running || busy || !fixtures.length}>
        {busy && !running ? 'Connecting…' : 'Start replay'}</button>
      <button className="secondary" onClick={stop} disabled={!running || busy}>Stop</button>
      <div className="timer" aria-label="Elapsed time">{time(snapshot?.elapsed_s || 0)}
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
        <span className="state" data-testid="audience-state">{state}</span></div>
        <div className="audience-faces" aria-label={`Example audience is ${state.toLowerCase()}`}>
          {[0, 1, 2].map(n => <div className={`seat state-${state.toLowerCase()}`} key={n}>
            <span aria-hidden="true">{faces[state]}</span><div /></div>)}
        </div><p className="muted">Example reactions follow the replay. They are simulated audience states.</p>
        <div className="transitions" aria-label="Audience transitions">
          {transitions.filter(e => e.type === 'engagement.state').map(e => <span key={e.event_id}>
            {time(e.timestamp_s)} · {e.type === 'engagement.state' && e.payload.state.toLowerCase()}</span>)}
        </div>
      </article>
      <article className="card observations"><div className="card-top"><h2>Rehearsal input</h2>
        <span className="muted">Example data</span></div>
        <div className="preview"><span aria-hidden="true">◉</span>
          <p>Camera is off during replay</p><small>No video is recorded.</small></div>
        <div className="metrics"><div><small>Example pace</small><strong>
          {speech?.type === 'speech.metrics' && speech.payload.wpm != null
            ? `${Math.round(speech.payload.wpm)} WPM` : '—'}</strong></div>
          <div><small>Inputs</small><strong>{snapshot?.input_status.speech.availability === 'available'
            ? 'Speech available' : 'Awaiting example'}</strong></div></div>
        <h3>Transcript</h3><p className="transcript">{transcript?.length
          ? transcript.map(e => e.type === 'speech.transcript' ? e.payload.text : '').join(' ')
          : 'No transcript in this example yet.'}</p>
        {Object.entries(snapshot?.input_status || {}).filter(([, value]) => value.availability !== 'available')
          .map(([name, value]) => <p className="notice" key={name}>
            {name === 'speech' ? 'Speech' : 'Camera'}: {value.reason.replaceAll('_', ' ')}</p>)}
      </article>
    </section>
    {feedback && <section className="summary" aria-label="Example coaching">
      <div className="eyebrow">AFTER THE REHEARSAL</div><h2>A few moments to learn from.</h2>
      <p className="muted">Authored example coaching · {time(feedback.duration_s)} rehearsal</p>
      <div className="moments">{feedback.moments.map((moment, index) => <article className="card" key={index}>
        <div className="moment-top"><span>{time(moment.timestamp_s)}</span>
          <strong>{moment.kind === 'strength' ? 'Keep doing this' : 'Try next time'}</strong></div>
        <p>{moment.observation}</p><p className="suggestion">{moment.suggestion}</p>
      </article>)}</div>
      {feedback.limitations.map((limitation, index) => <p className="notice" key={index}>{limitation}</p>)}
      {!feedback.moments.length && <p>No supported coaching moments in this example.</p>}
    </section>}
    {snapshot?.phase === 'completed' && snapshot.feedback_status === 'unavailable'
      && <p className="notice">Replay stopped early. The authored example summary is unavailable.</p>}
    <footer><span><i /> {connection}</span><span>Private practice, one rehearsal at a time.</span></footer>
  </main>;
}

createRoot(document.getElementById('root')!).render(<App />);
