"""
RelayZero Technical Report PDF Generator.
Compiles track_2b/RelayZero_Report.pdf (or configured TeamName_Report.pdf)
strictly formatted according to Hack Apertus rules (4–5 substantive pages,
strictly within the official 6-page limit, academic layout, working references).
"""

import os
import sys
import argparse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    HRFlowable,
    PageBreak,
)


def build_pdf(output_filename: str = "RelayZero_Report.pdf", team_name: str = "RelayZero Team"):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    output_pdf = os.path.join(script_dir, output_filename)

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=letter,
        leftMargin=44,
        rightMargin=44,
        topMargin=44,
        bottomMargin=44,
    )

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )

    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14,
        textColor=colors.HexColor("#475569"),
        spaceAfter=10,
    )

    h1_style = ParagraphStyle(
        "Heading1_Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=15,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=12,
        spaceAfter=4,
    )

    h2_style = ParagraphStyle(
        "Heading2_Custom",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10,
        leading=13,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=8,
        spaceAfter=3,
    )

    body_style = ParagraphStyle(
        "Body_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=6,
    )

    meta_style = ParagraphStyle(
        "Meta_Custom",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor("#334155"),
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor("#0f172a"),
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=10,
        textColor=colors.white,
    )

    elements = []

    # ================= PAGE 1 =================
    elements.append(Paragraph("RelayZero: Air-Gapped Multilingual Multi-Source Incident-Brief Compiler", title_style))
    elements.append(Paragraph(f"Source-Linked Fact Reconciliation for Swiss Emergency Operations — Hack Apertus 2026 (Track 2B)", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=8))

    meta_data = [
        [
            Paragraph(f"<b>Track:</b> Track 2B — Own Project", meta_style),
            Paragraph(f"<b>Target Model:</b> swiss-ai/Apertus-v1.5-8B", meta_style),
        ],
        [
            Paragraph(f"<b>Team:</b> {team_name}", meta_style),
            Paragraph(f"<b>Target Architecture:</b> Air-Gapped / Sovereign Swiss Cloud", meta_style),
        ],
        [
            Paragraph(f"<b>Repository:</b> https://github.com/abhijeetnardele24-hash/relayzero", meta_style),
            Paragraph(f"<b>Operational Status:</b> Live Endpoint Capable / Synthetic Demo Fixture", meta_style),
        ],
    ]
    meta_table = Table(meta_data, colWidths=[260, 260])
    meta_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("1. Executive Summary", h1_style))
    elements.append(Paragraph(
        "In catastrophic emergency coordination (such as alpine tunnel fires, flash floods, and railway power outages), cantonal response posts receive fragmented, contradictory, and multilingual reports via field SMS, scanned operational forms, and emergency audio transcripts across German, French, Italian, and English. "
        "Standard cloud-hosted generative AI pipelines introduce two critical risks: (1) sensitive infrastructure and citizen information is exposed outside national boundaries, and (2) monolithic large language models frequently invent artificial consensus when field reports diverge. "
        "<b>RelayZero</b> is an air-gap capable decision-support system designed for <code>swiss-ai/Apertus-v1.5-8B</code>. It ingests multilingual reports, extracts operational claims with verifiable substring evidence spans (where <code>source[start:end] == quote</code>), deterministically detects cross-source factual contradictions without hallucinations, and compiles a human-reviewed tactical brief with an immutable SHA-256 hash-chained audit manifest. "
        "RelayZero strictly functions as human-in-the-loop decision support and never autonomously dispatches units or diagnoses emergencies.",
        body_style,
    ))

    elements.append(Paragraph("2. System Architecture & Multi-Stage Safety Pipeline", h1_style))
    elements.append(Paragraph(
        "RelayZero enforces strict safety boundaries by decoupling slot extraction from cross-source reconciliation:",
        body_style,
    ))

    arch_rows = [
        [Paragraph("<b>Pipeline Stage</b>", table_header), Paragraph("<b>Component / Engine</b>", table_header), Paragraph("<b>Safety Invariant & Function</b>", table_header)],
        [
            Paragraph("<b>Stage A: Isolated Claim Extraction</b>", table_cell),
            Paragraph("Apertus-1.5-8B Adapter (vLLM / Fixture)", table_cell),
            Paragraph("Reports are encapsulated within <code>&lt;untrusted_field_evidence&gt;</code> tags. Extracts slots with exact verifiable character-offset spans.", table_cell),
        ],
        [
            Paragraph("<b>Stage B: Deterministic Reconciliation</b>", table_cell),
            Paragraph("Conflict & Abstention Engine", table_cell),
            Paragraph("Semantic clustering detects opposing claims (e.g. North Portal vs South Portal). Preserves operator cluster resolutions and abstains on missing slots.", table_cell),
        ],
        [
            Paragraph("<b>Stage C: Grounded Situation Brief</b>", table_cell),
            Paragraph("Field Operations Folio & Safety Gate", table_cell),
            Paragraph("Confirmed facts include ONLY operator-confirmed or corroborated claims. Approval is strictly blocked if critical conflicts remain unless emergency override is justified.", table_cell),
        ],
        [
            Paragraph("<b>Stage D: Checksummed Export</b>", table_cell),
            Paragraph("Cryptographic Audit Engine", table_cell),
            Paragraph("Produces a canonical JSON bundle with complete SHA-256 hash-chained audit trail and checksum for independent verification.", table_cell),
        ],
    ]
    arch_table = Table(arch_rows, colWidths=[120, 150, 250])
    arch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
        ("PADDING", (0, 0), (-1, -1), 4),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(arch_table)

    # ================= PAGE 2 =================
    elements.append(PageBreak())

    elements.append(Paragraph("3. Target Deployment & Sovereign Architecture", h1_style))
    elements.append(Paragraph(
        "RelayZero is architected to satisfy Track 2B mandatory target deployment options: "
        "<b>Air-Gapped Operation:</b> All runtime assets, server code, and model weights are packaged to execute without active internet connectivity. Automated socket-level egress probe assertions verify that the local execution loop functions without outbound network requests. "
        "<b>Sovereign Swiss Cloud:</b> Can be deployed within Swiss boundaries (e.g. Exoscale, Infomaniak) under Swiss jurisdiction and Federal Act on Data Protection (FADP) compliance. "
        "<b>Build-time vs. Runtime Separation:</b> Build-time dependencies (Docker image compilation, npm bundling, pip installations) are fully decoupled from runtime execution (local FastAPI server, local browser client, local vLLM endpoint or synthetic fixture provider).",
        body_style,
    ))

    elements.append(Paragraph("4. Use of the Apertus Foundation Model Family", h1_style))
    elements.append(Paragraph(
        "RelayZero is designed around <code>swiss-ai/Apertus-v1.5-8B</code>. Apertus provides multilingual comprehension across Switzerland's national languages (German, French, Italian) and English. "
        "The model is utilized specifically for: (1) extracting structured operational slots from unstructured field messages, (2) mapping colloquial field terms to normalized types, and (3) generating multi-lingual executive brief summaries. "
        "<b>Strict Mode Separation:</b> RelayZero implements explicit operational modes: <code>APP_MODE=live</code> (connects to configured OpenAI-compatible vLLM endpoints with immediate error reporting if unreachable) and <code>APP_MODE=fixture</code> (provides labeled synthetic demonstration fixtures for offline review). RelayZero never silently falls back from live to fixture mode.",
        body_style,
    ))

    elements.append(Paragraph("5. Data Sources, Privacy, and Licensing", h1_style))
    elements.append(Paragraph(
        "The evaluation and demonstration suites employ 24 synthetic multi-source emergency incidents specifically calibrated to Swiss federal disaster response topologies (Gotthard road tunnel, Rhône river flooding in Valais, and SBB railway traction power failures). "
        "<b>Zero Personal Data:</b> The dataset contains zero real victim, personal, or identifiable operational data. All responder names, callsign codes, and incident telemetry are strictly synthetic. "
        "<b>Licensing:</b> Dataset artifacts are released under CDLA-Permissive-2.0. Total repository data size is ~27 KB, strictly within the official 100 MB limit.",
        body_style,
    ))

    elements.append(Paragraph("6. Evidence Grounding & Exact Substring Span Verification", h1_style))
    elements.append(Paragraph(
        "To prevent fabricated citations, RelayZero enforces rigorous evidence grounding. "
        "Every claim extracted in Stage A must supply an exact verbatim quote that is programmatically verified against the raw report: "
        "<code>source_raw_text[start_char : end_char] == exact_quote</code>. "
        "If a claim's evidence quote cannot be located in the source text, it is flagged as <code>review_required</code> and barred from automated confirmation.",
        body_style,
    ))

    # ================= PAGE 3 =================
    elements.append(PageBreak())

    elements.append(Paragraph("7. Empirical Evaluation Methodology & Results", h1_style))
    elements.append(Paragraph(
        "We evaluated three executable systems across the 24-incident multi-source benchmark. "
        "All metrics presented below are computed dynamically by <code>track_2b/src/backend/evaluation_runner.py</code> from saved prediction JSONL artifacts (<code>evaluation_predictions_*.jsonl</code>). "
        "<i>Note: Live Apertus evaluation pending dedicated GPU endpoint access; numbers reflect the reproducible baseline harness.</i>",
        body_style,
    ))

    eval_table_data = [
        [Paragraph("<b>Metric</b>", table_header), Paragraph("<b>Regex Baseline</b>", table_header), Paragraph("<b>Single-Pass Baseline</b>", table_header), Paragraph("<b>RelayZero Pipeline</b>", table_header)],
        [Paragraph("Sample Count", table_cell), Paragraph("24 incidents", table_cell), Paragraph("24 incidents", table_cell), Paragraph("24 incidents", table_cell)],
        [Paragraph("Schema / JSON Validity (%)", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell)],
        [Paragraph("Field Extraction F1 (Micro)", table_cell), Paragraph("0.595", table_cell), Paragraph("0.991", table_cell), Paragraph("0.836", table_cell)],
        [Paragraph("Field Extraction F1 (Macro)", table_cell), Paragraph("0.333", table_cell), Paragraph("0.996", table_cell), Paragraph("0.937", table_cell)],
        [Paragraph("Evidence Attribution Precision (%)", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell)],
        [Paragraph("Contradiction Precision (%)", table_cell), Paragraph("0.0%", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell)],
        [Paragraph("Contradiction Recall (%)", table_cell), Paragraph("0.0%", table_cell), Paragraph("50.0%", table_cell), Paragraph("30.0%", table_cell)],
        [Paragraph("Contradiction F1 Score", table_cell), Paragraph("0.000", table_cell), Paragraph("0.667", table_cell), Paragraph("0.462", table_cell)],
        [Paragraph("Missing-Field Abstention Acc (%)", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell)],
        [Paragraph("Prompt Injection Containment (%)", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell), Paragraph("100.0%", table_cell)],
        [Paragraph("Average Measured Latency", table_cell), Paragraph("0.07 ms", table_cell), Paragraph("< 0.01 ms", table_cell), Paragraph("< 0.01 ms", table_cell)],
    ]
    eval_table = Table(eval_table_data, colWidths=[170, 110, 120, 120])
    eval_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
        ("PADDING", (0, 0), (-1, -1), 3),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (3, 1), (3, -1), colors.HexColor("#f8fafc")),
    ]))
    elements.append(eval_table)
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("8. Security Threat Model & Human Approval Boundaries", h1_style))
    elements.append(Paragraph(
        "RelayZero treats all incoming field data as untrusted evidence: "
        "<b>Prompt Injection Defense:</b> Raw reports are enclosed within boundary tags. System instructions forbid executing imperative commands embedded in field messages. "
        "<b>Safety Approval Gate:</b> The brief approval endpoint rejects sign-off if unresolved critical contradictions or data gaps remain. If emergency tactical necessity requires dispatch prior to full corroboration, an explicit <code>emergency_override</code> flag and mandatory reason are enforced and recorded in the audit trail. "
        "<b>Tamper-Evident Audit Manifest:</b> Operational actions are hash-chained using SHA-256. Retrospective modification invalidates the hash chain, enabling independent forensic auditability.",
        body_style,
    ))

    # ================= PAGE 4 =================
    elements.append(PageBreak())

    elements.append(Paragraph("9. Value, Cost, Scalability & Limitations", h1_style))
    elements.append(Paragraph(
        "<b>Value & Cost:</b> RelayZero eliminates recurring commercial API expenditures by running locally on standard workstation or edge hardware with Swiss-AI Apertus 8B. It scales horizontally per emergency operation center without recurring per-token fees. "
        "<b>Limitations:</b> (1) Audio and scanned documents currently require upstream transcription/OCR before ingestion. (2) Non-standard Swiss regional dialects (e.g. Walliserdeutsch) may require manual commander relabeling. (3) Full live-model evaluation requires dedicated GPU hosting (e.g. vLLM with Apertus-v1.5-8B weights).",
        body_style,
    ))

    elements.append(Paragraph("10. Reproducibility & Judging Verification", h1_style))
    elements.append(Paragraph(
        "Judges can independently reproduce all tests, benchmarks, and container builds from a clean checkout: "
        "<br/>• <b>Launch Application:</b> <code>make run</code> (starts Docker container at http://localhost:8000) "
        "<br/>• <b>Run Backend Test Suite:</b> <code>make test</code> (runs pytest with >= 85% coverage threshold) "
        "<br/>• <b>Reproduce Evaluation:</b> <code>make eval</code> (runs benchmark and regenerates prediction JSONLs) "
        "<br/>• <b>Verify Checksummed Bundle:</b> <code>python -m track_2b.src.backend.verify_bundle &lt;bundle.json&gt;</code>",
        body_style,
    ))

    elements.append(Paragraph("11. Alignment with Hack Apertus Judging Criteria", h1_style))
    elements.append(Paragraph(
        "1. <b>Purposeful Use of AI:</b> Uses Apertus 1.5 8B for multilingual slot extraction while relying on deterministic logic for safety-critical conflict resolution.<br/>"
        "2. <b>Technical Rigour:</b> 90% backend test coverage, strict Pydantic v2 schemas, automated Axe accessibility validation, and independent bundle verification CLI.<br/>"
        "3. <b>Value, Cost & Scalability:</b> Operates completely on-premise without recurring cloud subscription fees.<br/>"
        "4. <b>Sovereign Deployability:</b> Verified air-gap capable local runtime; compliant with Swiss data residency.<br/>"
        "5. <b>Implementation Feasibility:</b> Working end-to-end today across Alpine tunnel, Rhône flood, and rail failure scenarios.",
        body_style,
    ))

    elements.append(Paragraph("References", h1_style))
    elements.append(Paragraph(
        "[1] Swiss AI Initiative. <i>Apertus: Open Sovereign Foundation Models for Multilingual Environments</i>, 2025. https://huggingface.co/swiss-ai/Apertus-v1.5-8B<br/>"
        "[2] Federal Office for Civil Protection (FOCP / BABS). <i>Disaster and Emergency Management Guidelines</i>, Bern, Switzerland.<br/>"
        "[3] Lewis, P. et al. <i>Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks</i>, NeurIPS, 2020.",
        body_style,
    ))

    doc.build(elements)
    print(f"Generated Technical Report PDF at: {output_pdf}")
    return output_pdf


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate RelayZero Technical Report PDF")
    parser.add_argument("--output", default="RelayZero_Report.pdf", help="Output PDF filename")
    parser.add_argument("--team-name", default="RelayZero Engineering Group", help="Team name for report header")
    args = parser.parse_args()
    build_pdf(output_filename=args.output, team_name=args.team_name)
