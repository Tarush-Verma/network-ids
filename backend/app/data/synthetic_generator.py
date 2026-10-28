"""
Synthetic Protocol Event & Attack Traffic Generator
Simulates realistic protocol traffic consisting of normal communication flows
and specialized network attack vectors for intrusion detection benchmarking.
"""

import random
import time
import uuid
import csv
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

from backend.app.core.fsm import ProtocolState, EventType, ProtocolFSM


@dataclass
class NetworkPacketEvent:
    session_id: str
    seq_index: int
    timestamp: float
    delta_t: float
    src_ip: str
    dst_ip: str
    src_port: int
    dst_port: int
    event_type: str
    current_state: str
    next_state: str
    payload_size: int
    flags: List[str]
    is_anomaly: int  # 0 = Normal, 1 = Anomaly
    attack_category: str  # 'Normal', 'SYN_Flood', 'Out_Of_Order_ACK', etc.
    violation_type: Optional[str] = None  # Grammatical vs Statistical vs Temporal


class SyntheticTrafficGenerator:
    """
    Generates synthetic protocol event sequences representing normal TCP/session
    traffic alongside realistic network intrusion attack vectors.
    """

    def __init__(self, seed: Optional[int] = 42):
        if seed is not None:
            random.seed(seed)
        self.fsm = ProtocolFSM()

        self.normal_src_ips = [f"192.168.1.{i}" for i in range(10, 50)]
        self.attacker_ips = [f"10.0.0.{i}" for i in range(100, 115)]
        self.server_ip = "192.168.1.1"
        self.server_port = 8080

    def generate_normal_session(self, session_id: Optional[str] = None) -> List[NetworkPacketEvent]:
        """
        Generates a completely valid, legitimate communication session:
        3-way handshake -> Data payloads (with standard deltas) -> Graceful 4-way teardown.
        """
        session_id = session_id or str(uuid.uuid4())[:8]
        src_ip = random.choice(self.normal_src_ips)
        src_port = random.randint(30000, 65000)
        curr_time = time.time() - random.uniform(100, 1000)
        events: List[NetworkPacketEvent] = []

        # Sequence of normal operations
        # 1. SYN
        delta = random.uniform(0.001, 0.010)
        curr_time += delta
        events.append(NetworkPacketEvent(
            session_id=session_id,
            seq_index=0,
            timestamp=curr_time,
            delta_t=delta,
            src_ip=src_ip,
            dst_ip=self.server_ip,
            src_port=src_port,
            dst_port=self.server_port,
            event_type=EventType.SYN.value,
            current_state=ProtocolState.CLOSED.value,
            next_state=ProtocolState.SYN_SENT.value,
            payload_size=0,
            flags=["SYN"],
            is_anomaly=0,
            attack_category="Normal",
        ))

        # 2. SYN-ACK (Server response)
        delta = random.uniform(0.005, 0.025)
        curr_time += delta
        events.append(NetworkPacketEvent(
            session_id=session_id,
            seq_index=1,
            timestamp=curr_time,
            delta_t=delta,
            src_ip=self.server_ip,
            dst_ip=src_ip,
            src_port=self.server_port,
            dst_port=src_port,
            event_type=EventType.SYN_ACK.value,
            current_state=ProtocolState.SYN_SENT.value,
            next_state=ProtocolState.ESTABLISHED.value,
            payload_size=0,
            flags=["SYN", "ACK"],
            is_anomaly=0,
            attack_category="Normal",
        ))

        # 3. Data exchange transfers (1 to 6 packets)
        data_packets_count = random.randint(2, 6)
        curr_state = ProtocolState.ESTABLISHED.value
        for i in range(data_packets_count):
            delta = random.uniform(0.010, 0.080)
            curr_time += delta
            is_client_send = (i % 2 == 0)
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=len(events),
                timestamp=curr_time,
                delta_t=delta,
                src_ip=src_ip if is_client_send else self.server_ip,
                dst_ip=self.server_ip if is_client_send else src_ip,
                src_port=src_port if is_client_send else self.server_port,
                dst_port=self.server_port if is_client_send else src_port,
                event_type=EventType.DATA.value,
                current_state=curr_state,
                next_state=curr_state,
                payload_size=random.randint(64, 1460),
                flags=["PSH", "ACK"],
                is_anomaly=0,
                attack_category="Normal",
            ))

        # 4. Graceful Teardown: FIN -> ACK -> FIN -> TIMEOUT
        teardown_steps = [
            (EventType.FIN.value, ProtocolState.ESTABLISHED.value, ProtocolState.FIN_WAIT_1.value, ["FIN", "ACK"]),
            (EventType.ACK.value, ProtocolState.FIN_WAIT_1.value, ProtocolState.FIN_WAIT_2.value, ["ACK"]),
            (EventType.FIN.value, ProtocolState.FIN_WAIT_2.value, ProtocolState.TIME_WAIT.value, ["FIN", "ACK"]),
            (EventType.TIMEOUT.value, ProtocolState.TIME_WAIT.value, ProtocolState.CLOSED.value, []),
        ]

        for ev_type, s_from, s_to, flags in teardown_steps:
            delta = random.uniform(0.005, 0.050)
            curr_time += delta
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=len(events),
                timestamp=curr_time,
                delta_t=delta,
                src_ip=src_ip,
                dst_ip=self.server_ip,
                src_port=src_port,
                dst_port=self.server_port,
                event_type=ev_type,
                current_state=s_from,
                next_state=s_to,
                payload_size=0,
                flags=flags,
                is_anomaly=0,
                attack_category="Normal",
            ))

        return events

    def generate_syn_flood_attack(self, burst_size: int = 5) -> List[NetworkPacketEvent]:
        """
        Attack 1: SYN Flood (Denial of Service).
        High-frequency burst of SYN packets from spoofed IPs without sending final ACKs.
        Grammatically valid individually, but statistically / transitionally anomalous.
        """
        session_id = f"atk_syn_{uuid.uuid4().hex[:6]}"
        attacker_ip = random.choice(self.attacker_ips)
        curr_time = time.time()
        events = []

        for i in range(burst_size):
            # Extremely fast inter-arrival times (< 1 millisecond)
            delta = random.uniform(0.0001, 0.0008)
            curr_time += delta
            events.append(NetworkPacketEvent(
                session_id=f"{session_id}_{i}",
                seq_index=i,
                timestamp=curr_time,
                delta_t=delta,
                src_ip=attacker_ip,
                dst_ip=self.server_ip,
                src_port=random.randint(40000, 65000),
                dst_port=self.server_port,
                event_type=EventType.SYN.value,
                current_state=ProtocolState.CLOSED.value,
                next_state=ProtocolState.SYN_SENT.value,
                payload_size=0,
                flags=["SYN"],
                is_anomaly=1,
                attack_category="SYN_Flood",
                violation_type="STATISTICAL_FREQUENCY_ANOMALY",
            ))

        return events

    def generate_out_of_order_ack_attack(self) -> List[NetworkPacketEvent]:
        """
        Attack 2: Blind Out-of-Order ACK Injection.
        Strict FSM Grammar Violation: ACK packet received while socket is in CLOSED state.
        """
        session_id = f"atk_ack_{uuid.uuid4().hex[:6]}"
        attacker_ip = random.choice(self.attacker_ips)
        curr_time = time.time()
        delta = random.uniform(0.01, 0.05)

        return [
            NetworkPacketEvent(
                session_id=session_id,
                seq_index=0,
                timestamp=curr_time + delta,
                delta_t=delta,
                src_ip=attacker_ip,
                dst_ip=self.server_ip,
                src_port=random.randint(35000, 60000),
                dst_port=self.server_port,
                event_type=EventType.ACK.value,
                current_state=ProtocolState.CLOSED.value,
                next_state=ProtocolState.ERROR_STATE.value,
                payload_size=0,
                flags=["ACK"],
                is_anomaly=1,
                attack_category="Out_Of_Order_ACK",
                violation_type="FSM_GRAMMAR_VIOLATION",
            )
        ]

    def generate_premature_data_attack(self) -> List[NetworkPacketEvent]:
        """
        Attack 3: Premature Payload Injection.
        Strict FSM Grammar Violation: DATA payload injected into closed socket without handshake.
        """
        session_id = f"atk_data_{uuid.uuid4().hex[:6]}"
        attacker_ip = random.choice(self.attacker_ips)
        curr_time = time.time()
        delta = random.uniform(0.01, 0.05)

        return [
            NetworkPacketEvent(
                session_id=session_id,
                seq_index=0,
                timestamp=curr_time + delta,
                delta_t=delta,
                src_ip=attacker_ip,
                dst_ip=self.server_ip,
                src_port=random.randint(35000, 60000),
                dst_port=self.server_port,
                event_type=EventType.DATA.value,
                current_state=ProtocolState.CLOSED.value,
                next_state=ProtocolState.ERROR_STATE.value,
                payload_size=random.randint(128, 1024),
                flags=["PSH", "ACK"],
                is_anomaly=1,
                attack_category="Premature_Data",
                violation_type="FSM_GRAMMAR_VIOLATION",
            )
        ]

    def generate_stealth_fin_scan(self) -> List[NetworkPacketEvent]:
        """
        Attack 4: Stealth FIN Port Scan (Nmap style).
        Strict FSM Grammar Violation: Solitary FIN packet sent to closed port to deduce firewall rules.
        """
        session_id = f"atk_fin_{uuid.uuid4().hex[:6]}"
        attacker_ip = random.choice(self.attacker_ips)
        curr_time = time.time()
        delta = random.uniform(0.02, 0.10)

        return [
            NetworkPacketEvent(
                session_id=session_id,
                seq_index=0,
                timestamp=curr_time + delta,
                delta_t=delta,
                src_ip=attacker_ip,
                dst_ip=self.server_ip,
                src_port=random.randint(35000, 60000),
                dst_port=self.server_port,
                event_type=EventType.FIN.value,
                current_state=ProtocolState.CLOSED.value,
                next_state=ProtocolState.ERROR_STATE.value,
                payload_size=0,
                flags=["FIN"],
                is_anomaly=1,
                attack_category="Stealth_FIN_Scan",
                violation_type="FSM_GRAMMAR_VIOLATION",
            )
        ]

    def generate_slowloris_attack(self) -> List[NetworkPacketEvent]:
        """
        Attack 5: Slowloris State Dwell Anomaly.
        Grammatically valid handshake and transitions, but inter-arrival times
        are orders of magnitude higher (15 - 45 seconds) to hold server sockets open indefinitely.
        Fails pure FSM (it's syntactically valid), but caught by ML temporal features!
        """
        session_id = f"atk_slow_{uuid.uuid4().hex[:6]}"
        attacker_ip = random.choice(self.attacker_ips)
        curr_time = time.time() - 300
        events = []

        # Handshake
        delta = random.uniform(0.01, 0.05)
        curr_time += delta
        events.append(NetworkPacketEvent(
            session_id=session_id,
            seq_index=0,
            timestamp=curr_time,
            delta_t=delta,
            src_ip=attacker_ip,
            dst_ip=self.server_ip,
            src_port=random.randint(35000, 60000),
            dst_port=self.server_port,
            event_type=EventType.SYN.value,
            current_state=ProtocolState.CLOSED.value,
            next_state=ProtocolState.SYN_SENT.value,
            payload_size=0,
            flags=["SYN"],
            is_anomaly=1,
            attack_category="Slowloris_Dwell",
            violation_type="TEMPORAL_DWELL_ANOMALY",
        ))

        delta = random.uniform(0.01, 0.05)
        curr_time += delta
        events.append(NetworkPacketEvent(
            session_id=session_id,
            seq_index=1,
            timestamp=curr_time,
            delta_t=delta,
            src_ip=self.server_ip,
            dst_ip=attacker_ip,
            src_port=self.server_port,
            dst_port=events[0].src_port,
            event_type=EventType.SYN_ACK.value,
            current_state=ProtocolState.SYN_SENT.value,
            next_state=ProtocolState.ESTABLISHED.value,
            payload_size=0,
            flags=["SYN", "ACK"],
            is_anomaly=1,
            attack_category="Slowloris_Dwell",
            violation_type="TEMPORAL_DWELL_ANOMALY",
        ))

        # Slowloris drip: Tiny byte packets sent every 20-40 seconds
        for i in range(3):
            abnormal_delta = random.uniform(20.0, 45.0)  # Huge stall
            curr_time += abnormal_delta
            events.append(NetworkPacketEvent(
                session_id=session_id,
                seq_index=len(events),
                timestamp=curr_time,
                delta_t=abnormal_delta,
                src_ip=attacker_ip,
                dst_ip=self.server_ip,
                src_port=events[0].src_port,
                dst_port=self.server_port,
                event_type=EventType.DATA.value,
                current_state=ProtocolState.ESTABLISHED.value,
                next_state=ProtocolState.ESTABLISHED.value,
                payload_size=random.randint(1, 10),  # Tiny payload drip
                flags=["PSH", "ACK"],
                is_anomaly=1,
                attack_category="Slowloris_Dwell",
                violation_type="TEMPORAL_DWELL_ANOMALY",
            ))

        return events

    def generate_dataset(
        self,
        normal_sessions_count: int = 500,
        attack_ratio: float = 0.25,
    ) -> List[NetworkPacketEvent]:
        """
        Compiles a complete benchmark dataset with balanced/imbalanced distributions
        of normal and diverse attack vectors.
        """
        dataset: List[NetworkPacketEvent] = []

        # Generate normal sessions
        for i in range(normal_sessions_count):
            dataset.extend(self.generate_normal_session(f"norm_{i:04d}"))

        total_attack_sessions = int(normal_sessions_count * attack_ratio)

        attack_generators = [
            (self.generate_out_of_order_ack_attack, 0.25),
            (self.generate_premature_data_attack, 0.20),
            (self.generate_stealth_fin_scan, 0.20),
            (self.generate_syn_flood_attack, 0.20),
            (self.generate_slowloris_attack, 0.15),
        ]

        for gen_fn, weight in attack_generators:
            count = max(1, int(total_attack_sessions * weight))
            for _ in range(count):
                dataset.extend(gen_fn())

        # Sort dataset chronologically by timestamp
        dataset.sort(key=lambda pkt: pkt.timestamp)
        return dataset

    def export_to_csv(self, events: List[NetworkPacketEvent], file_path: Path):
        """Exports the generated packet events to a CSV file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if not events:
            return

        with open(file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "session_id", "seq_index", "timestamp", "delta_t",
                "src_ip", "dst_ip", "src_port", "dst_port",
                "event_type", "current_state", "next_state",
                "payload_size", "flags", "is_anomaly", "attack_category", "violation_type"
            ])
            writer.writeheader()
            for ev in events:
                row = asdict(ev)
                row["flags"] = "|".join(row["flags"])
                writer.writerow(row)

    def export_to_json(self, events: List[NetworkPacketEvent], file_path: Path):
        """Exports the generated packet events to a JSON file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, mode="w", encoding="utf-8") as f:
            json.dump([asdict(ev) for ev in events], f, indent=2)
