import re
from typing import Dict, List, Optional, Tuple
from app.services.clause_extractor import CLAUSE_DEFINITIONS


def _compare_clause_pair(
    clause_a: Optional[Dict],
    clause_b: Optional[Dict],
    clause_type: str,
    clause_title: str,
) -> Dict:
    """Compare two clauses and determine change type and impact."""
    a_found = clause_a and clause_a.get("found", False)
    b_found = clause_b and clause_b.get("found", False)
    a_content = clause_a.get("content", "") if clause_a else ""
    b_content = clause_b.get("content", "") if clause_b else ""

    if not a_found and not b_found:
        return {
            "clause_type": clause_type,
            "title": clause_title,
            "contract_a": "Not found",
            "contract_b": "Not found",
            "change_type": "unchanged",
            "impact": "No change — clause absent in both contracts.",
            "impact_level": "none",
        }

    if a_found and not b_found:
        return {
            "clause_type": clause_type,
            "title": clause_title,
            "contract_a": _truncate(a_content),
            "contract_b": "Not found",
            "change_type": "removed",
            "impact": f"{clause_title} clause was present in Contract A but is missing in Contract B — this increases risk.",
            "impact_level": _removal_impact(clause_type),
        }

    if not a_found and b_found:
        return {
            "clause_type": clause_type,
            "title": clause_title,
            "contract_a": "Not found",
            "contract_b": _truncate(b_content),
            "change_type": "added",
            "impact": f"{clause_title} clause added in Contract B — this may reduce or add risk depending on content.",
            "impact_level": _addition_impact(clause_type),
        }

    # Both found — check for meaningful changes
    similarity = _text_similarity(a_content, b_content)

    if similarity > 0.85:
        return {
            "clause_type": clause_type,
            "title": clause_title,
            "contract_a": _truncate(a_content),
            "contract_b": _truncate(b_content),
            "change_type": "unchanged",
            "impact": f"{clause_title} clause is substantially unchanged between versions.",
            "impact_level": "none",
        }

    # Extract key differences
    impact_description, impact_level = _analyze_clause_change(
        clause_type, a_content, b_content
    )

    return {
        "clause_type": clause_type,
        "title": clause_title,
        "contract_a": _truncate(a_content),
        "contract_b": _truncate(b_content),
        "change_type": "modified",
        "impact": impact_description,
        "impact_level": impact_level,
    }


def _text_similarity(text_a: str, text_b: str) -> float:
    """Simple token-based similarity measure."""
    if not text_a or not text_b:
        return 0.0
    tokens_a = set(re.findall(r'\b\w+\b', text_a.lower()))
    tokens_b = set(re.findall(r'\b\w+\b', text_b.lower()))
    if not tokens_a or not tokens_b:
        return 0.0
    intersection = tokens_a & tokens_b
    union = tokens_a | tokens_b
    return len(intersection) / len(union)


def _truncate(text: str, max_len: int = 400) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_len:
        return text
    return text[:max_len].rstrip() + "..."


def _removal_impact(clause_type: str) -> str:
    high_risk_clauses = {"liability", "limitation_of_liability", "confidentiality", "data_protection"}
    medium_risk_clauses = {"termination", "indemnification"}
    if clause_type in high_risk_clauses:
        return "high"
    if clause_type in medium_risk_clauses:
        return "medium"
    return "low"


def _addition_impact(clause_type: str) -> str:
    high_impact = {"liability", "limitation_of_liability", "renewal", "indemnification"}
    if clause_type in high_impact:
        return "medium"
    return "low"


