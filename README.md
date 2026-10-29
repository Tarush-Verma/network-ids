# ProtoGuard NIDS: Network Intrusion Detection via Finite-State Models & Machine Learning
### Academic Project for Problem 7: Network Intrusion Detection Using Finite-State Models and Machine Learning

[![Python 3.14](https://img.shields.io/badge/Python-3.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![Vite](https://img.shields.io/badge/Vite-8.3-646cff.svg)](https://vitejs.dev/)
[![Tests](https://img.shields.io/badge/Tests-28%20Passed-10b981.svg)]()

---

## 1. System Overview

**ProtoGuard NIDS** is a hybrid intrusion detection architecture that unifies:
1. **Deterministic Automata Theory (TOC)**: Models the protocol lifecycle as a formal Deterministic Finite Automaton (DFA) $M = (Q, \Sigma, \delta, q_0, F)$ to intercept illegal transitions $\delta(s, e) = \emptyset$ in microseconds ($0.06\text{ ms}$) with **0.00% False Positive Rate**.
2. **Data-Driven Machine Learning**: Uses a supervised **Random Forest** classifier for attack signature attribution and an unsupervised **Isolation Forest** for detecting temporal dwell anomalies (Slowloris), volumetric bursts (SYN floods), and zero-day sequences.
3. **Multi-Stage Hybrid Engine**: Combines the mathematical certainty of formal grammars with statistical sequence learning to achieve **100% detection rate (recall)** and **100% zero-day generalization**.
4. **Interactive React Dashboard**: A modern dark-mode glassmorphic visualizer with real-time SVG state machine animations, side-by-side detector comparison cards, and interactive sequence builders.

---

## 2. Theoretical Formulation (Theory of Computation)

- **Formal 5-Tuple**: $M = (Q, \Sigma, \delta, q_0, F)$
  - **States ($Q$)**: `CLOSED`, `LISTEN`, `SYN_SENT`, `SYN_RCVD`, `ESTABLISHED`, `FIN_WAIT_1`, `FIN_WAIT_2`, `CLOSE_WAIT`, `LAST_ACK`, `TIME_WAIT`, `ERROR_STATE`
  - **Alphabet ($\Sigma$)**: `LISTEN`, `SYN`, `SYN_ACK`, `ACK`, `DATA`, `FIN`, `RST`, `TIMEOUT`
  - **Initial State ($q_0$)**: `CLOSED`
  - **Accepting States ($F$)**: `CLOSED`, `TIME_WAIT`
- **Right-Linear Regular Grammar ($G$)**: Formalizes normal communication as a Type-3 regular language $L(M)$.
- **Complement Language ($L_{\text{anomaly}}$)**: Any intrusion sequence violates regular production rules and belongs to:
  $$L_{\text{anomaly}} = \Sigma^* \setminus L(M)$$

---

## 3. Empirical Benchmarks (300 Sessions / 2,184 Packets)

| Detector | Accuracy (%) | Detection Rate / Recall (%) | False Alarm Rate / FPR (%) | Average Latency | Zero-Day Generalization |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Pure Rule-Based FSM** | 77.60% | 36.11% | **0.00%** | **0.0608 ms** | 68.00% |
| **Pure ML (RF + IF)** | 97.73% | 100.00% | 3.50% | 44.8408 ms | 100.00% |
| **Hybrid Detector (Ours)**| **97.73%** | **100.00%** | 3.50% | 44.9240 ms | **100.00%** |

---

## 4. Quick Start: How to Run

### Step 1: Start Backend Server (FastAPI)
```bash
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

### Step 2: Start Frontend Application (React + Vite)
```bash
cd frontend
npm install
npm run dev -- --host 127.0.0.1 --port 5173
```
- Open browser at: `http://localhost:5173/`

### Step 3: Run the Automated Unit & API Test Suite
```bash
python -m unittest discover -s backend/tests -v
```
- Runs all 28 automated tests across FSM, Dataset, ML, and API endpoints.

---

## 5. Repository File Structure

```text
network-intrusion/
│
├── backend/
│   ├── app/
│   │   ├── main.py                     # FastAPI REST & WebSocket streaming server
│   │   ├── core/
│   │   │   ├── fsm.py                  # Formal DFA protocol model & diagnostics
│   │   │   ├── feature_extractor.py    # 27-D feature extractor (Markov, Entropy, N-grams)
│   │   │   └── hybrid_engine.py        # 2-Stage FSM + ML decision fusion logic
│   │   ├── models/
│   │   │   ├── random_forest.py        # Supervised multi-class signature model
│   │   │   └── isolation_forest.py     # Unsupervised anomaly & zero-day detector
│   │   └── data/
│   │       ├── synthetic_generator.py  # RFC-793 benign & attack sequence generator
│   │       └── dataset_loader.py       # Session grouping & statistics loader
│   ├── data/                           # Generated benchmark CSVs & JSONs
│   │   ├── train_traffic.csv           # 6,344 packets (869 sessions)
│   │   ├── test_traffic.csv            # 2,184 packets (300 sessions)
│   │   ├── zero_day_traffic.csv        # 93 packets (novel unseen attack variants)
│   │   └── benchmark_results.json      # Empirical benchmark comparison data
│   ├── saved_models/                   # Serialized ML models (.joblib)
│   ├── scripts/
│   │   ├── generate_datasets.py        # Data generator CLI script
│   │   └── train_models.py             # ML training & benchmark evaluation script
│   └── tests/
│       ├── test_fsm.py                 # FSM unit tests (11 tests)
│       ├── test_dataset_generator.py   # Dataset generator unit tests (5 tests)
│       ├── test_ml_pipeline.py         # ML feature & model tests (4 tests)
│       └── test_api.py                 # FastAPI integration tests (8 tests)
│
├── frontend/                           # React + Vite Interactive Dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── Navbar.jsx              # Navigation header with live status
│   │   │   ├── FsmGraphViewer.jsx      # SVG FSM state diagram with transition pulses
│   │   │   ├── DetectorScorecard.jsx   # 3-Way side-by-side comparison cards
│   │   │   ├── SimulationControls.jsx  # Attack selector, play, reset, speed controls
│   │   │   ├── AlertDetailModal.jsx    # Offending transition & CVE explanation drawer
│   │   │   ├── LivePacketTable.jsx     # Real-time packet log table
│   │   │   ├── BenchmarkView.jsx       # Benchmark evaluation charts & metrics
│   │   │   ├── CustomEvaluator.jsx     # Interactive sequence builder & tester
│   │   │   └── TheorySpecsView.jsx     # TOC formal 5-tuple & regular grammar specs
│   │   ├── App.jsx                     # Top-level state and layout container
│   │   ├── index.css                   # Dark-mode glassmorphic design system
│   │   └── main.jsx                    # React entrypoint
│   └── package.json
│
├── docs/                               # Comprehensive College Submission Materials
│   ├── phase1_theory_and_fsm.md        # Automata theory proofs & transition tables
│   ├── phase2_dataset_and_attacks.md   # Attack taxonomy & dataset schemas
│   ├── phase3_feature_engineering_and_ml.md # Feature math & ML evaluation
│   └── phase4_backend_api_and_websocket.md  # API & WebSocket specifications
└── README.md
```
..
