"use client";

import React, { useState, useMemo, useEffect, useCallback } from "react";
import Link from "next/link";
import {
  FileCheck2,
  ShieldCheck,
  AlertOctagon,
  AlertTriangle,
  ChevronRight,
  Building2,
  Layers,
  LayoutDashboard,
  Cpu,
  Settings2,
  RefreshCw,
} from "lucide-react";
import { formatINR } from "@/lib/utils";

type FrameworkType = "ALL" | "RBI" | "SEBI_CSCRF";
type AuditStatus = "COMPLIANT" | "NON_COMPLIANT";

interface AuditClause {
  clause_id: string;
  section: string;
  framework: "RBI" | "SEBI_CSCRF";
  title: string;
  domain: string;
  description: string;
  status: AuditStatus;
  mapped_control: string;
  potential_fine_inr: number;
}

interface Posture {
  has_edr_installed: boolean;
  mfa_enforced_on_admins: boolean;
  waf_active_blocking: boolean;
  immutable_backups_configured: boolean;
  soc_telemetry_integrated: boolean;
}

const POSTURE_LABELS: Record<keyof Posture, string> = {
  has_edr_installed: "EDR Deployed on Core Clusters",
  mfa_enforced_on_admins: "MFA Enforced on Admin Access",
  waf_active_blocking: "WAF in Active-Block Mode",
  immutable_backups_configured: "Immutable WORM Backups Configured",
  soc_telemetry_integrated: "SOC Telemetry Centrally Integrated",
};

