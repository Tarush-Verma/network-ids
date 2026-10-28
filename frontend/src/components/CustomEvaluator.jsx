import React, { useState } from 'react';
import { Terminal, Play, RotateCcw, AlertTriangle, CheckCircle, Shield } from 'lucide-react';

export default function CustomEvaluator() {
  const [tokens, setTokens] = useState(['SYN', 'SYN_ACK', 'ACK', 'DATA', 'FIN', 'ACK', 'FIN', 'TIMEOUT']);
  const [deltaT, setDeltaT] = useState(0.02);
  const [payloadSize, setPayloadSize] = useState(512);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const availableSymbols = ['SYN', 'SYN_ACK', 'ACK', 'DATA', 'FIN', 'RST', 'TIMEOUT'];

  const presets = [
    { name: 'Standard Legitimate TCP Flow', seq: ['SYN', 'SYN_ACK', 'ACK', 'DATA', 'FIN', 'ACK', 'FIN', 'TIMEOUT'], delta: 0.02, payload: 512 },
    { name: 'Attack: Out-of-Order ACK (Closed Socket)', seq: ['ACK'], delta: 0.01, payload: 0 },
    { name: 'Attack: Premature Payload Injection', seq: ['DATA'], delta: 0.01, payload: 1024 },
    { name: 'Attack: Stealth FIN Scan', seq: ['FIN'], delta: 0.05, payload: 0 },
    { name: 'Attack: Repeated SYN Flood Burst', seq: ['SYN', 'SYN', 'SYN', 'SYN', 'SYN', 'SYN'], delta: 0.0005, payload: 0 },
    { name: 'Attack: Slowloris High Dwell Stall', seq: ['SYN', 'SYN_ACK', 'DATA', 'DATA', 'DATA'], delta: 35.0, payload: 4 },
  ];

  const handleAddSymbol = (sym) => {
    setTokens([...tokens, sym]);
  };

  const handleRemoveToken = (idx) => {
    setTokens(tokens.filter((_, i) => i !== idx));
  };

  const handleApplyPreset = (p) => {
    setTokens(p.seq);
    setDeltaT(p.delta);
    setPayloadSize(p.payload);
    setResult(null);
  };

  const handleEvaluate = async () => {
    if (tokens.length === 0) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/detect/custom', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          events: tokens,
          delta_t: parseFloat(deltaT),
          payload_size: parseInt(payloadSize),
        }),
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      console.error('Failed to evaluate custom sequence:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
      
      {/* Intro */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: '800', marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Terminal size={20} color="#6366f1" />
          <span>Interactive Protocol Sequence Builder</span>
        </h2>
        <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
          Compose custom protocol event words <strong style={{ color: '#93c5fd', fontFamily: 'var(--font-mono)' }}>w &isin; &Sigma;*</strong> to test the grammar acceptance of the FSM and the classification of the ML models.
        </p>
      </div>

      {/* Presets Bar */}
      <div className="glass-panel" style={{ padding: '1rem' }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '0.6rem', fontWeight: '700' }}>
          Load Test Presets:
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {presets.map((p) => (
            <button
              key={p.name}
              onClick={() => handleApplyPreset(p)}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid rgba(255, 255, 255, 0.1)',
                color: '#cbd5e1',
                padding: '0.4rem 0.75rem',
                borderRadius: '8px',
                fontSize: '0.775rem',
                cursor: 'pointer',
                fontFamily: 'var(--font-sans)',
              }}
            >
              {p.name}
            </button>
          ))}
        </div>
      </div>

      {/* Builder Workspace */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
          <span style={{ fontSize: '0.85rem', fontWeight: '700' }}>Current Sequence w:</span>
          <button
            onClick={() => { setTokens([]); setResult(null); }}
            style={{ background: 'transparent', border: 'none', color: '#f87171', fontSize: '0.75rem', cursor: 'pointer' }}
          >
            Clear All
          </button>
        </div>

        {/* Tokens Container */}
        <div style={{
          minHeight: '60px',
          background: 'rgba(10, 15, 25, 0.8)',
          border: '1px dashed rgba(255, 255, 255, 0.15)',
          borderRadius: '10px',
          padding: '0.75rem',
          display: 'flex',
          flexWrap: 'wrap',
          gap: '0.5rem',
          alignItems: 'center',
          marginBottom: '1rem'
        }}>
          {tokens.length === 0 ? (
            <span style={{ color: 'var(--text-dim)', fontSize: '0.8rem' }}>
              Sequence is empty. Click any symbol below to append.
            </span>
          ) : (
            tokens.map((tok, i) => (
              <span
                key={i}
                style={{
                  background: 'rgba(99, 102, 241, 0.2)',
                  border: '1px solid rgba(99, 102, 241, 0.4)',
                  color: '#e0e7ff',
                  padding: '0.3rem 0.6rem',
                  borderRadius: '6px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.8rem',
                  fontWeight: '700',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.35rem',
                  cursor: 'pointer'
                }}
                onClick={() => handleRemoveToken(i)}
                title="Click to remove"
              >
                {tok} &times;
              </span>
            ))
          )}
        </div>

        {/* Available Symbols Keyboard */}
        <div style={{ marginBottom: '1.25rem' }}>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-dim)', textTransform: 'uppercase', marginBottom: '0.4rem', fontWeight: '700' }}>
            Available Alphabet Symbols (&Sigma;):
          </div>
          <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
            {availableSymbols.map((sym) => (
              <button
                key={sym}
                onClick={() => handleAddSymbol(sym)}
                style={{
                  background: 'rgba(6, 182, 212, 0.12)',
                  border: '1px solid rgba(6, 182, 212, 0.3)',
                  color: '#67e8f9',
                  padding: '0.45rem 0.85rem',
                  borderRadius: '8px',
                  fontFamily: 'var(--font-mono)',
                  fontSize: '0.85rem',
                  fontWeight: '700',
                  cursor: 'pointer'
                }}
              >
                + {sym}
              </button>
            ))}
          </div>
        </div>

        {/* Numerical Params */}
        <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>
              Inter-Arrival Time (&Delta;t in seconds):
            </label>
            <input
              type="number"
              step="0.001"
              value={deltaT}
              onChange={(e) => setDeltaT(e.target.value)}
              style={{
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
                padding: '0.5rem',
                borderRadius: '8px',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.85rem',
                width: '140px'
              }}
            />
          </div>

          <div>
            <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '0.3rem' }}>
              DATA Payload Size (bytes):
            </label>
            <input
              type="number"
              value={payloadSize}
              onChange={(e) => setPayloadSize(e.target.value)}
              style={{
                background: 'rgba(15, 23, 42, 0.8)',
                border: '1px solid var(--border-color)',
                color: 'var(--text-main)',
                padding: '0.5rem',
                borderRadius: '8px',
                fontFamily: 'var(--font-mono)',
                fontSize: '0.85rem',
                width: '140px'
              }}
            />
          </div>
        </div>

        {/* Evaluate Button */}
        <button
          onClick={handleEvaluate}
          disabled={loading || tokens.length === 0}
          className="btn btn-primary"
        >
          <Play size={16} fill="currentColor" />
          <span>{loading ? 'Evaluating Model...' : 'Run Detection Pipeline'}</span>
        </button>
      </div>

      {/* Result Display */}
      {result && (
        <div className="glass-panel" style={{ padding: '1.25rem', border: `1px solid ${result.hybrid_verdict.is_anomaly ? '#ef4444' : '#10b981'}` }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '800', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            {result.hybrid_verdict.is_anomaly ? <AlertTriangle color="#ef4444" size={20} /> : <CheckCircle color="#10b981" size={20} />}
            <span>Verdict: {result.hybrid_verdict.attack_category}</span>
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '0.75rem', marginBottom: '0.75rem' }}>
            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Rule-Based FSM:</span>
              <div style={{ fontWeight: '700', color: result.fsm_verdict.is_anomaly ? '#f87171' : '#34d399' }}>
                {result.fsm_verdict.is_anomaly ? 'ANOMALY (Syntax)' : 'VALID'} ({result.fsm_verdict.latency_ms} ms)
              </div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Pure ML:</span>
              <div style={{ fontWeight: '700', color: result.ml_verdict.is_anomaly ? '#f87171' : '#34d399' }}>
                {result.ml_verdict.attack_category} ({result.ml_verdict.latency_ms} ms)
              </div>
            </div>

            <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.65rem', borderRadius: '8px' }}>
              <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)' }}>Hybrid Engine:</span>
              <div style={{ fontWeight: '800', color: result.hybrid_verdict.is_anomaly ? '#f87171' : '#34d399' }}>
                {result.hybrid_verdict.attack_category} ({Math.round(result.hybrid_verdict.confidence * 100)}% Conf)
              </div>
            </div>
          </div>

          <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6' }}>
            {result.hybrid_verdict.explanation}
          </p>
        </div>
      )}

    </div>
  );
}
