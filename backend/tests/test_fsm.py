"""
Unit tests for Protocol FSM (Theory of Computation Finite-State Model).
Verifies:
1. Regular Language Acceptance L(M) on legitimate sequences.
2. Anomaly Detection and rejection on illegal protocol transitions.
3. Graph data serialization for frontend React visualization.
"""

import unittest
from backend.app.core.fsm import (
    ProtocolFSM,
    ProtocolState,
    EventType,
    ProtocolEvent,
)


class TestProtocolFSM(unittest.TestCase):

    def setUp(self):
        self.fsm = ProtocolFSM()

    def test_initial_state(self):
        self.assertEqual(self.fsm.current_state, ProtocolState.CLOSED)
        self.assertEqual(len(self.fsm.history), 0)

    def test_normal_client_handshake_and_teardown(self):
        """Tests standard normal TCP communication: 3-way handshake + data + 4-way teardown."""
        events = [
            ProtocolEvent(event_type=EventType.SYN),
            ProtocolEvent(event_type=EventType.SYN_ACK),
            ProtocolEvent(event_type=EventType.DATA, payload_size=512),
            ProtocolEvent(event_type=EventType.DATA, payload_size=1024),
            ProtocolEvent(event_type=EventType.FIN),
            ProtocolEvent(event_type=EventType.ACK),
            ProtocolEvent(event_type=EventType.FIN),
            ProtocolEvent(event_type=EventType.TIMEOUT),
        ]

        is_accepted, results = self.fsm.verify_sequence(events)

        self.assertTrue(is_accepted, "Legitimate TCP sequence should be accepted.")
        self.assertEqual(self.fsm.current_state, ProtocolState.CLOSED)
        self.assertEqual(len(results), len(events))
        for r in results:
            self.assertTrue(r.is_valid)

    def test_server_handshake(self):
        """Tests server-side listening and handshake acceptance."""
        events = [
            ProtocolEvent(event_type=EventType.LISTEN),
            ProtocolEvent(event_type=EventType.SYN),
            ProtocolEvent(event_type=EventType.ACK),
        ]
        is_accepted, results = self.fsm.verify_sequence(events)
        self.assertTrue(is_accepted)
        self.assertEqual(self.fsm.current_state, ProtocolState.ESTABLISHED)

    def test_anomaly_out_of_order_ack(self):
        """
        Attack Scenario: Out-of-order ACK injection.
        Sender sends an ACK while in CLOSED state without prior SYN.
        """
        event = ProtocolEvent(event_type=EventType.ACK)
        res = self.fsm.step(event)

        self.assertFalse(res.is_valid, "ACK in CLOSED state must be rejected.")
        self.assertEqual(res.to_state, ProtocolState.ERROR_STATE)
        self.assertEqual(res.severity, "CRITICAL")
        self.assertIn("SYN", [e.value for e in res.expected_events])

    def test_anomaly_data_before_handshake(self):
        """
        Attack Scenario: Data payload injection into closed/unauthenticated socket.
        """
        event = ProtocolEvent(event_type=EventType.DATA, payload_size=256)
        res = self.fsm.step(event)

        self.assertFalse(res.is_valid)
        self.assertEqual(res.to_state, ProtocolState.ERROR_STATE)
        self.assertIn("ANOMALY", res.reason)

    def test_anomaly_fin_scan_attack(self):
        """
        Attack Scenario: Stealth FIN Scan.
        Attacker sends unexpected FIN packet to probe port status.
        """
        event = ProtocolEvent(event_type=EventType.FIN)
        res = self.fsm.step(event)

        self.assertFalse(res.is_valid)
        self.assertEqual(self.fsm.current_state, ProtocolState.ERROR_STATE)

    def test_reset_recovery(self):
        """Verifies abrupt reset (RST) legitimately returns state to CLOSED."""
        self.fsm.step(ProtocolEvent(event_type=EventType.SYN))
        self.fsm.step(ProtocolEvent(event_type=EventType.SYN_ACK))
        self.assertEqual(self.fsm.current_state, ProtocolState.ESTABLISHED)

        rst_res = self.fsm.step(ProtocolEvent(event_type=EventType.RST))
        self.assertTrue(rst_res.is_valid)
        self.assertEqual(self.fsm.current_state, ProtocolState.CLOSED)

    def test_graph_export(self):
        """Verifies graph export produces valid nodes and edges for React UI."""
        graph_data = self.fsm.to_graph_data()
        self.assertIn("nodes", graph_data)
        self.assertIn("edges", graph_data)
        self.assertIn("states", graph_data)
        self.assertIn("alphabet", graph_data)

        # Check CLOSED node properties
        closed_node = next(n for n in graph_data["nodes"] if n["id"] == "CLOSED")
        self.assertTrue(closed_node["isInitial"])
        self.assertTrue(closed_node["isAccept"])

        # Check edge counts
        self.assertGreater(len(graph_data["edges"]), 10)

    def test_from_event_names_conversion(self):
        """Tests parsing list of event string tokens into typed ProtocolEvents."""
        names = ["SYN", "SYN_ACK", "ACK", "DATA"]
        events = ProtocolFSM.from_event_names(names)
        self.assertEqual(len(events), 4)
        self.assertEqual(events[0].event_type, EventType.SYN)
        self.assertEqual(events[1].event_type, EventType.SYN_ACK)

        # Invalid token test
        with self.assertRaises(ValueError):
            ProtocolFSM.from_event_names(["SYN", "BOGUS_PACKET"])

    def test_diagnose_violation(self):
        """Tests security attribution and CVE/CWE tagging of anomalous transitions."""
        diag = self.fsm.diagnose_violation(ProtocolState.CLOSED, EventType.ACK)
        self.assertEqual(diag["attack_type"], "OUT_OF_ORDER_ACK_INJECTION")
        self.assertIn("CWE-940", diag["reference"])

        diag_fin = self.fsm.diagnose_violation(ProtocolState.CLOSED, EventType.FIN)
        self.assertEqual(diag_fin["attack_type"], "STEALTH_FIN_SCAN")

    def test_transition_matrix(self):
        """Tests creation of formal transition matrix for Markov & theoretical analysis."""
        matrix = self.fsm.get_transition_matrix()
        self.assertIn("CLOSED", matrix)
        self.assertEqual(matrix["CLOSED"]["SYN_SENT"], "SYN")
        self.assertEqual(matrix["SYN_SENT"]["ESTABLISHED"], "SYN_ACK")
        self.assertIsNone(matrix["CLOSED"]["ESTABLISHED"])  # Direct jump is illegal


if __name__ == "__main__":
    unittest.main()

