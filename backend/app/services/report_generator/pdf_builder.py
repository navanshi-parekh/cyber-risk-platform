"""
Zero-Dependency Executive CISO Board Briefing PDF Generator.
Constructs valid binary PDF documents natively using Python's standard library.
100% compatible with Python 3.10 through Python 3.13+.
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
    """Minimalistic pure-Python PDF 1.4 stream builder."""

    def __init__(self):
        self.stream_commands = []
        self.width = 612.0
        self.height = 792.0

    def add_text(self, text: str, x: float, y: float, size: float = 10, font: str = "F1", r: float = 0, g: float = 0, b: float = 0):
        clean_text = text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        cmd = f"BT /{font} {size} Tf {r:.2f} {g:.2f} {b:.2f} rg {x:.2f} {y:.2f} Td ({clean_text}) Tj ET"
        self.stream_commands.append(cmd)

    def draw_rect(self, x: float, y: float, w: float, h: float, fill_rgb=(0.95, 0.96, 0.98), stroke_rgb=(0.8, 0.83, 0.88)):
        fr, fg, fb = fill_rgb
        sr, sg, sb = stroke_rgb
        cmd = f"{fr:.2f} {fg:.2f} {fb:.2f} rg {sr:.2f} {sg:.2f} {sb:.2f} RG 0.75 w {x:.2f} {y:.2f} {w:.2f} {h:.2f} re B"
        self.stream_commands.append(cmd)

    def draw_line(self, x1: float, y1: float, x2: float, y2: float, stroke_rgb=(0.02, 0.71, 0.83), width: float = 1.5):
        sr, sg, sb = stroke_rgb
        cmd = f"{sr:.2f} {sg:.2f} {sb:.2f} RG {width:.2f} w {x1:.2f} {y1:.2f} m {x2:.2f} {y2:.2f} l S"
        self.stream_commands.append(cmd)

    def compile(self) -> bytes:
        content_stream = "\n".join(self.stream_commands).encode("latin-1")
        
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {self.width} {self.height}] /Contents 4 0 R /Resources << /Font << /F1 5 0 R /F2 6 0 R >> >> >>".encode("latin-1"),
            f"<< /Length {len(content_stream)} >>\nstream\n".encode("latin-1") + content_stream + b"\nendstream",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
            b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>",
        ]

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


class CISOReportBuilder:
    @staticmethod
    def generate_pdf(
        scenario_name: str = "Core Banking Cluster Ransomware Exposure",
        baseline_eal: float = 2901400.0,
        var_95: float = 12300000.0,
        allocated_budget: float = 1000000.0,
        optimal_spend: float = 1000000.0,
        residual_eal: float = 1001400.0,
        risk_reduced: float = 1900000.0,
        rosi: float = 90.0,
        selected_controls: Optional[List[Dict[str, Any]]] = None,
        compliance_score: int = 67,
    ) -> bytes:
        if selected_controls is None:
            selected_controls = [
                {
                    "control_id": "CTRL-01",
                    "name": "Deploy EDR on Core DB Cluster",
                    "category": "Endpoint",
                    "cost": 800000,
                    "risk_reduction_delta": 1200000,
                },
                {
                    "control_id": "CTRL-02",
                    "name": "Enforce Multi-Factor Authentication (MFA)",
                    "category": "IAM",
                    "cost": 200000,
                    "risk_reduction_delta": 700000,
                },
            ]

        pdf = SimplePDFCanvas()

        # Header Title & Accents
        pdf.add_text("CYBER EXPOSURE & CAPITAL ALLOCATION REPORT", 36, 750, size=15, font="F2", r=0.06, g=0.09, b=0.16)
        pdf.add_text("Executive Board Briefing | Open FAIR Risk Quantification & MILP Capital Optimization", 36, 736, size=8.5, font="F1", r=0.39, g=0.45, b=0.55)
        pdf.add_text(f"Date: {datetime.now().strftime('%d %b %Y')}  |  Confidential", 390, 750, size=8.5, font="F1", r=0.39, g=0.45, b=0.55)
        pdf.draw_line(36, 726, 576, 726, stroke_rgb=(0.02, 0.71, 0.83), width=1.5)

        # Executive Summary Box
        pdf.draw_rect(36, 642, 540, 72, fill_rgb=(0.97, 0.98, 0.99), stroke_rgb=(0.8, 0.83, 0.88))
        pdf.add_text("Executive Summary & Quantitative Baseline:", 48, 698, size=9.5, font="F2", r=0.06, g=0.09, b=0.16)
        pdf.add_text(f"Under current unmitigated posture for {scenario_name},", 48, 683, size=8.5, font="F1", r=0.2, g=0.25, b=0.33)
        pdf.add_text(f"baseline Expected Annual Loss (EAL) is {format_inr(baseline_eal)} with a 95% Value-at-Risk (VaR) of {format_inr(var_95)}.", 48, 670, size=8.5, font="F1", r=0.2, g=0.25, b=0.33)
        pdf.add_text(f"Allocating an optimized security budget of {format_inr(optimal_spend)} achieves a net risk reduction of {format_inr(risk_reduced)},", 48, 657, size=8.5, font="F1", r=0.2, g=0.25, b=0.33)
        pdf.add_text(f"dropping residual exposure to {format_inr(residual_eal)} with an estimated Return on Security Investment (ROSI) of {rosi:.1f}%.", 48, 644, size=8.5, font="F1", r=0.2, g=0.25, b=0.33)

        # 4 Key Financial Risk Indicators
        pdf.add_text("1. Primary Financial & Exposure Indicators", 36, 624, size=10, font="F2", r=0.06, g=0.09, b=0.16)
        
        cards = [
            ("Baseline Annual Loss", format_inr(baseline_eal), (0.86, 0.15, 0.15)),
            ("95% Value-at-Risk", format_inr(var_95), (0.86, 0.15, 0.15)),
            ("Optimal Spend", format_inr(optimal_spend), (0.01, 0.52, 0.78)),
            ("Portfolio ROSI", f"{rosi:.1f}%", (0.02, 0.59, 0.41)),
        ]
        
        card_w = 127
        for i, (title, val, (vr, vg, vb)) in enumerate(cards):
            cx = 36 + (i * (card_w + 10))
            pdf.draw_rect(cx, 555, card_w, 55, fill_rgb=(0.95, 0.96, 0.98), stroke_rgb=(0.85, 0.88, 0.92))
            pdf.add_text(title, cx + 10, 594, size=8, font="F1", r=0.39, g=0.45, b=0.55)
            pdf.add_text(val, cx + 10, 574, size=12, font="F2", r=vr, g=vg, b=vb)
            pdf.add_text("Knapsack Calculated", cx + 10, 560, size=7, font="F1", r=0.6, g=0.65, b=0.7)

        # Control Allocation Table
        pdf.add_text("2. Recommended Capital Allocation Roadmap", 36, 535, size=10, font="F2", r=0.06, g=0.09, b=0.16)
        
        pdf.draw_rect(36, 507, 540, 18, fill_rgb=(0.06, 0.09, 0.16), stroke_rgb=(0.06, 0.09, 0.16))
        pdf.add_text("Control ID", 42, 513, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Security Control Title", 110, 513, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Category", 310, 513, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Cost (INR)", 390, 513, size=8, font="F2", r=1, g=1, b=1)
        pdf.add_text("Risk Reduction", 480, 513, size=8, font="F2", r=1, g=1, b=1)

        curr_y = 489
        for ctrl in selected_controls:
            pdf.draw_rect(36, curr_y, 540, 18, fill_rgb=(1, 1, 1), stroke_rgb=(0.88, 0.91, 0.94))
            pdf.add_text(ctrl["control_id"], 42, curr_y + 5, size=8, font="F2", r=0.06, g=0.09, b=0.16)
            pdf.add_text(ctrl["name"][:38], 110, curr_y + 5, size=8, font="F1", r=0.15, g=0.2, b=0.28)
            pdf.add_text(ctrl.get("category", "General"), 310, curr_y + 5, size=8, font="F1", r=0.39, g=0.45, b=0.55)
            pdf.add_text(format_inr(ctrl["cost"]), 390, curr_y + 5, size=8, font="F2", r=0.06, g=0.09, b=0.16)
            pdf.add_text(f"-{format_inr(ctrl['risk_reduction_delta'])}", 480, curr_y + 5, size=8, font="F2", r=0.02, g=0.59, b=0.41)
            curr_y -= 18

        pdf.draw_rect(36, curr_y, 540, 18, fill_rgb=(0.95, 0.96, 0.98), stroke_rgb=(0.85, 0.88, 0.92))
        pdf.add_text("TOTAL ALLOCATED SPEND", 42, curr_y + 5, size=8, font="F2", r=0.06, g=0.09, b=0.16)
        pdf.add_text(format_inr(optimal_spend), 390, curr_y + 5, size=8, font="F2", r=0.06, g=0.09, b=0.16)
        pdf.add_text(f"-{format_inr(risk_reduced)} EAL", 480, curr_y + 5, size=8, font="F2", r=0.02, g=0.59, b=0.41)

        # Sign-off Blocks
        curr_y -= 45
        pdf.add_text("Prepared By: Chief Information Security Officer (CISO)", 36, curr_y + 12, size=8, font="F2", r=0.2, g=0.25, b=0.33)
        pdf.add_text("Signature: ___________________________", 36, curr_y, size=8, font="F1", r=0.39, g=0.45, b=0.55)

        pdf.add_text("Approved By: Board Risk Committee / CFO", 370, curr_y + 12, size=8, font="F2", r=0.2, g=0.25, b=0.33)
        pdf.add_text("Signature: ___________________________", 370, curr_y, size=8, font="F1", r=0.39, g=0.45, b=0.55)

        return pdf.compile()