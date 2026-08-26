# CyberExposure Quant: Cyber Risk Quantification & Capital Allocation Platform
### Problem Statement: SIH26105 | Enterprise FinTech & Banking Risk Framework

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Frontend-Next.js%2014-black.svg?style=flat&logo=next.js)](https://nextjs.org/)
[![Open FAIR](https://img.shields.io/badge/Standard-Open%20FAIR%20v3.0-blue.svg)](https://www.opengroup.org/certifications/fair)
[![Optimization](https://img.shields.io/badge/Solver-0--1%20Knapsack%20MILP-orange.svg)](https://coin-or.github.io/pulp/)
[![Compliance](https://img.shields.io/badge/Regulatory-RBI%20%7C%20SEBI%20CSCRF-emerald.svg)](https://rbi.org.in/)

---

## 📌 Executive Overview

Traditional cybersecurity solutions report vulnerabilities in isolated technical jargon (e.g., *CVSS 9.8*, *15 Critical CVEs*), failing to communicate **actual financial exposure** or **capital allocation efficiency** to Executive Boards, CISOs, and CFOs.

**CyberExposure Quant** bridges technical SOC telemetry and boardroom risk governance by:
1. **Financializing Cyber Risk:** Ingesting vulnerability scanner dumps (OpenVAS XML / Tenable Nessus JSON) and calculating **Expected Annual Loss (EAL)** and **95% Value-at-Risk (VaR)** in Indian Rupees (₹) using 10,000-iteration vectorized Open FAIR Monte Carlo simulations.
2. **Optimizing Capital Allocation:** Employing a 0-1 Knapsack Mixed-Integer Linear Programming (MILP) solver to mathematically select the security control portfolio that maximizes **Return on Security Investment (ROSI)** under strict budget constraints.
3. **Automating Statutory Governance:** Continuously auditing enterprise posture against **RBI Cyber Security Framework** and **SEBI Cybersecurity & Cyber Resilience Framework (CSCRF)** statutory clauses to calculate secondary regulatory penalty exposure.
4. **C-Suite Reporting & Decision Support:** Delivering an interactive floating AI CISO decision-support assistant and a zero-dependency binary PDF board briefing generator.

---

## 🏗️ System Architecture & Processing Pipeline

┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  Vulnerability Scans   │ ──▶ │  Threat Intel Enriched  │ ──▶ │    Open FAIR Engine     │
│   OpenVAS XML / Nessus  │     │   FIRST.org EPSS + KEV  │     │ 10k Monte Carlo (NumPy) │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘
│
▼
┌─────────────────────────┐     ┌─────────────────────────┐     ┌─────────────────────────┐
│  Executive Board PDF    │ ◀── │  Statutory Compliance   │ ◀── │  0-1 Knapsack Optimizer │
│ Zero-Dependency Builder │     │   RBI CSF + SEBI CSCRF  │     │  MILP Budget Solver     │
└─────────────────────────┘     └─────────────────────────┘     └─────────────────────────┘


---

## 🔬 Mathematical Formulation & Algorithmic Design

### 1. Open FAIR Stochastic Loss Model
Loss Event Frequency ($\text{LEF}$) and Loss Magnitude are modeled stochastically over $N = 10{,}000$ iterations:
* **Loss Event Frequency:** $\text{LEF} \sim \text{Poisson}(\lambda)$, where $\lambda = \text{TEF} \times \text{Vuln}_{\text{FAIR}}$
* **Vulnerability Likelihood:** $\text{Vuln}_{\text{FAIR}} = \min(0.99, \max(0.05, 0.35 \cdot \frac{\text{CVSS}}{10} + 0.50 \cdot \max(\text{EPSS}, \mathbb{I}_{\text{KEV}} \cdot 0.75)))$
* **Total Annual Loss:** $L_{\text{Total}} = \sum_{i=1}^{\text{LEF}} \text{PLM}_i + \mathbb{I}_{\text{Sec}} \cdot \text{SLM}$
* **Expected Annual Loss (EAL):** $\text{EAL} = \frac{1}{N} \sum_{k=1}^N L_{\text{Total}}^{(k)}$
* **95% Value-at-Risk (VaR):** $\text{VaR}_{95} = \text{Percentile}_{95}(\{L_{\text{Total}}^{(1)}, \dots, L_{\text{Total}}^{(N)}\})$

### 2. 0-1 Knapsack Capital Allocation Optimization
Given a candidate control set $\mathcal{C} = \{c_1, c_2, \dots, c_m\}$ where each control has cost $w_i$, risk reduction $\Delta \text{EAL}_i$, and mandatory statutory flag $m_i \in \{0, 1\}$:

$$\max \sum_{i=1}^m \Delta \text{EAL}_i \cdot x_i$$
$$\text{subject to } \sum_{i=1}^m w_i \cdot x_i \le B \quad \text{and} \quad x_i = 1 \quad \forall i \text{ where } m_i = 1$$

$$\text{Portfolio ROSI} = \frac{\sum_{i=1}^m (\Delta \text{EAL}_i \cdot x_i) - \sum_{i=1}^m (w_i \cdot x_i)}{\sum_{i=1}^m (w_i \cdot x_i)} \times 100\%$$

---

## 💻 Tech Stack

| Layer | Technologies | Description |
| :--- | :--- | :--- |
| **Frontend** | Next.js 14 (App Router), TypeScript, Tailwind CSS, Apache ECharts, Lucide Icons | Responsive multi-role views, loss curves, and budget sliders |
| **Backend** | FastAPI, Python 3.11+, Pydantic v2, Uvicorn | Async REST APIs, parsing services, and telemetry bridges |
| **Risk & Solver** | NumPy, SciPy (PERT/Lognormal Distributions), PuLP MILP Solver | 10k Monte Carlo runs in < 40ms, 0-1 Knapsack optimizer |
| **Database** | SQLAlchemy 2.0 (Async), aiosqlite, SQLite3 | Persistent simulation run history and MoM risk audit ledger |
| **Threat Feeds** | FIRST.org EPSS API, CISA KEV Catalog, NIST NVD | Live and cached vulnerability weaponization telemetry |
| **Reporting** | Pure Python Binary PDF Canvas Compiler | Zero-dependency CISO board briefing PDF generator |

---

## 🚀 Quick Start Guide

### Prerequisites
* Python 3.11 or higher
* Node.js 18.x or higher
* Git

---

### Step 1: Clone Repository & Setup Environment

```bash
git clone [https://github.com/](https://github.com/)<your-username>/cyber-risk-platform.git
cd cyber-risk-platform

### Step 2: Backnend Setup and Execution

# 1. Create and activate virtual environment
python -m venv .venv

# Windows (PowerShell):
.\.venv\Scripts\Activate.ps1

# Linux / macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install --upgrade pip
pip install -r backend/requirements.txt

# 3. Launch FastAPI Server (from project root)
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
Swagger API Docs: http://127.0.0.1:8000/docs

Health Endpoint: http://127.0.0.1:8000/health


### Step 3: Frontend Setup & Execution
Open a separate terminal:

Bash
cd frontend
npm install
npm run dev
Executive Dashboard: http://localhost:3000/dashboard

Technical SOC Telemetry: http://localhost:3000/technical

Statutory Compliance Matrix: http://localhost:3000/compliance

What-If Scenario Modeler: http://localhost:3000/simulations


🧪 Master Test Suite Validation
Execute the unified offline integration test runner validating all parsers, Monte Carlo engines, Knapsack solvers, statutory compliance rules, and PDF compilers in sub-seconds:

Bash
python backend/tests/test_full_suite.py


📁 Repository Directory Structure
cyber-risk-platform/
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/   # Ingestion, Risk, Optimizer, Compliance, Agent, Reports
│   │   ├── core/               # Database engine, App config & CORS
│   │   ├── models/             # SQLAlchemy ORM historical run tables
│   │   ├── services/
│   │   │   ├── fair_engine/    # 10k Monte Carlo stochastic engine
│   │   │   ├── optimizer/      # 0-1 Knapsack MILP budget solver
│   │   │   ├── parsers/        # OpenVAS XML & Nessus JSON parsers
│   │   │   ├── threat_engine/  # EPSS & CISA KEV enrichers
│   │   │   ├── compliance/     # RBI & SEBI CSCRF rule mappers
│   │   │   └── report_generator/ # Zero-dependency PDF builder
│   │   └── main.py             # FastAPI entrypoint
│   ├── sample_data/            # Offline demonstration scan reports
│   ├── tests/                  # Unit and integration test suites
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── app/                # /dashboard, /technical, /compliance, /simulations
    │   ├── components/         # Header, AI Assistant Drawer, Loss Curves, Sliders
    │   └── lib/                # API client & formatting utilities
    ├── package.json
    └── tailwind.config.js

    
📜 Regulatory Framework Alignment
RBI Cyber Security Framework for Banks:

Annex 1 - Section 3.2: Continuous Endpoint Detection & Response (EDR)

Annex 2 - Section 5.1: Automated Critical Vulnerability Patching SLA (< 48 hrs)

Annex 1 - Section 4.1: Privileged Identity Multi-Factor Authentication

SEBI Cybersecurity & Cyber Resilience Framework (CSCRF):

Section 4.1: Multi-Factor Authentication on Market Intermediary Gateways

Section 7.3: Web Application Firewall (WAF) Layer 7 Inspection

Section 11.4: Immutable Air-Gapped Backup & Recovery (WORM Storage)

Section 14.1: Centralized SOC Telemetry & 6-Hour Incident Notification SLA

👥 Authors & Acknowledgments
Project: SIH26105 - Cyber Risk Quantification & Capital Allocation Platform

Built for Smart India Hackathon (SIH) Enterprise FinTech Cybersecurity Track.