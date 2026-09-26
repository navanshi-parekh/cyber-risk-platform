"""
Zero-Dependency Executive CISO Board Briefing PDF Generator.
Constructs valid binary multi-page PDF documents natively using Python's standard library.
100% compatible with Python 3.10 through Python 3.14+.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional


def format_inr(amount: float) -> str:
    """Formats numeric values to Indian Rupee notation (Lakhs/Crores)."""
    if amount >= 10000000:
        return f"Rs. {amount / 10000000:.2f} Cr"
    if amount >= 100000:
        return f"Rs. {amount / 100000:.2f} L"
    return f"Rs. {amount:,.0f}"


class SimplePDFCanvas:
    """Minimalistic pure-Python multi-page PDF 1.4 stream builder."""

    def __init__(self):
        self.pages: List[List[str]] = [[]]
        self.width = 612.0
        self.height = 792.0

    def new_page(self):
        self.pages.append([])

    def add_text(self, text: str, x: float, y: float, size: float = 10, font: str = "F1", r: float = 0, g: float = 0, b: float = 0):
        clean_text = str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        cmd = f"BT /{font} {size} Tf {r:.2f} {g:.2f} {b:.2f} rg {x:.2f} {y:.2f} Td ({clean_text}) Tj ET"
        self.pages[-1].append(cmd)

    def draw_rect(self, x: float, y: float, w: float, h: float, fill_rgb=(0.95, 0.96, 0.98), stroke_rgb=(0.8, 0.83, 0.88)):
        fr, fg, fb = fill_rgb
        sr, sg, sb = stroke_rgb
        cmd = f"{fr:.2f} {fg:.2f} {fb:.2f} rg {sr:.2f} {sg:.2f} {sb:.2f} RG 0.75 w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re B"
        self.pages[-1].append(cmd)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float, stroke_rgb=(0.02, 0.71, 0.83), width: float = 1.5):
        sr, sg, sb = stroke_rgb
        cmd = f"{sr:.2f} {sg:.2f} {sb:.2f} RG {width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S"
        self.pages[-1].append(cmd)

    def add_footer(self, page_num: int, total_pages: int, label: str):
        self.draw_line(36, 30, 576, 30, stroke_rgb=(0.85, 0.88, 0.92), width=0.75)
        self.add_text(label, 36, 18, size=7, font="F1", r=0.55, g=0.6, b=0.66)
        self.add_text(f"Page {page_num} of {total_pages}", 520, 18, size=7, font="F1", r=0.55, g=0.6, b=0.66)

    def compile(self) -> bytes:
        num_pages = len(self.pages)
        kids_ids = [3 + i for i in range(num_pages)]
        content_start = 3 + num_pages
        font1_id = content_start + num_pages
        font2_id = font1_id + 1

        objects: List[bytes] = []

        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        kids_str = " ".join(f"{k} 0 R" for k in kids_ids)
        objects.append(f"<< /Type /Pages /Kids [{kids_str}] /Count {num_pages} >>".encode("latin-1"))

        for i in range(num_pages):
            objects.append(
                (
                    f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.width} {self.height}] "
                    f"/Contents {content_start + i} 0 R /Resources << /Font << /F1 {font1_id} 0 R /F2 {font2_id} 0 R >> >> >>"
                ).encode("latin-1")
            )

        for i in range(num_pages):
            content_stream = "\n".join(self.pages[i]).encode("latin-1")
            obj = f"<< /Length {len(content_stream)} >>\nstream\n".encode("latin-1") + content_stream + b"\nendstream"
            objects.append(obj)

        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

        pdf = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]

        for i, obj in enumerate(objects, start=1):
            offsets.append(len(pdf))
            pdf.extend(f"{i} 0 obj\n".encode("latin-1"))
            pdf.extend(obj)
            pdf.extend(b"\nendobj\n")

        xref_pos = len(pdf)
        pdf.extend(f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode("latin-1"))
        for offset in offsets[1:]:
            pdf.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))

        pdf.extend(f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("latin-1"))
        return bytes(pdf)


DARK = (0.06, 0.09, 0.16)
MUTED = (0.39, 0.45, 0.55)
BODY = (0.2, 0.25, 0.33)
RED = (0.86, 0.15, 0.15)
BLUE = (0.01, 0.52, 0.78)
GREEN = (0.02, 0.59, 0.41)
LINE_BLUE = (0.02, 0.71, 0.83)
DARK_RGB = DARK


def _kw(rgb):
    r, g, b = rgb
    return {"r": r, "g": g, "b": b}


DARK_K = _kw(DARK)
MUTED_K = _kw(MUTED)
BODY_K = _kw(BODY)
RED_K = _kw(RED)
BLUE_K = _kw(BLUE)
GREEN_K = _kw(GREEN)


class CISOReportBuilder:
    @staticmethod
    def generate_pdf(
        scenario_name: str = "Core Banking Cluster Ransomware Exposure",
        baseline_eal: float = 2901400.0,
        median_loss: float = 0.0,
        std_dev: float = 0.0,
        var_90: float = 0.0,
        var_95: float = 12300000.0,
        var_99: float = 0.0,
        iterations: int = 10000,
        allocated_budget: float = 1000000.0,
        optimal_spend: float = 1000000.0,
        residual_eal: float = 1001400.0,
        risk_reduced: float = 1900000.0,
        rosi: float = 90.0,
        budget_utilized_percentage: float = 0.0,
        solver_status: str = "Optimal",
        selected_controls: Optional[List[Dict[str, Any]]] = None,
        deferred_controls: Optional[List[Dict[str, Any]]] = None,
        compliance_score: int = 67,
        compliance_clauses: Optional[List[Dict[str, Any]]] = None,
        scan_summary: Optional[Dict[str, Any]] = None,
        top_findings: Optional[List[Dict[str, Any]]] = None,
        historical_runs: Optional[List[Dict[str, Any]]] = None,
        data_source_note: str = "Baseline scenario (no live scan ingested).",
    ) -> bytes:
        if selected_controls is None:
            selected_controls = [
                {"control_id": "CTRL-01", "name": "Deploy EDR on Core DB Cluster", "category": "Endpoint", "cost": 800000, "risk_reduction_delta": 1200000},
                {"control_id": "CTRL-02", "name": "Enforce Multi-Factor Authentication (MFA)", "category": "IAM", "cost": 200000, "risk_reduction_delta": 700000},
            ]
        if deferred_controls is None:
            deferred_controls = []
        if compliance_clauses is None:
            compliance_clauses = [
                {"framework": "RBI CSF", "clause": "Annex 1 - Sec 3.2", "requirement": "Continuous Endpoint Detection & Response (EDR)", "status": "Partially Met"},
                {"framework": "RBI CSF", "clause": "Annex 2 - Sec 5.1", "requirement": "Automated Critical Vulnerability Patching SLA (< 48 hrs)", "status": "Gap"},
                {"framework": "RBI CSF", "clause": "Annex 1 - Sec 4.1", "requirement": "Privileged Identity Multi-Factor Authentication", "status": "Met"},
                {"framework": "SEBI CSCRF", "clause": "Sec 4.1", "requirement": "MFA on Market Intermediary Gateways", "status": "Met"},
                {"framework": "SEBI CSCRF", "clause": "Sec 7.3", "requirement": "Web Application Firewall (WAF) Layer 7 Inspection", "status": "Gap"},
                {"framework": "SEBI CSCRF", "clause": "Sec 11.4", "requirement": "Immutable Air-Gapped Backup & Recovery (WORM)", "status": "Partially Met"},
                {"framework": "SEBI CSCRF", "clause": "Sec 14.1", "requirement": "Centralized SOC Telemetry & 6-Hour Incident SLA", "status": "Met"},
            ]

        total_pages = 3 if scan_summary else 2
        pdf = SimplePDFCanvas()
        now_str = datetime.now().strftime("%d %b %Y, %H:%M")

        # ------------------------------------------------------------------
        # PAGE 1 — Executive Summary & Financial Exposure
        # ------------------------------------------------------------------
        pdf.add_text("CYBER EXPOSURE & CAPITAL ALLOCATION REPORT", 36, 750, size=15, font="F2", **DARK_K)
        pdf.add_text("Executive Board Briefing | Open FAIR Risk Quantification & MILP Capital Optimization", 36, 736, size=8.5, font="F1", **MUTED_K)
        pdf.add_text(f"Generated: {now_str}  |  Confidential", 390, 750, size=8.5, font="F1", **MUTED_K)
        pdf.draw_line(36, 726, 576, 726, stroke_rgb=LINE_BLUE, width=1.5)

        pdf.draw_rect(36, 630, 540, 84, fill_rgb=(0.97, 0.98, 0.99), stroke_rgb=(0.8, 0.83, 0.88))
        pdf.add_text("Executive Summary & Quantitative Baseline", 48, 698, size=9.5, font="F2", **DARK_K)
        pdf.add_text(f"Under current unmitigated posture for {scenario_name[:75]},", 48, 683, size=8.5, font="F1", **BODY_K)
        pdf.add_text(f"baseline Expected Annual Loss (EAL) is {format_inr(baseline_eal)} across {iterations:,} Monte Carlo iterations,", 48, 670, size=8.5, font="F1", **BODY_K)
        pdf.add_text(f"with a 95% Value-at-Risk (VaR) of {format_inr(var_95)} (1-in-20 year worst case).", 48, 657, size=8.5, font="F1", **BODY_K)
        pdf.add_text(f"An optimized budget of {format_inr(optimal_spend)} ({budget_utilized_percentage:.1f}% of {format_inr(allocated_budget)} available)", 48, 644, size=8.5, font="F1", **BODY_K)
        pdf.add_text(f"reduces exposure to {format_inr(residual_eal)}, an estimated ROSI of {rosi:.1f}%. Data source: {data_source_note}", 48, 631, size=8.5, font="F1", **BODY_K)

        pdf.add_text("1. Primary Financial & Exposure Indicators", 36, 610, size=10, font="F2", **DARK_K)
        cards = [
            ("Baseline Annual Loss", format_inr(baseline_eal), RED),
            ("95% Value-at-Risk", format_inr(var_95), RED),
            ("Optimal Spend", format_inr(optimal_spend), BLUE),
            ("Portfolio ROSI", f"{rosi:.1f}%", GREEN),
        ]
        card_w = 127
        for i, (title, val, (vr, vg, vb)) in enumerate(cards):
            cx = 36 + (i * (card_w + 10))
            pdf.draw_rect(cx, 541, card_w, 55, fill_rgb=(0.95, 0.96, 0.98), stroke_rgb=(0.85, 0.88, 0.92))
            pdf.add_text(title, cx + 10, 580, size=8, font="F1", **MUTED_K)
            pdf.add_text(val, cx + 10, 560, size=12, font="F2", r=vr, g=vg, b=vb)
            pdf.add_text("Monte Carlo Calculated", cx + 10, 546, size=7, font="F1", r=0.6, g=0.65, b=0.7)

        pdf.add_text("2. Loss Distribution Statistics", 36, 512, size=10, font="F2", **DARK_K)
        stats_rows = [
            ("Mean EAL", format_inr(baseline_eal)),
            ("90% VaR", format_inr(var_90)),
            ("95% VaR", format_inr(var_95)),
            ("99% VaR", format_inr(var_99)),
        ]
        stat_w = 130
        for i, (label, val) in enumerate(stats_rows):
            cx = 36 + (i * stat_w)
            pdf.draw_rect(cx, 470, stat_w - 4, 34, fill_rgb=(1, 1, 1), stroke_rgb=(0.88, 0.91, 0.94))
            pdf.add_text(label, cx + 6, 495, size=6.5, font="F1", **MUTED_K)
            pdf.add_text(val, cx + 6, 480, size=8, font="F2", **DARK_K)

        pdf.add_text("3. 6-Month Risk Reduction Trajectory", 36, 448, size=10, font="F2", **DARK_K)
        pdf.draw_rect(36, 425, 540, 16, fill_rgb=DARK_RGB, stroke_rgb=DARK_RGB)
        pdf.add_text("Period", 42, 430, size=7.5, font="F2", r=1, g=1, b=1)
        pdf.add_text("Mean EAL", 170, 430, size=7.5, font="F2", r=1, g=1, b=1)
        pdf.add_text("95% VaR", 290, 430, size=7.5, font="F2", r=1, g=1, b=1)
        pdf.add_text("Budget Allocated", 400, 430, size=7.5, font="F2", r=1, g=1, b=1)
        pdf.add_text("ROSI", 510, 430, size=7.5, font="F2", r=1, g=1, b=1)

        hist_y = 409
        history_rows = (historical_runs or [])[-6:]
        if not history_rows:
            pdf.add_text("No historical runs recorded yet.", 42, hist_y, size=7.5, font="F1", **MUTED_K)
            hist_y -= 16
        for row in history_rows:
            pdf.draw_rect(36, hist_y, 540, 16, fill_rgb=(1, 1, 1), stroke_rgb=(0.9, 0.92, 0.95))
            pdf.add_text(str(row.get("timestamp", "")), 42, hist_y + 4, size=7.5, font="F1", **BODY_K)
            pdf.add_text(format_inr(row.get("mean_eal", 0)), 170, hist_y + 4, size=7.5, font="F1", **BODY_K)
            pdf.add_text(format_inr(row.get("var_95", 0)), 290, hist_y + 4, size=7.5, font="F1", **BODY_K)
            pdf.add_text(format_inr(row.get("allocated_budget", 0)), 400, hist_y + 4, size=7.5, font="F1", **BODY_K)
            pdf.add_text(f"{row.get('portfolio_rosi', 0):.1f}%", 510, hist_y + 4, size=7.5, font="F2", **GREEN_K)
            hist_y -= 16

        pdf.add_footer(1, total_pages, "CyberExposure Quant | SIH26105 | Enterprise FinTech & Banking Risk Framework")

        # ------------------------------------------------------------------
        # PAGE 2 — Capital Allocation Roadmap & Regulatory Compliance
        # ------------------------------------------------------------------
        pdf.new_page()
        pdf.add_text("CAPITAL ALLOCATION & REGULATORY COMPLIANCE", 36, 750, size=13, font="F2", **DARK_K)
        pdf.draw_line(36, 738, 576, 738, stroke_rgb=LINE_BLUE, width=1.5)

        pdf.add_text("4. Recommended Capital Allocation Roadmap (Selected Controls)", 36, 718, size=10, font="F2", **DARK_K)
        pdf.draw_rect(36, 690, 540, 18, fill_rgb=DARK_RGB, stroke_rgb=DARK_RGB)
        pdf.add_text("Control ID", 42, 696, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Security Control Title", 110, 696, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Category", 310, 696, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Cost (INR)", 390, 696, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Risk Reduction", 480, 696, size=8, font="F2", r=1, g=1, b=1)

        curr_y = 672
        for ctrl in selected_controls:
            pdf.draw_rect(36, curr_y, 540, 18, fill_rgb=(1, 1, 1), stroke_rgb=(0.88, 0.91, 0.94))
            pdf.add_text(ctrl["control_id"], 42, curr_y + 5, size=8, font="F2", **DARK_K)
            pdf.add_text(str(ctrl["name"])[:38], 110, curr_y + 5, size=8, font="F1", r=0.15, g=0.2, b=0.28)
            pdf.add_text(ctrl.get("category", "General"), 310, curr_y + 5, size=8, font="F1", **MUTED_K)
            pdf.add_text(format_inr(ctrl["cost"]), 390, curr_y + 5, size=8, font="F2", **DARK_K)
            pdf.add_text(f"-{format_inr(ctrl['risk_reduction_delta'])}", 480, curr_y + 5, size=8, font="F2", **GREEN_K)
            curr_y -= 18

        pdf.draw_rect(36, curr_y, 540, 18, fill_rgb=(0.95, 0.96, 0.98), stroke_rgb=(0.85, 0.88, 0.92))
        pdf.add_text("TOTAL ALLOCATED SPEND", 42, curr_y + 5, size=8, font="F2", **DARK_K)
        pdf.add_text(format_inr(optimal_spend), 390, curr_y + 5, size=8, font="F2", **DARK_K)
        pdf.add_text(f"-{format_inr(risk_reduced)} EAL", 480, curr_y + 5, size=8, font="F2", **GREEN_K)
        curr_y -= 30

        if deferred_controls:
            pdf.add_text(f"5. Deferred Controls ({len(deferred_controls)}, budget-constrained)", 36, curr_y, size=9.5, font="F2", **DARK_K)
            curr_y -= 20
            for ctrl in deferred_controls[:4]:
                pdf.add_text(f"- {ctrl['name'][:70]} ({format_inr(ctrl['cost'])}, would reduce EAL by {format_inr(ctrl['risk_reduction_delta'])})", 42, curr_y, size=7.5, font="F1", **MUTED_K)
                curr_y -= 13
            curr_y -= 10

        pdf.add_text(f"Solver Status: {solver_status}", 36, curr_y, size=8, font="F1", **MUTED_K)
        curr_y -= 24

        pdf.add_text("6. Statutory & Regulatory Compliance Matrix", 36, curr_y, size=10, font="F2", **DARK_K)
        curr_y -= 22
        pdf.draw_rect(36, curr_y, 540, 16, fill_rgb=DARK_RGB, stroke_rgb=DARK_RGB)
        pdf.add_text("Framework", 42, curr_y + 4, size=7.5, font="F2", r=1, g=1, b=1)
        pdf.add_text("Clause", 150, curr_y + 4, size=7.5, font="F2", r=1, g=1, b=1)
        pdf.add_text("Requirement", 240, curr_y + 4, size=7.5, font="F2", r=1, g=1, b=1)
        pdf.add_text("Status", 500, curr_y + 4, size=7.5, font="F2", r=1, g=1, b=1)
        curr_y -= 16
        for clause in compliance_clauses:
            status = clause.get("status", "Gap")
            sr, sg, sb = GREEN if status == "Met" else (BLUE if status == "Partially Met" else RED)
            pdf.draw_rect(36, curr_y, 540, 16, fill_rgb=(1, 1, 1), stroke_rgb=(0.9, 0.92, 0.95))
            pdf.add_text(clause.get("framework", ""), 42, curr_y + 4, size=7, font="F1", **BODY_K)
            pdf.add_text(clause.get("clause", ""), 150, curr_y + 4, size=7, font="F1", **BODY_K)
            pdf.add_text(str(clause.get("requirement", ""))[:52], 240, curr_y + 4, size=7, font="F1", **BODY_K)
            pdf.add_text(status, 500, curr_y + 4, size=7, font="F2", r=sr, g=sg, b=sb)
            curr_y -= 16

        curr_y -= 10
        pdf.add_text(f"Overall Statutory Compliance Score: {compliance_score}%", 36, curr_y, size=8.5, font="F2", **DARK_K)

        pdf.add_footer(2, total_pages, "CyberExposure Quant | SIH26105 | Enterprise FinTech & Banking Risk Framework")

        # ------------------------------------------------------------------
        # PAGE 3 — Technical SOC Telemetry (only if a real scan was ingested)
        # ------------------------------------------------------------------
        if scan_summary:
            pdf.new_page()
            pdf.add_text("TECHNICAL SOC TELEMETRY & THREAT INTELLIGENCE", 36, 750, size=13, font="F2", **DARK_K)
            pdf.draw_line(36, 738, 576, 738, stroke_rgb=LINE_BLUE, width=1.5)

            pdf.add_text("7. Ingested Scan Summary", 36, 718, size=10, font="F2", **DARK_K)
            pdf.add_text(f"Source File: {scan_summary.get('filename', 'N/A')}  ({scan_summary.get('detected_scanner', 'N/A')})", 42, 700, size=8.5, font="F1", **BODY_K)
            pdf.add_text(f"Total Findings: {scan_summary.get('total_findings_parsed', 0)}   |   Critical (CVSS>=9.0): {scan_summary.get('critical_findings_count', 0)}   |   CISA KEV Weaponized: {scan_summary.get('kev_weaponized_count', 0)}", 42, 686, size=8.5, font="F1", **BODY_K)
            pdf.add_text(f"Mean FAIR Vulnerability Probability: {scan_summary.get('mean_fair_vuln_prob', 0) * 100:.1f}%", 42, 672, size=8.5, font="F1", **BODY_K)

            pdf.add_text("8. Top Enriched Vulnerability Findings", 36, 648, size=10, font="F2", **DARK_K)
            pdf.draw_rect(36, 622, 540, 16, fill_rgb=DARK_RGB, stroke_rgb=DARK_RGB)
            pdf.add_text("Asset", 42, 626, size=7.5, font="F2", r=1, g=1, b=1)
            pdf.add_text("Vulnerability", 130, 626, size=7.5, font="F2", r=1, g=1, b=1)
            pdf.add_text("CVSS", 340, 626, size=7.5, font="F2", r=1, g=1, b=1)
            pdf.add_text("EPSS", 385, 626, size=7.5, font="F2", r=1, g=1, b=1)
            pdf.add_text("KEV", 430, 626, size=7.5, font="F2", r=1, g=1, b=1)
            pdf.add_text("FAIR Vuln", 470, 626, size=7.5, font="F2", r=1, g=1, b=1)
            pdf.add_text("CVE", 525, 626, size=7.5, font="F2", r=1, g=1, b=1)

            f_y = 606
            for finding in (top_findings or [])[:16]:
                pdf.draw_rect(36, f_y, 540, 16, fill_rgb=(1, 1, 1), stroke_rgb=(0.9, 0.92, 0.95))
                pdf.add_text(str(finding.get("asset_ip", ""))[:16], 42, f_y + 4, size=7, font="F1", **BODY_K)
                pdf.add_text(str(finding.get("vulnerability_name", ""))[:35], 130, f_y + 4, size=7, font="F1", **BODY_K)
                pdf.add_text(f"{finding.get('cvss_score', 0):.1f}", 340, f_y + 4, size=7, font="F2", **RED_K)
                pdf.add_text(f"{finding.get('epss_probability', 0) * 100:.1f}%", 385, f_y + 4, size=7, font="F1", **BODY_K)
                kv_r, kv_g, kv_b = RED if finding.get("is_cisa_kev") else (0.6, 0.65, 0.7)
                pdf.add_text("YES" if finding.get("is_cisa_kev") else "no", 430, f_y + 4, size=7, font="F2", r=kv_r, g=kv_g, b=kv_b)
                pdf.add_text(f"{finding.get('fair_vulnerability_probability', 0) * 100:.0f}%", 470, f_y + 4, size=7, font="F1", **BODY_K)
                cves = ", ".join(finding.get("cve_list", [])[:1])
                pdf.add_text(cves[:16], 525, f_y + 4, size=6.5, font="F1", **MUTED_K)
                f_y -= 16

            pdf.add_footer(3, total_pages, "CyberExposure Quant | SIH26105 | Enterprise FinTech & Banking Risk Framework")

        # ------------------------------------------------------------------
        # Sign-off block on the last page
        # ------------------------------------------------------------------
        sign_y = 70
        pdf.add_text("Prepared By: Chief Information Security Officer (CISO)", 36, sign_y + 12, size=8, font="F2", **BODY_K)
        pdf.add_text("Signature: ___________________________", 36, sign_y, size=8, font="F1", **MUTED_K)
        pdf.add_text("Approved By: Board Risk Committee / CFO", 370, sign_y + 12, size=8, font="F2", **BODY_K)
        pdf.add_text("Signature: ___________________________", 370, sign_y, size=8, font="F1", **MUTED_K)

        return pdf.compile()
