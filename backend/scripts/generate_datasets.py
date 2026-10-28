"""
CLI script to generate benchmark training, testing, and zero-day intrusion datasets.
Run:
    python backend/scripts/generate_datasets.py
"""

import sys
from pathlib import Path

# Ensure workspace root is in python path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from backend.app.data.synthetic_generator import (
    SyntheticTrafficGenerator,
    NetworkPacketEvent,
)
from backend.app.data.dataset_loader import DatasetLoader
from backend.app.core.fsm import ProtocolState, EventType
import random
import time
import uuid


def generate_unseen_zero_day_traffic(generator: SyntheticTrafficGenerator, count: int = 40) -> list[NetworkPacketEvent]:
    """
    Generates novel, unseen protocol attacks not included in standard training sets:
    1. Reset Storm (repeated RST packets injected across invalid states)
    2. Handshake Skip to Teardown (SYN followed immediately by FIN without establishing)
    3. Simultaneous Out-of-Order PUSH-ACK Flood
    """
    events = []
    attacker_ip = "10.0.99.99"
    curr_time = time.time()

    for i in range(count):
        session_id = f"zero_day_{i:03d}"
        variant = i % 3

        if variant == 0:
            # Variant 1: Handshake Skip to Teardown (Illegal sequence SYN -> FIN)
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=0,
                timestamp=curr_time,
                delta_t=0.01,
                src_ip=attacker_ip,
                dst_ip=generator.server_ip,
                src_port=44000 + i,
                dst_port=generator.server_port,
                event_type=EventType.SYN.value,
                current_state=ProtocolState.CLOSED.value,
                next_state=ProtocolState.SYN_SENT.value,
                payload_size=0,
                flags=["SYN"],
                is_anomaly=1,
                attack_category="ZeroDay_Handshake_Bypass",
                violation_type="UNSEEN_TRANSITION_SEQUENCE",
            ))
            curr_time += 0.02
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=1,
                timestamp=curr_time,
                delta_t=0.02,
                src_ip=attacker_ip,
                dst_ip=generator.server_ip,
                src_port=44000 + i,
                dst_port=generator.server_port,
                event_type=EventType.FIN.value,
                current_state=ProtocolState.SYN_SENT.value,
                next_state=ProtocolState.ERROR_STATE.value,
                payload_size=0,
                flags=["FIN"],
                is_anomaly=1,
                attack_category="ZeroDay_Handshake_Bypass",
                violation_type="UNSEEN_TRANSITION_SEQUENCE",
            ))
        elif variant == 1:
            # Variant 2: RST Storm (Abrupt resets to arbitrary non-active sockets)
            curr_time += 0.005
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=0,
                timestamp=curr_time,
                delta_t=0.005,
                src_ip=attacker_ip,
                dst_ip=generator.server_ip,
                src_port=45000 + i,
                dst_port=generator.server_port,
                event_type=EventType.RST.value,
                current_state=ProtocolState.CLOSED.value,
                next_state=ProtocolState.CLOSED.value,
                payload_size=0,
                flags=["RST"],
                is_anomaly=1,
                attack_category="ZeroDay_RST_Storm",
                violation_type="STATISTICAL_RESET_FLOOD",
            ))
        else:
            # Variant 3: Rapid Double SYN with contradictory payloads
            curr_time += 0.001
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=0,
                timestamp=curr_time,
                delta_t=0.001,
                src_ip=attacker_ip,
                dst_ip=generator.server_ip,
                src_port=46000 + i,
                dst_port=generator.server_port,
                event_type=EventType.SYN.value,
                current_state=ProtocolState.CLOSED.value,
                next_state=ProtocolState.SYN_SENT.value,
                payload_size=0,
                flags=["SYN"],
                is_anomaly=1,
                attack_category="ZeroDay_Double_SYN",
                violation_type="UNSEEN_TRANSITION_SEQUENCE",
            ))
            curr_time += 0.001
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=1,
                timestamp=curr_time,
                delta_t=0.001,
                src_ip=attacker_ip,
                dst_ip=generator.server_ip,
                src_port=46000 + i,
                dst_port=generator.server_port,
                event_type=EventType.SYN.value,
                current_state=ProtocolState.SYN_SENT.value,
                next_state=ProtocolState.SYN_RCVD.value,
                payload_size=512,  # Anomalous payload attached to SYN
                flags=["SYN", "PSH"],
                is_anomaly=1,
                attack_category="ZeroDay_Double_SYN",
                violation_type="UNSEEN_TRANSITION_SEQUENCE",
            ))

    return events


def main():
    print("=" * 65)
    print("Generating Protocol Datasets for Intrusion Detection Benchmark")
    print("=" * 65)

    base_data_dir = Path("backend/data")
    base_data_dir.mkdir(parents=True, exist_ok=True)

    # 1. Training Set
    gen_train = SyntheticTrafficGenerator(seed=42)
    train_events = gen_train.generate_dataset(normal_sessions_count=600, attack_ratio=0.25)
    train_path = base_data_dir / "train_traffic.csv"
    gen_train.export_to_csv(train_events, train_path)
    print(f"[*] Generated Train Dataset: {train_path} ({len(train_events)} packets)")

    # 2. Test Set
    gen_test = SyntheticTrafficGenerator(seed=999)
    test_events = gen_test.generate_dataset(normal_sessions_count=200, attack_ratio=0.30)
    test_path = base_data_dir / "test_traffic.csv"
    gen_test.export_to_csv(test_events, test_path)
    print(f"[*] Generated Test Dataset:  {test_path} ({len(test_events)} packets)")

    # 3. Zero-Day Unseen Evaluation Set
    gen_zeroday = SyntheticTrafficGenerator(seed=777)
    zeroday_events = gen_zeroday.generate_normal_session("norm_zd_1")
    zeroday_events.extend(generate_unseen_zero_day_traffic(gen_zeroday, count=50))
    zeroday_events.sort(key=lambda x: x.timestamp)
    zeroday_path = base_data_dir / "zero_day_traffic.csv"
    gen_zeroday.export_to_csv(zeroday_events, zeroday_path)
    print(f"[*] Generated Zero-Day Set:  {zeroday_path} ({len(zeroday_events)} packets)")

    # Print summary of training data
    loaded_train = DatasetLoader.load_csv(train_path)
    stats = DatasetLoader.get_summary_statistics(loaded_train)
    print("\n--- Training Dataset Statistical Summary ---")
    print(f"Total Sessions:       {stats['total_sessions']}")
    print(f"Total Packets:        {stats['total_packets']}")
    print(f"Normal Packets:       {stats['normal_packets']}")
    print(f"Anomalous Packets:    {stats['anomalous_packets']} ({stats['anomaly_rate_percent']}%)")
    print("Attack Breakdown:")
    for cat, cnt in stats["category_distribution"].items():
        print(f"  - {cat:22s}: {cnt}")
    print("=" * 65)


if __name__ == "__main__":
    main()
