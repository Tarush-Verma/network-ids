import React from 'react';
import { Shield, Activity, BarChart3, Terminal, Cpu } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, isConnected }) {
  const tabs = [
    { id: 'simulation', label: 'Live FSM & Simulation', icon: Activity },
    { id: 'benchmarks', label: '3-Way Benchmarking', icon: BarChart3 },
    { id: 'custom', label: 'Custom Sequence Tester', icon: Terminal },
    { id: 'theory', label: 'TOC Automata Specs', icon: Cpu },
  ];

  return (
    <header className="app-header">
      <div style={{ maxWidth: '1600px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '1rem' }}>
        
        {/* Brand */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.85rem' }}>
          <div style={{
            background: 'linear-gradient(135deg, #6366f1 0%, #06b6d4 100%)',
            width: '42px',
            height: '42px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 0 20px rgba(99, 102, 241, 0.4)'
          }}>
            <Shield size={24} color="#ffffff" />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <h1 style={{ fontSize: '1.25rem', fontWeight: '800', letterSpacing: '-0.02em', background: 'linear-gradient(to right, #ffffff, #cbd5e1)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                ProtoGuard NIDS
              </h1>
              <span className="badge badge-indigo" style={{ fontSize: '0.65rem' }}>Hybrid Model</span>
            </div>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Network Intrusion Detection via Finite-State Automata & Machine Learning
            </p>
          </div>
        </div>

        {/* Navigation Tabs */}
        <nav style={{ display: 'flex', gap: '0.35rem', background: 'rgba(0,0,0,0.3)', padding: '0.3rem', borderRadius: '10px', border: '1px solid var(--border-color)' }}>
          {tabs.map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`nav-tab-btn ${isActive ? 'active' : ''}`}
                id={`tab-${tab.id}`}
              >
                <Icon size={16} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Backend Status Pill */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
          <div style={{
            width: '8px',
            height: '8px',
            borderRadius: '50%',
            background: isConnected ? '#10b981' : '#ef4444',
            boxShadow: isConnected ? '0 0 10px #10b981' : '0 0 10px #ef4444'
          }} />
          <span style={{ fontSize: '0.8rem', color: isConnected ? '#34d399' : '#f87171', fontFamily: 'var(--font-mono)' }}>
            {isConnected ? 'LIVE ENGINE READY' : 'RECONNECTING...'}
          </span>
        </div>

      </div>
    </header>
  );
}
