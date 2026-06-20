import re
from typing import Dict, List, Tuple


def _check_liability_cap(text: str, clauses: List[Dict]) -> Tuple[bool, str]:
    """Check if there's an unlimited liability exposure."""
    liability_text = ""
    for c in clauses:
        if c["type"] in ("liability", "limitation_of_liability") and c["found"]:
            liability_text += c["content"] + " "

    if not liability_text:
        return True, "No liability limitation clause found in the contract."

    cap_indicators = [
        r"shall\s+not\s+exceed",
        r"limited\s+to",
        r"maximum\s+(?:aggregate\s+)?liability",
        r"in\s+no\s+event\s+shall",
        r"liability\s+cap",
        r"not\s+exceed",
        r"\$[\d,]+",
        r"\d+\s*times?\s+the\s+(?:annual\s+)?(?:contract|fee)",
    ]

    for pattern in cap_indicators:
        if re.search(pattern, liability_text, re.IGNORECASE):
            return False, "Liability cap is present."

    unlimited_indicators = [
        r"unlimited\s+liability",
        r"no\s+limitation",
        r"waives?\s+(?:any\s+)?limitation",
    ]
    for pattern in unlimited_indicators:
        if re.search(pattern, liability_text, re.IGNORECASE):
            return True, "Contract explicitly states unlimited liability."

    return True, "Liability limitation terms are ambiguous or missing a clear cap."


def _check_confidentiality(clauses: List[Dict]) -> Tuple[bool, str]:
    """Check if confidentiality clause is missing or weak."""
    conf_clause = next((c for c in clauses if c["type"] == "confidentiality"), None)
    if not conf_clause or not conf_clause["found"]:
        return True, "No confidentiality clause found — proprietary information may be unprotected."

    content = conf_clause["content"].lower()
    weak_indicators = ["may disclose", "except as required", "without restriction"]
    strong_indicators = ["shall not disclose", "must not", "strictly confidential", "perpetual", "survive"]

    strong_count = sum(1 for s in strong_indicators if s in content)
    weak_count = sum(1 for w in weak_indicators if w in content)

    if strong_count == 0 and weak_count > 0:
        return True, "Confidentiality clause exists but contains permissive language allowing disclosure."
    if strong_count == 0:
        return True, "Confidentiality clause is present but lacks strong protective language."

    return False, "Confidentiality clause is adequately protective."


def _check_auto_renewal(clauses: List[Dict]) -> Tuple[bool, str]:
    """Check if auto-renewal is present with short opt-out window."""
    renewal_clause = next((c for c in clauses if c["type"] == "renewal"), None)
    if not renewal_clause or not renewal_clause["found"]:
        return False, "No auto-renewal clause found."

    content = renewal_clause["content"].lower()
    auto_patterns = ["automatically renew", "auto-renew", "auto renew", "shall renew", "automatic renewal"]
    has_auto = any(p in content for p in auto_patterns)

    if not has_auto:
        return False, "Renewal requires affirmative action — no auto-renewal risk."

    # Check for opt-out window
    short_window = re.search(r"(\d+)\s+days?\s+(?:prior\s+)?(?:written\s+)?notice", content)
    if short_window:
        days = int(short_window.group(1))
        if days <= 30:
            return True, f"Auto-renewal with only {days}-day opt-out window — high risk of unintended renewal."
        return True, f"Auto-renewal clause present with {days}-day notice period."

    return True, "Auto-renewal clause present without clear opt-out procedure."


def _check_termination_rights(clauses: List[Dict]) -> Tuple[bool, str]:
    """Check if termination rights are weak."""
    term_clause = next((c for c in clauses if c["type"] == "termination"), None)
    if not term_clause or not term_clause["found"]:
        return True, "No termination clause found — party may be locked into contract indefinitely."

    content = term_clause["content"].lower()

    # Check for termination for convenience
    convenience = ["convenience", "without cause", "for any reason"]
    has_convenience = any(c in content for c in convenience)

    # Check notice period
    notice_match = re.search(r"(\d+)\s+(?:calendar\s+|business\s+)?days?\s+(?:(?:prior|advance)\s+)?(?:written\s+)?notice", content)
    notice_days = int(notice_match.group(1)) if notice_match else None

    if not has_convenience:
        if notice_days and notice_days > 90:
            return True, f"Termination requires {notice_days} days notice with no termination for convenience."
        return True, "No termination for convenience — exit from contract is restricted to cause only."

    if notice_days and notice_days > 90:
        return True, f"Termination for convenience exists but requires {notice_days} days notice."

    return False, "Termination rights are adequate with reasonable notice period."