def _analyze_clause_change(
    clause_type: str, text_a: str, text_b: str
) -> Tuple[str, str]:
    """Analyze the nature of changes between two clause versions."""
    text_a_lower = text_a.lower()
    text_b_lower = text_b.lower()

    if clause_type == "payment_terms":
        net_a = re.search(r"net\s*(\d+)", text_a_lower)
        net_b = re.search(r"net\s*(\d+)", text_b_lower)
        if net_a and net_b:
            days_a, days_b = int(net_a.group(1)), int(net_b.group(1))
            if days_b > days_a:
                return (
                    f"Payment terms extended from Net {days_a} to Net {days_b} — cash flow risk increased.",
                    "high",
                )
            return (
                f"Payment terms shortened from Net {days_a} to Net {days_b} — favorable change.",
                "low",
            )
        return "Payment terms modified — review for cash flow and credit risk implications.", "medium"

    if clause_type in ("liability", "limitation_of_liability"):
        cap_a = bool(re.search(r"shall\s+not\s+exceed|limited\s+to|maximum\s+liability", text_a_lower))
        cap_b = bool(re.search(r"shall\s+not\s+exceed|limited\s+to|maximum\s+liability", text_b_lower))
        if cap_a and not cap_b:
            return "Liability cap removed in Contract B — significantly increases financial exposure.", "high"
        if not cap_a and cap_b:
            return "Liability cap added in Contract B — reduces financial exposure.", "low"
        return "Liability terms modified — review scope and cap amounts carefully.", "medium"

    if clause_type == "renewal":
        auto_a = any(p in text_a_lower for p in ["automatically renew", "auto-renew", "automatic renewal"])
        auto_b = any(p in text_b_lower for p in ["automatically renew", "auto-renew", "automatic renewal"])
        if not auto_a and auto_b:
            return "Auto-renewal added in Contract B — risk of unintended commitment.", "high"
        if auto_a and not auto_b:
            return "Auto-renewal removed in Contract B — favorable change.", "low"
        return "Renewal terms modified — verify opt-out notice period requirements.", "medium"

    if clause_type == "termination":
        notice_a = re.search(r"(\d+)\s+days?\s+notice", text_a_lower)
        notice_b = re.search(r"(\d+)\s+days?\s+notice", text_b_lower)
        if notice_a and notice_b:
            days_a, days_b = int(notice_a.group(1)), int(notice_b.group(1))
            if days_b > days_a:
                return (
                    f"Termination notice extended from {days_a} to {days_b} days — harder to exit contract.",
                    "medium",
                )
            return (
                f"Termination notice reduced from {days_a} to {days_b} days — easier to exit.",
                "low",
            )
        return "Termination provisions modified — review exit rights carefully.", "medium"

    if clause_type == "confidentiality":
        strong_b = any(
            kw in text_b_lower for kw in ["strictly confidential", "shall not disclose", "perpetual"]
        )
        strong_a = any(
            kw in text_a_lower for kw in ["strictly confidential", "shall not disclose", "perpetual"]
        )
        if strong_a and not strong_b:
            return "Confidentiality protections weakened in Contract B — proprietary information at greater risk.", "high"
        if not strong_a and strong_b:
            return "Confidentiality protections strengthened in Contract B — favorable change.", "low"
        return "Confidentiality terms modified — review scope of protected information.", "medium"

    # Generic change description
    return f"{clause_type.replace('_', ' ').title()} clause modified between versions — review changes carefully.", "medium"


def compare_contracts(
    contract_a: Dict,
    contract_b: Dict,
    clauses_a: List[Dict],
    clauses_b: List[Dict],
    risk_a: Dict,
    risk_b: Dict,
) -> Dict:
    """Generate a comprehensive comparison report between two contracts."""
    changes = []

    for clause_type, clause_def in CLAUSE_DEFINITIONS.items():
        clause_a = next((c for c in clauses_a if c["type"] == clause_type), None)
        clause_b = next((c for c in clauses_b if c["type"] == clause_type), None)

        change = _compare_clause_pair(clause_a, clause_b, clause_type, clause_def["title"])
        changes.append(change)

    # Calculate overall impact
    risk_delta = round((risk_b.get("score", 0) - risk_a.get("score", 0)), 1)
    high_changes = sum(1 for c in changes if c["impact_level"] == "high")
    medium_changes = sum(1 for c in changes if c["impact_level"] == "medium")

    if high_changes >= 2 or risk_delta > 20:
        overall_impact = "Significantly Higher Risk"
    elif high_changes == 1 or (medium_changes >= 2 and risk_delta > 0):
        overall_impact = "Moderately Higher Risk"
    elif risk_delta < -15:
        overall_impact = "Significantly Lower Risk"
    elif risk_delta < 0:
        overall_impact = "Marginally Lower Risk"
    else:
        overall_impact = "Similar Risk Profile"

    # Build summary narrative
    changed_clauses = [c["title"] for c in changes if c["change_type"] != "unchanged"]
    if changed_clauses:
        summary = (
            f"Contract B shows {len(changed_clauses)} clause changes compared to Contract A, "
            f"affecting: {', '.join(changed_clauses[:4])}{'...' if len(changed_clauses) > 4 else ''}. "
            f"Overall risk {'increased by' if risk_delta > 0 else 'decreased by'} "
            f"{abs(risk_delta)} points."
        )
    else:
        summary = "Contracts are substantively similar with no significant clause changes detected."

    return {
        "overall_impact": overall_impact,
        "risk_delta": risk_delta,
        "changes": changes,
        "summary": summary,
    }
