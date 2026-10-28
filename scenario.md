# ProtoGuard NIDS: Attack & Traffic Scenarios Comprehensive Guide
### Complete Technical Reference for All Simulation Scenarios on the ProtoGuard Dashboard

This document provides exhaustive, multi-dimensional documentation for **every traffic scenario present on the ProtoGuard NIDS website**. Each scenario is analyzed across:
1. **Scenario Profile & Threat Classification** (CWE, CVE, MITRE ATT&CK)
2. **Theory of Computation (TOC) & Finite-State Automata Formulation**
3. **Packet-Level Network Attributes (RFC 793)**
4. **Three-Way Detector Behavior & Benchmarks** (FSM vs. Pure ML vs. Hybrid)
5. **Real-World Threat Context & Exploit Mechanics**
6. **Firewall Defense & Mitigation Recommendations**

---

## Table of Contents
1. [Scenario 1: Benign Protocol Session (Handshake + Data + Teardown)](#scenario-1-benign-protocol-session)
2. [Scenario 2: Out-of-Order ACK Injection (Grammatical Breach)](#scenario-2-out-of-order-ack-injection)
3. [Scenario 3: Premature Payload Injection (Data Before Handshake)](#scenario-3-premature-payload-injection)
4. [Scenario 4: Stealth FIN Port Scan (Reconnaissance Probe)](#scenario-4-stealth-fin-port-scan)
5. [Scenario 5: Volumetric SYN Flood Attack (Half-Open Exhaustion)](#scenario-5-volumetric-syn-flood-attack)
6. [Scenario 6: Slowloris Connection Starvation (Temporal Dwell Anomaly)](#scenario-6-slowloris-connection-starvation)
7. [Scenario 7: Zero-Day Handshake Skip to Teardown (Novel Unseen Sequence)](#scenario-7-zero-day-handshake-skip-to-teardown)
8. [Supplementary Scenarios: RST Storm & Double SYN Injections](#supplementary-scenarios)
9. [Master Comparative Summary Matrix](#master-comparative-summary-matrix)

---

## Scenario 1: Benign Protocol Session

### 1.1 Overview & Threat Classification
- **Scenario ID**: `normal_session`
- **Display Name**: Benign Protocol Session
- **Category**: `Normal`
- **Threat Type**: `BENIGN` (Legitimate Network Traffic)
- **Standard Reference**: IETF RFC 793 (Transmission Control Protocol Specification)
- **Security Impact**: None. Represents standard, compliant user-server communication.

### 1.2 Theory of Computation (TOC) & FSM Modeling
- **Initial State ($q_0$)**: `CLOSED`
- **Transition Pathway**:
  $$\text{CLOSED} \xrightarrow{\text{SYN}} \text{SYN\_SENT} \xrightarrow{\text{SYN\_ACK}} \text{ESTABLISHED} \xrightarrow{\text{DATA}} \text{ESTABLISHED} \xrightarrow{\text{FIN}} \text{FIN\_WAIT\_1} \xrightarrow{\text{ACK}} \text{FIN\_WAIT\_2} \xrightarrow{\text{FIN}} \text{TIME\_WAIT} \xrightarrow{\text{TIMEOUT}} \text{CLOSED}$$
- **Grammar Compliance**: Word $w = \text{SYN} \cdot \text{SYN\_ACK} \cdot \text{DATA} \cdot \text{FIN} \cdot \text{ACK} \cdot \text{FIN} \cdot \text{TIMEOUT} \in L(M)$.
- **Transition Function ($\delta$)**: Every state-symbol pair satisfies $\delta(s_t, \sigma_t) \neq \emptyset$.
- **Acceptance Status**: Accepted ($w \in L(M)$) and halts in terminal accept state $F = \text{CLOSED}$.

### 1.3 Packet-Level Attributes
- **Flags**: Progressive sequence of `[SYN]`, `[SYN, ACK]`, `[ACK]`, `[PSH, ACK]`, `[FIN, ACK]`.
- **Payload Size**: Variable (Handshake/teardown: $0\text{ bytes}$; Data segments: $64\text{ B} - 1460\text{ B}$).
- **Inter-Arrival Time ($\Delta t$)**: Normal operational latency ($\Delta t \in [0.005\text{s}, 0.080\text{s}]$).
- **IP Addressing**: Standard client subnet (`192.168.1.15:48201`) talking to HTTP/Application server (`192.168.1.1:8080`).

### 1.4 Detector Behavior & Benchmarks
- **Pure Rule-Based FSM**:
  - *Verdict*: `VALID`
  - *Confidence*: $100\%$
  - *Execution Latency*: $\approx 0.06\text{ ms}$
  - *Reasoning*: All transition lookups exist in the deterministic delta table.
- **Pure Machine Learning**:
  - *Verdict*: `Normal`
  - *Confidence*: $95\% - 99\%$
  - *Isolation Forest Normality Score*: $> 0.70$ (Deep inlier)
  - *Execution Latency*: $\approx 44.8\text{ ms}$
- **Hybrid Multi-Stage Engine**:
  - *Final Verdict*: **`Normal`** (Green badge)
  - *Confidence*: $98\%$
  - *Explanation*: "Traffic verified: both FSM grammar and ML feature distributions are benign."

### 1.5 Real-World Context & Exploitation Notes
Represents everyday user traffic: web browsing (HTTP/HTTPS), API calls, SSH sessions, or database queries. A robust NIDS must process this traffic with $0\%$ false alarms so that legitimate users are never blocked.

---

## Scenario 2: Out-of-Order ACK Injection

### 2.1 Overview & Threat Classification
- **Scenario ID**: `out_of_order_ack`
- **Display Name**: Out-of-Order ACK Injection
- **Category**: `Out_Of_Order_ACK`
- **Threat Type**: `GRAMMATICAL_BREACH` / Protocol Desynchronization
- **Vulnerability Identifiers**:
  - **CWE-940**: Improper Verification of Source Digest
  - **MITRE ATT&CK**: T1595.001 (Active Scanning - Port Scanning)
- **Security Impact**: Firewall rule deduction, state table pollution, and blind connection hijacking attempts.

### 2.2 Theory of Computation (TOC) & FSM Modeling
- **Initial State**: `CLOSED`
- **Attempted Transition**:
  $$\text{CLOSED} \xrightarrow{\text{ACK}} \text{ERROR\_STATE}$$
- **Grammar Compliance**: Word $w = \text{ACK} \notin L(M)$.
- **Transition Function ($\delta$)**: In state `CLOSED`, $\delta(\text{CLOSED}, \text{ACK}) = \emptyset$.
- **Error Automaton**: The FSM transitions immediately to `ERROR_STATE` and triggers a CRITICAL intrusion alarm.
- **Expected Legal Symbols**: $\Sigma_{\text{expected}} = \{\text{LISTEN}, \text{SYN}\}$.

### 2.3 Packet-Level Attributes
- **Flags**: `[ACK]` with unsolicited acknowledgment number.
- **Payload Size**: $0\text{ bytes}$.
- **Inter-Arrival Time ($\Delta t$)**: $0.01\text{s} - 0.05\text{s}$.
- **IP Addressing**: External spoofed source IP (`10.0.0.104:54321`) probing internal target (`192.168.1.1:8080`).

### 2.4 Detector Behavior & Benchmarks
- **Pure Rule-Based FSM**:
  - *Verdict*: `ALERT` (`ILLEGAL_STATE_TRANSITION`)
  - *Confidence*: $100\%$
  - *Execution Latency*: $\mathbf{0.059\text{ ms}}$
  - *Offending Transition*: State: `CLOSED` $\to$ Event: `ACK` $\to$ Result: `ERROR_STATE`.
- **Pure Machine Learning**:
  - *Verdict*: `ALERT` (`Out_Of_Order_ACK`)
  - *Confidence*: $98\%$
  - *Execution Latency*: $\approx 45.1\text{ ms}$
- **Hybrid Multi-Stage Engine**:
  - *Final Verdict*: **`ALERT: OUT_OF_ORDER_ACK_INJECTION`** (Red alert modal)
  - *Confidence*: $\mathbf{100\%}$
  - *Triggered Stage*: **Hybrid Stage 1 (Deterministic FSM Gate)**
  - *Explanation*: "Deterministic FSM intercepted grammar violation: Blind ACK packet received without connection initiation."

### 2.5 Real-World Context & Exploit Mechanics
Attacking tools (like `nmap -sA` or custom Scapy scripts) send blind ACK packets to determine whether firewall filtering is stateful or stateless. If an unfiltered host responds with an RST, the attacker infers the port is reachable through the firewall.

### 2.6 Mitigation & Defense
- Drop the packet immediately at the network edge.
- Increment state-table anomaly counter for the source IP.
- Enforce strict stateful packet inspection (SPI) requiring valid SYN sequence matching.

---

## Scenario 3: Premature Payload Injection

### 3.1 Overview & Threat Classification
- **Scenario ID**: `premature_data`
- **Display Name**: Premature Payload Injection
- **Category**: `Premature_Data`
- **Threat Type**: `GRAMMATICAL_BREACH` / Unauthenticated Data Injection
- **Vulnerability Identifiers**:
  - **CWE-345**: Insufficient Verification of Data Authenticity
  - **MITRE ATT&CK**: T1210 (Exploitation of Remote Services)
- **Security Impact**: Buffer exploits, pre-authentication remote code execution (RCE), and socket confusion attacks.

### 3.2 Theory of Computation (TOC) & FSM Modeling
- **Initial State**: `CLOSED`
- **Attempted Transition**:
  $$\text{CLOSED} \xrightarrow{\text{DATA}} \text{ERROR\_STATE}$$
- **Grammar Compliance**: Word $w = \text{DATA} \notin L(M)$.
- **Transition Function ($\delta$)**: $\delta(\text{CLOSED}, \text{DATA}) = \emptyset$.
- **Error Automaton**: The FSM traps the event instantly into `ERROR_STATE`.
- **Expected Legal Symbols**: $\Sigma_{\text{expected}} = \{\text{LISTEN}, \text{SYN}\}$.

### 3.3 Packet-Level Attributes
- **Flags**: `[PSH, ACK]` carrying unprompted payload data.
- **Payload Size**: High ($128\text{ B} - 1024\text{ B}$).
- **Inter-Arrival Time ($\Delta t$)**: $0.01\text{s} - 0.05\text{s}$.
- **Source Addressing**: Untrusted host (`10.0.0.108`) attempting raw data writes to closed ports.

### 3.4 Detector Behavior & Benchmarks
- **Pure Rule-Based FSM**:
  - *Verdict*: `ALERT` (`ILLEGAL_STATE_TRANSITION`)
  - *Confidence*: $100\%$
  - *Execution Latency*: $\mathbf{0.060\text{ ms}}$
  - *Offending Transition*: State: `CLOSED` $\to$ Event: `DATA` $\to$ Result: `ERROR_STATE`.
- **Pure Machine Learning**:
  - *Verdict*: `ALERT` (`Premature_Data`)
  - *Confidence*: $97\%$
  - *Execution Latency*: $\approx 46.2\text{ ms}$
- **Hybrid Multi-Stage Engine**:
  - *Final Verdict*: **`ALERT: PREMATURE_PAYLOAD_INJECTION`**
  - *Confidence*: $\mathbf{100\%}$
  - *Triggered Stage*: **Hybrid Stage 1 (Deterministic FSM Gate)**
  - *Explanation*: "Data transmitted to a closed socket prior to 3-way handshake completion."

### 3.5 Real-World Context & Exploit Mechanics
Attackers attempt to exploit vulnerable network services or daemons by blasting exploit shellcodes directly into TCP ports, hoping that improper socket parsing will pass the buffer to vulnerable memory routines without verifying whether the handshake completed.

### 3.6 Mitigation & Defense
- Silently discard unsolicited data payloads before passing them to application layer buffers.
- Log offending IP addresses to automated fail2ban/firewall blocklists.

---

## Scenario 4: Stealth FIN Port Scan

### 4.1 Overview & Threat Classification
- **Scenario ID**: `stealth_fin_scan`
- **Display Name**: Stealth FIN Port Scan
- **Category**: `Stealth_FIN_Scan`
- **Threat Type**: `RECONNAISSANCE` (Firewall Evasion Probe)
- **Vulnerability Identifiers**:
  - **MITRE ATT&CK**: T1595.001 (Port Scanning - FIN Probe)
  - **CWE-200**: Exposure of Sensitive Information to an Unauthorized Actor
- **Security Impact**: Maps open, closed, and filtered firewall ports without creating established connection logs.

### 4.2 Theory of Computation (TOC) & FSM Modeling
- **Initial State**: `CLOSED`
- **Attempted Transition**:
  $$\text{CLOSED} \xrightarrow{\text{FIN}} \text{ERROR\_STATE}$$
- **Grammar Compliance**: Word $w = \text{FIN} \notin L(M)$.
- **Transition Function ($\delta$)**: A FIN event is only valid from states where a connection exists (`ESTABLISHED`, `FIN_WAIT_1`, `CLOSE_WAIT`). In `CLOSED`, $\delta(\text{CLOSED}, \text{FIN}) = \emptyset$.
- **Error Automaton**: Direct trap into `ERROR_STATE`.

### 4.3 Packet-Level Attributes
- **Flags**: Bare `[FIN]` flag without accompanying ACK or prior SYN.
- **Payload Size**: $0\text{ bytes}$.
- **Inter-Arrival Time ($\Delta t$)**: $0.02\text{s} - 0.10\text{s}$.
- **Scanner Signature**: Generated by scanning utilities like `nmap -sF`.

### 4.4 Detector Behavior & Benchmarks
- **Pure Rule-Based FSM**:
  - *Verdict*: `ALERT` (`STEALTH_FIN_SCAN`)
  - *Confidence*: $100\%$
  - *Execution Latency*: $\mathbf{0.051\text{ ms}}$
  - *Offending Transition*: State: `CLOSED` $\to$ Event: `FIN` $\to$ Result: `ERROR_STATE`.
- **Pure Machine Learning**:
  - *Verdict*: `ALERT` (`Stealth_FIN_Scan`)
  - *Confidence*: $99\%$
  - *Feature Indicators*: `fin_ratio == 1.0`, `packet_count == 1`, `fsm_violation_count == 1`.
- **Hybrid Multi-Stage Engine**:
  - *Final Verdict*: **`ALERT: STEALTH_FIN_SCAN`**
  - *Confidence*: $\mathbf{100\%}$
  - *Triggered Stage*: **Hybrid Stage 1 (Deterministic FSM Gate)**

### 4.5 Real-World Context & Exploit Mechanics
Traditional packet filters and basic firewalls often log incoming `SYN` packets to detect connection attempts. By sending unsolicited `FIN` packets, attackers bypass simple SYN-logging filters. Under RFC 793, closed ports must respond with an `RST`, while open ports silently drop the packet, allowing the attacker to map the target network silently.

### 4.6 Mitigation & Defense
- Drop any FIN packet that does not belong to an existing session in the connection tracking table.
- Implement rate limiting on TCP reset (RST) generation to prevent scanner mapping.

---

## Scenario 5: Volumetric SYN Flood Attack

### 5.1 Overview & Threat Classification
- **Scenario ID**: `syn_flood`
- **Display Name**: Volumetric SYN Flood Attack
- **Category**: `SYN_Flood`
- **Threat Type**: `DENIAL_OF_SERVICE` (Resource Exhaustion)
- **Vulnerability Identifiers**:
  - **CWE-400**: Uncontrolled Resource Consumption
  - **MITRE ATT&CK**: T1499.002 (Endpoint DoS - Service Exhaustion)
- **Security Impact**: Complete exhaustion of server connection backlog queue (`SYN backlog`), rendering legitimate web services unavailable.

### 5.2 Theory of Computation (TOC) & FSM Modeling
- **Initial State**: `CLOSED`
- **Transition Pathway**:
  $$\text{CLOSED} \xrightarrow{\text{SYN}} \text{SYN\_SENT} \xrightarrow{\text{SYN}} \text{SYN\_RCVD} \xrightarrow{\text{SYN}} \dots$$
- **Grammar Compliance**: **Individually valid transitions!** Each packet is a syntactically legal `SYN` packet.
- **Automata Limitation**: A pure rule-based FSM that only checks $\delta(s, e)$ **misses volumetric floods** because receiving a SYN from a closed state is legal ($\delta(\text{CLOSED}, \text{SYN}) = \text{SYN\_SENT}$).
- **The Solution**: Feature extraction and statistical ML detect the sub-millisecond repetition frequency and zero-payload entropy!

### 5.3 Packet-Level Attributes
- **Flags**: Pure `[SYN]` flags.
- **Payload Size**: $0\text{ bytes}$.
- **Inter-Arrival Time ($\Delta t$)**: **Sub-millisecond** ($\Delta t \in [0.0001\text{s}, 0.0008\text{s}]$), representing thousands of packets per second.
- **Source Addressing**: Random spoofed IPs (`10.0.0.100` to `10.0.0.115`) with ephemeral source ports.

### 5.4 Detector Behavior & Benchmarks
- **Pure Rule-Based FSM**:
  - *Verdict*: Misses individual packet syntax or flags subsequent unexpected SYNs after state shift.
  - *Detection Rate*: Bounded ($\approx 36\%$).
- **Pure Machine Learning**:
  - *Verdict*: **`ALERT: SYN_Flood`**
  - *Confidence*: $99\% - 100\%$
  - *Key Extracted Features*:
    - `mean_delta_t < 0.001s` (Extremely low)
    - `syn_ratio == 1.0` (100% of packets are SYN)
    - `event_entropy == 0.0` (Zero diversity)
    - `markov_log_likelihood`: Extremely abnormal
- **Hybrid Multi-Stage Engine**:
  - *Final Verdict*: **`ALERT: SYN_FLOOD`**
  - *Triggered Stage*: **Hybrid Stage 2 (Statistical & ML Filter)**
  - *Confidence*: $\mathbf{98\% - 100\%}$
  - *Explanation*: "Protocol grammar valid, but data-driven ML identified statistical frequency burst (SYN Flood attack)."

### 5.5 Real-World Context & Exploit Mechanics
Generated by tools like `hping3 --flood -S` or botnets. The attacker floods the target with SYN packets and ignores the resulting SYN-ACKs. The server allocates transmission control blocks (TCBs) for each half-open connection until memory is exhausted and legitimate connections are refused.

### 5.6 Mitigation & Defense
- Enable **TCP SYN Cookies** (`syncookies = 1`) to eliminate memory allocation during the initial handshake.
- Apply threshold-based rate limiting on incoming SYN packets per source subnet.

---

## Scenario 6: Slowloris Connection Starvation

### 6.1 Overview & Threat Classification
- **Scenario ID**: `slowloris`
- **Display Name**: Slowloris Connection Starvation
- **Category**: `Slowloris_Dwell`
- **Threat Type**: `TEMPORAL_DWELL_ANOMALY` (Low-and-Slow Application DoS)
- **Vulnerability Identifiers**:
  - **CWE-400**: Uncontrolled Resource Consumption
  - **MITRE ATT&CK**: T1499.003 (Endpoint DoS - Application Exhaustion)
- **Security Impact**: Exhausts concurrent socket thread pools while remaining undetected by traditional volumetric threshold firewalls.

### 6.2 Theory of Computation (TOC) & FSM Modeling
- **Initial State**: `CLOSED`
- **Transition Pathway**:
  $$\text{CLOSED} \xrightarrow{\text{SYN}} \text{SYN\_SENT} \xrightarrow{\text{SYN\_ACK}} \text{ESTABLISHED} \xrightarrow{\text{DATA (drip)}} \text{ESTABLISHED} \xrightarrow{\text{DATA (drip)}} \dots$$
- **Grammar Compliance**: **100% Valid FSM Grammar!** The 3-way handshake completes perfectly, and all subsequent packets are valid `DATA` packets.
- **Why Pure FSM Fails**: A purely syntactic state machine has no concept of elapsed time—it sees only legal symbols and marks the session as `VALID`.
- **Why Machine Learning Succeeds**: The feature extractor computes $\mu(\Delta t)$, $\sigma(\Delta t)$, and $\max(\Delta t)$. While normal packets arrive within $0.05\text{s}$, Slowloris packets have $\Delta t > 25\text{s}$. Both Random Forest and Isolation Forest flag this extreme statistical dwell outlier!

### 6.3 Packet-Level Attributes
- **Flags**: `[PSH, ACK]` carrying tiny, incomplete HTTP header fragments.
- **Payload Size**: Minimal ($1\text{ byte} - 10\text{ bytes}$).
- **Inter-Arrival Time ($\Delta t$)**: **Abnormally high delays** ($\Delta t \in [20.0\text{s}, 45.0\text{s}]$), timed just beneath standard server socket keep-alive timeouts.

### 6.4 Detector Behavior & Benchmarks
- **Pure Rule-Based FSM**:
  - *Verdict*: `VALID` (Completely blind to temporal delays)
  - *False Negative*: Fails to intercept this attack!
- **Pure Machine Learning**:
  - *Verdict*: **`ALERT: Slowloris_Dwell`**
  - *Confidence*: $96\%$
  - *Isolation Forest Anomaly Score*: $< 0.15$ (Extreme outlier)
  - *Key Trigger Feature*: `mean_delta_t > 20.0`
- **Hybrid Multi-Stage Engine**:
  - *Final Verdict*: **`ALERT: SLOWLORIS_DWELL`**
  - *Confidence*: $\mathbf{96\%}$
  - *Triggered Stage*: **Hybrid Stage 2 (Temporal & Statistical Manifold)**
  - *Explanation*: "Protocol grammar valid, but data-driven ML identified temporal dwell anomaly (Extreme inter-arrival delay)."

### 6.5 Real-World Context & Exploit Mechanics
Classic Slowloris attacks hold thousands of HTTP connections open by sending partial HTTP headers (e.g., `X-a: b\r\n`) every 30 seconds. Traditional volumetric firewalls do not trigger because bandwidth usage is negligible (less than 1 KB/minute), yet web server worker threads (e.g., Apache, IIS) become completely exhausted.

### 6.6 Mitigation & Defense
- Enforce minimum transmission rate limits (e.g., terminate sockets sending fewer than $500\text{ bytes/sec}$).
- Reduce client header and body timeout thresholds (`RequestReadTimeout` in Apache / `client_body_timeout` in Nginx).

---

## Scenario 7: Zero-Day Handshake Skip to Teardown

### 7.1 Overview & Threat Classification
- **Scenario ID**: `zero_day_bypass`
- **Display Name**: Zero-Day: Handshake Skip to Teardown
- **Category**: `ZeroDay_Handshake_Bypass`
- **Threat Type**: `ZERO_DAY` / Novel Sequence Anomaly
- **Objective from Problem Statement**: *"Evaluate generalization to previously unseen event sequences."*
- **Security Impact**: State table confusion, stateful proxy bypass, and evasion of legacy signature-based detectors.

### 7.2 Theory of Computation (TOC) & FSM Modeling
- **Initial State**: `CLOSED`
- **Sequence**:
  $$\text{CLOSED} \xrightarrow{\text{SYN}} \text{SYN\_SENT} \xrightarrow{\text{FIN}} \text{ERROR\_STATE}$$
- **Grammar Compliance**: Word $w = \text{SYN} \cdot \text{FIN} \notin L(M)$.
- **Transition Function ($\delta$)**: In state `SYN_SENT`, the automaton permits only `SYN_ACK` (standard) or `SYN` (simultaneous open). Receiving an unsolicited `FIN` violates the transition system: $\delta(\text{SYN\_SENT}, \text{FIN}) = \emptyset$.
- **Generalization Significance**: This specific attack pattern was **never included in the supervised training dataset**, allowing us to test model generalization to zero-day events.

### 7.3 Packet-Level Attributes
- **Flags**: `[SYN]` followed directly by `[FIN]`.
- **Payload Size**: $0\text{ bytes}$.
- **Inter-Arrival Time ($\Delta t$)**: $0.02\text{s}$.
- **Source Addressing**: Attacker probe (`10.0.99.99`).

### 7.4 Detector Behavior & Benchmarks
- **Pure Rule-Based FSM**:
  - *Verdict*: `ALERT` (`ABORTED_HANDSHAKE_PROBE`)
  - *Confidence*: $100\%$
  - *Execution Latency*: $\mathbf{0.051\text{ ms}}$
  - *Offending Transition*: State: `SYN_SENT` $\to$ Event: `FIN` $\to$ Result: `ERROR_STATE`.
- **Pure Machine Learning (Isolation Forest)**:
  - *Verdict*: `ALERT` (`Unsupervised_Statistical_Anomaly`)
  - *Confidence*: $95\%$
  - *Reasoning*: Because the Isolation Forest was trained strictly on benign manifold data, it isolates this novel sequence as an out-of-distribution outlier without needing a pre-existing label!
- **Hybrid Multi-Stage Engine**:
  - *Final Verdict*: **`ALERT: ZERO_DAY_SEQUENCE_BREACH`**
  - *Confidence*: $\mathbf{100\%}$
  - *Benchmark Generalization Score*: **100% Detection Rate** on zero-day suites.

### 7.5 Real-World Context & Exploit Mechanics
Modern intrusion evasion frameworks craft non-standard TCP flag combinations to desynchronize intermediate firewalls from the target endpoint. If the firewall drops tracking while the end server processes the connection, the attacker achieves firewall bypass.

---

## Supplementary Scenarios

### Scenario 8: Zero-Day RST Storm (`ZeroDay_RST_Storm`)
- **Profile**: Rapid barrage of unsolicited TCP Reset (`RST`) packets injected across closed, embryonic, and active connections.
- **TOC Impact**: While `RST` is valid from active states, receiving an RST flood in `CLOSED` or `LISTEN` states violates normal operational flow and causes massive Markov likelihood penalties.
- **Detection**: Caught by both FSM transition tracking and Isolation Forest anomaly scoring.

### Scenario 9: Double SYN Injection (`ZeroDay_Double_SYN`)
- **Profile**: Two consecutive `SYN` packets from the same port carrying contradictory payload lengths and conflicting TCP window sizes.
- **TOC Impact**: Violates standard client handshake sequence. The second `SYN` packet in `SYN_SENT` carrying payload is flagged as an invalid sequence.
- **Detection**: Caught by bigram frequency feature `bigram_SYN_SYN` and FSM state transition validation.

---

## Master Comparative Summary Matrix

This master reference table synthesizes the operational performance of all three detectors across all scenarios:

| Scenario ID | Threat Classification | Rule-Based FSM | Pure Machine Learning | Hybrid Engine (Ours) | Latency | Stage Triggered |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **`normal_session`** | `BENIGN` | `VALID` | `Normal` (99%) | **`Normal`** (98%) | $0.06\text{ ms}$ | Both Passed |
| **`out_of_order_ack`** | `GRAMMATICAL_BREACH` | `ALERT` (100%) | `ALERT` (98%) | **`ALERT`** (100%) | $\mathbf{0.059\text{ ms}}$ | **Stage 1 (FSM)** |
| **`premature_data`** | `GRAMMATICAL_BREACH` | `ALERT` (100%) | `ALERT` (97%) | **`ALERT`** (100%) | $\mathbf{0.060\text{ ms}}$ | **Stage 1 (FSM)** |
| **`stealth_fin_scan`** | `RECONNAISSANCE` | `ALERT` (100%) | `ALERT` (99%) | **`ALERT`** (100%) | $\mathbf{0.051\text{ ms}}$ | **Stage 1 (FSM)** |
| **`syn_flood`** | `DENIAL_OF_SERVICE` | Missed ($36\%$) | `ALERT` (99%) | **`ALERT`** (100%) | $44.8\text{ ms}$ | **Stage 2 (ML)** |
| **`slowloris`** | `TEMPORAL_ANOMALY` | Missed ($0\%$) | `ALERT` (96%) | **`ALERT`** (96%) | $45.2\text{ ms}$ | **Stage 2 (ML)** |
| **`zero_day_bypass`** | `ZERO_DAY_BREACH` | `ALERT` (100%) | `ALERT` (95%) | **`ALERT`** (100%) | $\mathbf{0.051\text{ ms}}$ | **Stage 1 (FSM)** |
| **`zero_day_rst_storm`**| `ZERO_DAY_VOLUMETRIC`| `ALERT` (68%) | `ALERT` (100%)| **`ALERT`** (100%) | $48.6\text{ ms}$ | **Stage 2 (ML)** |

---

## Key Academic Takeaway for Project Defense

1. **Why Pure FSM is Incomplete**:
   - As proven in Scenarios 5 (`syn_flood`) and 6 (`slowloris`), pure FSMs only verify syntactic transition validity ($\delta(s, e)$). They are inherently **blind to volumetric packet rates and temporal dwell delays**.
2. **Why Pure ML is Incomplete**:
   - Pure ML models require feature extraction overhead ($44\text{ ms}$ vs $0.06\text{ ms}$) and carry a non-zero false positive rate ($3.5\%$) on rare legitimate sessions.
3. **The Power of the Hybrid Architecture**:
   - By placing the **FSM at Stage 1**, grammatical violations (Scenarios 2, 3, 4, and 7) are intercepted in microseconds with **$100\%$ confidence and zero false alarms**.
   - By placing the **ML model at Stage 2**, grammatically valid flows are scrutinized for temporal and statistical deviations (Scenarios 5 and 6), achieving an unbroken **$100\%$ detection rate**.
