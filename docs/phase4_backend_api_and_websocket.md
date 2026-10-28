# Phase 4: Backend API Specification & Real-Time Simulation Engine

## 1. Overview
Phase 4 implements a high-performance **FastAPI** backend (`backend/app/main.py`) serving both RESTful endpoints and real-time WebSockets to bridge the Python FSM/ML engines with the interactive React dashboard.

---

## 2. REST Endpoints Reference

### 2.1 Topology & Architecture
- **`GET /api/fsm/topology`**
  - **Purpose**: Returns the formal states ($Q$), input alphabet ($\Sigma$), curated $(x, y)$ coordinate positions, initial/accept flags, and labeled directed edges for rendering in React Flow / Graph visualizers.
  - **Response Payload**:
    ```json
    {
      "states": ["CLOSED", "LISTEN", "SYN_SENT", "SYN_RCVD", "ESTABLISHED", ...],
      "alphabet": ["SYN", "SYN_ACK", "ACK", "DATA", "FIN", "RST", "TIMEOUT"],
      "nodes": [
        {"id": "CLOSED", "label": "CLOSED", "isInitial": true, "isAccept": true, "position": {"x": 100, "y": 300}}
      ],
      "edges": [
        {"id": "e_CLOSED_SYN_SENT_SYN_0", "source": "CLOSED", "target": "SYN_SENT", "label": "SYN"}
      ]
    }
    ```

- **`GET /api/fsm/matrix`**
  - **Purpose**: Returns the formal state-to-state transition matrix $M[s][s'] = \sigma$.

---

### 2.2 Benchmarks & Metrics
- **`GET /api/metrics/benchmark`**
  - **Purpose**: Exposes empirical performance metrics comparing **Rule-Based FSM vs Pure ML vs Hybrid** across both test traffic and novel zero-day attack suites.
  - **Fields Returned**: Accuracy, Detection Rate (Recall), False Alarm Rate (FPR), Precision, F1-Score, Average Latency (ms), P95 Latency (ms), and Confusion Matrices.

---

### 2.3 Attack Simulation Scenarios
- **`GET /api/simulation/scenarios`**
  - **Purpose**: Catalogs predefined attack and normal operational sequences:
    1. `normal_session`: RFC 793 3-way handshake + payload exchange + clean 4-way teardown.
    2. `out_of_order_ack`: Immediate blind ACK injection on a closed socket (CWE-940).
    3. `premature_data`: Data payload transmission before connection establishment (CWE-345).
    4. `stealth_fin_scan`: Unsolicited FIN port probe (MITRE ATT&CK T1595).
    5. `syn_flood`: High-frequency sub-millisecond SYN packet burst.
    6. `slowloris`: Dwell time anomaly with 25-45s delays and 1-byte payloads.
    7. `zero_day_bypass`: Unseen sequence testing model generalization (`SYN` $\to$ `FIN`).

- **`POST /api/simulation/generate/{scenario_id}`**
  - **Purpose**: Generates packet sequences for the selected scenario ready for client-side playback.

---

### 2.4 Real-Time Detection
- **`POST /api/detect/sequence`**
  - **Payload**: `{"session_id": "...", "events": [...]}`
  - **Returns**: Individual verdicts from FSM, ML, and Hybrid detectors with latency, confidence, category, and offending transition details.

- **`POST /api/detect/custom`**
  - **Payload**: `{"events": ["SYN", "SYN_ACK", "ACK", "DATA"], "delta_t": 0.02, "payload_size": 512}`
  - **Returns**: Evaluates arbitrary token combinations submitted by the user.

---

## 3. Real-Time WebSocket Protocol: `/ws/stream`

The WebSocket protocol streams simulated network events step-by-step to power live graph pulse animations:

### 3.1 Client Command
```json
{
  "action": "run_scenario",
  "scenario_id": "out_of_order_ack",
  "speed": 1.0
}
```

### 3.2 Server Event Emissions (per packet)
```json
{
  "type": "PACKET_EVENT",
  "packet": {
    "session_id": "atk_ack_9c2a",
    "seq_index": 0,
    "event_type": "ACK",
    "src_ip": "10.0.0.104",
    "dst_ip": "192.168.1.1",
    "delta_t": 0.03
  },
  "transition": {
    "from_state": "CLOSED",
    "event": "ACK",
    "to_state": "ERROR_STATE",
    "is_valid": false,
    "reason": "ANOMALY: Illegal transition attempted! State 'CLOSED' cannot accept event 'ACK'..."
  },
  "verdicts": {
    "fsm": {"is_anomaly": true, "confidence": 1.0, "latency_ms": 0.051},
    "ml": {"is_anomaly": true, "confidence": 0.98, "latency_ms": 44.2},
    "hybrid": {"is_anomaly": true, "confidence": 1.0, "attack_category": "OUT_OF_ORDER_ACK_INJECTION"}
  }
}
```
