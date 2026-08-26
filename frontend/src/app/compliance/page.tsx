"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import {
  FileCheck2,
  ShieldCheck,
  AlertOctagon,
  AlertTriangle,
  Search,
  ChevronRight,
  Building2,
  Layers,
  LayoutDashboard,
  Cpu,
} from "lucide-react";
import { formatINR } from "@/lib/utils";

type FrameworkType = "ALL" | "RBI" | "SEBI_CSCRF" | "ISO_27001" | "NIST_CSF";
type AuditStatus = "COMPLIANT" | "NON_COMPLIANT" | "PARTIAL";

interface StatutoryClause {
  id: string;
  clause_code: string;
  title: string;
  framework: "RBI" | "SEBI_CSCRF" | "ISO_27001" | "NIST_CSF";
  domain: string;
  description: string;
  mapped_control_id: string;
  mapped_control_name: string;
  status: AuditStatus;
  affected_assets: string[];
  penalty_exposure: number;
  audit_evidence: string;
  recommended_action: string;
}

const STATUTORY_CLAUSES: StatutoryClause[] = [
  {
    id: "CLAUSE-01",
    clause_code: "RBI Annex 1 - Sec 3.2",
    title: "Continuous Endpoint Detection & Response (EDR)",
    framework: "RBI",
    domain: "Network & Endpoint Security",
    description: "Scheduled and continuous host-level behavioral monitoring across critical database clusters.",
    mapped_control_id: "CTRL-01",
    mapped_control_name: "Deploy EDR on Core DB Cluster",
    status: "NON_COMPLIANT",
    affected_assets: ["Core Banking Oracle DB Cluster (10.14.20.15)"],
    penalty_exposure: 1500000,
    audit_evidence: "No active behavioral EDR telemetry detected on Oracle RAC host nodes.",
    recommended_action: "Deploy agent-based EDR telemetry node on AST-PROD-DB-01 to satisfy RBI Sec 3.2 mandate.",
  },
  {
    id: "CLAUSE-02",
    clause_code: "SEBI CSCRF Sec 4.1",
    title: "Multi-Factor Authentication on Privileged Access",
    framework: "SEBI_CSCRF",
    domain: "Identity & Access Management",
    description: "Mandatory hardware or biometric MFA for all system administrators and high-privilege access gateways.",
    mapped_control_id: "CTRL-02",
    mapped_control_name: "Enforce Multi-Factor Authentication (MFA)",
    status: "COMPLIANT",
    affected_assets: ["Keycloak Identity Microservice (10.14.30.12)"],
    penalty_exposure: 0,
    audit_evidence: "FIDO2 / WebAuthn MFA enforced across all IAM administration roles.",
    recommended_action: "Maintain current access policy review intervals every 90 days.",
  },
  {
    id: "CLAUSE-03",
    clause_code: "SEBI CSCRF Sec 7.3",
    title: "Critical Attack Surface Web Application Firewall (WAF)",
    framework: "SEBI_CSCRF",
    domain: "Application Security",
    description: "L7 inspection and TLS inspection for all internet-facing payment gateways.",
    mapped_control_id: "CTRL-03",
    mapped_control_name: "Deploy Web Application Firewall (WAF)",
    status: "PARTIAL",
    affected_assets: ["UPI / IMPS API Gateway Reverse Proxy (172.16.4.88)"],
    penalty_exposure: 750000,
    audit_evidence: "WAF deployed in detection mode; signature enforcement blocking currently deferred.",
    recommended_action: "Switch WAF inspection mode from 'Monitor' to 'Active Block' on DMZ edge.",
  },
  {
    id: "CLAUSE-04",
    clause_code: "RBI Annex 2 - Sec 5.1",
    title: "Automated Patch Management & Zero-Day SLA",
    framework: "RBI",
    domain: "Vulnerability Management",
    description: "Mandatory remediation of CVSS >= 9.0 and CISA KEV vulnerabilities within 48 hours.",
    mapped_control_id: "CTRL-04",
    mapped_control_name: "Automated Patch Automation Engine",
    status: "NON_COMPLIANT",
    affected_assets: ["Core Banking Oracle DB Cluster", "UPI API Gateway"],
    penalty_exposure: 2000000,
    audit_evidence: "Open Log4j (CVE-2021-44228) and XZ (CVE-2024-3094) open beyond 14 days.",
    recommended_action: "Authorize automated CI/CD micro-patch orchestration for critical CVEs.",
  },
  {
    id: "CLAUSE-05",
    clause_code: "ISO/IEC 27001:2022 A.8.8",
    title: "Management of Technical Vulnerabilities",
    framework: "ISO_27001",
    domain: "Information Security Operations",
    description: "Systematic evaluation of technical vulnerabilities and timely risk mitigation measures.",
    mapped_control_id: "CTRL-04",
    mapped_control_name: "Automated Patch Automation Engine",
    status: "PARTIAL",
    affected_assets: ["Core Banking Oracle DB Cluster"],
    penalty_exposure: 500000,
    audit_evidence: "Quarterly vulnerability scans conducted, but lack prioritized EPSS / FAIR remediation queue.",
    recommended_action: "Align remediation backlog directly with EPSS and FAIR Value-at-Risk scores.",
  },
  {
    id: "CLAUSE-06",
    clause_code: "NIST CSF 2.0 PR.AT-01",
    title: "Personnel Security & Anti-Phishing Training",
    framework: "NIST_CSF",
    domain: "Human Security",
    description: "Mandatory baseline security awareness and role-based social engineering resilience training.",
    mapped_control_id: "CTRL-05",
    mapped_control_name: "Employee Security & Anti-Phishing Training",
    status: "COMPLIANT",
    affected_assets: ["All Enterprise Personnel"],
    penalty_exposure: 0,
    audit_evidence: "96.4% employee completion rate recorded on annual cybersecurity training platform.",
    recommended_action: "Conduct unannounced quarterly simulated phishing tests.",
  },
];

