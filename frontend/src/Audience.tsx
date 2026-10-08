import { useEffect, useState } from 'react';
import { type AudienceState, stateCopy } from './copy';

// Simple 2D audience. Seats adopt the engine's state one after another so a change
// ripples through the room instead of flipping every face at once.

const SEATS = [
  { skin: '#e8c2a0', hair: '#3b2b22', shirt: '#7f9c86' },
  { skin: '#c99671', hair: '#1f1a17', shirt: '#c9a46b' },
  { skin: '#f0d3b8', hair: '#a5683a', shirt: '#6e8aa6' },
  { skin: '#8d5e41', hair: '#17110e', shirt: '#b47c6a' },
  { skin: '#d7a77f', hair: '#5a4130', shirt: '#9a8fb3' },
  { skin: '#f3dcc6', hair: '#d0a45d', shirt: '#6f9a95' },
  { skin: '#b07a55', hair: '#2b211b', shirt: '#cf8f5e' },
  { skin: '#e3b593', hair: '#6c6c6c', shirt: '#8a9a6a' },
];
const RIPPLE_MS = 140;

function seatState(state: AudienceState, index: number): AudienceState {
  // Not every listener reacts negatively at once; keeps the room readable, not alarming.
  if ((state === 'CONFUSED' || state === 'BORED') && index % 4 === 3) return 'NEUTRAL';
  return state;
}

const mouths: Record<AudienceState, string> = {
  ENGAGED: 'M42 54 Q50 62 58 54',
  INTERESTED: 'M44 55 Q50 59 56 55',
  NEUTRAL: 'M44 56 L56 56',
  CONFUSED: 'M43 57 Q47 54 50 57 Q53 60 57 56',
  BORED: 'M44 58 L55 57',
};

function Face({ state }: { state: AudienceState }) {
  const sleepy = state === 'BORED';
  const lift = state === 'INTERESTED' || state === 'ENGAGED' ? -2 : 0;
  return <g className="face">
    {sleepy
      ? <><path d="M39 46 L46 46" /><path d="M54 46 L61 46" /></>
      : <><circle cx="42.5" cy="45" r={state === 'INTERESTED' ? 3 : 2.5} />
        <circle cx="57.5" cy="45" r={state === 'INTERESTED' ? 3 : 2.5} /></>}
    {state === 'CONFUSED'
      ? <><path d="M38 38 L46 40" /><path d="M54 37 L62 35" /></>
      : <><path d={`M38 ${39 + lift} L46 ${39 + lift}`} /><path d={`M54 ${39 + lift} L62 ${39 + lift}`} /></>}
    <path className="mouth" d={mouths[state]} />
  </g>;
}

function Seat({ index, state }: { index: number; state: AudienceState }) {
  const look = SEATS[index % SEATS.length];
  return <div className={`seat seat-${state.toLowerCase()}`} style={{ ['--i' as string]: index }}>
    <svg viewBox="0 0 100 112" aria-hidden="true">
      <rect className="chair" x="14" y="58" width="72" height="54" rx="12" />
      <g className="person">
        <path d="M20 112 Q20 76 50 73 Q80 76 80 112 Z" fill={look.shirt} />
        <g className="head">
          <rect x="45" y="60" width="10" height="12" fill={look.skin} />
          <circle cx="50" cy="46" r="19" fill={look.skin} />
          <path d={index % 2 ? 'M31 44 Q31 24 50 25 Q69 24 69 44 Q63 33 50 34 Q37 33 31 44 Z'
            : 'M31 46 Q30 23 52 26 Q70 28 69 42 Q58 30 40 36 Q34 40 31 46 Z'} fill={look.hair} />
          <Face state={state} />
        </g>
      </g>
      {state === 'CONFUSED' && index % 3 === 0 && <text className="bubble" x="74" y="22">?</text>}
      {state === 'BORED' && index % 3 === 1 && <text className="bubble" x="72" y="22">z</text>}
    </svg>
  </div>;
}

export function Audience({ state, label }: { state: AudienceState; label: string }) {
  const [seats, setSeats] = useState<AudienceState[]>(() => SEATS.map(() => 'NEUTRAL'));

  useEffect(() => {
    const timers = SEATS.map((_, index) => setTimeout(() => {
      setSeats(current => current.map((value, i) => i === index ? seatState(state, index) : value));
    }, index * RIPPLE_MS));
    return () => timers.forEach(clearTimeout);
  }, [state]);

  return <div className="room" role="img" aria-label={`${label}: ${stateCopy[state].label.toLowerCase()}`}>
    <div className="row back">{seats.slice(0, 4).map((value, i) => <Seat key={i} index={i} state={value} />)}</div>
    <div className="row front">{seats.slice(4).map((value, i) => <Seat key={i + 4} index={i + 4} state={value} />)}</div>
  </div>;
}
