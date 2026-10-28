import React, { useRef, useEffect } from 'react';
import { Terminal, ShieldAlert, ShieldCheck } from 'lucide-react';

export default function LivePacketTable({ packets = [] }) {
  const tableEndRef = useRef(null);

  useEffect(() => {
    tableEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [packets]);

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', marginTop: '1rem', display: 'flex', flexDirection: 'column', height: '360px' }}>
      
      {/* Table Header Info */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <h3 style={{ fontSize: '0.95rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <Terminal size={16} color="#6366f1" />
          <span>Live Protocol Event Sequence Log</span>
        </h3>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', fontFamily: 'var(--font-mono)' }}>
          {packets.length} Packets Captured
        </span>
      </div>

      {/* Scrollable Packet Log */}
      <div style={{ flex: 1, overflowY: 'auto', borderRadius: '8px', border: '1px solid rgba(255,255,255,0.06)' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.775rem', textAlign: 'left', fontFamily: 'var(--font-mono)' }}>
          <thead style={{ background: 'rgba(15, 23, 42, 0.95)', position: 'sticky', top: 0, zIndex: 1, borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
            <tr style={{ color: 'var(--text-muted)' }}>
              <th style={{ padding: '0.5rem 0.75rem' }}>#</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Event</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Flow (Src &rarr; Dst)</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>&Delta;t (s)</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Payload</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Resulting State</th>
              <th style={{ padding: '0.5rem 0.75rem' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            {packets.length === 0 ? (
              <tr>
                <td colSpan={7} style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-dim)' }}>
                  Awaiting simulation start... Click "Inject & Analyze Traffic" to begin packet capture.
                </td>
              </tr>
            ) : (
              packets.map((pkt, idx) => {
                const isViolation = pkt.is_anomaly === 1 || pkt.next_state === 'ERROR_STATE';
                const eventColor = {
                  SYN: '#06b6d4',
                  SYN_ACK: '#38bdf8',
                  ACK: '#a855f7',
                  DATA: '#10b981',
                  FIN: '#f59e0b',
                  RST: '#ef4444',
                  TIMEOUT: '#64748b',
                }[pkt.event_type] || '#cbd5e1';

                return (
                  <tr
                    key={idx}
                    style={{
                      borderBottom: '1px solid rgba(255,255,255,0.04)',
                      background: isViolation ? 'rgba(239, 68, 68, 0.12)' : 'transparent',
                      transition: 'background 0.2s ease',
                    }}
                  >
                    <td style={{ padding: '0.45rem 0.75rem', color: 'var(--text-dim)' }}>{idx + 1}</td>
                    
                    {/* Event Type Badge */}
                    <td style={{ padding: '0.45rem 0.75rem' }}>
                      <span style={{
                        display: 'inline-block',
                        padding: '0.15rem 0.45rem',
                        borderRadius: '4px',
                        background: `rgba(255,255,255,0.05)`,
                        border: `1px solid ${eventColor}`,
                        color: eventColor,
                        fontWeight: '700',
                        fontSize: '0.725rem'
                      }}>
                        {pkt.event_type}
                      </span>
                    </td>

                    {/* Flow */}
                    <td style={{ padding: '0.45rem 0.75rem', color: '#cbd5e1' }}>
                      {pkt.src_ip}:{pkt.src_port} &rarr; {pkt.dst_ip}:{pkt.dst_port}
                    </td>

                    {/* Delta t */}
                    <td style={{ padding: '0.45rem 0.75rem', color: pkt.delta_t > 5 ? '#f59e0b' : '#94a3b8' }}>
                      {typeof pkt.delta_t === 'number' ? pkt.delta_t.toFixed(4) : pkt.delta_t}s
                    </td>

                    {/* Payload */}
                    <td style={{ padding: '0.45rem 0.75rem', color: pkt.payload_size > 0 ? '#34d399' : 'var(--text-dim)' }}>
                      {pkt.payload_size} B
                    </td>

                    {/* Resulting State */}
                    <td style={{ padding: '0.45rem 0.75rem', fontWeight: '600', color: pkt.next_state === 'ERROR_STATE' ? '#f87171' : '#93c5fd' }}>
                      {pkt.next_state || 'ESTABLISHED'}
                    </td>

                    {/* Status Badge */}
                    <td style={{ padding: '0.45rem 0.75rem' }}>
                      {isViolation ? (
                        <span style={{ color: '#f87171', display: 'flex', alignItems: 'center', gap: '0.25rem', fontWeight: '700' }}>
                          <ShieldAlert size={13} /> VIOLATION
                        </span>
                      ) : (
                        <span style={{ color: '#34d399', display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                          <ShieldCheck size={13} /> VALID
                        </span>
                      )}
                    </td>
                  </tr>
                );
              })
            )}
            <tr ref={tableEndRef} />
          </tbody>
        </table>
      </div>

    </div>
  );
}
