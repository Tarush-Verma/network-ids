"""
Protocol Finite-State Machine (FSM) Core Module
Theory of Computation (TOC) Foundation:
M = (Q, Sigma, delta, q0, F)
- Q: Finite set of protocol states (RFC 793 inspired)
- Sigma: Finite set of input symbols (Protocol Events / Packet Flags)
- delta: Transition function Q x Sigma -> Q
- q0: Initial state (CLOSED)
- F: Accept/Terminal states (CLOSED, TIME_WAIT)
"""

from enum import Enum
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import time


class ProtocolState(str, Enum):
    CLOSED = "CLOSED"
    LISTEN = "LISTEN"
    SYN_SENT = "SYN_SENT"
    SYN_RCVD = "SYN_RCVD"
    ESTABLISHED = "ESTABLISHED"
    FIN_WAIT_1 = "FIN_WAIT_1"
    FIN_WAIT_2 = "FIN_WAIT_2"
    CLOSE_WAIT = "CLOSE_WAIT"
    LAST_ACK = "LAST_ACK"
    TIME_WAIT = "TIME_WAIT"
    ERROR_STATE = "ERROR_STATE"


class EventType(str, Enum):
    LISTEN = "LISTEN"          # Passive open command
    SYN = "SYN"                # Active open / connection request
    SYN_ACK = "SYN_ACK"        # Handshake response
    ACK = "ACK"                # Acknowledgment
    DATA = "DATA"              # Valid bidirectional payload transfer
    FIN = "FIN"                # Graceful connection termination request
    RST = "RST"                # Abrupt reset
    TIMEOUT = "TIMEOUT"        # Protocol timer expiration (e.g., 2MSL in TIME_WAIT)


@dataclass
class ProtocolEvent:
    event_type: EventType
    timestamp: float = field(default_factory=time.time)
    payload_size: int = 0
    seq_num: Optional[int] = None
    flags: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)


@dataclass
class TransitionResult:
    is_valid: bool
    from_state: ProtocolState
    to_state: ProtocolState
    event: EventType
    timestamp: float
    reason: str
    expected_events: List[EventType] = field(default_factory=list)
    severity: str = "INFO"  # INFO, WARNING, CRITICAL