export default function ComplianceAuditPage() {
  const [clauses] = useState<StatutoryClause[]>(STATUTORY_CLAUSES);
  const [selectedFramework, setSelectedFramework] = useState<FrameworkType>("ALL");
  const [statusFilter, setStatusFilter] = useState<string>("ALL");
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedClause, setSelectedClause] = useState<StatutoryClause | null>(STATUTORY_CLAUSES[0]);

  const filteredClauses = useMemo(() => {
    return clauses.filter((c) => {
      const matchesSearch =
        c.clause_code.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.domain.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesFramework = selectedFramework === "ALL" || c.framework === selectedFramework;
      const matchesStatus = statusFilter === "ALL" || c.status === statusFilter;
      return matchesSearch && matchesFramework && matchesStatus;
    });
  }, [clauses, searchQuery, selectedFramework, statusFilter]);

  const totalClauses = clauses.length;
  const compliantCount = clauses.filter((c) => c.status === "COMPLIANT").length;
  const nonCompliantCount = clauses.filter((c) => c.status === "NON_COMPLIANT").length;
  const partialCount = clauses.filter((c) => c.status === "PARTIAL").length;
  const complianceScore = Math.round(((compliantCount + partialCount * 0.5) / totalClauses) * 100);
  const totalPenaltyExposure = clauses.reduce((acc, c) => acc + c.penalty_exposure, 0);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl">
            <FileCheck2 className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-100">
              Statutory Compliance & Regulatory Audit Matrix
            </h1>
            <p className="text-xs text-slate-400">
              Cross-Framework Control Mapping, Compliance Readiness & Secondary Penalty Loss Exposure
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <Link
            href="/technical"
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 border border-slate-700 hover:bg-slate-800 text-xs font-medium rounded-lg text-slate-300 transition"
          >
            <Cpu className="w-3.5 h-3.5" />
            <span>Technical SOC View</span>
          </Link>
          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 px-3.5 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold text-xs rounded-lg transition shadow-sm"
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Executive Dashboard</span>
          </Link>
        </div>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Compliance Score</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-2">{complianceScore}%</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Penalty Exposure</span>
            <AlertOctagon className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-red-400 mt-2">{formatINR(totalPenaltyExposure)}</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Non-Compliant Clauses</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-2">{nonCompliantCount} Clauses</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Fully Met Mandates</span>
            <Building2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100 mt-2">{compliantCount} / {totalClauses} Met</div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex flex-wrap gap-1 bg-slate-950 border border-slate-800 rounded-lg p-1 text-[11px]">
              {["ALL", "RBI", "SEBI_CSCRF", "ISO_27001", "NIST_CSF"].map((f) => (
                <button
                  key={f}
                  onClick={() => setSelectedFramework(f as FrameworkType)}
                  className={`px-2.5 py-1 rounded transition ${
                    selectedFramework === f ? "bg-cyan-500/20 text-cyan-400 font-semibold" : "text-slate-400"
                  }`}
                >
                  {f.replace("_", " ")}
                </button>
              ))}
            </div>

            <div className="space-y-2 max-h-[580px] overflow-y-auto pr-1">
              {filteredClauses.map((clause) => {
                const isSelected = selectedClause?.id === clause.id;
                return (
                  <div
                    key={clause.id}
                    onClick={() => setSelectedClause(clause)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start justify-between gap-3 ${
                      isSelected
                        ? "bg-cyan-950/30 border-cyan-500/50 shadow-sm"
                        : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold font-mono text-cyan-400">{clause.clause_code}</span>
                        <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                          {clause.status.replace("_", " ")}
                        </span>
                      </div>
                      <div className="text-xs font-semibold text-slate-200">{clause.title}</div>
                      {clause.penalty_exposure > 0 && (
                        <div className="text-[10px] text-red-400 font-mono">Fine: {formatINR(clause.penalty_exposure)}</div>
                      )}
                    </div>
                    <ChevronRight className="w-4 h-4 text-slate-600 mt-1 shrink-0" />
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="lg:col-span-7 flex flex-col gap-4">
          {selectedClause && (
            <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <span className="text-xs font-mono px-2 py-0.5 bg-slate-800 text-cyan-400 rounded">
                  {selectedClause.clause_code}
                </span>
                <h2 className="text-base font-bold text-slate-100 mt-2">{selectedClause.title}</h2>
              </div>

              <div className="text-xs text-slate-300 bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                {selectedClause.description}
              </div>

              <div className="p-3.5 bg-slate-950/80 border border-slate-800/80 rounded-xl space-y-1.5">
                <span className="text-[10px] text-slate-500 font-bold uppercase">Auditor Finding:</span>
                <p className="text-xs text-slate-300 font-mono">{selectedClause.audit_evidence}</p>
              </div>

              <div className="p-4 bg-slate-950/90 border border-cyan-900/50 rounded-xl space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-semibold text-slate-200">Mapped Control</span>
                  </div>
                  <span className="text-xs font-mono text-cyan-400 font-bold">{selectedClause.mapped_control_id}</span>
                </div>
                <div className="text-xs font-medium text-slate-300">{selectedClause.mapped_control_name}</div>
                <div className="text-xs bg-slate-900 p-2.5 rounded border border-slate-800 text-slate-400">
                  {selectedClause.recommended_action}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}