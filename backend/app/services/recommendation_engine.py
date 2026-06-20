from typing import List, Dict


RECOMMENDATION_TEMPLATES = {
    "unlimited_liability": {
        "issue": "Unlimited Liability Exposure",
        "business_impact": "Without a liability cap, your organization could face financial claims that far exceed the value of this contract, potentially causing catastrophic financial damage.",
        "suggested_action": "Negotiate a liability cap equal to 12 months of fees paid under the contract or a fixed monetary amount. Add language such as: 'Each party's total aggregate liability shall not exceed the greater of (i) amounts paid in the 12 months preceding the claim, or (ii) USD $[X].'",
        "severity": "Critical",
        "category": "Liability",
    },
    "missing_confidentiality": {
        "issue": "Weak or Missing Confidentiality Protection",
        "business_impact": "Confidential business information, trade secrets, and proprietary data may be disclosed without legal recourse, damaging competitive advantage.",
        "suggested_action": "Add a comprehensive confidentiality clause with: (1) clear definition of confidential information, (2) restrictions on disclosure to third parties, (3) standard of care obligation (at minimum, same care as for own confidential information), (4) exceptions for publicly known information, and (5) survival clause extending obligations beyond contract termination.",
        "severity": "High",
        "category": "Confidentiality",
    },
    "auto_renewal": {
        "issue": "Auto-Renewal Trap",
        "business_impact": "Automatic renewal with a short notice window can result in unintended multi-year commitments, binding the organization to unfavorable terms or unnecessary costs.",
        "suggested_action": "Negotiate removal of auto-renewal or extend the opt-out notice period to minimum 90 days. Add a written confirmation requirement prior to each renewal. Set internal calendar reminders 4 months before contract anniversary dates.",
        "severity": "High",
        "category": "Renewal",
    },
    "weak_termination": {
        "issue": "Weak Termination Rights",
        "business_impact": "Limited ability to exit the contract exposes the business to extended obligations even when the relationship is no longer viable or the counterparty is underperforming.",
        "suggested_action": "Negotiate a mutual termination for convenience clause with no more than 30 days written notice. Ensure termination rights are not conditional solely on material breach. Add service level failure as an independent trigger for termination.",
        "severity": "High",
        "category": "Termination",
    },
    "long_payment_terms": {
        "issue": "Unfavorable Payment Terms",
        "business_impact": "Extended payment cycles strain cash flow and increase credit risk, particularly if the counterparty faces financial difficulty during the payment window.",
        "suggested_action": "Renegotiate to Net 30 payment terms. If Net 60+ is unavoidable, add late payment interest provisions (e.g., 1.5% per month), invoice dispute procedures, and the right to suspend services after 60 days of non-payment.",
        "severity": "Medium",
        "category": "Payment",
    },
    "missing_data_protection": {
        "issue": "Missing Data Protection Provisions",
        "business_impact": "Processing personal data without proper contractual provisions violates GDPR, CCPA, and other data protection regulations, potentially resulting in regulatory fines up to 4% of global annual turnover.",
        "suggested_action": "Add a Data Processing Agreement (DPA) or data protection addendum specifying: data controller/processor roles, lawful basis for processing, data subject rights, security obligations, data retention and deletion procedures, breach notification timeline (72 hours), and sub-processor restrictions.",
        "severity": "Critical",
        "category": "Data Protection",
    },
    "missing_indemnification": {
        "issue": "Indemnification Clause Risk",
        "business_impact": "Broad or one-sided indemnification exposes the organization to third-party claims that may arise from the counterparty's actions, without proportionate protection.",
        "suggested_action": "Negotiate mutual indemnification obligations limited to each party's own actions, gross negligence, or willful misconduct. Add a cap on indemnification obligations aligned with the liability cap. Exclude consequential and indirect damages from indemnification scope.",
        "severity": "Medium",
        "category": "Indemnification",
    },
}


def generate_recommendations(risk_data: Dict) -> List[Dict]:
    """Generate actionable recommendations based on risk analysis."""
    recommendations = []
    rec_id = 1

    factor_to_template = {
        "Unlimited Liability Exposure": "unlimited_liability",
        "Weak/Missing Confidentiality": "missing_confidentiality",
        "Auto-Renewal Trap": "auto_renewal",
        "Weak Termination Rights": "weak_termination",
        "Unfavorable Payment Terms": "long_payment_terms",
        "Missing Data Protection": "missing_data_protection",
        "Indemnification Risk": "missing_indemnification",
    }

    for factor in risk_data.get("factors", []):
        if not factor.get("present"):
            continue

        template_key = factor_to_template.get(factor["factor"])
        if not template_key or template_key not in RECOMMENDATION_TEMPLATES:
            continue

        template = RECOMMENDATION_TEMPLATES[template_key]
        recommendations.append({
            "id": rec_id,
            "issue": template["issue"],
            "business_impact": template["business_impact"],
            "suggested_action": template["suggested_action"],
            "severity": template["severity"],
            "category": template["category"],
        })
        rec_id += 1

    # Sort by severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    recommendations.sort(key=lambda r: severity_order.get(r["severity"], 99))

    # Re-number after sort
    for i, rec in enumerate(recommendations, 1):
        rec["id"] = i

    return recommendations
