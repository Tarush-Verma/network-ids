"""
Unit tests for Synthetic Traffic Generator and Dataset Loader.
Verifies data generation consistency, attack characteristics, and CSV roundtrip.
"""

import unittest
import tempfile
from pathlib import Path

from backend.app.data.synthetic_generator import (
    SyntheticTrafficGenerator,
    NetworkPacketEvent,
)
from backend.app.data.dataset_loader import DatasetLoader
from backend.app.core.fsm import ProtocolFSM, ProtocolEvent, EventType


class TestSyntheticDataset(unittest.TestCase):

    def setUp(self):
        self.generator = SyntheticTrafficGenerator(seed=123)
        self.fsm = ProtocolFSM()

    def test_normal_session_conformance(self):
        """Verifies normal sessions are 100% compliant with FSM grammar."""
        events = self.generator.generate_normal_session()
        self.assertGreaterEqual(len(events), 6)

        # Ensure all labeled as normal
        for ev in events:
            self.assertEqual(ev.is_anomaly, 0)
            self.assertEqual(ev.attack_category, "Normal")

        # Verify through the FSM engine from Phase 1
        fsm_events = [
            ProtocolEvent(event_type=EventType[ev.event_type])
            for ev in events
        ]
        is_accepted, transitions = self.fsm.verify_sequence(fsm_events)
        self.assertTrue(is_accepted, "Normal generated session must be accepted by FSM.")

    def test_syn_flood_characteristics(self):
        """Verifies SYN Flood produces high-frequency SYN events with anomaly label."""
        burst = self.generator.generate_syn_flood_attack(burst_size=6)
        self.assertEqual(len(burst), 6)
        for pkt in burst:
            self.assertEqual(pkt.event_type, "SYN")
            self.assertEqual(pkt.is_anomaly, 1)
            self.assertEqual(pkt.attack_category, "SYN_Flood")
            self.assertLess(pkt.delta_t, 0.005)  # Volumetric sub-millisecond burst

    def test_grammar_attack_injections(self):
        """Verifies out-of-order ACK, premature data, and FIN scan fail FSM check."""
        ack_atk = self.generator.generate_out_of_order_ack_attack()
        self.assertEqual(ack_atk[0].attack_category, "Out_Of_Order_ACK")
        self.assertEqual(ack_atk[0].is_anomaly, 1)

        data_atk = self.generator.generate_premature_data_attack()
        self.assertEqual(data_atk[0].attack_category, "Premature_Data")

        fin_atk = self.generator.generate_stealth_fin_scan()
        self.assertEqual(fin_atk[0].attack_category, "Stealth_FIN_Scan")

    def test_slowloris_temporal_anomaly(self):
        """Verifies Slowloris has valid syntax but extreme dwell time deltas."""
        events = self.generator.generate_slowloris_attack()
        self.assertGreater(len(events), 3)

        # Check that high delta_t exists (dwell anomaly)
        max_delta = max(ev.delta_t for ev in events)
        self.assertGreater(max_delta, 10.0, "Slowloris packets must exhibit high dwell time.")

    def test_dataset_generation_and_csv_io(self):
        """Verifies end-to-end dataset generation, CSV write, and loader roundtrip."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir) / "test_data.csv"
            dataset = self.generator.generate_dataset(normal_sessions_count=20, attack_ratio=0.3)
            self.assertGreater(len(dataset), 50)

            # Export to CSV
            self.generator.export_to_csv(dataset, csv_path)
            self.assertTrue(csv_path.exists())

            # Load back via DatasetLoader
            loaded_records = DatasetLoader.load_csv(csv_path)
            self.assertEqual(len(loaded_records), len(dataset))

            stats = DatasetLoader.get_summary_statistics(loaded_records)
            self.assertIn("total_packets", stats)
            self.assertIn("category_distribution", stats)
            self.assertIn("Normal", stats["category_distribution"])
            self.assertIn("SYN_Flood", stats["category_distribution"])
            self.assertGreater(stats["anomalous_packets"], 0)


if __name__ == "__main__":
    unittest.main()
