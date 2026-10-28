import React from 'react';
import { AlertTriangle, ShieldX, ExternalLink, ArrowRight, ShieldCheck } from 'lucide-react';

export default function AlertDetailModal({ alert = null, onClose }) {
  if (!alert) return null;

  return (
    <div style={{
      position: 'relative',
      background: 'linear-gradient(135deg, rgba(35, 12, 18, 0.95) 0%, rgba(20, 10, 15, 0.95) 100%)',
      border: '1px solid rgba(239, 68, 68, 0.4)',
      borderRadius: '12px',
      padding: '1.25rem',
      boxShadow: 'var(--shadow-alert)',
      marginTop: '1rem',
      animation: 'pulse-border 2.5s infinite',
    }}>
      
      {/* Alert Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{
            background: 'rgba(239, 68, 68, 0.25)',
            padding: '0.5rem',
            borderRadius: '10px',
            color: '#ef4444'
          }}>
            <ShieldX size={22} />
          </div>
          <div>
            <span className="badge badge-rose" style={{ marginBottom: '0.2rem' }}>
              Security Anomaly Triggered
            </span>
            <h3 style={{ fontSize: '1.05rem', fontWeight: '800', color: '#f87171' }}>
              {alert.category || 'Intrusion Alert'}
            </h3>
          </div>
        </div>

        {alert.cve_reference && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', fontSize: '0.75rem', color: '#cbd5e1', background: 'rgba(0,0,0,0.3)', padding: '0.35rem 0.75rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.1)' }}>
            <ExternalLink size={12} />
            <span>{alert.cve_reference}</span>
          </div>
        )}
      </div>

      {/* Offending Transition Box - Key Requirement of the Problem Statement! */}
      <div style={{
        background: 'rgba(0, 0, 0, 0.45)',
        border: '1px solid rgba(239, 68, 68, 0.3)',
        borderRadius: '10px',
        padding: '1rem',
        marginBottom: '0.85rem'
      }}>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '0.4rem' }}>
          Transition Responsible for Alert:
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', flexWrap: 'wrap' }}>
          <div style={{ background: '#1e293b', padding: '0.4rem 0.8rem', borderRadius: '6px', fontFamily: 'var(--font-mono)', fontWeight: '700', color: '#93c5fd' }}>
            State: {alert.from_state || 'UNKNOWN'}
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', color: '#ef4444', fontWeight: '700', fontFamily: 'var(--font-mono)' }}>
            <ArrowRight size={16} />
            <span style={{ background: 'rgba(239, 68, 68, 0.2)', padding: '0.3rem 0.6rem', borderRadius: '6px', border: '1px solid rgba(239, 68, 68, 0.4)' }}>
              Event: {alert.event || 'UNKNOWN'}
            </span>
            <ArrowRight size={16} />
          </div>

          <div style={{ background: 'rgba(239, 68, 68, 0.3)', padding: '0.4rem 0.8rem', borderRadius: '6px', fontFamily: 'var(--font-mono)', fontWeight: '800', color: '#fca5a5' }}>
            Result: ERROR_STATE (Rejection)
          </div>
        </div>

        {alert.allowed_events && alert.allowed_events.length > 0 && (
          <div style={{ marginTop: '0.65rem', fontSize: '0.8rem', color: 'var(--text-dim)' }}>
            RFC 793 Grammatically Expected Symbols: <strong style={{ color: '#34d399', fontFamily: 'var(--font-mono)' }}>{alert.allowed_events.join(', ')}</strong>
          </div>
        )}
      </div>

      {/* Detailed Explanation */}
      <p style={{ fontSize: '0.85rem', color: '#cbd5e1', lineHeight: '1.6', marginBottom: '0.75rem' }}>
        {alert.explanation}
      </p>

      {/* Mitigation Action */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.75rem', color: '#38bdf8', background: 'rgba(6, 182, 212, 0.1)', padding: '0.5rem 0.8rem', borderRadius: '8px', border: '1px solid rgba(6, 182, 212, 0.2)' }}>
        <ShieldCheck size={14} />
        <span><strong>Recommended Firewall Defense:</strong> Drop incoming packet segment and increment firewall state violation counter.</span>
      </div>

    </div>
  );
}
