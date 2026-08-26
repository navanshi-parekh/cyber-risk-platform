"""
Statutory Compliance & Regulatory Framework Mapping Service.
Evaluates normalized vulnerability and infrastructure telemetry against
RBI Cyber Security Framework and SEBI CSCRF mandates, computing compliance
scores and statutory penalty exposure.
"""

from typing import List, Dict, Any, Optional


class StatutoryComplianceEngine:
    """Evaluates enterprise telemetry against RBI and SEBI CSCRF regulatory mandates."""

    RBI_MANDATES = [
        {
            "clause_id": "RBI-ANNEX-1-3.2",
            "section": "RBI Annex 1 - Section 3.2",
            "framework": "RBI",
            "title": "Continuous Endpoint Detection & Response (EDR)",
            "domain": "Network & Endpoint Security",
            "required_control_id": "CTRL-01",
            "penalty_base_inr": 1500000.0,  # ₹ 15 Lakhs fine liability
            "check_rule": lambda t: t.get("has_edr_installed", False),
            "description": "Continuous behavioral monitoring across critical database clusters and transaction processing nodes.",
        },
        {
            "clause_id": "RBI-ANNEX-2-5.1",
            "section": "RBI Annex 2 - Section 5.1",
            "framework": "RBI",
            "title": "Automated Patch Management & Critical CVE SLA",
            "domain": "Vulnerability Management",
            "required_control_id": "CTRL-04",
            "penalty_base_inr": 2000000.0,  # ₹ 20 Lakhs fine liability
            "check_rule": lambda t: t.get("unpatched_critical_cves", 0) == 0,
            "description": "Remediation of CVSS >= 9.0 and CISA KEV vulnerabilities within 48 hours on critical banking infrastructure.",
        },
        {
            "clause_id": "RBI-ANNEX-1-4.1",
            "section": "RBI Annex 1 - Section 4.1",
            "framework": "RBI",
            "title": "Privileged Identity Multi-Factor Authentication",
            "domain": "IAM & Access Control",
            "required_control_id": "CTRL-02",
            "penalty_base_inr": 1000000.0,  # ₹ 10 Lakhs fine liability
            "check_rule": lambda t: t.get("mfa_enforced_on_admins", True),
            "description": "Hardware or biometric MFA enforcement across all administrator and database access roles.",
        },
    ]

    SEBI_CSCRF_MANDATES = [
        {
            "clause_id": "SEBI-CSCRF-4.1",
            "section": "SEBI CSCRF Section 4.1",
            "framework": "SEBI_CSCRF",
            "title": "Multi-Factor Authentication on Privileged Access Gateways",
            "domain": "Identity & Access Management",
            "required_control_id": "CTRL-02",
            "penalty_base_inr": 1000000.0,  # ₹ 10 Lakhs
            "check_rule": lambda t: t.get("mfa_enforced_on_admins", True),
            "description": "Mandatory phishing-resistant MFA across all market intermediary administration and API jump boxes.",
        },
        {
            "clause_id": "SEBI-CSCRF-7.3",
            "section": "SEBI CSCRF Section 7.3",
            "framework": "SEBI_CSCRF",
            "title": "Critical Attack Surface Web Application Firewall (WAF)",
            "domain": "Application Security",
            "required_control_id": "CTRL-03",
            "penalty_base_inr": 750000.0,  # ₹ 7.5 Lakhs
            "check_rule": lambda t: t.get("waf_active_blocking", False),
            "description": "Layer 7 stateful inspection and TLS decryption on internet-facing market portals.",
        },
        {
            "clause_id": "SEBI-CSCRF-8.2",
            "section": "SEBI CSCRF Section 8.2",
            "framework": "SEBI_CSCRF",
            "title": "Vulnerability Assessment & Penetration Testing (VAPT) SLA",
            "domain": "Vulnerability Management",
            "required_control_id": "CTRL-04",
            "penalty_base_inr": 1200000.0,  # ₹ 12 Lakhs
            "check_rule": lambda t: t.get("vapt_sla_breached", False) is False,
            "description": "Mandatory closure of high-risk audit findings prior to production deployment.",
        },
        {
            "clause_id": "SEBI-CSCRF-11.4",
            "section": "SEBI CSCRF Section 11.4",
            "framework": "SEBI_CSCRF",
            "title": "Immutable Air-Gapped Backup & Disaster Recovery",
            "domain": "Resilience & Business Continuity",
            "required_control_id": "CTRL-06",
            "penalty_base_inr": 2500000.0,  # ₹ 25 Lakhs
            "check_rule": lambda t: t.get("immutable_backups_configured", True),
            "description": "WORM (Write Once Read Many) backup storage with sub-4-hour Recovery Point Objective (RPO).",
        },
        {
            "clause_id": "SEBI-CSCRF-14.1",
            "section": "SEBI CSCRF Section 14.1",
            "framework": "SEBI_CSCRF",
            "title": "Continuous SOC Log Telemetry & 6-Hour Incident Reporting",
            "domain": "Security Operations Center",
            "required_control_id": "CTRL-01",
            "penalty_base_inr": 1800000.0,  # ₹ 18 Lakhs
            "check_rule": lambda t: t.get("soc_telemetry_integrated", True),
            "description": "Centralized SIEM/SOC event correlation with statutory incident notification to SEBI within 6 hours.",
        },
    ]

    @classmethod
    def _evaluate_clause_list(
        cls, clauses: List[Dict[str, Any]], telemetry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Helper to evaluate a specific set of regulatory clauses."""
        results = []
        total_penalty = 0.0
        passed = 0

        for m in clauses:
            is_compliant = bool(m["check_rule"](telemetry))
            status = "COMPLIANT" if is_compliant else "NON_COMPLIANT"
            penalty = 0.0 if is_compliant else m["penalty_base_inr"]

            if is_compliant:
                passed += 1
            else:
                total_penalty += penalty

            results.append({
                "clause_id": m["clause_id"],
                "section": m["section"],
                "framework": m["framework"],
                "title": m["title"],
                "domain": m["domain"],
                "description": m["description"],
                "status": status,
                "mapped_control": m["required_control_id"],
                "potential_fine_inr": penalty,
            })

        score = round((passed / len(clauses)) * 100, 1) if clauses else 100.0

        return {
            "compliance_score": score,
            "total_clauses": len(clauses),
            "passed_clauses": passed,
            "failed_clauses": len(clauses) - passed,
            "total_penalty_exposure_inr": total_penalty,
            "clauses": results,
        }

    @classmethod
    def evaluate_rbi(cls, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates posture exclusively for the RBI Cyber Security Framework."""
        res = cls._evaluate_clause_list(cls.RBI_MANDATES, telemetry)
        res["framework"] = "RBI Cyber Security Framework"
        return res

    @classmethod
    def evaluate_sebi(cls, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates posture exclusively for SEBI CSCRF."""
        res = cls._evaluate_clause_list(cls.SEBI_CSCRF_MANDATES, telemetry)
        res["framework"] = "SEBI Cybersecurity & Cyber Resilience Framework (CSCRF)"
        return res

    @classmethod
    def evaluate_all(cls, telemetry: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluates posture across all Indian statutory frameworks simultaneously."""
        all_clauses = cls.RBI_MANDATES + cls.SEBI_CSCRF_MANDATES
        res = cls._evaluate_clause_list(all_clauses, telemetry)
        res["framework"] = "Unified Indian Regulatory Audit (RBI + SEBI CSCRF)"
        res["rbi_breakdown"] = cls.evaluate_rbi(telemetry)
        res["sebi_breakdown"] = cls.evaluate_sebi(telemetry)
        return res