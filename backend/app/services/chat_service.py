import re
from typing import Dict, List, Optional


def _find_answer_in_contract(question: str, text: str, clauses: List[Dict], risk_data: Dict) -> str:
    """Generate an intelligent response to a contract question."""
    q_lower = question.lower()

    # Risk-related questions
    if any(kw in q_lower for kw in ["risk", "risks", "dangerous", "concern", "worry", "problem", "issue"]):
        return _answer_risk_question(risk_data, clauses)

    # Auto-renewal questions
    if any(kw in q_lower for kw in ["auto-renewal", "auto renewal", "automatically renew", "renew automatically", "evergreen"]):
        return _answer_renewal_question(clauses)

    # Liability questions
    if any(kw in q_lower for kw in ["liability", "liable", "liability cap", "damages cap", "maximum liability"]):
        return _answer_liability_question(clauses)

    # Payment questions
    if any(kw in q_lower for kw in ["payment", "pay", "invoice", "billing", "net 30", "net 60", "fee", "cost"]):
        return _answer_payment_question(clauses)

    # Termination questions
    if any(kw in q_lower for kw in ["terminate", "termination", "cancel", "exit", "end the contract", "get out"]):
        return _answer_termination_question(clauses)

    # Confidentiality questions
    if any(kw in q_lower for kw in ["confidential", "nda", "secret", "proprietary", "disclose"]):
        return _answer_confidentiality_question(clauses)

    # Governing law questions
    if any(kw in q_lower for kw in ["governing law", "jurisdiction", "laws", "courts", "legal venue", "dispute"]):
        return _answer_governing_law_question(clauses)

    # Data protection questions
    if any(kw in q_lower for kw in ["data", "gdpr", "privacy", "personal data", "data protection"]):
        return _answer_data_protection_question(clauses)

    # Duration/term questions
    if any(kw in q_lower for kw in ["duration", "term", "how long", "period", "expir"]):
        return _answer_duration_question(text)

    # Parties questions
    if any(kw in q_lower for kw in ["parties", "who", "company", "client", "vendor", "counterparty"]):
        return _answer_parties_question(text)

    # Indemnification questions
    if any(kw in q_lower for kw in ["indemnif", "hold harmless", "defend"]):
        return _answer_indemnification_question(clauses)

    # Summary questions
    if any(kw in q_lower for kw in ["summary", "summarize", "overview", "what is this", "what does this contract", "what is the contract about"]):
        return _answer_summary_question(text, clauses, risk_data)

    # Recommendation questions
    if any(kw in q_lower for kw in ["recommend", "suggest", "should i", "what should", "advice", "advise"]):
        return _answer_recommendation_question(risk_data)

    # Fallback: search for relevant content
    return _fallback_search(question, text, clauses)


def _answer_risk_question(risk_data: Dict, clauses: List[Dict]) -> str:
    score = risk_data.get("score", 0)
    level = risk_data.get("level", "Unknown")
    factors = risk_data.get("factors", [])
    active_risks = [f for f in factors if f.get("present")]

    if not active_risks:
        return f"Based on my analysis, this contract has a **{level} risk profile** (score: {score}/100). No significant risk factors were identified. The contract appears well-structured."

    risk_list = "\n".join(f"- **{r['factor']}** ({r['severity']}): {r['explanation']}" for r in active_risks[:5])
    return (
        f"This contract has a **{level} risk profile** with a risk score of **{score}/100**.\n\n"
        f"The key risks identified are:\n\n{risk_list}\n\n"
        f"{risk_data.get('summary', '')}"
    )


