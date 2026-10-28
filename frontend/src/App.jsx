import React, { useState, useEffect, useRef } from 'react';
import Navbar from './components/Navbar';
import FsmGraphViewer from './components/FsmGraphViewer';
import DetectorScorecard from './components/DetectorScorecard';
import SimulationControls from './components/SimulationControls';
import AlertDetailModal from './components/AlertDetailModal';
import LivePacketTable from './components/LivePacketTable';
import BenchmarkView from './components/BenchmarkView';
import CustomEvaluator from './components/CustomEvaluator';
import TheorySpecsView from './components/TheorySpecsView';

export default function App() {
  const [activeTab, setActiveTab] = useState('simulation');
  const [isConnected, setIsConnected] = useState(false);
  const [scenarios, setScenarios] = useState([]);
  const [selectedScenario, setSelectedScenario] = useState('normal_session');
  const [isRunning, setIsRunning] = useState(false);
  const [speed, setSpeed] = useState(1.0);

  // Live simulation states
  const [currentState, setCurrentState] = useState('CLOSED');
  const [lastTransition, setLastTransition] = useState(null);
  const [isAnomaly, setIsAnomaly] = useState(false);
  const [offendingTransition, setOffendingTransition] = useState(null);
  const [verdicts, setVerdicts] = useState({
    fsm: { is_anomaly: false, confidence: 1.0, latency_ms: 0.05, attack_category: 'Normal' },
    ml: { is_anomaly: false, confidence: 0.95, latency_ms: 44.8, attack_category: 'Normal' },
    hybrid: { is_anomaly: false, confidence: 0.98, latency_ms: 44.9, attack_category: 'Normal' },
  });
  const [packets, setPackets] = useState([]);
  const [activeAlert, setActiveAlert] = useState(null);
  const [benchmarks, setBenchmarks] = useState(null);

  const socketRef = useRef(null);

  // Initialize data from API
  useEffect(() => {
    // 1. Fetch scenarios
    fetch('http://localhost:8000/api/simulation/scenarios')
      .then((res) => res.json())
      .then((data) => {
        setScenarios(data);
        if (data.length > 0) setSelectedScenario(data[0].id);
        setIsConnected(true);
      })
      .catch((err) => {
        console.warn('Backend not yet reachable on localhost:8000, using mock catalog:', err);
        setScenarios([
          { id: 'normal_session', name: 'Benign Protocol Session', type: 'BENIGN' },
          { id: 'out_of_order_ack', name: 'Out-of-Order ACK Injection', type: 'GRAMMAR' },
          { id: 'premature_data', name: 'Premature Payload Injection', type: 'GRAMMAR' },
          { id: 'stealth_fin_scan', name: 'Stealth FIN Port Scan', type: 'RECON' },
          { id: 'syn_flood', name: 'Volumetric SYN Flood', type: 'DOS' },
          { id: 'slowloris', name: 'Slowloris Connection Starvation', type: 'TEMPORAL' },
          { id: 'zero_day_bypass', name: 'Zero-Day: Handshake Skip', type: 'ZERO-DAY' },
        ]);
      });

    // 2. Fetch benchmark metrics
    fetch('http://localhost:8000/api/metrics/benchmark')
      .then((res) => res.json())
      .then((data) => setBenchmarks(data))
      .catch((err) => console.warn('Could not load benchmarks:', err));

    // 3. Connect WebSocket for live streaming
    connectWebSocket();

    return () => {
      if (socketRef.current) socketRef.current.close();
    };
  }, []);

  const connectWebSocket = () => {
    try {
      const ws = new WebSocket('ws://localhost:8000/ws/stream');
      socketRef.current = ws;

      ws.onopen = () => {
        setIsConnected(true);
      };

      ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);

        if (msg.type === 'PACKET_EVENT') {
          const { packet, transition, verdicts: newVerdicts } = msg;

          setPackets((prev) => [...prev, packet]);
          setCurrentState(transition.to_state);
          setLastTransition(transition);

          if (newVerdicts) {
            setVerdicts(newVerdicts);

            if (newVerdicts.hybrid?.is_anomaly) {
              setIsAnomaly(true);
              const offTrans = newVerdicts.fsm?.offending_transition;
              if (offTrans) {
                setOffendingTransition(offTrans);
              }
              setActiveAlert({
                category: newVerdicts.hybrid.attack_category,
                from_state: transition.from_state,
                event: transition.event,
                allowed_events: offTrans?.allowed_events || ['LISTEN', 'SYN'],
                explanation: newVerdicts.hybrid.explanation,
                cve_reference: offTrans?.cve_reference || 'RFC 793 Protocol Deviation',
              });
            }
          }
        } else if (msg.type === 'SESSION_COMPLETE') {
          setIsRunning(false);
        }
      };

      ws.onerror = () => {
        setIsConnected(false);
      };

      ws.onclose = () => {
        setIsConnected(false);
        // Attempt reconnect in 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
    } catch (e) {
      setIsConnected(false);
    }
  };

  const handleStartSimulation = async () => {
    // Reset state before running
    handleReset();
    setIsRunning(true);

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      socketRef.current.send(JSON.stringify({
        action: 'run_scenario',
        scenario_id: selectedScenario,
        speed: speed,
      }));
    } else {
      // Fallback: REST simulation endpoint
      try {
        const res = await fetch(`http://localhost:8000/api/simulation/generate/${selectedScenario}`, {
          method: 'POST'
        });
        const generatedPackets = await res.json();
        
        // Evaluate full sequence
        const evalRes = await fetch('http://localhost:8000/api/detect/sequence', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            session_id: generatedPackets[0]?.session_id || 'sim_001',
            events: generatedPackets,
          }),
        });
        const evalData = await evalRes.json();

        // Animate client-side
        for (let i = 0; i < generatedPackets.length; i++) {
          const pkt = generatedPackets[i];
          setPackets((prev) => [...prev, pkt]);
          setCurrentState(pkt.next_state);
          setLastTransition({
            from_state: pkt.current_state,
            event: pkt.event_type,
            to_state: pkt.next_state,
            is_valid: pkt.is_anomaly === 0,
            reason: pkt.is_anomaly === 1 ? 'Anomaly flagged' : 'RFC valid step',
          });
          await new Promise((r) => setTimeout(r, 400 / speed));
        }

        setVerdicts({
          fsm: evalData.fsm_verdict,
          ml: evalData.ml_verdict,
          hybrid: evalData.hybrid_verdict,
        });

        if (evalData.hybrid_verdict.is_anomaly) {
          setIsAnomaly(true);
          const offTrans = evalData.fsm_verdict.offending_transition;
          if (offTrans) setOffendingTransition(offTrans);
          setActiveAlert({
            category: evalData.hybrid_verdict.attack_category,
            from_state: offTrans?.from_state || 'CLOSED',
            event: offTrans?.event || 'ACK',
            allowed_events: offTrans?.allowed_events || ['SYN'],
            explanation: evalData.hybrid_verdict.explanation,
            cve_reference: offTrans?.cve_reference || 'RFC 793 Deviation',
          });
        }
      } catch (err) {
        console.error('REST simulation error:', err);
      } finally {
        setIsRunning(false);
      }
    }
  };

  const handleReset = () => {
    setCurrentState('CLOSED');
    setLastTransition(null);
    setIsAnomaly(false);
    setOffendingTransition(null);
    setPackets([]);
    setActiveAlert(null);
    setVerdicts({
      fsm: { is_anomaly: false, confidence: 1.0, latency_ms: 0.05, attack_category: 'Normal' },
      ml: { is_anomaly: false, confidence: 0.95, latency_ms: 44.8, attack_category: 'Normal' },
      hybrid: { is_anomaly: false, confidence: 0.98, latency_ms: 44.9, attack_category: 'Normal' },
    });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      
      {/* Top Navbar */}
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        isConnected={isConnected}
      />

      {/* Main Content Body */}
      <main style={{ flex: 1, maxWidth: '1600px', width: '100%', margin: '0 auto', padding: '1.5rem 2rem' }}>
        
        {/* Tab 1: Live FSM & Attack Simulation */}
        {activeTab === 'simulation' && (
          <div>
            {/* Simulation Controls Bar */}
            <SimulationControls
              scenarios={scenarios}
              selectedScenario={selectedScenario}
              setSelectedScenario={setSelectedScenario}
              isRunning={isRunning}
              onStartSimulation={handleStartSimulation}
              onReset={handleReset}
              speed={speed}
              setSpeed={setSpeed}
            />

            {/* Split Grid: FSM Graph on Left, Stream & Alerts on Right */}
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0, 1.4fr) minmax(0, 1fr)', gap: '1.25rem', alignItems: 'start' }}>
              
              {/* Left Column: Interactive State Graph */}
              <div>
                <FsmGraphViewer
                  currentState={currentState}
                  lastTransition={lastTransition}
                  isAnomaly={isAnomaly}
                  offendingTransition={offendingTransition}
                />

                {/* 3-Way Side-by-Side Detector Comparison Scorecard */}
                <DetectorScorecard verdicts={verdicts} />
              </div>

              {/* Right Column: Offending Alert Drawer + Packet Sequence Stream */}
              <div>
                {/* Alert Modal (appears when breach occurs) */}
                {activeAlert && (
                  <AlertDetailModal
                    alert={activeAlert}
                    onClose={() => setActiveAlert(null)}
                  />
                )}

                {/* Live Sequence Event Log */}
                <LivePacketTable packets={packets} />
              </div>

            </div>
          </div>
        )}

        {/* Tab 2: 3-Way Detector Benchmarking */}
        {activeTab === 'benchmarks' && (
          <BenchmarkView benchmarks={benchmarks} />
        )}

        {/* Tab 3: Interactive Custom Sequence Tester */}
        {activeTab === 'custom' && (
          <CustomEvaluator />
        )}

        {/* Tab 4: Theory of Computation Formal Specifications */}
        {activeTab === 'theory' && (
          <TheorySpecsView />
        )}

      </main>

      {/* Footer */}
      <footer style={{ borderTop: '1px solid var(--border-color)', padding: '1rem 2rem', textAlign: 'center', fontSize: '0.775rem', color: 'var(--text-dim)' }}>
        ProtoGuard NIDS &bull; Problem 7: Network Intrusion Detection Using Finite-State Models & Machine Learning &bull; College Capstone Project
      </footer>

    </div>
  );
}