export default function ComplianceAuditPage() {
  const [clauses, setClauses] = useState<AuditClause[]>([]);
  const [loading, setLoading] = useState(true);
  const [posture, setPosture] = useState<Posture | null>(null);
  const [savingPosture, setSavingPosture] = useState(false);
  const [selectedFramework, setSelectedFramework] = useState<FrameworkType>("ALL");
  const [selectedClause, setSelectedClause] = useState<AuditClause | null>(null);

  const fetchAudit = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/compliance/unified-audit");
      if (res.ok) {
        const data = await res.json();
        setClauses(data.clauses || []);
        setSelectedClause((prev) => prev ?? data.clauses?.[0] ?? null);
      }
    } catch (err) {
      console.error("Compliance audit fetch failed:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  const fetchPosture = useCallback(async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/compliance/posture");
      if (res.ok) setPosture(await res.json());
    } catch (err) {
      console.error("Posture fetch failed:", err);
    }
  }, []);

  useEffect(() => {
    fetchAudit();
    fetchPosture();
  }, [fetchAudit, fetchPosture]);

  const togglePosture = async (key: keyof Posture) => {
    if (!posture) return;
    const updated = { ...posture, [key]: !posture[key] };
    setPosture(updated);
    setSavingPosture(true);
    try {
      await fetch("http://127.0.0.1:8000/api/v1/compliance/posture", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updated),
      });
      await fetchAudit();
    } catch (err) {
      console.error("Posture update failed:", err);
    } finally {
      setSavingPosture(false);
    }
  };

  const filteredClauses = useMemo(() => {
    if (selectedFramework === "ALL") return clauses;
    return clauses.filter((c) => c.framework === selectedFramework);
  }, [clauses, selectedFramework]);

  const totalClauses = clauses.length;
  const compliantCount = clauses.filter((c) => c.status === "COMPLIANT").length;
  const nonCompliantCount = clauses.filter((c) => c.status === "NON_COMPLIANT").length;
  const complianceScore = totalClauses > 0 ? Math.round((compliantCount / totalClauses) * 100) : 0;
  const totalPenaltyExposure = clauses.reduce((acc, c) => acc + c.potential_fine_inr, 0);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-6 space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl">
            <FileCheck2 className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Statutory Compliance & Regulatory Audit Matrix
            </h1>
            <p className="text-xs text-slate-400">
              Live RBI / SEBI CSCRF Audit &mdash; Vulnerability Clauses from Ingested Scans, Controls from Infrastructure Posture
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={fetchAudit}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-50 dark:bg-slate-900border border-slate-700 hover:bg-slate-100 dark:bg-slate-800 text-xs font-medium rounded-lg text-slate-300 transition"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? "animate-spin text-cyan-400" : ""}`} />
            <span>Re-run Audit</span>
          </button>
          <Link
            href="/technical"
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-50 dark:bg-slate-900border border-slate-700 hover:bg-slate-100 dark:bg-slate-800 text-xs font-medium rounded-lg text-slate-300 transition"
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
        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Compliance Score</span>
            <ShieldCheck className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-400 mt-2">{complianceScore}%</div>
        </div>

        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Penalty Exposure</span>
            <AlertOctagon className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-red-400 mt-2">{formatINR(totalPenaltyExposure)}</div>
        </div>

        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Non-Compliant Clauses</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-2">{nonCompliantCount} Clauses</div>
        </div>

        <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Fully Met Mandates</span>
            <Building2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-100 mt-2">{compliantCount} / {totalClauses} Met</div>
        </div>
      </section>

      {posture && (
        <section className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl p-4">
          <div className="flex items-center gap-2 mb-3">
            <Settings2 className="w-4 h-4 text-cyan-400" />
            <span className="text-xs font-semibold text-slate-900 dark:text-slate-200">Infrastructure Control Posture</span>
            <span className="text-[10px] text-slate-500">
              (toggle actual control state &mdash; the audit re-scores live; vulnerability clauses are driven by your last ingested scan)
            </span>
            {savingPosture && <RefreshCw className="w-3 h-3 animate-spin text-cyan-400 ml-auto" />}
          </div>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-2">
            {(Object.keys(POSTURE_LABELS) as (keyof Posture)[]).map((key) => (
              <button
                key={key}
                onClick={() => togglePosture(key)}
                className={`flex items-center justify-between gap-2 px-3 py-2.5 rounded-lg border text-left transition ${
                  posture[key]
                    ? "bg-emerald-500/10 border-emerald-500/40 text-emerald-300"
                    : "bg-slate-50 dark:bg-slate-950/60 border-slate-800 text-slate-400 hover:border-slate-700"
                }`}
              >
                <span className="text-[11px] font-medium">{POSTURE_LABELS[key]}</span>
                <span
                  className={`shrink-0 w-8 h-4 rounded-full relative transition ${
                    posture[key] ? "bg-emerald-500" : "bg-slate-700"
                  }`}
                >
                  <span
                    className={`absolute top-0.5 w-3 h-3 rounded-full bg-white transition ${
                      posture[key] ? "left-4" : "left-0.5"
                    }`}
                  />
                </span>
              </button>
            ))}
          </div>
        </section>
      )}

      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex flex-wrap gap-1 bg-slate-50 dark:bg-slate-950 border border-slate-800 rounded-lg p-1 text-[11px]">
              {(["ALL", "RBI", "SEBI_CSCRF"] as FrameworkType[]).map((f) => (
                <button
                  key={f}
                  onClick={() => setSelectedFramework(f)}
                  className={`px-2.5 py-1 rounded transition ${
                    selectedFramework === f ? "bg-cyan-500/20 text-cyan-400 font-semibold" : "text-slate-400"
                  }`}
                >
                  {f.replace("_", " ")}
                </button>
              ))}
            </div>

            <div className="space-y-2 max-h-[580px] overflow-y-auto pr-1">
              {loading && (
                <div className="text-xs text-slate-500 text-center py-8">Loading live audit...</div>
              )}
              {!loading && filteredClauses.length === 0 && (
                <div className="text-xs text-slate-500 text-center py-8">No clauses found.</div>
              )}
              {filteredClauses.map((clause) => {
                const isSelected = selectedClause?.clause_id === clause.clause_id;
                return (
                  <div
                    key={clause.clause_id}
                    onClick={() => setSelectedClause(clause)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition flex items-start justify-between gap-3 ${
                      isSelected
                        ? "bg-cyan-950/30 border-cyan-500/50 shadow-sm"
                        : "bg-slate-50 dark:bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold font-mono text-cyan-400">{clause.section}</span>
                        <span
                          className={`text-[9px] font-mono font-bold px-1.5 py-0.2 rounded ${
                            clause.status === "COMPLIANT"
                              ? "bg-emerald-500/15 text-emerald-400"
                              : "bg-red-500/15 text-red-400"
                          }`}
                        >
                          {clause.status.replace("_", " ")}
                        </span>
                      </div>
                      <div className="text-xs font-semibold text-slate-900 dark:text-slate-200">{clause.title}</div>
                      {clause.potential_fine_inr > 0 && (
                        <div className="text-[10px] text-red-400 font-mono">Fine: {formatINR(clause.potential_fine_inr)}</div>
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
            <div className="bg-white dark:bg-slate-900/90 border border-slate-200 dark:border-slate-800 rounded-xl p-5 space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <span className="text-xs font-mono px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-cyan-400 rounded">
                  {selectedClause.section}
                </span>
                <h2 className="text-base font-bold text-slate-900 dark:text-slate-100 mt-2">{selectedClause.title}</h2>
              </div>

              <div className="text-xs text-slate-700 dark:text-slate-300 bg-slate-100 dark:bg-slate-50 dark:bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                {selectedClause.description}
              </div>

              <div className="p-3.5 bg-slate-50 dark:bg-slate-950/80 border border-slate-800/80 rounded-xl space-y-1.5">
                <span className="text-[10px] text-slate-600 dark:text-slate-500 font-bold uppercase">Domain:</span>
                <p className="text-xs text-slate-300 font-mono">{selectedClause.domain}</p>
              </div>

              <div className="p-4 bg-slate-50 dark:bg-slate-950/90 border border-cyan-900/50 rounded-xl space-y-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Layers className="w-4 h-4 text-cyan-400" />
                    <span className="text-xs font-semibold text-slate-900 dark:text-slate-200">Mapped Control</span>
                  </div>
                  <span className="text-xs font-mono text-cyan-400 font-bold">{selectedClause.mapped_control}</span>
                </div>
                <div className="text-xs bg-slate-50 dark:bg-slate-900p-2.5 rounded border border-slate-800 text-slate-400">
                  {selectedClause.status === "COMPLIANT"
                    ? "Control satisfied under current infrastructure posture / scan results."
                    : `Non-compliant. Estimated statutory penalty exposure: ${formatINR(selectedClause.potential_fine_inr)}.`}
                </div>
              </div>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
