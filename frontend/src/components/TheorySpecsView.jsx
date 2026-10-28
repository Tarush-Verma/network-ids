import React from 'react';
import { Cpu, BookOpen, Layers, CheckCircle2 } from 'lucide-react';

export default function TheorySpecsView() {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      
      {/* Overview Banner */}
      <div className="glass-panel" style={{ padding: '1.5rem', background: 'linear-gradient(135deg, rgba(6, 182, 212, 0.12) 0%, rgba(18, 24, 38, 0.8) 100%)' }}>
        <h2 style={{ fontSize: '1.25rem', fontWeight: '800', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <Cpu size={22} color="#06b6d4" />
          <span>Theory of Computation (TOC): Formal Automata Foundations</span>
        </h2>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
          Under the Chomsky Hierarchy, communication protocol event sequences can be strictly defined as a <strong>Type-3 Regular Language L(M)</strong> recognized by a Deterministic Finite-State Automaton (DFA).
        </p>
      </div>

      {/* 5-Tuple Definition */}
      <div className="glass-panel" style={{ padding: '1.25rem' }}>
        <h3 style={{ fontSize: '1.05rem', fontWeight: '700', marginBottom: '0.75rem', color: '#93c5fd' }}>
          Formal 5-Tuple Definition: M = (Q, &Sigma;, &delta;, q₀, F)
        </h3>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1rem', fontSize: '0.85rem' }}>
          
          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <strong style={{ color: '#06b6d4' }}>Q (Finite Set of States):</strong>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#cbd5e1', marginTop: '0.35rem' }}>
              &#123;CLOSED, LISTEN, SYN_SENT, SYN_RCVD, ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2, CLOSE_WAIT, LAST_ACK, TIME_WAIT, ERROR_STATE&#125;
            </p>
          </div>

          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <strong style={{ color: '#a855f7' }}>&Sigma; (Input Alphabet / Events):</strong>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#cbd5e1', marginTop: '0.35rem' }}>
              &#123;LISTEN, SYN, SYN_ACK, ACK, DATA, FIN, RST, TIMEOUT&#125;
            </p>
          </div>

          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <strong style={{ color: '#34d399' }}>q₀ (Initial State):</strong>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#cbd5e1', marginTop: '0.35rem' }}>
              q₀ = CLOSED
            </p>
          </div>

          <div style={{ background: 'rgba(0,0,0,0.3)', padding: '0.85rem', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.05)' }}>
            <strong style={{ color: '#fbbf24' }}>F (Accepting / Clean States):</strong>
            <p style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: '#cbd5e1', marginTop: '0.35rem' }}>
              F = &#123;CLOSED, TIME_WAIT&#125;
            </p>
          </div>

        </div>
      </div>

      {/* Regular Grammar & Anomaly Language Complement */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))', gap: '1rem' }}>
        
        {/* Right-Linear Grammar */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BookOpen size={18} color="#6366f1" />
            <span>Right-Linear Regular Grammar G</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
            Production rules generating legitimate protocol sentences:
          </p>

          <pre style={{
            background: 'rgba(10, 15, 25, 0.9)',
            padding: '0.85rem',
            borderRadius: '8px',
            fontSize: '0.8rem',
            fontFamily: 'var(--font-mono)',
            color: '#a5b4fc',
            lineHeight: '1.6',
            border: '1px solid rgba(255,255,255,0.06)'
          }}>
{`S  -> SYN · A | LISTEN · B
A  -> SYN_ACK · C
B  -> SYN · D
D  -> ACK · C
C  -> DATA · C | ACK · C | FIN · E | RST · CLOSED
E  -> ACK · F
F  -> FIN · G
G  -> TIMEOUT | ε`}
          </pre>
        </div>

        {/* Anomaly Complement Space */}
        <div className="glass-panel" style={{ padding: '1.25rem' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: '700', marginBottom: '0.65rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={18} color="#ef4444" />
            <span>Complement Language Anomaly Space</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.85rem' }}>
            Intrusion detection leverages the theorem that regular languages are <strong>closed under complementation</strong>:
          </p>

          <div style={{ background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '0.85rem', borderRadius: '8px', marginBottom: '0.85rem' }}>
            <div style={{ fontFamily: 'var(--font-mono)', fontSize: '1.05rem', fontWeight: '700', color: '#f87171', textAlign: 'center' }}>
              L_anomaly = &Sigma;* \ L(M)
            </div>
          </div>

          <p style={{ fontSize: '0.825rem', color: '#cbd5e1', lineHeight: '1.6' }}>
            Any event sequence <code style={{ color: '#fca5a5' }}>w &isin; L_anomaly</code> contains at least one symbol <code style={{ color: '#fca5a5' }}>&sigma;_k</code> such that <code style={{ color: '#fca5a5' }}>&delta;(q_&#123;k-1&#125;, &sigma;_k) = &empty;</code>. The deterministic automaton immediately traps this into <strong style={{ color: '#ef4444' }}>ERROR_STATE</strong> with zero latency.
          </p>
        </div>

      </div>

    </div>
  );
}
