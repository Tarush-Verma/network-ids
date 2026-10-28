"""
Feature Extraction Engine
Transforms raw protocol event sequences, transition histories, and temporal
dynamics into structured feature vectors for machine learning classifiers.
"""

import math
from typing import List, Dict, Tuple, Optional
from collections import Counter
import numpy as np

from backend.app.core.fsm import ProtocolState, EventType, ProtocolFSM


class SequenceFeatureExtractor:
    """
    Extracts statistical, temporal, n-gram, and Markov transition features
    from protocol event sessions.
    """

    # Fixed vocabulary of events and states for consistent vectorization
    EVENT_TYPES = [e.value for e in EventType]
    STATES = [s.value for s in ProtocolState if s != ProtocolState.ERROR_STATE]

    # Pre-defined prominent bigrams
    KEY_BIGRAMS = [
        ("SYN", "SYN_ACK"),
        ("SYN_ACK", "ACK"),
        ("ACK", "DATA"),
        ("DATA", "DATA"),
        ("DATA", "FIN"),
        ("FIN", "ACK"),
        ("ACK", "FIN"),
        ("FIN", "TIMEOUT"),
        ("SYN", "SYN"),       # Repeated SYN (flood indicator)
        ("SYN", "FIN"),       # Immediate teardown bypass
        ("CLOSED", "ACK"),    # Out of order indicator
    ]

    def __init__(self, markov_matrix: Optional[Dict[str, Dict[str, float]]] = None):
        self.fsm = ProtocolFSM()
        # Precomputed or learned Markov transition probabilities P(s_{t+1} | s_t)
        self.markov_matrix = markov_matrix or self._initialize_default_markov_priors()
        self.feature_names = self._generate_feature_names()

    def _initialize_default_markov_priors(self) -> Dict[str, Dict[str, float]]:
        """
        Initializes baseline Markov transition probability distribution based on
        RFC 793 standard operational paths.
        """
        matrix = {s: {s_prime: 1e-6 for s_prime in self.STATES} for s in self.STATES}

        standard_transitions = [
            ("CLOSED", "SYN_SENT", 0.95),
            ("CLOSED", "LISTEN", 0.05),
            ("LISTEN", "SYN_RCVD", 0.99),
            ("SYN_SENT", "ESTABLISHED", 0.95),
            ("SYN_SENT", "SYN_RCVD", 0.05),
            ("SYN_RCVD", "ESTABLISHED", 0.98),
            ("ESTABLISHED", "ESTABLISHED", 0.85),
            ("ESTABLISHED", "FIN_WAIT_1", 0.10),
            ("ESTABLISHED", "CLOSE_WAIT", 0.05),
            ("FIN_WAIT_1", "FIN_WAIT_2", 0.95),
            ("FIN_WAIT_2", "TIME_WAIT", 0.98),
            ("TIME_WAIT", "CLOSED", 0.99),
            ("CLOSE_WAIT", "LAST_ACK", 0.98),
            ("LAST_ACK", "CLOSED", 0.99),
        ]

        for s1, s2, prob in standard_transitions:
            if s1 in matrix and s2 in matrix[s1]:
                matrix[s1][s2] = prob

        return matrix

    def _generate_feature_names(self) -> List[str]:
        names = [
            "packet_count",
            "duration",
            "mean_delta_t",
            "std_delta_t",
            "max_delta_t",
            "min_delta_t",
            "total_payload_bytes",
            "mean_payload_size",
            "event_entropy",
            "markov_log_likelihood",
            "fsm_violation_count",
            "syn_ratio",
            "ack_ratio",
            "data_ratio",
            "fin_ratio",
            "rst_count",
        ]
        # Append bigram frequencies
        for e1, e2 in self.KEY_BIGRAMS:
            names.append(f"bigram_{e1}_{e2}")
        return names

    def extract_features(self, session_events: List[Dict]) -> np.ndarray:
        """
        Transforms a sequence of packet events into a 1D numerical feature vector.
        Each item in session_events should be a dictionary with keys:
        [event_type, delta_t, payload_size, current_state, next_state, timestamp, etc.]
        """
        if not session_events:
            return np.zeros(len(self.feature_names), dtype=np.float32)

        packet_count = len(session_events)
        deltas = [float(e.get("delta_t", 0.0)) for e in session_events]
        payloads = [float(e.get("payload_size", 0)) for e in session_events]
        event_names = [str(e.get("event_type", "DATA")) for e in session_events]

        duration = sum(deltas)
        mean_delta_t = float(np.mean(deltas)) if deltas else 0.0
        std_delta_t = float(np.std(deltas)) if len(deltas) > 1 else 0.0
        max_delta_t = float(np.max(deltas)) if deltas else 0.0
        min_delta_t = float(np.min(deltas)) if deltas else 0.0

        total_payload_bytes = float(sum(payloads))
        mean_payload_size = total_payload_bytes / max(1, packet_count)

        # 1. Event Frequency Ratios & Entropy
        event_counts = Counter(event_names)
        syn_ratio = event_counts.get("SYN", 0) / packet_count
        ack_ratio = event_counts.get("ACK", 0) / packet_count
        data_ratio = event_counts.get("DATA", 0) / packet_count
        fin_ratio = event_counts.get("FIN", 0) / packet_count
        rst_count = float(event_counts.get("RST", 0))

        # Shannon entropy of event distribution
        entropy = 0.0
        for count in event_counts.values():
            p = count / packet_count
            if p > 0:
                entropy -= p * math.log2(p)

        # 2. Bigram Counts
        bigram_counts = Counter()
        for i in range(len(event_names) - 1):
            bigram = (event_names[i], event_names[i + 1])
            bigram_counts[bigram] += 1

        # 3. Transition Histories & Markov Sequence Log-Likelihood
        log_likelihood = 0.0
        fsm_violations = 0

        self.fsm.reset()
        for pkt in session_events:
            ev_type_str = pkt.get("event_type", "DATA")
            if hasattr(EventType, ev_type_str):
                ev = EventType[ev_type_str]
                prev_state = self.fsm.current_state.value
                res = self.fsm.step(self.fsm.from_event_names([ev_type_str])[0])
                if not res.is_valid:
                    fsm_violations += 1
                curr_state = self.fsm.current_state.value

                # Markov transition likelihood
                if prev_state in self.markov_matrix and curr_state in self.markov_matrix[prev_state]:
                    prob = self.markov_matrix[prev_state][curr_state]
                else:
                    prob = 1e-6
                log_likelihood += math.log(max(prob, 1e-6))

        # Normalized log likelihood per packet
        norm_log_likelihood = log_likelihood / max(1, packet_count)

        features = [
            float(packet_count),
            float(duration),
            mean_delta_t,
            std_delta_t,
            max_delta_t,
            min_delta_t,
            total_payload_bytes,
            mean_payload_size,
            entropy,
            norm_log_likelihood,
            float(fsm_violations),
            syn_ratio,
            ack_ratio,
            data_ratio,
            fin_ratio,
            rst_count,
        ]

        # Append bigram frequencies
        for e1, e2 in self.KEY_BIGRAMS:
            features.append(float(bigram_counts.get((e1, e2), 0)))

        return np.array(features, dtype=np.float32)

    def extract_batch(self, sessions_dict: Dict[str, List[Dict]]) -> Tuple[np.ndarray, List[str], List[int], List[str]]:
        """
        Extracts features for all sessions.
        Returns:
            X: 2D numpy array [n_sessions, n_features]
            session_ids: list of session IDs
            y_binary: list of 0 (Normal) or 1 (Anomaly)
            y_categories: list of attack category strings
        """
        X_list = []
        session_ids = []
        y_binary = []
        y_categories = []

        for s_id, events in sessions_dict.items():
            feat = self.extract_features(events)
            X_list.append(feat)
            session_ids.append(s_id)

            # Session label: anomalous if any packet in session was flagged
            is_anom = 1 if any(int(e.get("is_anomaly", 0)) == 1 for e in events) else 0
            y_binary.append(is_anom)

            # Attack category: first non-Normal category found, else Normal
            cat = "Normal"
            for e in events:
                if e.get("attack_category", "Normal") != "Normal":
                    cat = e["attack_category"]
                    break
            y_categories.append(cat)

        X = np.vstack(X_list) if X_list else np.empty((0, len(self.feature_names)), dtype=np.float32)
        return X, session_ids, y_binary, y_categories
