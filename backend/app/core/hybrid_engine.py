"""
Hybrid Intrusion Detection Engine
Combines deterministic Finite-State Machine (FSM) protocol verification
with data-driven Machine Learning (Random Forest + Isolation Forest) models.
Compares:
1. Pure Rule-Based FSM Detector
2. Pure ML Detector
3. Hybrid Multi-Stage Detector
"""

import time
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import numpy as np

from backend.app.core.fsm import ProtocolFSM, ProtocolState, EventType, ProtocolEvent
from backend.app.core.feature_extractor import SequenceFeatureExtractor
from backend.app.models.random_forest import RandomForestDetector
from backend.app.models.isolation_forest import IsolationForestDetector


@dataclass
class DetectorVerdict:
    detector_name: str  # "Rule_Based_FSM", "Pure_ML", "Hybrid"
    is_anomaly: bool
    confidence: float   # 0.0 to 1.0
    latency_ms: float   # Processing time in milliseconds
    attack_category: str
    explanation: str
    offending_transition: Optional[Dict] = None


@dataclass
class ComprehensiveDetectionResult:
    session_id: str
    fsm_verdict: DetectorVerdict
    ml_verdict: DetectorVerdict
    hybrid_verdict: DetectorVerdict
    sequence_length: int
    summary: str


