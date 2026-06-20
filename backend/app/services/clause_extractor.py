import re
from typing import Dict, List, Optional, Tuple


CLAUSE_DEFINITIONS = {
    "payment_terms": {
        "title": "Payment Terms",
        "keywords": [
            "payment", "invoice", "fee", "fees", "amount due", "payable", "net 30",
            "net 60", "net 90", "payment schedule", "billing", "compensation",
            "remuneration", "payment terms", "days after", "business days",
        ],
        "section_patterns": [
            r"payment\s+terms?",
            r"fees?\s+and\s+payment",
            r"compensation",
            r"billing",
            r"financial\s+terms?",
        ],
        "extraction_patterns": [
            r"(payment.{0,300}?(?:days|months|upon receipt).{0,100})",
            r"((?:net|within)\s+\d+\s+(?:days|business days).{0,200})",
            r"(invoices?.{0,300}?(?:due|payable|within).{0,100})",
        ],
    },
    "confidentiality": {
        "title": "Confidentiality",
        "keywords": [
            "confidential", "non-disclosure", "nda", "proprietary", "secret",
            "confidentiality", "disclose", "disclosure", "trade secret",
            "confidential information",
        ],
        "section_patterns": [
            r"confidentiality",
            r"non-?disclosure",
            r"nda",
            r"trade\s+secrets?",
        ],
        "extraction_patterns": [
            r"(confidential\s+information.{0,400}?(?:shall|will|must|may).{0,200})",
            r"((?:disclose|disclosure).{0,400})",
            r"(non-?disclosure.{0,400})",
        ],
    },
    "liability": {
        "title": "Liability",
        "keywords": [
            "liability", "liable", "damages", "loss", "harm", "warranty",
            "indemnify", "responsible", "responsibility", "obligation",
        ],
        "section_patterns": [
            r"liability",
            r"damages?",
            r"warranties?",
            r"limitation\s+of\s+liability",
        ],
        "extraction_patterns": [
            r"(liabilit.{0,400}?(?:shall|will|limited|excluded).{0,100})",
            r"(in\s+no\s+event.{0,400})",
        ],
    },
    "limitation_of_liability": {
        "title": "Limitation of Liability",
        "keywords": [
            "limitation of liability", "limit liability", "aggregate liability",
            "maximum liability", "total liability", "cap on liability",
            "in no event", "not exceed", "limited to", "sole remedy",
        ],
        "section_patterns": [
            r"limitation\s+of\s+liability",
            r"liability\s+cap",
            r"aggregate\s+liability",
        ],
        "extraction_patterns": [
            r"((?:in\s+no\s+event|limitation\s+of\s+liability).{0,500})",
            r"((?:aggregate|maximum|total)\s+liability.{0,300})",
            r"(liability.{0,200}?(?:shall\s+not\s+exceed|limited\s+to).{0,200})",
        ],
    },
    "indemnification": {
        "title": "Indemnification",
        "keywords": [
            "indemnify", "indemnification", "indemnified", "hold harmless",
            "defend", "indemnitor", "indemnitee", "third-party claims",
        ],
        "section_patterns": [
            r"indemnif",
            r"hold\s+harmless",
        ],
        "extraction_patterns": [
            r"((?:shall|will)\s+indemnify.{0,500})",
            r"(indemnif.{0,500})",
            r"(hold\s+harmless.{0,400})",
        ],
    },
    "termination": {
        "title": "Termination",
        "keywords": [
            "terminate", "termination", "cancellation", "cancel", "end",
            "notice of termination", "right to terminate", "immediate termination",
            "for cause", "without cause", "expiration",
        ],
        "section_patterns": [
            r"termination",
            r"cancellation",
            r"expiration",
        ],
        "extraction_patterns": [
            r"((?:may|shall|right\s+to)\s+terminate.{0,400})",
            r"(termination.{0,500})",
            r"((?:days|months)\s+(?:written\s+)?notice.{0,200})",
        ],
    },
    "renewal": {
        "title": "Renewal",
        "keywords": [
            "renewal", "renew", "auto-renewal", "automatically renew",
            "automatic renewal", "renews automatically", "evergreen",
            "successive terms", "roll over",
        ],
        "section_patterns": [
            r"renewal",
            r"auto-?renewal",
            r"term\s+and\s+renewal",
        ],
        "extraction_patterns": [
            r"((?:auto|automatic|automatically).{0,400}renew.{0,200})",
            r"(renewal.{0,400})",
            r"(shall\s+renew.{0,300})",
        ],
    },
    "governing_law": {
        "title": "Governing Law",
        "keywords": [
            "governing law", "jurisdiction", "applicable law", "governed by",
            "courts of", "laws of", "venue", "dispute resolution", "arbitration",
        ],
        "section_patterns": [
            r"governing\s+law",
            r"jurisdiction",
            r"dispute\s+resolution",
            r"arbitration",
        ],
        "extraction_patterns": [
            r"((?:governed\s+by|governing\s+law).{0,400})",
            r"(jurisdiction.{0,400})",
            r"(laws?\s+of\s+the\s+(?:state|country).{0,300})",
        ],
    },
    "data_protection": {
        "title": "Data Protection",
        "keywords": [
            "data protection", "gdpr", "personal data", "privacy", "data processing",
            "data controller", "data processor", "personal information",
            "data security", "privacy policy", "ccpa", "data breach",
        ],
        "section_patterns": [
            r"data\s+protection",
            r"privacy",
            r"gdpr",
            r"personal\s+data",
            r"data\s+processing",
        ],
        "extraction_patterns": [
            r"((?:personal\s+data|data\s+protection|gdpr).{0,500})",
            r"(privacy.{0,400})",
            r"(data\s+processing.{0,400})",
        ],
    },
}


