import re
from typing import Dict, List, Optional


def _extract_parties(text: str) -> List[str]:
    """Extract party names from contract."""
    parties = []

    # Common party identification patterns
    patterns = [
        r'(?:this\s+agreement\s+is\s+(?:entered\s+into\s+)?(?:by\s+and\s+)?between)\s+([A-Z][^,\n]+?)(?:\s+\("?(?:Company|Client|Vendor|Service\s+Provider|Licensor|Licensee|Contractor|Customer|Buyer|Seller|Party\s+[AB])"?\))',
        r'"((?:Company|Client|Vendor|Service\s*Provider|Licensor|Licensee|Contractor|Customer|Buyer|Seller))"',
        r'(?:hereinafter\s+referred\s+to\s+as\s+)"([^"]+)"',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            name = match.strip()
            if 2 < len(name) < 80 and name not in parties:
                parties.append(name)
            if len(parties) >= 2:
                return parties

    # Fallback: look for common party names
    fallback = re.findall(
        r'\b([A-Z][A-Za-z\s&,\.]+(?:Inc\.|LLC|Ltd\.|Corp\.|Corporation|Company|LLP))\b',
        text[:2000]
    )
    seen = set()
    for name in fallback:
        name = name.strip().rstrip(',')
        if name not in seen and len(name) > 3:
            seen.add(name)
            parties.append(name)
        if len(parties) >= 2:
            break

    if not parties:
        parties = ["Party A", "Party B"]

    return parties[:2]


def _extract_duration(text: str) -> str:
    """Extract contract duration/term."""
    patterns = [
        r'(?:term\s+of\s+(?:this\s+agreement\s+)?shall\s+be)\s+([^\.]+)',
        r'(?:initial\s+term\s+of)\s+([^\.]+)',
        r'(?:agreement\s+shall\s+(?:remain\s+in\s+force|continue)\s+for)\s+([^\.]+)',
        r'(?:for\s+a\s+period\s+of)\s+([\d\w\s]+?)(?:\.|,|\n)',
        r'(\d+)\s*(?:year|month|week)s?\s+(?:term|period|duration)',
        r'effective\s+(?:date|through)\s+([^\.\n]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            duration = match.group(1).strip()
            if len(duration) < 100:
                return duration

    # Look for date ranges
    date_range = re.search(
        r'(?:from|commencing)\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})\s+(?:to|through|until)\s+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
        text,
        re.IGNORECASE
    )
    if date_range:
        return f"{date_range.group(1)} through {date_range.group(2)}"

    return "Not specified in contract"


def _extract_purpose(text: str) -> str:
    """Extract the contract's primary purpose."""
    purpose_patterns = [
        r'(?:this\s+agreement\s+(?:is\s+)?(?:for|covers?|relates?\s+to|governs?))\s+([^\.]{10,200})',
        r'(?:purpose\s+of\s+this\s+agreement\s+is\s+to)\s+([^\.]{10,200})',
        r'(?:the\s+parties\s+(?:agree|wish|desire)\s+to)\s+([^\.]{10,200})',
        r'(?:in\s+consideration\s+of\s+(?:the\s+)?mutual\s+(?:covenants|obligations))[^,]*,\s*([^\.]{10,200})',
    ]

    for pattern in purpose_patterns:
        match = re.search(pattern, text[:3000], re.IGNORECASE)
        if match:
            purpose = match.group(1).strip().rstrip(',;')
            return purpose[:300]

    # Try to infer from contract type keywords
    contract_types = {
        "service agreement": "provision of professional services",
        "software license": "licensing of software and related services",
        "saas": "access to software-as-a-service platform",
        "non-disclosure": "protection of confidential information between parties",
        "employment": "establishment of employment relationship and terms",
        "vendor": "procurement of vendor services and goods",
        "master services": "establishment of master terms for ongoing service delivery",
        "subscription": "subscription-based access to services or software",
        "purchase order": "purchase of goods or services",
        "consulting": "provision of consulting and advisory services",
    }

    text_lower = text[:3000].lower()
    for key, purpose in contract_types.items():
        if key in text_lower:
            return purpose.capitalize()

    # Extract from first paragraph
    first_para = text.strip().split('\n\n')[0] if text else ""
    sentences = re.split(r'(?<=[.!?])\s+', first_para)
    for sentence in sentences[:3]:
        if 20 < len(sentence) < 300:
            return sentence.strip()

    return "General commercial agreement governing the relationship between the parties."


def _extract_key_obligations(text: str, clauses: List[Dict]) -> List[str]:
    """Extract key obligations from the contract."""
    obligations = []

    # Extract from payment terms
    payment_clause = next((c for c in clauses if c["type"] == "payment_terms" and c["found"]), None)
    if payment_clause:
        content = payment_clause["content"]
        net_match = re.search(r"net\s*(\d+)|within\s+(\d+)\s+days?", content, re.IGNORECASE)
        if net_match:
            days = net_match.group(1) or net_match.group(2)
            obligations.append(f"Payment must be made within {days} days of invoice")
        else:
            obligations.append("Payment obligations as specified in financial terms")

    # Termination obligations
    term_clause = next((c for c in clauses if c["type"] == "termination" and c["found"]), None)
    if term_clause:
        content = term_clause["content"]
        notice = re.search(r"(\d+)\s+days?\s+(?:written\s+)?notice", content, re.IGNORECASE)
        if notice:
            obligations.append(f"Termination requires {notice.group(1)} days written notice")

    # Confidentiality obligations
    conf_clause = next((c for c in clauses if c["type"] == "confidentiality" and c["found"]), None)
    if conf_clause:
        obligations.append("All confidential information must be protected from unauthorized disclosure")

    # Data protection obligations
    dp_clause = next((c for c in clauses if c["type"] == "data_protection" and c["found"]), None)
    if dp_clause:
        obligations.append("Data processing must comply with applicable data protection regulations")

    # Indemnification obligations
    indemnity = next((c for c in clauses if c["type"] == "indemnification" and c["found"]), None)
    if indemnity:
        obligations.append("Indemnification obligations apply for third-party claims arising from breach")

    # Generic obligations if few were found
    if len(obligations) < 3:
        generic = [
            "Both parties must perform obligations in good faith",
            "Disputes must be resolved through the specified dispute resolution process",
            "Material changes require written consent from both parties",
        ]
        for g in generic:
            if len(obligations) < 5:
                obligations.append(g)

    return obligations[:6]


def _extract_key_risks(risk_data: Dict) -> List[str]:
    """Extract key risks from risk analysis."""
    risks = []
    for factor in risk_data.get("factors", []):
        if factor.get("present"):
            risks.append(factor["explanation"])
    return risks[:5]


def generate_summary(text: str, clauses: List[Dict], risk_data: Dict) -> Dict:
    """Generate executive summary of the contract."""
    parties = _extract_parties(text)
    duration = _extract_duration(text)
    purpose = _extract_purpose(text)
    obligations = _extract_key_obligations(text, clauses)
    key_risks = _extract_key_risks(risk_data)

    recommendations_preview = []
    if risk_data.get("score", 0) > 65:
        recommendations_preview.append("Engage legal counsel before signing — significant risks identified")
    if any(f["factor"] == "Unlimited Liability Exposure" and f["present"] for f in risk_data.get("factors", [])):
        recommendations_preview.append("Negotiate liability cap to limit financial exposure")
    if any(f["factor"] == "Weak/Missing Confidentiality" and f["present"] for f in risk_data.get("factors", [])):
        recommendations_preview.append("Strengthen confidentiality provisions to protect proprietary information")
    if any(f["factor"] == "Auto-Renewal Trap" and f["present"] for f in risk_data.get("factors", [])):
        recommendations_preview.append("Add calendar reminder for renewal opt-out notice deadline")

    return {
        "purpose": purpose,
        "parties": parties,
        "duration": duration,
        "key_obligations": obligations,
        "key_risks": key_risks if key_risks else ["No major risks identified"],
        "recommendations_preview": recommendations_preview[:3] if recommendations_preview else ["Contract appears generally sound"],
    }
