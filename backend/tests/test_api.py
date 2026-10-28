"""
Unit and integration tests for FastAPI REST and WebSocket endpoints.
Uses FastAPI TestClient to verify API responses, topology export, and detection endpoints.
"""

import unittest
from fastapi.testclient import TestClient
from backend.app.main import app


class TestBackendAPI(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Use TestClient with context manager to trigger lifespan events
        cls.client = TestClient(app)

    def test_health_check(self):
        """Verifies health check endpoint returns 200 and model status."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertIn("models_loaded", data)

    def test_fsm_topology(self):
        """Verifies FSM topology returns formatted nodes and edges for React Flow."""
        response = self.client.get("/api/fsm/topology")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertIn("states", data)
        self.assertIn("alphabet", data)

        node_ids = [n["id"] for n in data["nodes"]]
        self.assertIn("CLOSED", node_ids)
        self.assertIn("ESTABLISHED", node_ids)
        self.assertIn("ERROR_STATE", node_ids)

    def test_fsm_matrix(self):
        """Verifies transition matrix endpoint."""
        response = self.client.get("/api/fsm/matrix")
        self.assertEqual(response.status_code, 200)
        matrix = response.json()
        self.assertIn("CLOSED", matrix)
        self.assertEqual(matrix["CLOSED"]["SYN_SENT"], "SYN")

    def test_benchmark_metrics(self):
        """Verifies benchmark metrics endpoint returns 3 detectors comparison."""
        response = self.client.get("/api/metrics/benchmark")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("test_dataset", data)
        test_data = data["test_dataset"]
        self.assertIn("Rule_Based_FSM", test_data)
        self.assertIn("Pure_ML", test_data)
        self.assertIn("Hybrid", test_data)

    def test_simulation_scenarios(self):
        """Verifies catalog of attack scenarios."""
        response = self.client.get("/api/simulation/scenarios")
        self.assertEqual(response.status_code, 200)
        scenarios = response.json()
        self.assertGreaterEqual(len(scenarios), 6)
        scenario_ids = [s["id"] for s in scenarios]
        self.assertIn("normal_session", scenario_ids)
        self.assertIn("syn_flood", scenario_ids)
        self.assertIn("out_of_order_ack", scenario_ids)

    def test_generate_scenario_events(self):
        """Verifies generating packet events for a specific scenario."""
        response = self.client.post("/api/simulation/generate/out_of_order_ack")
        self.assertEqual(response.status_code, 200)
        packets = response.json()
        self.assertEqual(len(packets), 1)
        self.assertEqual(packets[0]["event_type"], "ACK")

    def test_detect_custom_tokens_valid(self):
        """Verifies custom event sequence token detection."""
        payload = {
            "events": ["SYN", "SYN_ACK", "ACK", "DATA", "FIN", "ACK", "FIN", "TIMEOUT"],
            "delta_t": 0.02,
            "payload_size": 512,
        }
        response = self.client.post("/api/detect/custom", json=payload)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("hybrid_verdict", data)
        self.assertFalse(data["hybrid_verdict"]["is_anomaly"])

    def test_detect_custom_tokens_grammar_violation(self):
        """Verifies custom tokens with illegal transition trigger alert."""
        payload = {
            "events": ["CLOSED", "ACK"],  # Illegal
            "delta_t": 0.02,
            "payload_size": 0,
        }
        # First test invalid token symbol
        response = self.client.post("/api/detect/custom", json=payload)
        # CLOSED is a state, not an event symbol, so should reject with 400
        self.assertEqual(response.status_code, 400)

        # Now test single illegal ACK
        valid_payload = {
            "events": ["ACK"],  # ACK on initial CLOSED state
            "delta_t": 0.01,
            "payload_size": 0,
        }
        res2 = self.client.post("/api/detect/custom", json=valid_payload)
        self.assertEqual(res2.status_code, 200)
        data2 = res2.json()
        self.assertTrue(data2["fsm_verdict"]["is_anomaly"])
        self.assertTrue(data2["hybrid_verdict"]["is_anomaly"])
        self.assertIsNotNone(data2["fsm_verdict"]["offending_transition"])


if __name__ == "__main__":
    unittest.main()