def _score_paragraph(paragraph: str, keywords: List[str]) -> float:
    """Score a paragraph based on keyword density."""
    paragraph_lower = paragraph.lower()
    matches = sum(1 for kw in keywords if kw.lower() in paragraph_lower)
    if len(paragraph) == 0:
        return 0.0
    # Normalize by paragraph length (prefer focused paragraphs)
    density = matches / max(1, len(paragraph.split()))
    return min(1.0, matches * 0.15 + density * 2.0)


def _extract_relevant_section(text: str, clause_def: dict) -> Tuple[Optional[str], float]:
    """Extract the most relevant section for a clause type."""
    keywords = clause_def["keywords"]
    section_patterns = clause_def.get("section_patterns", [])
    extraction_patterns = clause_def.get("extraction_patterns", [])

    # Split into paragraphs and sections
    paragraphs = re.split(r'\n\s*\n', text)

    # First, try to find a dedicated section header
    for i, para in enumerate(paragraphs):
        para_lines = para.strip().split('\n')
        header = para_lines[0].strip() if para_lines else ""

        for sp in section_patterns:
            if re.search(sp, header, re.IGNORECASE):
                # Found a section header - collect content
                content_parts = [para]
                # Look ahead for continuation
                for j in range(i + 1, min(i + 3, len(paragraphs))):
                    next_para = paragraphs[j].strip()
                    # Stop if we hit another section header
                    next_header = next_para.split('\n')[0] if next_para else ""
                    if len(next_header) < 60 and re.search(
                        r'^[A-Z\s\d\.]+$|^\d+[\.\)]\s+[A-Z]',
                        next_header
                    ):
                        break
                    content_parts.append(next_para)
                combined = "\n\n".join(content_parts)
                confidence = min(1.0, 0.7 + _score_paragraph(combined, keywords) * 0.3)
                return combined[:1000], confidence

    # Try extraction patterns
    for pattern in extraction_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
        if matches:
            best_match = max(matches, key=lambda m: len(m))
            confidence = min(0.85, 0.5 + _score_paragraph(best_match, keywords) * 0.5)
            return best_match[:1000].strip(), confidence

    # Score all paragraphs and return best
    scored = [(para, _score_paragraph(para, keywords)) for para in paragraphs if len(para.strip()) > 50]
    if not scored:
        return None, 0.0

    scored.sort(key=lambda x: x[1], reverse=True)
    best_para, best_score = scored[0]

    if best_score < 0.1:
        return None, 0.0

    return best_para[:1000].strip(), min(0.7, best_score)


def extract_all_clauses(text: str) -> List[Dict]:
    """Extract all clause types from contract text."""
    results = []

    for clause_type, clause_def in CLAUSE_DEFINITIONS.items():
        content, confidence = _extract_relevant_section(text, clause_def)

        results.append({
            "type": clause_type,
            "title": clause_def["title"],
            "content": content if content else "This clause was not identified in the contract.",
            "found": content is not None and confidence > 0.15,
            "confidence": round(confidence, 2),
        })

    return results


def get_clause_text(clauses: List[Dict], clause_type: str) -> Optional[str]:
    """Get extracted text for a specific clause type."""
    for clause in clauses:
        if clause["type"] == clause_type and clause["found"]:
            return clause["content"]
    return None