def _check_payment_terms(text: str, clauses: List[Dict]) -> Tuple[bool, str]:
    """Check for unfavorable payment terms."""
    payment_clause = next((c for c in clauses if c["type"] == "payment_terms"), None)
    if not payment_clause or not payment_clause["found"]:
        return True, "No payment terms clause identified."

    content = payment_clause["content"].lower()

    # Look for NET X days
    net_match = re.search(r"net\s*(\d+)", content)
    days_match = re.search(r"(?:within|in)\s+(\d+)\s+(?:business\s+)?days", content)

    if net_match:
        days = int(net_match.group(1))
        if days >= 90:
            return True, f"Payment terms of Net {days} create significant cash flow risk."
        if days >= 60:
            return True, f"Payment terms of Net {days} — consider negotiating to Net 30."
        return False, f"Payment terms of Net {days} are reasonable."

    if days_match:
        days = int(days_match.group(1))
        if days >= 90:
            return True, f"Payment due in {days} days — very long payment cycle."

    return False, "Payment terms appear standard."


def _check_data_protection(clauses: List[Dict]) -> Tuple[bool, str]:
    """Check if data protection provisions are missing."""
    dp_clause = next((c for c in clauses if c["type"] == "data_protection"), None)
    if not dp_clause or not dp_clause["found"]:
        return True, "No data protection clause — personal data handling obligations are undefined."

    content = dp_clause["content"].lower()
    gdpr_indicators = ["gdpr", "data controller", "data processor", "lawful basis", "data subject"]
    breach_indicators = ["breach notification", "security incident", "notify", "72 hours"]

    has_gdpr = any(i in content for i in gdpr_indicators)
    has_breach = any(i in content for i in breach_indicators)

    if not has_breach:
        return True, "Data protection clause lacks breach notification requirements."
    if not has_gdpr:
        return True, "Data protection clause present but lacks GDPR compliance language."

    return False, "Data protection clause is comprehensive."


def _check_indemnification(clauses: List[Dict]) -> Tuple[bool, str]:
    """Check for broad indemnification obligations."""
    indemnity_clause = next((c for c in clauses if c["type"] == "indemnification"), None)
    if not indemnity_clause or not indemnity_clause["found"]:
        return True, "No indemnification clause — risk allocation between parties is undefined."

    content = indemnity_clause["content"].lower()
    broad_indicators = ["any and all", "unlimited", "without limitation", "including all"]
    mutual_indicators = ["mutual", "each party", "reciprocal"]

    is_broad = any(b in content for b in broad_indicators)
    is_mutual = any(m in content for m in mutual_indicators)

    if is_broad and not is_mutual:
        return True, "One-sided, broad indemnification obligation — significantly increases liability exposure."
    if is_broad:
        return True, "Broad indemnification language present — consider capping indemnification obligations."

    return False, "Indemnification clause appears balanced."


def calculate_risk(text: str, clauses: List[Dict]) -> Dict:
    """Calculate comprehensive risk score and factors."""
    risk_checks = [
        ("unlimited_liability", "Unlimited Liability Exposure", _check_liability_cap(text, clauses), 25),
        ("missing_data_protection", "Missing Data Protection", _check_data_protection(clauses), 18),
        ("missing_confidentiality", "Weak/Missing Confidentiality", _check_confidentiality(clauses), 15),
        ("missing_indemnification", "Indemnification Risk", _check_indemnification(clauses), 12),
        ("auto_renewal", "Auto-Renewal Trap", _check_auto_renewal(clauses), 10),
        ("weak_termination", "Weak Termination Rights", _check_termination_rights(clauses), 12),
        ("long_payment_terms", "Unfavorable Payment Terms", _check_payment_terms(text, clauses), 8),
    ]

    total_weight = sum(w for _, _, _, w in risk_checks)
    accumulated_score = 0
    factors = []

    for factor_key, factor_name, (is_risk, explanation), weight in risk_checks:
        severity = "High" if weight >= 18 else "Medium" if weight >= 10 else "Low"
        factors.append({
            "factor": factor_name,
            "severity": severity if is_risk else "None",
            "explanation": explanation,
            "present": is_risk,
        })
        if is_risk:
            accumulated_score += weight

    # Normalize to 0-100 scale
    raw_score = (accumulated_score / total_weight) * 100

    # Apply a smoothing curve — most contracts are between 20-80
    # low weight on base: every contract starts at 15
    score = round(15 + (raw_score * 0.85), 1)
    score = min(100.0, max(0.0, score))

    if score >= 65:
        level = "High"
        summary = "This contract presents significant legal and business risks. Immediate review by legal counsel is strongly recommended before signing."
    elif score >= 35:
        level = "Medium"
        summary = "This contract contains several areas of concern. Legal review is recommended to address identified gaps before execution."
    else:
        level = "Low"
        summary = "This contract presents manageable risk levels. Minor improvements are recommended but the contract is generally sound."

    return {
        "score": score,
        "level": level,
        "factors": factors,
        "summary": summary,
    }