def _answer_renewal_question(clauses: List[Dict]) -> str:
    renewal = next((c for c in clauses if c["type"] == "renewal"), None)
    if not renewal or not renewal.get("found"):
        return "No auto-renewal clause was found in this contract. The contract does not appear to renew automatically — renewal would require affirmative action by the parties."

    content = renewal["content"].lower()
    auto_patterns = ["automatically renew", "auto-renew", "automatic renewal", "shall renew"]
    has_auto = any(p in content for p in auto_patterns)

    if not has_auto:
        return f"The contract contains a renewal clause, but it does not appear to include automatic renewal. Review the following provision:\n\n*\"{renewal['content'][:300]}...\"*"

    notice_match = re.search(r"(\d+)\s+days?\s+(?:written\s+)?notice", content)
    notice_info = f"with a **{notice_match.group(1)}-day notice period** to opt out" if notice_match else "and the opt-out procedure is not clearly specified"

    return (
        f"⚠️ **Yes, this contract contains an auto-renewal clause** {notice_info}.\n\n"
        f"Relevant provision:\n\n*\"{renewal['content'][:400]}\"*\n\n"
        f"**Recommendation:** Set a calendar reminder at least 90 days before the contract anniversary date to evaluate whether to opt out of renewal."
    )


def _answer_liability_question(clauses: List[Dict]) -> str:
    for ct in ("limitation_of_liability", "liability"):
        clause = next((c for c in clauses if c["type"] == ct and c.get("found")), None)
        if clause:
            content = clause["content"]
            cap_match = re.search(
                r"(?:shall\s+not\s+exceed|limited\s+to|maximum\s+(?:aggregate\s+)?liability)\s+([^\.\n]{5,100})",
                content,
                re.IGNORECASE,
            )
            if cap_match:
                return (
                    f"This contract **does contain a liability cap**. The limitation states:\n\n"
                    f"*\"{cap_match.group(0).strip()}\"*\n\n"
                    f"Full clause excerpt:\n\n*\"{content[:400]}\"*"
                )
            return (
                f"A liability clause was found, but **no clear liability cap** was identified in the provision:\n\n"
                f"*\"{content[:400]}\"*\n\n"
                f"**Recommendation:** Negotiate an explicit monetary cap to limit financial exposure."
            )

    return (
        "**No liability limitation clause was found** in this contract. This is a significant risk — without a liability cap, "
        "your organization could face claims for the full extent of any damages. "
        "**Strongly recommend** adding a liability limitation clause before signing."
    )


def _answer_payment_question(clauses: List[Dict]) -> str:
    clause = next((c for c in clauses if c["type"] == "payment_terms" and c.get("found")), None)
    if not clause:
        return "No payment terms clause was identified in this contract. Payment obligations, schedules, and conditions should be clearly defined before signing."

    content = clause["content"]
    net_match = re.search(r"net\s*(\d+)", content, re.IGNORECASE)
    days_match = re.search(r"(?:within|in)\s+(\d+)\s+(?:business\s+)?days?", content, re.IGNORECASE)

    payment_info = ""
    if net_match:
        payment_info = f"Payment is due **Net {net_match.group(1)}** (within {net_match.group(1)} days of invoice)."
    elif days_match:
        payment_info = f"Payment is due within **{days_match.group(1)} days**."

    return (
        f"{payment_info}\n\nPayment terms provision:\n\n*\"{content[:500]}\"*"
        if payment_info
        else f"Payment terms found:\n\n*\"{content[:500]}\"*"
    )


def _answer_termination_question(clauses: List[Dict]) -> str:
    clause = next((c for c in clauses if c["type"] == "termination" and c.get("found")), None)
    if not clause:
        return "No termination clause was found in this contract. The absence of termination provisions is a significant risk — the parties may be bound indefinitely with no clear exit mechanism."

    content = clause["content"]
    notice_match = re.search(r"(\d+)\s+(?:calendar\s+|business\s+)?days?\s+(?:(?:prior|advance|written)\s+)?notice", content, re.IGNORECASE)
    convenience = any(kw in content.lower() for kw in ["convenience", "without cause", "for any reason"])

    details = []
    if convenience:
        details.append("✅ Termination for convenience is permitted (no cause required)")
    else:
        details.append("⚠️ Termination for convenience is NOT explicitly permitted")

    if notice_match:
        days = notice_match.group(1)
        details.append(f"📋 Notice period: **{days} days** written notice required")

    details_text = "\n".join(details)
    return (
        f"Termination provisions summary:\n\n{details_text}\n\n"
        f"Relevant provision:\n\n*\"{content[:500]}\"*"
    )