class ProtocolFSM:
    """
    Finite-State Machine for Protocol Transition Verification.
    Implements deterministic validation of protocol event sequences.
    """

    def __init__(self, initial_state: ProtocolState = ProtocolState.CLOSED):
        self.initial_state = initial_state
        self.current_state = initial_state
        self.history: List[TransitionResult] = []
        self._build_transition_table()

    def _build_transition_table(self):
        """
        Defines the valid transition function: delta(state, event) -> next_state.
        Based on RFC 793 TCP state automaton + Session data transfer extension.
        """
        self.delta: Dict[Tuple[ProtocolState, EventType], ProtocolState] = {
            # --- Handshake Phase ---
            (ProtocolState.CLOSED, EventType.LISTEN): ProtocolState.LISTEN,
            (ProtocolState.CLOSED, EventType.SYN): ProtocolState.SYN_SENT,       # Active open
            (ProtocolState.LISTEN, EventType.SYN): ProtocolState.SYN_RCVD,       # Passive open receives SYN
            (ProtocolState.SYN_SENT, EventType.SYN_ACK): ProtocolState.ESTABLISHED, # Client receives SYN-ACK, completes handshake
            (ProtocolState.SYN_SENT, EventType.SYN): ProtocolState.SYN_RCVD,     # Simultaneous open
            (ProtocolState.SYN_RCVD, EventType.ACK): ProtocolState.ESTABLISHED,  # Server receives final ACK

            # --- Established / Data Transfer Phase ---
            (ProtocolState.ESTABLISHED, EventType.DATA): ProtocolState.ESTABLISHED, # Bidirectional data
            (ProtocolState.ESTABLISHED, EventType.ACK): ProtocolState.ESTABLISHED,  # Pure keepalive/ACK

            # --- Active Close Phase (Initiator) ---
            (ProtocolState.ESTABLISHED, EventType.FIN): ProtocolState.FIN_WAIT_1,
            (ProtocolState.FIN_WAIT_1, EventType.ACK): ProtocolState.FIN_WAIT_2,
            (ProtocolState.FIN_WAIT_2, EventType.FIN): ProtocolState.TIME_WAIT,
            (ProtocolState.TIME_WAIT, EventType.TIMEOUT): ProtocolState.CLOSED,

            # --- Passive Close Phase (Receiver) ---
            (ProtocolState.CLOSE_WAIT, EventType.FIN): ProtocolState.LAST_ACK,
            (ProtocolState.LAST_ACK, EventType.ACK): ProtocolState.CLOSED,

            # --- Resets (RST can occur from any active state back to CLOSED) ---
            (ProtocolState.SYN_SENT, EventType.RST): ProtocolState.CLOSED,
            (ProtocolState.SYN_RCVD, EventType.RST): ProtocolState.CLOSED,
            (ProtocolState.ESTABLISHED, EventType.RST): ProtocolState.CLOSED,
            (ProtocolState.FIN_WAIT_1, EventType.RST): ProtocolState.CLOSED,
            (ProtocolState.FIN_WAIT_2, EventType.RST): ProtocolState.CLOSED,
            (ProtocolState.CLOSE_WAIT, EventType.RST): ProtocolState.CLOSED,
        }

        # Normalize deterministic mapping
        # In a standard client/server peer representation:
        # Client side active close: ESTABLISHED + FIN -> FIN_WAIT_1
        # Receiver side passive close: ESTABLISHED receives FIN -> CLOSE_WAIT
        self.valid_transitions: Dict[ProtocolState, Dict[EventType, ProtocolState]] = {
            state: {} for state in ProtocolState
        }

        for src_state, event, dest_state in [
            # Connection Initiation
            (ProtocolState.CLOSED, EventType.LISTEN, ProtocolState.LISTEN),
            (ProtocolState.CLOSED, EventType.SYN, ProtocolState.SYN_SENT),
            (ProtocolState.LISTEN, EventType.SYN, ProtocolState.SYN_RCVD),
            (ProtocolState.SYN_SENT, EventType.SYN_ACK, ProtocolState.ESTABLISHED),
            (ProtocolState.SYN_SENT, EventType.SYN, ProtocolState.SYN_RCVD),
            (ProtocolState.SYN_RCVD, EventType.ACK, ProtocolState.ESTABLISHED),
            # Data Flow
            (ProtocolState.ESTABLISHED, EventType.DATA, ProtocolState.ESTABLISHED),
            (ProtocolState.ESTABLISHED, EventType.ACK, ProtocolState.ESTABLISHED),
            # Active Teardown
            (ProtocolState.ESTABLISHED, EventType.FIN, ProtocolState.FIN_WAIT_1),
            (ProtocolState.FIN_WAIT_1, EventType.ACK, ProtocolState.FIN_WAIT_2),
            (ProtocolState.FIN_WAIT_2, EventType.FIN, ProtocolState.TIME_WAIT),
            (ProtocolState.TIME_WAIT, EventType.TIMEOUT, ProtocolState.CLOSED),
            # Passive Teardown
            (ProtocolState.CLOSE_WAIT, EventType.FIN, ProtocolState.LAST_ACK),
            (ProtocolState.LAST_ACK, EventType.ACK, ProtocolState.CLOSED),
            # Resets
            (ProtocolState.SYN_SENT, EventType.RST, ProtocolState.CLOSED),
            (ProtocolState.SYN_RCVD, EventType.RST, ProtocolState.CLOSED),
            (ProtocolState.ESTABLISHED, EventType.RST, ProtocolState.CLOSED),
            (ProtocolState.FIN_WAIT_1, EventType.RST, ProtocolState.CLOSED),
            (ProtocolState.FIN_WAIT_2, EventType.RST, ProtocolState.CLOSED),
            (ProtocolState.CLOSE_WAIT, EventType.RST, ProtocolState.CLOSED),
            (ProtocolState.LAST_ACK, EventType.RST, ProtocolState.CLOSED),
            (ProtocolState.TIME_WAIT, EventType.RST, ProtocolState.CLOSED),
        ]:
            self.valid_transitions[src_state][event] = dest_state

    def get_allowed_events(self, state: ProtocolState) -> List[EventType]:
        """Returns the list of valid input symbols sigma in Sigma allowed from current state."""
        return list(self.valid_transitions.get(state, {}).keys())

    def step(self, event: ProtocolEvent) -> TransitionResult:
        """
        Executes a single state transition step delta(s_t, e_t) -> s_{t+1}.
        If (s_t, e_t) is not in delta, flags an anomaly and transitions to ERROR_STATE.
        """
        src = self.current_state
        allowed = self.get_allowed_events(src)

        if event.event_type in self.valid_transitions.get(src, {}):
            dest = self.valid_transitions[src][event.event_type]
            self.current_state = dest
            result = TransitionResult(
                is_valid=True,
                from_state=src,
                to_state=dest,
                event=event.event_type,
                timestamp=event.timestamp,
                reason=f"Valid transition: {src.value} --({event.event_type.value})--> {dest.value}",
                expected_events=allowed,
                severity="INFO",
            )
        else:
            # Rule-based FSM Anomaly Detected!
            dest = ProtocolState.ERROR_STATE
            reason = (
                f"ANOMALY: Illegal transition attempted! State '{src.value}' "
                f"cannot accept event '{event.event_type.value}'. "
                f"Expected one of: {[e.value for e in allowed]}."
            )
            self.current_state = dest
            result = TransitionResult(
                is_valid=False,
                from_state=src,
                to_state=dest,
                event=event.event_type,
                timestamp=event.timestamp,
                reason=reason,
                expected_events=allowed,
                severity="CRITICAL",
            )

        self.history.append(result)
        return result

    def verify_sequence(self, events: List[ProtocolEvent], reset: bool = True) -> Tuple[bool, List[TransitionResult]]:
        """
        Verifies an entire word w = e_1 e_2 ... e_n against the regular language L(M).
        Returns (is_accepted, list_of_transitions).
        """
        if reset:
            self.reset()

        results = []
        is_accepted = True

        for ev in events:
            res = self.step(ev)
            results.append(res)
            if not res.is_valid:
                is_accepted = False
                break

        # A word is strictly accepted if it halts without error and finishes in an accept state
        is_clean_finish = self.current_state in {ProtocolState.CLOSED, ProtocolState.TIME_WAIT, ProtocolState.ESTABLISHED}
        return (is_accepted and is_clean_finish), results

    def reset(self):
        """Resets the automaton to initial state q0 (CLOSED)."""
        self.current_state = self.initial_state
        self.history.clear()

    @staticmethod
    def from_event_names(names: List[str]) -> List[ProtocolEvent]:
        """Convenience utility to convert list of event name strings into ProtocolEvent objects."""
        events = []
        for name in names:
            name_clean = name.strip().upper()
            if hasattr(EventType, name_clean):
                events.append(ProtocolEvent(event_type=EventType[name_clean]))
            else:
                raise ValueError(f"Unknown protocol event: {name}. Must be one of {[e.value for e in EventType]}")
        return events

    def diagnose_violation(self, from_state: ProtocolState, event: EventType) -> Dict:
        """
        Classifies the security context and attack profile of an invalid state transition.
        Useful for real-time alerting on the security dashboard.
        """
        attack_type = "ILLEGAL_STATE_TRANSITION"
        description = f"Unexpected {event.value} in state {from_state.value}"
        cve_reference = "RFC-793 Violation"

        if from_state == ProtocolState.CLOSED and event == EventType.ACK:
            attack_type = "OUT_OF_ORDER_ACK_INJECTION"
            description = "Blind ACK packet received without connection initiation. Common in ACK scan or state spoofing."
            cve_reference = "CWE-940: Improper Verification of Source Digest"
        elif from_state == ProtocolState.CLOSED and event == EventType.DATA:
            attack_type = "PREMATURE_PAYLOAD_INJECTION"
            description = "Data transmitted to a closed socket prior to 3-way handshake."
            cve_reference = "CWE-345: Insufficient Verification of Data Authenticity"
        elif from_state == ProtocolState.CLOSED and event == EventType.FIN:
            attack_type = "STEALTH_FIN_SCAN"
            description = "FIN probe sent to closed port to determine open/closed firewall status (Nmap FIN scan)."
            cve_reference = "MITRE ATT&CK T1595: Active Scanning"
        elif from_state in {ProtocolState.SYN_SENT, ProtocolState.SYN_RCVD} and event == EventType.FIN:
            attack_type = "ABORTED_HANDSHAKE_PROBE"
            description = "Premature termination during handshake negotiation."
            cve_reference = "MITRE ATT&CK T1499: Endpoint DoS"

        return {
            "attack_type": attack_type,
            "description": description,
            "reference": cve_reference,
            "from_state": from_state.value,
            "offending_event": event.value,
            "allowed_events": [e.value for e in self.get_allowed_events(from_state)],
        }

    def get_transition_matrix(self) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Returns the formal transition matrix M[s][s'] = event.
        Rows and columns represent states; values indicate the event triggering the transition.
        """
        states = [s.value for s in ProtocolState if s != ProtocolState.ERROR_STATE]
        matrix = {s: {s_prime: None for s_prime in states} for s in states}

        for src, transitions in self.valid_transitions.items():
            if src.value in matrix:
                for evt, dest in transitions.items():
                    if dest.value in matrix[src.value]:
                        matrix[src.value][dest.value] = evt.value

        return matrix

    def to_graph_data(self) -> Dict:
        """
        Exports the FSM topology as nodes and directed edges formatted for
        graph visualization (React Flow / Cytoscape) in the frontend dashboard.
        """
        # Node positions curated for intuitive circular/hierarchical state layout
        state_coords = {
            ProtocolState.CLOSED: {"x": 100, "y": 300},
            ProtocolState.LISTEN: {"x": 260, "y": 140},
            ProtocolState.SYN_SENT: {"x": 260, "y": 460},
            ProtocolState.SYN_RCVD: {"x": 450, "y": 200},
            ProtocolState.ESTABLISHED: {"x": 620, "y": 300},
            ProtocolState.FIN_WAIT_1: {"x": 800, "y": 180},
            ProtocolState.FIN_WAIT_2: {"x": 980, "y": 180},
            ProtocolState.TIME_WAIT: {"x": 980, "y": 360},
            ProtocolState.CLOSE_WAIT: {"x": 800, "y": 420},
            ProtocolState.LAST_ACK: {"x": 620, "y": 460},
            ProtocolState.ERROR_STATE: {"x": 500, "y": 600},
        }

        nodes = [
            {
                "id": state.value,
                "label": state.value,
                "isInitial": state == ProtocolState.CLOSED,
                "isAccept": state in {ProtocolState.CLOSED, ProtocolState.TIME_WAIT},
                "isError": state == ProtocolState.ERROR_STATE,
                "position": state_coords.get(state, {"x": 0, "y": 0}),
            }
            for state in ProtocolState
        ]

        edges = []
        edge_idx = 0
        for src, transitions in self.valid_transitions.items():
            for evt, dest in transitions.items():
                edges.append({
                    "id": f"e_{src.value}_{dest.value}_{evt.value}_{edge_idx}",
                    "source": src.value,
                    "target": dest.value,
                    "label": evt.value,
                    "event": evt.value,
                })
                edge_idx += 1

        return {
            "states": [s.value for s in ProtocolState],
            "alphabet": [e.value for e in EventType],
            "nodes": nodes,
            "edges": edges,
            "initial_state": self.initial_state.value,
        }