class HybridIntrusionDetectionEngine:
    """
    Unified detection engine that executes and benchmarks:
    - Pure Rule-Based FSM
    - Pure ML (Random Forest + Isolation Forest)
    - Hybrid (FSM Grammar Gate + ML Manifold Inspection)
    """

    def __init__(
        self,
        rf_detector: Optional[RandomForestDetector] = None,
        if_detector: Optional[IsolationForestDetector] = None,
        feature_extractor: Optional[SequenceFeatureExtractor] = None,
    ):
        self.fsm = ProtocolFSM()
        self.rf_detector = rf_detector
        self.if_detector = if_detector
        self.feature_extractor = feature_extractor or SequenceFeatureExtractor()

    def detect_pure_fsm(self, events: List[Dict]) -> DetectorVerdict:
        """
        Detector 1: Pure Rule-Based FSM.
        Strict verification against delta(s_t, e_t). Zero false negatives on syntax,
        ultra-fast O(1) per step, but blind to valid-syntax attacks (like Slowloris/SYN Flood).
        """
        start_time = time.perf_counter()
        self.fsm.reset()

        is_anomaly = False
        offending_trans = None
        explanation = "Protocol sequence conforms strictly to RFC 793 regular language L(M)."
        category = "Normal"

        for pkt in events:
            ev_str = pkt.get("event_type", "DATA")
            if hasattr(EventType, ev_str):
                ev = EventType[ev_str]
                prev_state = self.fsm.current_state
                res = self.fsm.step(ProtocolEvent(event_type=ev))

                if not res.is_valid:
                    is_anomaly = True
                    diag = self.fsm.diagnose_violation(prev_state, ev)
                    category = diag["attack_type"]
                    explanation = diag["description"]
                    offending_trans = {
                        "from_state": prev_state.value,
                        "event": ev.value,
                        "to_state": ProtocolState.ERROR_STATE.value,
                        "allowed_events": diag["allowed_events"],
                        "cve_reference": diag["reference"],
                        "seq_index": pkt.get("seq_index", 0),
                        "timestamp": pkt.get("timestamp", 0.0),
                    }
                    break

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return DetectorVerdict(
            detector_name="Rule_Based_FSM",
            is_anomaly=is_anomaly,
            confidence=1.0 if is_anomaly else 0.95,
            latency_ms=round(latency_ms, 4),
            attack_category=category,
            explanation=explanation,
            offending_transition=offending_trans,
        )

    def detect_pure_ml(self, events: List[Dict]) -> DetectorVerdict:
        """
        Detector 2: Pure ML Engine.
        Uses Random Forest for supervised signature detection and
        Isolation Forest for unsupervised anomaly scoring.
        """
        start_time = time.perf_counter()

        feat = self.feature_extractor.extract_features(events)
        X = np.expand_dims(feat, axis=0)

        is_anomaly = False
        category = "Normal"
        confidence = 0.5
        explanation = "Traffic feature metrics lie within normal statistical bounds."

        # 1. Random Forest Supervised check
        if self.rf_detector and self.rf_detector.is_trained:
            rf_preds, rf_probs = self.rf_detector.predict(X)
            pred_class = rf_preds[0]
            max_prob = float(np.max(rf_probs[0]))

            if pred_class != "Normal":
                is_anomaly = True
                category = pred_class
                confidence = max_prob
                explanation = f"Random Forest identified attack signature '{pred_class}' with {round(confidence * 100, 1)}% probability."

        # 2. Isolation Forest Unsupervised check (Catches outliers/zero-day deviations)
        if self.if_detector and self.if_detector.is_trained:
            if_preds, if_scores = self.if_detector.predict(X)
            is_outlier = (if_preds[0] == 1)
            normal_score = float(if_scores[0])

            is_rf_confidently_normal = (
                (pred_class == "Normal" and max_prob >= 0.70)
                if (self.rf_detector and self.rf_detector.is_trained)
                else False
            )

            if is_outlier and not is_anomaly and not is_rf_confidently_normal:
                is_anomaly = True
                category = "Unsupervised_Statistical_Anomaly"
                confidence = float(1.0 - normal_score)
                explanation = f"Isolation Forest identified out-of-distribution sequence deviation (Normality score: {round(normal_score, 3)})."

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        return DetectorVerdict(
            detector_name="Pure_ML",
            is_anomaly=is_anomaly,
            confidence=round(confidence, 3),
            latency_ms=round(latency_ms, 4),
            attack_category=category,
            explanation=explanation,
        )

    def detect_hybrid(self, events: List[Dict]) -> Tuple[DetectorVerdict, DetectorVerdict, DetectorVerdict]:
        """
        Detector 3: Hybrid Engine.
        Stage 1: Deterministic FSM filters illegal transitions immediately with zero latency escape.
        Stage 2: Statistical/temporal ML detector inspects grammatically valid flows for subtle anomalies.
        """
        start_time = time.perf_counter()

        # Step 1: Run FSM check
        fsm_verdict = self.detect_pure_fsm(events)

        # Step 2: Run ML check
        ml_verdict = self.detect_pure_ml(events)

        # Step 3: Hybrid Decision Fusion
        if fsm_verdict.is_anomaly:
            # FSM caught a strict protocol syntax breach
            hybrid_is_anomaly = True
            hybrid_category = fsm_verdict.attack_category
            hybrid_confidence = 1.0
            hybrid_explanation = (
                f"[Hybrid Stage 1 Triggered] Deterministic FSM intercepted grammar violation: "
                f"{fsm_verdict.explanation}"
            )
            offending_trans = fsm_verdict.offending_transition
        elif ml_verdict.is_anomaly:
            # Syntax was valid, but ML caught temporal/volumetric attack (e.g. Slowloris or SYN Flood)
            hybrid_is_anomaly = True
            hybrid_category = ml_verdict.attack_category
            hybrid_confidence = ml_verdict.confidence
            hybrid_explanation = (
                f"[Hybrid Stage 2 Triggered] Protocol grammar valid, but data-driven ML identified "
                f"statistical anomaly: {ml_verdict.explanation}"
            )
            offending_trans = None
        else:
            # Both verified legitimate
            hybrid_is_anomaly = False
            hybrid_category = "Normal"
            hybrid_confidence = round((fsm_verdict.confidence + (1.0 - ml_verdict.confidence)) / 2.0, 3)
            hybrid_explanation = "Traffic verified: both FSM grammar and ML feature distributions are benign."
            offending_trans = None

        latency_ms = (time.perf_counter() - start_time) * 1000.0

        hybrid_verdict = DetectorVerdict(
            detector_name="Hybrid",
            is_anomaly=hybrid_is_anomaly,
            confidence=round(hybrid_confidence, 3),
            latency_ms=round(latency_ms, 4),
            attack_category=hybrid_category,
            explanation=hybrid_explanation,
            offending_transition=offending_trans,
        )

        return fsm_verdict, ml_verdict, hybrid_verdict

    def evaluate_session(self, session_id: str, events: List[Dict]) -> ComprehensiveDetectionResult:
        """
        Evaluates a complete session through all three detectors and formats
        a comparative result ready for the React dashboard.
        """
        fsm_v, ml_v, hyb_v = self.detect_hybrid(events)

        summary = (
            f"FSM: {'ALERT' if fsm_v.is_anomaly else 'OK'} ({fsm_v.latency_ms}ms) | "
            f"ML: {'ALERT' if ml_v.is_anomaly else 'OK'} ({ml_v.latency_ms}ms) | "
            f"Hybrid: {'ALERT' if hyb_v.is_anomaly else 'OK'} ({hyb_v.latency_ms}ms)"
        )

        return ComprehensiveDetectionResult(
            session_id=session_id,
            fsm_verdict=fsm_v,
            ml_verdict=ml_v,
            hybrid_verdict=hyb_v,
            sequence_length=len(events),
            summary=summary,
        )
