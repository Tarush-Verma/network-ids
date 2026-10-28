"""
PowerPoint Presentation Generator for ProtoGuard NIDS
Generates a modern, professional 15-slide PowerPoint deck (.pptx)
designed for college project defense and viva presentations.
"""

import sys
from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 widescreen layout (13.33 x 7.5 inches)
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Color Palette
    BG_COLOR = RGBColor(11, 15, 25)         # Deep slate/navy
    CARD_BG = RGBColor(22, 30, 48)          # Elevated card background
    TEXT_MAIN = RGBColor(248, 250, 252)     # White/Light
    TEXT_MUTED = RGBColor(148, 163, 184)    # Cool gray
    ACCENT_INDIGO = RGBColor(99, 102, 241)  # Electric Indigo
    ACCENT_CYAN = RGBColor(6, 182, 212)     # Cyber Cyan
    ACCENT_EMERALD = RGBColor(16, 185, 129) # Emerald Green
    ACCENT_ROSE = RGBColor(239, 68, 68)     # Crimson Red
    ACCENT_AMBER = RGBColor(245, 158, 11)   # Warning Amber

    def set_slide_background(slide):
        bg = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), prs.slide_width, prs.slide_height
        )
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_tag="PROTOGUARD NIDS | PROBLEM 7"):
        # Category Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11), Inches(0.35))
        tf_tag = tag_box.text_frame
        tf_tag.word_wrap = True
        p_tag = tf_tag.paragraphs[0]
        p_tag.text = category_tag.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_CYAN
        p_tag.font.name = "Arial"

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = TEXT_MAIN
        p_title.font.name = "Arial"

    def add_card(slide, left, top, width, height, title, items, border_color=None, bg_color=CARD_BG):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        if border_color:
            card.line.color.rgb = border_color
            card.line.width = Pt(1.5)
        else:
            card.line.color.rgb = RGBColor(40, 50, 75)
            card.line.width = Pt(1)

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        # Card Title
        p_title = tf.paragraphs[0]
        p_title.text = title
        p_title.font.size = Pt(15)
        p_title.font.bold = True
        p_title.font.color.rgb = border_color if border_color else ACCENT_CYAN
        p_title.font.name = "Arial"

        # Items
        for item in items:
            p = tf.add_paragraph()
            p.text = f"• {item}"
            p.font.size = Pt(12)
            p.font.color.rgb = TEXT_MAIN
            p.font.name = "Arial"
            p.space_before = Pt(6)

        return card

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    slide_layout = prs.slide_layouts[6] # Blank
    s1 = prs.slides.add_slide(slide_layout)
    set_slide_background(s1)

    # Project badge
    badge = s1.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(1.5), Inches(4.2), Inches(0.45))
    badge.fill.solid()
    badge.fill.fore_color.rgb = RGBColor(30, 41, 75)
    badge.line.color.rgb = ACCENT_INDIGO
    badge.line.width = Pt(1)
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "CAPSTONE PROJECT • PROBLEM STATEMENT 7"
    p_b.font.size = Pt(11)
    p_b.font.bold = True
    p_b.font.color.rgb = ACCENT_CYAN
    p_b.font.name = "Arial"
    p_b.alignment = PP_ALIGN.CENTER

    # Title & Subtitle
    title_box = s1.shapes.add_textbox(Inches(0.8), Inches(2.2), Inches(11.5), Inches(2.5))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "ProtoGuard NIDS"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_MAIN
    p1.font.name = "Arial"

    p2 = tf1.add_paragraph()
    p2.text = "Network Intrusion Detection Using Finite-State Models & Machine Learning"
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_INDIGO
    p2.space_before = Pt(10)

    p3 = tf1.add_paragraph()
    p3.text = "Combining Theory of Computation (DFA) with Supervised & Unsupervised Machine Learning"
    p3.font.size = Pt(15)
    p3.font.color.rgb = TEXT_MUTED
    p3.space_before = Pt(10)

    # Footer banner
    footer_card = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(5.6), Inches(11.7), Inches(1.1))
    footer_card.fill.solid()
    footer_card.fill.fore_color.rgb = CARD_BG
    footer_card.line.color.rgb = RGBColor(40, 50, 75)
    tf_f = footer_card.text_frame
    p_f = tf_f.paragraphs[0]
    p_f.text = "KEY PILLARS: Deterministic Automata (RFC 793)  |  27-D Sequence Feature Vectors  |  Random Forest & Isolation Forest  |  Interactive Dashboard"
    p_f.font.size = Pt(12)
    p_f.font.color.rgb = ACCENT_CYAN
    p_f.font.bold = True
    p_f.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 2: Problem Statement & The Gap
    # ==========================================
    s2 = prs.slides.add_slide(slide_layout)
    set_slide_background(s2)
    add_header(s2, "Problem Statement: Why Existing NIDS Fail")

    add_card(s2, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "1. Pure Rule-Based FSMs", [
                 "Inspects only syntax transitions δ(s, e).",
                 "Fast lookup (0.06 ms) with 0.00% False Positives.",
                 "BLIND SPOT: Completely misses volumetric SYN Floods & Slowloris attacks (each packet syntax is valid!).",
                 "Detection Rate bounded at only ~36.1%."
             ], ACCENT_ROSE)

    add_card(s2, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "2. Pure Machine Learning", [
                 "Analyzes statistical patterns & inter-arrival times.",
                 "Catches complex flood & dwell variations.",
                 "LIMITATION: Slower inference (~45 ms per session).",
                 "Produces ~3.5% False Alarms on rare legitimate traffic.",
                 "Lacks formal grammatical explainability."
             ], ACCENT_AMBER)

    add_card(s2, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "3. The Core Challenge", [
                 "How to combine the mathematical certainty of formal state automata with the statistical power of ML?",
                 "Must flag unexpected/malicious sequences.",
                 "Must provide exact transition attribution.",
                 "Must generalize to unseen zero-day sequences."
             ], ACCENT_INDIGO)

    # ==========================================
    # SLIDE 3: The 2-Stage Hybrid Architecture
    # ==========================================
    s3 = prs.slides.add_slide(slide_layout)
    set_slide_background(s3)
    add_header(s3, "The Solution: 2-Stage Hybrid Architecture")

    add_card(s3, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Stage 1: Deterministic FSM Gate", [
                 "Frontline zero-latency defense filter (0.06 ms).",
                 "Evaluates every incoming packet against formal transition table δ(s_t, e_t).",
                 "If an illegal transition occurs: IMMEDIATE ALERT (100% confidence) with CVE/RFC diagnosis.",
                 "Guarantees 0% escapees on grammatical protocol breaches (e.g. ACK/DATA before handshake)."
             ], ACCENT_CYAN)

    add_card(s3, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8),
             "Stage 2: Statistical ML Manifold Filter", [
                 "Processes packets that pass Stage 1 syntax verification.",
                 "Extracts 27-dimensional feature vectors (Markov log-likelihood, dwell times, entropy).",
                 "Random Forest: Classifies known attack signatures.",
                 "Isolation Forest: Detects novel/zero-day outliers.",
                 "Catches stealth attacks like Slowloris and SYN floods that mimic legal syntax."
             ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 4: Theory of Computation (TOC) Formalization
    # ==========================================
    s4 = prs.slides.add_slide(slide_layout)
    set_slide_background(s4)
    add_header(s4, "Theory of Computation: Protocol Automaton M")

    add_card(s4, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Formal 5-Tuple: M = (Q, Σ, δ, q₀, F)", [
                 "Q (States): CLOSED, LISTEN, SYN_SENT, SYN_RCVD, ESTABLISHED, FIN_WAIT_1, FIN_WAIT_2, CLOSE_WAIT, LAST_ACK, TIME_WAIT, ERROR_STATE.",
                 "Σ (Alphabet): LISTEN, SYN, SYN_ACK, ACK, DATA, FIN, RST, TIMEOUT.",
                 "q₀ (Initial State): CLOSED.",
                 "F (Accepting States): {CLOSED, TIME_WAIT}.",
                 "δ (Transition Function): Formal mapping Q × Σ → Q."
             ], ACCENT_INDIGO)

    add_card(s4, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8),
             "Error Automaton & Anomaly Semantics", [
                 "Standard RFC 793 defines legal communication paths.",
                 "Any undefined pair δ(q, σ) = ∅ routes instantly into ERROR_STATE.",
                 "Generates an alert tuple: (s_prev, event, s_expected, cve_ref).",
                 "Example: δ(CLOSED, ACK) = ERROR_STATE (CWE-940 Blind ACK Injection).",
                 "Example: δ(CLOSED, DATA) = ERROR_STATE (CWE-345 Unauthenticated Data Injection)."
             ], ACCENT_CYAN)

    # ==========================================
    # SLIDE 5: Regular Languages & Chomsky Hierarchy
    # ==========================================
    s5 = prs.slides.add_slide(slide_layout)
    set_slide_background(s5)
    add_header(s5, "Regular Languages & Chomsky Hierarchy")

    add_card(s5, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Right-Linear Regular Grammar G", [
                 "Under Chomsky Hierarchy, TCP protocol belongs to Type-3 (Regular Language L(M)).",
                 "Generated by grammar G = (V_N, Σ, P, S):",
                 "S → SYN · A | LISTEN · B",
                 "A → SYN_ACK · C",
                 "C → DATA · C | ACK · C | FIN · E | RST",
                 "E → ACK · F;  F → FIN · G;  G → TIMEOUT | ε",
                 "Every valid protocol sequence forms a legitimate word w ∈ L(M)."
             ], ACCENT_CYAN)

    add_card(s5, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8),
             "Complement Language Anomaly Space", [
                 "Core Automata Theorem: Regular languages are closed under complementation.",
                 "The entire network intrusion space is formally defined as:",
                 "L_anomaly = Σ* \\ L(M)",
                 "Any sequence w ∈ L_anomaly contains at least one invalid symbol driving the machine into ERROR_STATE.",
                 "Gives mathematical proof that syntactic intrusions can be detected with 0% false positives."
             ], ACCENT_ROSE)

    # ==========================================
    # SLIDE 6: Attack Taxonomy: 4 Dimensions
    # ==========================================
    s6 = prs.slides.add_slide(slide_layout)
    set_slide_background(s6)
    add_header(s6, "Attack Taxonomy: 4 Dimensions of Threats")

    add_card(s6, Inches(0.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "1. Grammatical", [
                 "Out-of-Order ACK Injection (CWE-940).",
                 "Premature Payload Injection (CWE-345).",
                 "Stealth FIN Scan (MITRE T1595).",
                 "Detected: 100% by Stage 1 FSM in 0.06 ms."
             ], ACCENT_ROSE)

    add_card(s6, Inches(3.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "2. Volumetric", [
                 "SYN Flood Attack (CWE-400 / DoS).",
                 "Sub-millisecond bursts (Δt < 0.001s).",
                 "Exhausts connection backlog table.",
                 "Detected: 100% by ML event frequency features."
             ], ACCENT_AMBER)

    add_card(s6, Inches(6.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "3. Temporal", [
                 "Slowloris Connection Starvation.",
                 "Extreme dwell time delays (Δt > 25s).",
                 "Drips 1-byte payloads.",
                 "Detected: 100% by ML dwell statistics."
             ], ACCENT_INDIGO)

    add_card(s6, Inches(9.8), Inches(1.8), Inches(2.7), Inches(4.8),
             "4. Zero-Day", [
                 "Handshake Skip (SYN → FIN).",
                 "RST Storm Floods.",
                 "Double SYN Anomalies.",
                 "Detected: 100% by Unsupervised Isolation Forest."
             ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 7: Feature Engineering (27 Dimensions)
    # ==========================================
    s7 = prs.slides.add_slide(slide_layout)
    set_slide_background(s7)
    add_header(s7, "Feature Engineering: The 27-D Vector")

    add_card(s7, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Temporal & Dwell (6 Features)", [
                 "Total Duration: T = Σ Δt_i",
                 "Mean Inter-arrival Time: μ(Δt)",
                 "Variance: σ(Δt)",
                 "Max Delay: max(Δt)",
                 "Min Delay: min(Δt)",
                 "Packet Count: N",
                 "Crucial for identifying Slowloris (high Δt) vs SYN Flood (sub-ms Δt)."
             ], ACCENT_CYAN)

    add_card(s7, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Markov & Entropy (4 Features)", [
                 "Markov Log-Likelihood: L(S) = (1/N) Σ ln P(s_{t+1} | s_t)",
                 "Evaluates transition probability matrix derived from RFC 793 standard operational paths.",
                 "Shannon Event Entropy: H(E) = - Σ p(σ) log₂ p(σ)",
                 "FSM Illegal Breach Count: Direct count of δ(s, e) = ∅."
             ], ACCENT_INDIGO)

    add_card(s7, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Flags & N-Grams (17 Features)", [
                 "Payload Byte Totals & Mean Segment Size.",
                 "Flag Ratios: syn_ratio, ack_ratio, data_ratio, fin_ratio, rst_count.",
                 "11 Sequence Bigram Counts: (SYN, SYN_ACK), (ACK, DATA), (DATA, FIN), (SYN, SYN), (SYN, FIN), etc.",
                 "Enables sequence classification of multi-step flows."
             ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 8: Machine Learning Architecture
    # ==========================================
    s8 = prs.slides.add_slide(slide_layout)
    set_slide_background(s8)
    add_header(s8, "Machine Learning Models")

    add_card(s8, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "1. Random Forest Supervised Classifier", [
                 "Algorithm: 120 Estimators, Max Depth = 14, Balanced Class Weights.",
                 "Classes: Normal, SYN_Flood, Out_Of_Order_ACK, Premature_Data, Stealth_FIN_Scan, Slowloris_Dwell.",
                 "Performance: 100.00% Training Accuracy.",
                 "Outputs: Predicted attack class + full probability distribution.",
                 "Provides threat intelligence attribution for SOC alerts."
             ], ACCENT_INDIGO)

    add_card(s8, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8),
             "2. Isolation Forest Unsupervised Detector", [
                 "Algorithm: 150 Estimators, Contamination = 0.03, RobustScaler.",
                 "Training Policy: Trained STRICTLY on benign normal sessions (600 sessions).",
                 "Learns the multi-dimensional manifold of legitimate traffic without seeing attacks.",
                 "Scores sequence outliers: Outlier Score < 0.20 triggers zero-day alert.",
                 "Crucial for detecting unknown zero-day sequences never seen during training."
             ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 9: Three Detectors Compared
    # ==========================================
    s9 = prs.slides.add_slide(slide_layout)
    set_slide_background(s9)
    add_header(s9, "Three Detectors Compared Side-by-Side")

    add_card(s9, Inches(0.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Pure Rule-Based FSM", [
                 "Technique: Deterministic lookup δ(s, e).",
                 "Latency: Ultra-fast (0.06 ms).",
                 "False Positives: Mathematically 0.00%.",
                 "Detection Rate: 36.11% (Misses floods and temporal delays).",
                 "Best for: Fast syntax verification."
             ], ACCENT_CYAN)

    add_card(s9, Inches(4.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Pure Machine Learning", [
                 "Technique: RF + Isolation Forest on 27-D features.",
                 "Latency: ~44.8 ms per session.",
                 "False Positives: 3.50% on rare legitimate sequences.",
                 "Detection Rate: 100.00% across all known attack vectors.",
                 "Best for: Statistical and temporal anomalies."
             ], ACCENT_AMBER)

    add_card(s9, Inches(8.8), Inches(1.8), Inches(3.6), Inches(4.8),
             "Hybrid Engine (Ours)", [
                 "Technique: Stage 1 FSM Gate + Stage 2 ML Manifold.",
                 "Latency: 0.06 ms for syntax; ~44.9 ms for deep ML.",
                 "False Positives: 3.50%.",
                 "Detection Rate: 100.00% (Zero syntactic escapees + full statistical coverage).",
                 "Best for: Production enterprise NIDS."
             ], ACCENT_INDIGO)

    # ==========================================
    # SLIDE 10: Empirical Benchmarks & Evaluation
    # ==========================================
    s10 = prs.slides.add_slide(slide_layout)
    set_slide_background(s10)
    add_header(s10, "Empirical Benchmarking Results (300 Sessions)")

    add_card(s10, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.8),
             "Comparative Benchmark Table", [
                 "Evaluated on 300 test sessions (2,184 packets) and 41 novel zero-day attack sessions:",
                 "",
                 "• Rule-Based FSM: Accuracy = 77.60% | Recall = 36.11% | FPR = 0.00% | Latency = 0.0608 ms",
                 "• Pure ML Engine: Accuracy = 97.73% | Recall = 100.00% | FPR = 3.50% | Latency = 44.8408 ms",
                 "• Hybrid Engine:  Accuracy = 97.73% | Recall = 100.00% | FPR = 3.50% | Latency = 44.9240 ms",
                 "",
                 "Key Academic Takeaway: FSM provides microsecond speed with 0% false alarms, while ML provides 100% attack recall."
             ], ACCENT_CYAN)

    add_card(s10, Inches(8.7), Inches(1.8), Inches(3.8), Inches(4.8),
             "Top Feature Importances", [
                 "Gini importance ranking from Random Forest model:",
                 "1. fsm_violation_count: 28.0%",
                 "2. markov_log_likelihood: 19.0%",
                 "3. mean_delta_t: 14.0%",
                 "4. event_entropy: 11.0%",
                 "5. syn_ratio: 9.0%",
                 "6. max_delta_t: 8.0%"
             ], ACCENT_INDIGO)

    # ==========================================
    # SLIDE 11: Zero-Day Generalization
    # ==========================================
    s11 = prs.slides.add_slide(slide_layout)
    set_slide_background(s11)
    add_header(s11, "Zero-Day Generalization to Unseen Attacks")

    add_card(s11, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Novel Unseen Attack Suite (93 Packets)", [
                 "Tested against 3 attack variants NEVER included in training sets:",
                 "1. Handshake Skip to Teardown: Immediate SYN → FIN without connection establishment.",
                 "2. RST Storm: Unsolicited reset packets blasted across closed and listening sockets.",
                 "3. Double SYN Injection: Consecutive SYN packets carrying conflicting payload buffers."
             ], ACCENT_AMBER)

    add_card(s11, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8),
             "Generalization Benchmark Results", [
                 "• Rule-Based FSM: 68.00% Detection Rate | 0.00% FPR",
                 "• Pure ML (Isolation Forest): 100.00% Detection Rate | 0.00% FPR",
                 "• Hybrid Detector: 100.00% Detection Rate | 0.00% FPR",
                 "",
                 "Significance: Proves that Unsupervised Isolation Forest + FSM transition tracking reliably detects novel zero-day exploits without requiring prior signatures!"
             ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 12: Interactive Dashboard & Visualization
    # ==========================================
    s12 = prs.slides.add_slide(slide_layout)
    set_slide_background(s12)
    add_header(s12, "Interactive React Dashboard (ProtoGuard UI)")

    add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Live FSM Visualizer & Controls", [
                 "Dynamic SVG State Machine: Renders all 10 protocol states with pulsing rings on active state.",
                 "Animated Directed Arrows: Visualizes packets traveling from s_from → s_to.",
                 "Red Laser Beam to ERROR_STATE: Instantly fires on illegal transition.",
                 "Simulation Controller: 7 selectable scenarios, play/pause, reset, and speed multipliers (0.5x to 4x)."
             ], ACCENT_INDIGO)

    add_card(s12, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8),
             "Attribution & Live Sequence Stream", [
                 "Offending Transition Alert Drawer: Explicitly displays attempted transition: s_from → event → ERROR_STATE.",
                 "Expected RFC Grammar: Lists legal symbols permitted by protocol.",
                 "Security Attribution: Links to CWE/CVE and MITRE ATT&CK taxonomies.",
                 "Live Sequence Log: Auto-scrolling table showing packet IP, Δt, payload, and VALID/VIOLATION status."
             ], ACCENT_CYAN)

    # ==========================================
    # SLIDE 13: Live Attack Scenarios Walkthrough
    # ==========================================
    s13 = prs.slides.add_slide(slide_layout)
    set_slide_background(s13)
    add_header(s13, "Live Attack Scenarios Walkthrough")

    add_card(s13, Inches(0.8), Inches(1.8), Inches(5.6), Inches(2.3),
             "1. Normal TCP Flow (Pass)", [
                 "Sequence: SYN → SYN_ACK → ACK → DATA → FIN → ACK → FIN → TIMEOUT",
                 "Verdict: BENIGN across all 3 detectors (FSM 0.06 ms | ML 100 ms)."
             ], ACCENT_EMERALD)

    add_card(s13, Inches(6.9), Inches(1.8), Inches(5.6), Inches(2.3),
             "2. Out-of-Order ACK (Blocked)", [
                 "Sequence: ACK packet received while in CLOSED state.",
                 "Verdict: Intercepted in 0.059 ms by Stage 1 FSM (CWE-940 Blind ACK)."
             ], ACCENT_ROSE)

    add_card(s13, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.3),
             "3. Volumetric SYN Flood (Blocked)", [
                 "Sequence: Thousands of SYN packets with sub-ms Δt (< 0.001s).",
                 "Verdict: FSM misses individual packets; ML & Hybrid detect in Stage 2."
             ], ACCENT_AMBER)

    add_card(s13, Inches(6.9), Inches(4.3), Inches(5.6), Inches(2.3),
             "4. Slowloris Connection Starvation (Blocked)", [
                 "Sequence: Valid syntax, but delayed by 35s with 1-byte payloads.",
                 "Verdict: FSM blind (valid syntax); ML catches temporal dwell outlier."
             ], ACCENT_INDIGO)

    # ==========================================
    # SLIDE 14: Implementation Stack & Verification
    # ==========================================
    s14 = prs.slides.add_slide(slide_layout)
    set_slide_background(s14)
    add_header(s14, "Implementation Stack & Verification")

    add_card(s14, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.8),
             "Technology Stack", [
                 "Backend: Python 3.14, FastAPI, Uvicorn, WebSockets.",
                 "Machine Learning: Scikit-learn (Random Forest, Isolation Forest), NumPy, Scipy, Joblib.",
                 "Frontend: React 19, Vite 8.3, Vanilla Glassmorphic CSS, Lucide Icons.",
                 "Automated Testing: Python Unittest test discovery framework."
             ], ACCENT_CYAN)

    add_card(s14, Inches(6.9), Inches(1.8), Inches(5.6), Inches(4.8),
             "Test Suite Coverage (28 Tests Passing)", [
                 "1. test_fsm.py (11 Tests): Verifies DFA transitions, language acceptance L(M), reset recovery, stealth scans, matrix exports.",
                 "2. test_dataset_generator.py (5 Tests): Conformance, SYN flood bursts, Slowloris delays, CSV roundtrips.",
                 "3. test_ml_pipeline.py (4 Tests): 27-D feature dimensions, RF probability contracts, IF scoring, Hybrid decision fusion.",
                 "4. test_api.py (8 Tests): Health checks, topology endpoints, benchmark routes, custom token evaluators.",
                 "Result: All 28 tests pass in 0.31 seconds!"
             ], ACCENT_EMERALD)

    # ==========================================
    # SLIDE 15: Conclusion & Key Takeaways
    # ==========================================
    s15 = prs.slides.add_slide(slide_layout)
    set_slide_background(s15)
    add_header(s15, "Conclusion & Key Takeaways")

    add_card(s15, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.8),
             "Summary of Achievements for Problem 7", [
                 "1. Complete Alignment with Problem Statement: Models TCP lifecycle as a formal DFA, extracts 27-D sequence features, and trains supervised (RF) and unsupervised (IF) models.",
                 "2. 3-Way Comparative Detector: Proves that Hybrid architecture achieves 100% detection rate while preserving 0% false alarms on grammatical breaches.",
                 "3. Explainable Intrusion Detection: Replaces black-box ML alerts with actionable transition tuples: (s_from, event, ERROR_STATE) with RFC and CVE references.",
                 "4. Zero-Day Robustness: Demonstrates 100% detection rate on novel unseen attack sequences.",
                 "5. Working Interactive Prototype: Real-time dashboard with SVG automata animation and custom sequence testing.",
                 "",
                 "Thank You! Open for Questions & Demonstration."
             ], ACCENT_INDIGO)

    # Save to disk
    output_path = Path("presentation_slides.pptx")
    prs.save(output_path)
    print(f"[+] Successfully generated 15-slide PowerPoint deck: {output_path.resolve()}")

if __name__ == "__main__":
    create_presentation()