def _answer_confidentiality_question(clauses: List[Dict]) -> str:
    clause = next((c for c in clauses if c["type"] == "confidentiality" and c.get("found")), None)
    if not clause:
        return "**No confidentiality clause was found** in this contract. This is a significant gap — both parties' confidential and proprietary information has no contractual protection. A comprehensive confidentiality or NDA provision should be added."

    content = clause["content"]
    return (
        f"This contract **contains a confidentiality clause**.\n\n"
        f"Provision excerpt:\n\n*\"{content[:500]}\"*"
    )


def _answer_governing_law_question(clauses: List[Dict]) -> str:
    clause = next((c for c in clauses if c["type"] == "governing_law" and c.get("found")), None)
    if not clause:
        return "No governing law or jurisdiction clause was found. This could lead to disputes about which courts have authority to resolve conflicts — governing law should be explicitly stated."

    content = clause["content"]
    jurisdiction_match = re.search(
        r"(?:laws?\s+of\s+(?:the\s+)?|governed\s+by\s+(?:the\s+)?)([A-Za-z\s]+?)(?:\.|,|\n|$)",
        content, re.IGNORECASE
    )
    jurisdiction = jurisdiction_match.group(1).strip() if jurisdiction_match else "as specified in the clause"

    return (
        f"This contract is governed by the laws of **{jurisdiction}**.\n\n"
        f"Governing law provision:\n\n*\"{content[:400]}\"*"
    )


def _answer_data_protection_question(clauses: List[Dict]) -> str:
    clause = next((c for c in clauses if c["type"] == "data_protection" and c.get("found")), None)
    if not clause:
        return (
            "**No data protection clause was found** in this contract. "
            "If this contract involves processing personal data, the absence of data protection provisions "
            "may constitute a violation of GDPR, CCPA, or other applicable regulations. "
            "A Data Processing Agreement (DPA) should be included or appended."
        )

    content = clause["content"]
    gdpr = "GDPR" in content.upper()
    ccpa = "CCPA" in content.upper()

    reg_text = ""
    if gdpr:
        reg_text += " It references **GDPR** compliance obligations."
    if ccpa:
        reg_text += " It references **CCPA** compliance requirements."

    return (
        f"This contract **contains data protection provisions**.{reg_text}\n\n"
        f"Data protection provision:\n\n*\"{content[:500]}\"*"
    )


def _answer_duration_question(text: str) -> str:
    from app.services.summary_engine import _extract_duration
    duration = _extract_duration(text)
    return (
        f"The contract term/duration is: **{duration}**\n\n"
        f"If the duration is unclear, review the 'Term', 'Duration', or 'Effective Date' sections of the contract."
    )


def _answer_parties_question(text: str) -> str:
    from app.services.summary_engine import _extract_parties
    parties = _extract_parties(text)
    if len(parties) >= 2:
        return f"This contract is between:\n\n1. **{parties[0]}**\n2. **{parties[1]}**"
    if parties:
        return f"The primary party identified is: **{parties[0]}**. Review the contract header for all parties."
    return "Unable to clearly identify all parties from the contract text. Check the recitals or opening paragraphs."


def _answer_indemnification_question(clauses: List[Dict]) -> str:
    clause = next((c for c in clauses if c["type"] == "indemnification" and c.get("found")), None)
    if not clause:
        return "No indemnification clause was found in this contract. Without indemnification provisions, risk allocation for third-party claims is undefined."

    content = clause["content"]
    mutual = any(kw in content.lower() for kw in ["mutual", "each party", "reciprocal"])
    broad = any(kw in content.lower() for kw in ["any and all", "unlimited", "without limitation"])

    assessment = ""
    if mutual:
        assessment = "✅ Indemnification appears to be **mutual** (both parties indemnify each other)."
    else:
        assessment = "⚠️ Indemnification may be **one-sided** — verify which party bears the primary obligation."

    if broad:
        assessment += "\n⚠️ The indemnification scope uses **broad language** — consider negotiating a cap."

    return f"{assessment}\n\nIndemnification provision:\n\n*\"{content[:500]}\"*"


