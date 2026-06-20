import os
import json
from datetime import datetime
from typing import Dict, List

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch, cm
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


DARK_BG = HexColor("#0F172A") if REPORTLAB_AVAILABLE else None
ACCENT = HexColor("#6366F1") if REPORTLAB_AVAILABLE else None
TEXT_COLOR = HexColor("#1E293B") if REPORTLAB_AVAILABLE else None
MUTED = HexColor("#64748B") if REPORTLAB_AVAILABLE else None
HIGH_RISK = HexColor("#EF4444") if REPORTLAB_AVAILABLE else None
MED_RISK = HexColor("#F59E0B") if REPORTLAB_AVAILABLE else None
LOW_RISK = HexColor("#10B981") if REPORTLAB_AVAILABLE else None
CARD_BG = HexColor("#F8FAFC") if REPORTLAB_AVAILABLE else None
BORDER = HexColor("#E2E8F0") if REPORTLAB_AVAILABLE else None


def _get_risk_color(level: str):
    if level == "High":
        return HIGH_RISK
    if level == "Medium":
        return MED_RISK
    return LOW_RISK


def generate_pdf_report(
    contract: Dict,
    clauses: List[Dict],
    risk: Dict,
    summary: Dict,
    recommendations: List[Dict],
    output_path: str,
) -> str:
    """Generate a professional PDF report for a contract analysis."""
    if not REPORTLAB_AVAILABLE:
        raise RuntimeError("ReportLab is not installed. Run: pip install reportlab")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=1.8 * cm,
        leftMargin=1.8 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Normal"],
        fontSize=24,
        textColor=ACCENT,
        fontName="Helvetica-Bold",
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=10,
        textColor=MUTED,
        fontName="Helvetica",
        spaceAfter=4,
    )
    section_header_style = ParagraphStyle(
        "SectionHeader",
        parent=styles["Normal"],
        fontSize=13,
        textColor=ACCENT,
        fontName="Helvetica-Bold",
        spaceBefore=16,
        spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=9,
        textColor=TEXT_COLOR,
        fontName="Helvetica",
        leading=14,
        spaceAfter=4,
    )
    bold_body_style = ParagraphStyle(
        "BoldBody",
        parent=body_style,
        fontName="Helvetica-Bold",
    )
    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        textColor=MUTED,
        fontName="Helvetica",
        leading=12,
    )

    elements = []

    # ── HEADER ─────────────────────────────────────────────────────────────
    elements.append(Paragraph("LEXORA AI", title_style))
    elements.append(Paragraph("Contract Intelligence Platform", subtitle_style))
    elements.append(Paragraph("Transforming Contracts into Actionable Intelligence", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=ACCENT, spaceAfter=12))

    # Report meta
    meta_data = [
        ["Contract:", contract.get("original_name", "Unknown")],
        ["Report Generated:", datetime.utcnow().strftime("%B %d, %Y at %H:%M UTC")],
        ["Risk Level:", risk.get("level", "Unknown")],
        ["Risk Score:", f"{risk.get('score', 0):.1f} / 100"],
    ]
    meta_table = Table(meta_data, colWidths=[3 * cm, 13 * cm])
    meta_table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TEXTCOLOR", (0, 0), (0, -1), MUTED),
        ("TEXTCOLOR", (1, 0), (1, -1), TEXT_COLOR),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [CARD_BG, white]),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(meta_table)
    elements.append(Spacer(1, 0.4 * cm))

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────────────────
    elements.append(Paragraph("Executive Summary", section_header_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

    elements.append(Paragraph(f"<b>Purpose:</b> {summary.get('purpose', 'N/A')}", body_style))
    elements.append(Paragraph(f"<b>Parties:</b> {' and '.join(summary.get('parties', []))}", body_style))
    elements.append(Paragraph(f"<b>Duration:</b> {summary.get('duration', 'N/A')}", body_style))
    elements.append(Spacer(1, 0.2 * cm))

    if summary.get("key_obligations"):
        elements.append(Paragraph("<b>Key Obligations:</b>", bold_body_style))
        for obligation in summary["key_obligations"]:
            elements.append(Paragraph(f"• {obligation}", body_style))

    elements.append(Spacer(1, 0.2 * cm))
    if summary.get("key_risks"):
        elements.append(Paragraph("<b>Key Risks Identified:</b>", bold_body_style))
        for risk_item in summary["key_risks"]:
            elements.append(Paragraph(f"• {risk_item}", body_style))

    # ── RISK ANALYSIS ──────────────────────────────────────────────────────
    elements.append(Paragraph("Risk Analysis", section_header_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

    risk_level = risk.get("level", "Unknown")
    risk_color = _get_risk_color(risk_level)
    risk_score = risk.get("score", 0)

    # Risk score box
    risk_box_data = [[
        Paragraph(f"<b>Risk Score</b><br/><font size=20 color='#{risk_color.hexval()[2:]}'>{risk_score:.0f}</font>/100", body_style),
        Paragraph(f"<b>Risk Level</b><br/><font size=14 color='#{risk_color.hexval()[2:]}'>{risk_level} Risk</font>", body_style),
    ]]
    risk_box = Table(risk_box_data, colWidths=[8 * cm, 8 * cm])
    risk_box.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CARD_BG),
        ("BOX", (0, 0), (-1, -1), 1, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0.5, BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (-1, -1), 16),
    ]))
    elements.append(risk_box)
    elements.append(Spacer(1, 0.3 * cm))

    elements.append(Paragraph(risk.get("summary", ""), body_style))
    elements.append(Spacer(1, 0.2 * cm))

    # Risk factors table
    active_factors = [f for f in risk.get("factors", []) if f.get("present")]
    if active_factors:
        elements.append(Paragraph("<b>Active Risk Factors:</b>", bold_body_style))
        factor_data = [["Factor", "Severity", "Explanation"]]
        for factor in active_factors:
            factor_data.append([
                factor.get("factor", ""),
                factor.get("severity", ""),
                factor.get("explanation", ""),
            ])

        sev_colors = {"High": HIGH_RISK, "Medium": MED_RISK, "Low": LOW_RISK, "Critical": HIGH_RISK}

        factor_table = Table(factor_data, colWidths=[4.5 * cm, 2 * cm, 9.5 * cm])
        factor_style = [
            ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
            ("TEXTCOLOR", (0, 0), (-1, 0), white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [CARD_BG, white]),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("WORDWRAP", (2, 1), (2, -1), True),
        ]
        for row_i, factor in enumerate(active_factors, 1):
            sev = factor.get("severity", "Low")
            color = sev_colors.get(sev, LOW_RISK)
            factor_style.append(("TEXTCOLOR", (1, row_i), (1, row_i), color))
            factor_style.append(("FONTNAME", (1, row_i), (1, row_i), "Helvetica-Bold"))

        factor_table.setStyle(TableStyle(factor_style))
        elements.append(factor_table)

    # ── CLAUSE ANALYSIS ────────────────────────────────────────────────────
    elements.append(Paragraph("Clause Analysis", section_header_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

    for clause in clauses:
        found = clause.get("found", False)
        status = "FOUND" if found else "NOT FOUND"
        status_color = LOW_RISK if found else HIGH_RISK
        confidence = clause.get("confidence", 0)

        clause_data = [[
            Paragraph(f"<b>{clause.get('title', '')}</b>", bold_body_style),
            Paragraph(f"<font color='#{status_color.hexval()[2:]}'><b>{status}</b></font>", body_style),
            Paragraph(f"Confidence: {confidence:.0%}" if found else "", small_style),
        ]]

        if found:
            content = clause.get("content", "")[:300]
            clause_data.append([
                Paragraph(f"<i>{content}...</i>", small_style),
                "",
                "",
            ])

        clause_table = Table(clause_data, colWidths=[5 * cm, 3 * cm, 8 * cm])
        clause_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), CARD_BG),
            ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("SPAN", (0, 1), (-1, 1)),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))
        elements.append(clause_table)
        elements.append(Spacer(1, 0.15 * cm))

    # ── RECOMMENDATIONS ────────────────────────────────────────────────────
    if recommendations:
        elements.append(Paragraph("Recommendations", section_header_style))
        elements.append(HRFlowable(width="100%", thickness=1, color=BORDER, spaceAfter=8))

        for rec in recommendations:
            sev = rec.get("severity", "Medium")
            sev_color = {"Critical": HIGH_RISK, "High": HIGH_RISK, "Medium": MED_RISK, "Low": LOW_RISK}.get(sev, MED_RISK)

            rec_content = [
                [
                    Paragraph(f"<b>{rec.get('issue', '')}</b>", bold_body_style),
                    Paragraph(f"<font color='#{sev_color.hexval()[2:]}'><b>{sev}</b></font>", body_style),
                ],
                [Paragraph(f"<b>Business Impact:</b> {rec.get('business_impact', '')}", small_style), ""],
                [Paragraph(f"<b>Suggested Action:</b> {rec.get('suggested_action', '')}", small_style), ""],
            ]

            rec_table = Table(rec_content, colWidths=[13 * cm, 3 * cm])
            rec_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), CARD_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("SPAN", (0, 1), (-1, 1)),
                ("SPAN", (0, 2), (-1, 2)),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]))
            elements.append(rec_table)
            elements.append(Spacer(1, 0.2 * cm))

    # ── FOOTER ─────────────────────────────────────────────────────────────
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=BORDER))
    elements.append(Paragraph(
        f"Generated by Lexora AI Contract Intelligence Platform • {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} • Confidential",
        small_style
    ))

    doc.build(elements)
    return output_path
