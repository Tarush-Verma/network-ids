import React from 'react';
import { AlertTriangle, CheckCircle, Info } from 'lucide-react';

export default function FsmGraphViewer({
  currentState = 'CLOSED',
  lastTransition = null,
  isAnomaly = false,
  offendingTransition = null
}) {
  // Pre-calculated ergonomic layout coordinates for 11 states
  const nodes = [
    { id: 'CLOSED', x: 120, y: 320, label: 'CLOSED', isInitial: true, isAccept: true },
    { id: 'LISTEN', x: 280, y: 150, label: 'LISTEN' },
    { id: 'SYN_SENT', x: 280, y: 490, label: 'SYN_SENT' },
    { id: 'SYN_RCVD', x: 480, y: 220, label: 'SYN_RCVD' },
    { id: 'ESTABLISHED', x: 650, y: 320, label: 'ESTABLISHED' },
    { id: 'FIN_WAIT_1', x: 820, y: 170, label: 'FIN_WAIT_1' },
    { id: 'FIN_WAIT_2', x: 1000, y: 170, label: 'FIN_WAIT_2' },
    { id: 'TIME_WAIT', x: 1000, y: 360, label: 'TIME_WAIT', isAccept: true },
    { id: 'CLOSE_WAIT', x: 820, y: 450, label: 'CLOSE_WAIT' },
    { id: 'LAST_ACK', x: 650, y: 490, label: 'LAST_ACK' },
    { id: 'ERROR_STATE', x: 500, y: 620, label: 'ERROR_STATE', isError: true },
  ];

  // Transition connections
  const edges = [
    { from: 'CLOSED', to: 'LISTEN', event: 'LISTEN', curve: -15 },
    { from: 'CLOSED', to: 'SYN_SENT', event: 'SYN', curve: 15 },
    { from: 'LISTEN', to: 'SYN_RCVD', event: 'SYN', curve: 0 },
    { from: 'SYN_SENT', to: 'ESTABLISHED', event: 'SYN_ACK', curve: 0 },
    { from: 'SYN_RCVD', to: 'ESTABLISHED', event: 'ACK', curve: 0 },
    { from: 'ESTABLISHED', to: 'ESTABLISHED', event: 'DATA', selfLoop: true },
    { from: 'ESTABLISHED', to: 'FIN_WAIT_1', event: 'FIN', curve: -15 },
    { from: 'FIN_WAIT_1', to: 'FIN_WAIT_2', event: 'ACK', curve: 0 },
    { from: 'FIN_WAIT_2', to: 'TIME_WAIT', event: 'FIN', curve: 0 },
    { from: 'TIME_WAIT', to: 'CLOSED', event: 'TIMEOUT', curve: 50 },
    { from: 'ESTABLISHED', to: 'CLOSE_WAIT', event: 'FIN', curve: 15 },
    { from: 'CLOSE_WAIT', to: 'LAST_ACK', event: 'FIN', curve: 0 },
    { from: 'LAST_ACK', to: 'CLOSED', event: 'ACK', curve: 45 },
  ];

  const getNode = (id) => nodes.find(n => n.id === id) || { x: 0, y: 0 };

  return (
    <div className="glass-panel" style={{ padding: '1.25rem', position: 'relative', overflow: 'hidden' }}>
      
      {/* Header bar */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem' }}>
        <div>
          <h2 style={{ fontSize: '1rem', fontWeight: '700', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>Protocol State Automaton M = (Q, &Sigma;, &delta;, q₀, F)</span>
            {isAnomaly ? (
              <span className="badge badge-rose">
                <AlertTriangle size={12} /> State Breach
              </span>
            ) : (
              <span className="badge badge-emerald">
                <CheckCircle size={12} /> RFC 793 Conforming
              </span>
            )}
          </h2>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            Current State: <strong style={{ color: currentState === 'ERROR_STATE' ? '#ef4444' : '#06b6d4', fontFamily: 'var(--font-mono)' }}>{currentState}</strong>
            {lastTransition && (
              <span style={{ marginLeft: '0.75rem' }}>
                | Last Event: <code style={{ color: '#a5b4fc' }}>{lastTransition.event}</code>
              </span>
            )}
          </p>
        </div>

        {/* Legend */}
        <div style={{ display: 'flex', gap: '0.85rem', fontSize: '0.7rem', color: 'var(--text-dim)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#6366f1' }} /> Active
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#10b981' }} /> Accept (F)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#ef4444' }} /> Error State
          </span>
        </div>
      </div>

      {/* SVG Canvas for State Machine */}
      <div style={{ width: '100%', height: '520px', background: 'rgba(5, 7, 12, 0.65)', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)', position: 'relative' }}>
        <svg viewBox="0 0 1150 720" style={{ width: '100%', height: '100%' }}>
          
          <defs>
            {/* Standard edge marker */}
            <marker id="arrow" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="rgba(255, 255, 255, 0.35)" />
            </marker>

            {/* Active edge marker */}
            <marker id="arrow-active" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
              <path d="M 0 1 L 9 5 L 0 9 z" fill="#06b6d4" />
            </marker>

            {/* Anomaly violation marker */}
            <marker id="arrow-anomaly" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#ef4444" />
            </marker>
          </defs>

          {/* Regular Transition Edges */}
          {edges.map((edge, idx) => {
            const src = getNode(edge.from);
            const dst = getNode(edge.to);
            const isActive = lastTransition && lastTransition.from_state === edge.from && lastTransition.to_state === edge.to;

            if (edge.selfLoop) {
              return (
                <g key={`loop-${idx}`}>
                  <path
                    d={`M ${src.x - 15} ${src.y - 32} C ${src.x - 40} ${src.y - 85}, ${src.x + 40} ${src.y - 85}, ${src.x + 15} ${src.y - 32}`}
                    fill="none"
                    stroke={isActive ? '#06b6d4' : 'rgba(255,255,255,0.2)'}
                    strokeWidth={isActive ? 2.5 : 1.2}
                    className={isActive ? 'edge-active' : ''}
                    markerEnd={isActive ? 'url(#arrow-active)' : 'url(#arrow)'}
                  />
                  <text x={src.x} y={src.y - 75} fill={isActive ? '#06b6d4' : 'rgba(255,255,255,0.5)'} fontSize="11" textAnchor="middle" fontFamily="var(--font-mono)">
                    {edge.event}
                  </text>
                </g>
              );
            }

            const dx = dst.x - src.x;
            const dy = dst.y - src.y;
            const cx = (src.x + dst.x) / 2 + (edge.curve || 0);
            const cy = (src.y + dst.y) / 2 + (edge.curve || 0);

            return (
              <g key={`edge-${idx}`}>
                <path
                  d={`M ${src.x} ${src.y} Q ${cx} ${cy} ${dst.x} ${dst.y}`}
                  fill="none"
                  stroke={isActive ? '#06b6d4' : 'rgba(255, 255, 255, 0.2)'}
                  strokeWidth={isActive ? 2.5 : 1.2}
                  className={isActive ? 'edge-active' : ''}
                  markerEnd={isActive ? 'url(#arrow-active)' : 'url(#arrow)'}
                />
                <text
                  x={cx}
                  y={cy - 4}
                  fill={isActive ? '#38bdf8' : 'rgba(255, 255, 255, 0.45)'}
                  fontSize="10.5"
                  fontWeight="600"
                  textAnchor="middle"
                  fontFamily="var(--font-mono)"
                >
                  {edge.event}
                </text>
              </g>
            );
          })}

          {/* Anomaly Laser Path (rendered when illegal transition occurs) */}
          {offendingTransition && (
            <g>
              <line
                x1={getNode(offendingTransition.from_state).x}
                y1={getNode(offendingTransition.from_state).y}
                x2={getNode('ERROR_STATE').x}
                y2={getNode('ERROR_STATE').y}
                stroke="#ef4444"
                strokeWidth="3.5"
                strokeDasharray="8, 4"
                className="edge-active"
                markerEnd="url(#arrow-anomaly)"
              />
              <text
                x={(getNode(offendingTransition.from_state).x + getNode('ERROR_STATE').x) / 2}
                y={(getNode(offendingTransition.from_state).y + getNode('ERROR_STATE').y) / 2 - 10}
                fill="#f87171"
                fontSize="12"
                fontWeight="700"
                textAnchor="middle"
                fontFamily="var(--font-mono)"
              >
                ILLEGAL: {offendingTransition.event} ⚠
              </text>
            </g>
          )}

          {/* State Nodes */}
          {nodes.map((node) => {
            const isCurrent = currentState === node.id;
            const isErrorState = node.id === 'ERROR_STATE';
            const radius = isCurrent ? 36 : 30;

            let fillColor = 'rgba(15, 23, 42, 0.9)';
            let strokeColor = 'rgba(255, 255, 255, 0.15)';
            let textColor = '#cbd5e1';

            if (isErrorState) {
              strokeColor = '#ef4444';
              fillColor = isCurrent ? 'rgba(239, 68, 68, 0.25)' : 'rgba(30, 10, 15, 0.9)';
              textColor = '#f87171';
            } else if (isCurrent) {
              strokeColor = '#6366f1';
              fillColor = 'rgba(99, 102, 241, 0.25)';
              textColor = '#ffffff';
            } else if (node.isAccept) {
              strokeColor = 'rgba(16, 185, 129, 0.4)';
              textColor = '#a7f3d0';
            }

            return (
              <g
                key={node.id}
                style={{
                  cursor: 'pointer',
                  animation: isCurrent ? (isErrorState ? 'pulse-error 1.5s infinite' : 'pulse-node 2s infinite') : 'none'
                }}
              >
                {/* Outer Glow Halo for Active State */}
                {isCurrent && (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={radius + 8}
                    fill="none"
                    stroke={isErrorState ? 'rgba(239, 68, 68, 0.4)' : 'rgba(99, 102, 241, 0.4)'}
                    strokeWidth="2"
                    strokeDasharray="4, 4"
                  />
                )}

                {/* Double Ring for Accept States F */}
                {node.isAccept && (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={radius + 4}
                    fill="none"
                    stroke={strokeColor}
                    strokeWidth="1"
                    strokeOpacity="0.5"
                  />
                )}

                {/* State Circle Body */}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={radius}
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={isCurrent ? 2.5 : 1.5}
                />

                {/* Initial Arrow for q0 (CLOSED) */}
                {node.isInitial && (
                  <g>
                    <line x1={node.x - 55} y1={node.y} x2={node.x - radius - 2} y2={node.y} stroke="#94a3b8" strokeWidth="2" markerEnd="url(#arrow)" />
                    <text x={node.x - 58} y={node.y - 8} fill="#94a3b8" fontSize="10" textAnchor="end" fontFamily="var(--font-mono)">Start (q₀)</text>
                  </g>
                )}

                {/* State Label */}
                <text
                  x={node.x}
                  y={node.y + 4}
                  fill={textColor}
                  fontSize={node.id.length > 9 ? '9.5' : '11'}
                  fontWeight={isCurrent ? '800' : '600'}
                  textAnchor="middle"
                  fontFamily="var(--font-mono)"
                >
                  {node.label}
                </text>
              </g>
            );
          })}
        </svg>
      </div>

    </div>
  );
}
