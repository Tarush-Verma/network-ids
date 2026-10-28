import React from 'react';
import { ShieldCheck, ShieldAlert, Cpu, Zap, Layers, Clock } from 'lucide-react';

export default function DetectorScorecard({ verdicts = {} }) {
  const fsm = verdicts.fsm || { is_anomaly: false, confidence: 1.0, latency_ms: 0.05, attack_category: 'Normal' };
  const ml = verdicts.ml || { is_anomaly: false, confidence: 0.95, latency_ms: 44.8, attack_category: 'Normal' };
  const hybrid = verdicts.hybrid || { is_anomaly: false, confidence: 0.98, latency_ms: 44.9, attack_category: 'Normal' };

  const cards = [
    {
      name: 'Pure Rule-Based FSM',
      icon: Cpu,
      color: '#06b6d4',
      verdict: fsm,
      technique: 'Deterministic Lookup: δ(s_t, e_t)',
      description: 'Zero false negatives on grammar breaches. Sub-millisecond lookup, but blind to volumetric/temporal dwell attacks.',
    },
    {
      name: 'Pure Machine Learning',
      icon: Zap,
      color: '#a855f7',
      verdict: ml,
      technique: 'Random Forest + Isolation Forest',
      description: 'Evaluates sequence n-grams, Markov log-likelihood, and inter-arrival time statistics.',
    },
    {
      name: 'Hybrid Multi-Stage Engine',
      icon: Layers,
      color: '#6366f1',
      verdict: hybrid,
      isPrimary: true,
      technique: 'Stage 1 FSM Gate + Stage 2 ML Manifold',
      description: 'Intercepts syntactic breaches instantly (100% confidence) while catching statistical & zero-day attacks.',
    },
  ];

  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', marginTop: '1rem' }}>
      {cards.map((c) => {
        const Icon = c.icon;
        const isAlert = c.verdict.is_anomaly;
        const statusColor = isAlert ? '#ef4444' : '#10b981';

        return (
          <div
            key={c.name}
            className="glass-panel"
            style={{
              padding: '1.25rem',
              borderTop: `3px solid ${c.isPrimary ? (isAlert ? '#ef4444' : '#6366f1') : c.color}`,
              background: isAlert ? 'rgba(30, 15, 20, 0.7)' : 'var(--bg-card)',
            }}
          >
            {/* Card Header */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '0.75rem' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                <div style={{
                  background: `rgba(${c.isPrimary ? '99, 102, 241' : '6, 182, 212'}, 0.15)`,
                  padding: '0.45rem',
                  borderRadius: '8px',
                  color: c.color
                }}>
                  <Icon size={18} />
                </div>
                <div>
                  <h3 style={{ fontSize: '0.925rem', fontWeight: '700' }}>{c.name}</h3>
                  <span style={{ fontSize: '0.7rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>{c.technique}</span>
                </div>
              </div>

              {/* Status Badge */}
              <span className={`badge ${isAlert ? 'badge-rose' : 'badge-emerald'}`}>
                {isAlert ? <ShieldAlert size={12} /> : <ShieldCheck size={12} />}
                {isAlert ? 'ALERT' : 'BENIGN'}
              </span>
            </div>

            {/* Attack Category / Verdict Callout */}
            <div style={{
              background: isAlert ? 'rgba(239, 68, 68, 0.12)' : 'rgba(16, 185, 129, 0.08)',
              border: `1px solid ${isAlert ? 'rgba(239, 68, 68, 0.3)' : 'rgba(16, 185, 129, 0.2)'}`,
              borderRadius: '8px',
              padding: '0.65rem',
              marginBottom: '0.85rem'
            }}>
              <div style={{ fontSize: '0.725rem', color: 'var(--text-dim)', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
                Classification
              </div>
              <div style={{ fontSize: '0.95rem', fontWeight: '700', color: statusColor, fontFamily: 'var(--font-mono)' }}>
                {c.verdict.attack_category || (isAlert ? 'Threat Detected' : 'Normal Traffic')}
              </div>
            </div>

            {/* Confidence & Latency Metrics */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.775rem', marginBottom: '0.5rem' }}>
              <span style={{ color: 'var(--text-muted)' }}>Confidence:</span>
              <span style={{ fontWeight: '700', color: '#f8fafc', fontFamily: 'var(--font-mono)' }}>
                {Math.round((c.verdict.confidence || 0.95) * 100)}%
              </span>
            </div>

            {/* Meter Bar */}
            <div style={{ width: '100%', height: '6px', background: 'rgba(255,255,255,0.08)', borderRadius: '3px', overflow: 'hidden', marginBottom: '0.85rem' }}>
              <div style={{
                width: `${Math.round((c.verdict.confidence || 0.95) * 100)}%`,
                height: '100%',
                background: isAlert ? 'linear-gradient(90deg, #f59e0b, #ef4444)' : 'linear-gradient(90deg, #6366f1, #10b981)',
                transition: 'width 0.3s ease'
              }} />
            </div>

            {/* Latency Footer */}
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.75rem', color: 'var(--text-dim)', borderTop: '1px solid rgba(255,255,255,0.06)', paddingTop: '0.5rem' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
                <Clock size={12} /> Execution Latency:
              </span>
              <strong style={{ color: '#38bdf8', fontFamily: 'var(--font-mono)' }}>
                {c.verdict.latency_ms ? `${c.verdict.latency_ms} ms` : '0.05 ms'}
              </strong>
            </div>

          </div>
        );
      })}
    </div>
  );
}
