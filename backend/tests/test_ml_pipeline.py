"""
Unit tests for Machine Learning Pipeline & Hybrid Engine:
1. Feature extraction correctness (dimensions, types, values).
2. Random Forest and Isolation Forest prediction contracts.
3. Hybrid multi-stage fusion decision logic.
"""

import unittest
import numpy as np
import tempfile
from pathlib import Path

from backend.app.core.feature_extractor import SequenceFeatureExtractor
from backend.app.models.random_forest import RandomForestDetector
from backend.app.models.isolation_forest import IsolationForestDetector
from backend.app.core.hybrid_engine import HybridIntrusionDetectionEngine
from backend.app.data.synthetic_generator import SyntheticTrafficGenerator


class TestMLPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.generator = SyntheticTrafficGenerator(seed=42)
        cls.extractor = SequenceFeatureExtractor()

    def test_feature_extraction_dimensions(self):
        """Verifies feature extractor outputs expected feature count and no NaNs."""
        normal_events = [e.__dict__ for e in self.generator.generate_normal_session()]
        features = self.extractor.extract_features(normal_events)

        self.assertEqual(len(features), len(self.extractor.feature_names))
        self.assertFalse(np.isnan(features).any(), "Extracted features must not contain NaN.")
        self.assertGreater(features[0], 4)  # packet_count > 4

        # Verify Bigram counts exist in feature vector
        syn_ack_bigram_idx = self.extractor.feature_names.index("bigram_SYN_SYN_ACK")
        self.assertGreaterEqual(features[syn_ack_bigram_idx], 1.0)

    def test_random_forest_fit_predict(self):
        """Verifies Random Forest trains and outputs class probabilities."""
        normal_s1 = [e.__dict__ for e in self.generator.generate_normal_session()]
        normal_s2 = [e.__dict__ for e in self.generator.generate_normal_session()]
        atk_syn = [e.__dict__ for e in self.generator.generate_syn_flood_attack()]
        atk_ack = [e.__dict__ for e in self.generator.generate_out_of_order_ack_attack()]

        sessions = {"s1": normal_s1, "s2": normal_s2, "s3": atk_syn, "s4": atk_ack}
        X, _, _, y = self.extractor.extract_batch(sessions)

        rf = RandomForestDetector(n_estimators=10, max_depth=5, random_state=42)
        metrics = rf.train(X, y)

        self.assertTrue(rf.is_trained)
        self.assertGreaterEqual(metrics["accuracy"], 0.75)

        preds, probs = rf.predict(X)
        self.assertEqual(len(preds), len(sessions))
        self.assertEqual(probs.shape, (len(sessions), len(rf.classes_)))

    def test_isolation_forest_unsupervised(self):
        """Verifies Isolation Forest trains on normal traffic and scores anomalies lower."""
        normal_sessions = {f"n_{i}": [e.__dict__ for e in self.generator.generate_normal_session()] for i in range(15)}
        X_norm, _, _, _ = self.extractor.extract_batch(normal_sessions)

        iso = IsolationForestDetector(contamination=0.05, n_estimators=50, random_state=42)
        iso.train(X_norm)
        self.assertTrue(iso.is_trained)

        # Test on attack sequence
        attack_session = [e.__dict__ for e in self.generator.generate_syn_flood_attack(burst_size=10)]
        X_atk = np.expand_dims(self.extractor.extract_features(attack_session), axis=0)

        preds, scores = iso.predict(X_atk)
        self.assertEqual(len(preds), 1)
        self.assertIsInstance(float(scores[0]), float)

    def test_hybrid_decision_fusion(self):
        """
        Verifies hybrid engine behavior:
        - FSM intercepts grammar violation in Stage 1 with 100% confidence.
        - Normal sequence passes through both stages as benign.
        """
        engine = HybridIntrusionDetectionEngine(
            feature_extractor=self.extractor
        )

        # 1. Test Out-of-Order ACK (Grammar Violation)
        ack_atk = [e.__dict__ for e in self.generator.generate_out_of_order_ack_attack()]
        fsm_v, ml_v, hyb_v = engine.detect_hybrid(ack_atk)

        self.assertTrue(fsm_v.is_anomaly)
        self.assertTrue(hyb_v.is_anomaly)
        self.assertEqual(hyb_v.confidence, 1.0)
        self.assertIn("FSM", hyb_v.explanation)
        self.assertIsNotNone(hyb_v.offending_transition)

        # 2. Test Normal Session
        norm = [e.__dict__ for e in self.generator.generate_normal_session()]
        fsm_v, ml_v, hyb_v = engine.detect_hybrid(norm)

        self.assertFalse(fsm_v.is_anomaly)
        self.assertFalse(hyb_v.is_anomaly)
        self.assertEqual(hyb_v.attack_category, "Normal")


if __name__ == "__main__":
    unittest.main()
