"""
Derives candidate security controls from real ingested scan telemetry,
replacing static demo control lists with cost/impact figures scaled to
actual findings (critical count, KEV weaponization, mean FAIR vulnerability).
"""

from backend.app.services.optimizer.milp_solver import CandidateControl


def derive_controls_from_scan(
    total_findings: int,
    critical_count: int,
    kev_count: int,
    mean_fair_vuln_prob: float,
    baseline_eal: float,
) -> list[CandidateControl]:
    """
    Rule-based control recommendation. Cost scales with remediation volume
    (finding counts); risk_reduction_delta scales as a share of the scenario's
    own EAL so recommendations stay proportionate to the actual exposure.
    """
    controls: list[CandidateControl] = []

    if kev_count > 0:
        controls.append(
            CandidateControl(
                control_id="CTRL-KEV-PATCH",
                name=f"Emergency Patch Sprint: {kev_count} CISA KEV-Listed CVE(s)",
                category="Vulnerability",
                cost=round(150000.0 * kev_count, 2),
                risk_reduction_delta=round(baseline_eal * min(0.5, 0.12 * kev_count), 2),
                framework_mapping=["RBI Sec 5.1", "CISA BOD 22-01"],
                mandatory=True,
            )
        )

    if critical_count > 0:
        controls.append(
            CandidateControl(
                control_id="CTRL-CRIT-REMEDIATE",
                name=f"Critical CVE Remediation ({critical_count} findings, CVSS >= 9.0)",
                category="Vulnerability",
                cost=round(80000.0 * critical_count, 2),
                risk_reduction_delta=round(baseline_eal * min(0.4, 0.06 * critical_count), 2),
                framework_mapping=["RBI Sec 5.1"],
                mandatory=False,
            )
        )

    controls.append(
        CandidateControl(
            control_id="CTRL-MFA",
            name="Enforce Multi-Factor Authentication (MFA)",
            category="IAM",
            cost=200000.0,
            risk_reduction_delta=round(baseline_eal * 0.15, 2),
            framework_mapping=["SEBI CSCRF 4.1", "ISO 27001 A.9"],
            mandatory=True,
        )
    )

    if mean_fair_vuln_prob >= 0.5 or total_findings >= 5:
        controls.append(
            CandidateControl(
                control_id="CTRL-EDR",
                name="Deploy EDR Across Affected Asset Fleet",
                category="Endpoint",
                cost=round(50000.0 * max(1, total_findings), 2),
                risk_reduction_delta=round(baseline_eal * 0.25, 2),
                framework_mapping=["RBI Sec 3.2", "NIST CSF DE.CM"],
                mandatory=False,
            )
        )

    controls.append(
        CandidateControl(
            control_id="CTRL-WAF",
            name="Deploy Web Application Firewall (WAF)",
            category="Network",
            cost=500000.0,
            risk_reduction_delta=round(baseline_eal * 0.12, 2),
            framework_mapping=["ISO 27001 A.12", "PCI-DSS 6.6"],
            mandatory=False,
        )
    )

    controls.append(
        CandidateControl(
            control_id="CTRL-TRAINING",
            name="Employee Security & Anti-Phishing Training",
            category="Human Layer",
            cost=150000.0,
            risk_reduction_delta=round(baseline_eal * 0.08, 2),
            framework_mapping=["NIST CSF PR.AT"],
            mandatory=False,
        )
    )

    return controls