def _answer_summary_question(text: str, clauses: List[Dict], risk_data: Dict) -> str:
    from app.services.summary_engine import _extract_parties, _extract_duration, _extract_purpose
    purpose = _extract_purpose(text)
    parties = _extract_parties(text)
    duration = _extract_duration(text)
    score = risk_data.get("score", 0)
    level = risk_data.get("level", "Unknown")
    found_clauses = [c["title"] for c in clauses if c.get("found")]

    return (
        f"**Contract Summary:**\n\n"
        f"**Purpose:** {purpose}\n\n"
        f"**Parties:** {' and '.join(parties)}\n\n"
        f"**Duration:** {duration}\n\n"
        f"**Risk Level:** {level} ({score}/100)\n\n"
        f"**Key Clauses Identified:** {', '.join(found_clauses) if found_clauses else 'None identified'}"
    )


def _answer_recommendation_question(risk_data: Dict) -> str:
    factors = risk_data.get("factors", [])
    active = [f for f in factors if f.get("present")]

    if not active:
        return "Based on the risk analysis, this contract appears to be in good shape. No critical recommendations at this time. Standard legal review before signing is always advisable."

    top_issues = active[:3]
    items = "\n".join(f"{i+1}. **{r['factor']}** — {r['explanation']}" for i, r in enumerate(top_issues))
    return (
        f"Based on the risk analysis, here are the top recommendations:\n\n{items}\n\n"
        f"Navigate to the **Recommendations** tab for full details on each issue with suggested contract language."
    )


def _fallback_search(question: str, text: str, clauses: List[Dict]) -> str:
    """Search the contract text for relevant content when no specific handler matches."""
    # Extract key terms from the question
    words = re.findall(r'\b[a-z]{4,}\b', question.lower())
    stop_words = {'what', 'when', 'where', 'which', 'that', 'this', 'with', 'from', 'have', 'does', 'about', 'tell', 'find', 'show', 'list'}
    keywords = [w for w in words if w not in stop_words]

    if not keywords:
        return (
            "I can help you analyze this contract. You can ask me about:\n"
            "- **Risks** (biggest risks, risk score)\n"
            "- **Liability** (liability cap, damages)\n"
            "- **Payment Terms** (payment schedule, invoice terms)\n"
            "- **Termination** (how to exit, notice period)\n"
            "- **Confidentiality** (NDA, proprietary information)\n"
            "- **Auto-Renewal** (automatic renewal, opt-out)\n"
            "- **Governing Law** (jurisdiction, applicable law)\n"
            "- **Data Protection** (GDPR, privacy)"
        )

    # Search paragraphs
    paragraphs = re.split(r'\n\s*\n', text)
    scored = []
    for para in paragraphs:
        if len(para.strip()) < 30:
            continue
        score = sum(1 for kw in keywords if kw in para.lower())
        if score > 0:
            scored.append((para, score))

    if not scored:
        return f"I couldn't find specific information about '{question}' in this contract. Try asking about specific clauses like payment terms, liability, termination, or confidentiality."

    scored.sort(key=lambda x: x[1], reverse=True)
    best = scored[0][0][:600]

    return f"Here's the most relevant section I found regarding your question:\n\n*\"{best}...\"*\n\nIf this doesn't answer your question, try asking about a specific clause type."


def generate_chat_response(
    question: str,
    text: str,
    clauses: List[Dict],
    risk_data: Dict,
    history: List[Dict],
) -> str:
    """Main entry point for the chat engine."""
    if not text or len(text.strip()) < 50:
        return "The contract text could not be extracted or is too short to analyze. Please ensure a valid PDF was uploaded and re-analyze."

    return _find_answer_in_contract(question, text, clauses, risk_data)
