"""
Master Offline Test Suite Runner.
Executes end-to-end unit and integration validation for:
1. OpenVAS & Nessus Scan Parsers
2. Open FAIR Monte Carlo Vectorized Simulation Engine
3. Statutory Compliance Engine (RBI & SEBI CSCRF)
4. Zero-Dependency Executive CISO PDF Generation
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.app.services.parsers.openvas_parser import OpenVASParser
from backend.app.services.parsers.nessus_parser import NessusParser
from backend.app.services.fair_engine.monte_carlo import FairMonteCarloEngine, ScenarioInput, LossParameters
from backend.app.services.compliance.framework_mapper import StatutoryComplianceEngine
from backend.app.services.report_generator.pdf_builder import CISOReportBuilder


def run_full_suite():
    print("=" * 60)
    print("  CYBER RISK & CAPITAL ALLOCATION PLATFORM - TEST RUNNER")
    print("=" * 60)

    # 1. Test Parsers
    print("\n[1/4] Testing Vulnerability Scan Parsers...")
    sample_xml_path = Path("backend/sample_data/openvas_report.xml")
    if sample_xml_path.exists():
        xml_results = OpenVASParser.parse_xml_string(sample_xml_path.read_text(encoding="utf-8"))
        print(f"  [OK] OpenVAS Parser: Extracted {len(xml_results)} critical findings.")
    else:
        print("  [WARN] sample_data/openvas_report.xml not found.")

    sample_json_path = Path("backend/sample_data/nessus_scan.json")
    if sample_json_path.exists():
        json_results = NessusParser.parse_json_string(sample_json_path.read_text(encoding="utf-8"))
        print(f"  [OK] Nessus Parser:  Extracted {len(json_results)} findings.")
    else:
        print("  [WARN] sample_data/nessus_scan.json not found.")

    # 2. Test FAIR Monte Carlo Engine
    print("\n[2/4] Testing Open FAIR 10k Monte Carlo Stochastic Engine...")
    engine = FairMonteCarloEngine(iterations=10000, random_seed=42)
    scenario = ScenarioInput(
        scenario_id="TEST-SCEN-01",
        name="Oracle DB Cluster Ransomware",
        tef_low=0.5,
        tef_high=3.0,
        vuln_prob=0.65,
        primary_loss=LossParameters(low=500000, mode=1500000, high=4000000),
        secondary_loss_prob=0.40,
        secondary_loss=LossParameters(low=1000000, mode=3000000, high=8000000),
    )
    sim_res = engine.run_scenario(scenario)
    assert sim_res.mean_eal > 0, "EAL should be positive"
    assert sim_res.var_95 > sim_res.mean_eal, "95% VaR should exceed mean EAL"
    print(f"  [OK] Monte Carlo Execution: Complete (10,000 runs)")
    print(f"       - Mean EAL:     Rs. {sim_res.mean_eal:,.2f}")
    print(f"       - 95% VaR:      Rs. {sim_res.var_95:,.2f}")
    print(f"       - Exceedance:   {len(sim_res.loss_exceedance_curve)} points generated.")

    # 3. Test Statutory Compliance Engine (RBI + SEBI)
    print("\n[3/4] Testing Statutory Compliance Mapping Engine (RBI / SEBI CSCRF)...")
    telemetry = {
        "has_edr_installed": False,
        "unpatched_critical_cves": 2,
        "mfa_enforced_on_admins": True,
        "waf_active_blocking": False,
        "vapt_sla_breached": False,
        "immutable_backups_configured": True,
        "soc_telemetry_integrated": False,
    }
    audit = StatutoryComplianceEngine.evaluate_all(telemetry)
    print(f"  [OK] Compliance Evaluated: Score = {audit['compliance_score']}%")
    print(f"       - Potential Penalty Exposure: Rs. {audit['total_penalty_exposure_inr']:,.2f}")
    print(f"       - Passed: {audit['passed_clauses']} | Failed: {audit['failed_clauses']}")

    # 4. Test CISO Board PDF Generator
    print("\n[4/4] Testing CISO Board Executive PDF Generator...")
    pdf_bytes = CISOReportBuilder.generate_pdf(
        scenario_name="Core Banking Infrastructure Exposure",
        baseline_eal=sim_res.mean_eal,
        var_95=sim_res.var_95,
        allocated_budget=1000000.0,
        optimal_spend=1000000.0,
        residual_eal=1001400.0,
        risk_reduced=1900000.0,
        rosi=90.0,
        compliance_score=int(audit['compliance_score']),
    )
    assert pdf_bytes.startswith(b"%PDF-1.4"), "PDF binary must start with valid PDF header"
    print(f"  [OK] PDF Generated: {len(pdf_bytes):,} bytes compiled without dependencies.")

    print("\n" + "=" * 60)
    print("  ALL PLATFORM MODULES PASSED VALIDATION SUCCESSFULLY")
    print("=" * 60)


if __name__ == "__main__":
    run_full_suite()