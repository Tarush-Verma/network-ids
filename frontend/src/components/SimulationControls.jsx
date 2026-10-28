import React from 'react';
import { Play, RotateCcw, FastForward, Shield, AlertOctagon, Terminal } from 'lucide-react';

export default function SimulationControls({
  scenarios = [],
  selectedScenario = 'normal_session',
  setSelectedScenario,
  isRunning = false,
  onStartSimulation,
  onReset,
  speed = 1.0,
  setSpeed,
}) {
  return (
    <div className="glass-panel" style={{ padding: '1.25rem', marginBottom: '1rem' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Scenario Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem', flex: '1 1 360px' }}>
          <label style={{ fontSize: '0.85rem', fontWeight: '700', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
            Attack Scenario:
          </label>
          <select
            value={selectedScenario}
            onChange={(e) => setSelectedScenario(e.target.value)}
            disabled={isRunning}
            style={{
              flex: 1,
              background: 'rgba(15, 23, 42, 0.8)',
              border: '1px solid var(--border-color)',
              color: 'var(--text-main)',
              padding: '0.65rem 0.9rem',
              borderRadius: '10px',
              fontFamily: 'var(--font-sans)',
              fontSize: '0.875rem',
              outline: 'none',
              cursor: isRunning ? 'not-allowed' : 'pointer'
            }}
          >
            {scenarios.map((sc) => (
              <option key={sc.id} value={sc.id} style={{ background: '#0f172a' }}>
                {sc.name} ({sc.type})
              </option>
            ))}
          </select>
        </div>

        {/* Playback Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <button
            onClick={onStartSimulation}
            disabled={isRunning}
            className="btn btn-primary"
            id="btn-run-simulation"
          >
            <Play size={16} fill="currentColor" />
            <span>{isRunning ? 'Simulating Stream...' : 'Inject & Analyze Traffic'}</span>
          </button>

          <button
            onClick={onReset}
            disabled={isRunning}
            className="btn btn-secondary"
            title="Reset FSM and clear stream"
          >
            <RotateCcw size={16} />
            <span>Reset</span>
          </button>
        </div>

        {/* Speed Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', background: 'rgba(0,0,0,0.25)', padding: '0.25rem', borderRadius: '8px' }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-dim)', padding: '0 0.35rem' }}>Speed:</span>
          {[0.5, 1.0, 2.0, 4.0].map((s) => (
            <button
              key={s}
              onClick={() => setSpeed(s)}
              style={{
                background: speed === s ? 'rgba(99, 102, 241, 0.3)' : 'transparent',
                border: speed === s ? '1px solid rgba(99, 102, 241, 0.5)' : 'none',
                color: speed === s ? '#ffffff' : 'var(--text-dim)',
                padding: '0.25rem 0.55rem',
                borderRadius: '6px',
                fontSize: '0.75rem',
                fontWeight: '600',
                cursor: 'pointer'
              }}
            >
              {s}x
            </button>
          ))}
        </div>

      </div>
    </div>
  );
}
