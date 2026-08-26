import sys
from pathlib import Path

# Add project root to sys.path so 'backend' is discoverable
sys.path.append(str(Path(__file__).resolve().parents[2]))

from backend.app.services.optimizer.milp_solver import SecurityInvestmentOptimizer, CandidateControl

controls = [
    CandidateControl("CTRL-01", "EDR on Core Servers", "Endpoint", 800000, 1200000, ["RBI Sec 3.2"]),
    CandidateControl("CTRL-02", "Enforce Admin MFA", "IAM", 200000, 700000, ["SEBI CSCRF 4.1"], mandatory=True),
    CandidateControl("CTRL-03", "WAF Deployment", "Network", 500000, 600000, ["ISO 27001 A.12"]),
    CandidateControl("CTRL-04", "Employee Phishing Training", "HR", 150000, 300000, ["NIST CSF PR.AT"])
]

solver = SecurityInvestmentOptimizer()
out = solver.optimize_allocation(controls, budget_limit=1000000, baseline_eal=2900000)

print("=" * 60)
print(f"Solver Status:          {out.solver_status}")
print(f"Budget Limit:           INR {out.budget_constraint:,.2f}")
print(f"Total Spend:            INR {out.total_spend:,.2f} ({out.budget_utilized_percentage}% utilized)")
print(f"Baseline EAL:           INR {out.baseline_eal:,.2f}")
print(f"Residual EAL:           INR {out.residual_eal:,.2f}")
print(f"Total Risk Reduced:     INR {out.total_risk_reduced:,.2f}")
print(f"Portfolio ROSI:         {out.portfolio_rosi:.2f}%")
print("Selected Controls:")
for ctrl in out.selected_controls:
    print(f"  - [x] {ctrl['name']} (INR {ctrl['cost']:,}) -> Reduces EAL by INR {ctrl['risk_reduction_delta']:,}")
print("Deferred Controls:")
for ctrl in out.deferred_controls:
    print(f"  - [ ] {ctrl['name']} (INR {ctrl['cost']:,})")
print("=" * 60)