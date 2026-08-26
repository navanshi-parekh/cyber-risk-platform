"use client";

import React, { useState, useRef } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Cpu,
  UploadCloud,
  AlertOctagon,
  ShieldAlert,
  Search,
  Flame,
  LayoutDashboard,
  CheckCircle2,
  RefreshCw,
  ExternalLink,
  Layers,
  TrendingUp,
} from "lucide-react";

interface EnrichedFinding {
  asset_ip: string;
  port: string;
  vulnerability_name: string;
  cvss_score: number;
  threat_level: string;
  cve_list: string[];
  epss_probability: number;
  epss_percentile: number;
  is_cisa_kev: boolean;
  fair_vulnerability_probability: number;
  description: string;
  solution: string;
  scanner_source: string;
}

const INITIAL_FINDINGS: EnrichedFinding[] = [
  {
    asset_ip: "10.14.20.15",
    port: "443/tcp",
    vulnerability_name: "Apache Log4j Remote Code Execution (Log4Shell)",
    cvss_score: 10.0,
    threat_level: "Critical",
    cve_list: ["CVE-2021-44228"],
    epss_probability: 0.9754,
    epss_percentile: 0.9998,
    is_cisa_kev: true,
    fair_vulnerability_probability: 0.911,
    description: "Apache Log4j2 <=2.14.1 JNDI features allow unauthenticated attacker RCE.",
    solution: "Upgrade log4j-core to version 2.17.1 or higher immediately.",
    scanner_source: "OpenVAS XML",
  },
  {
    asset_ip: "172.16.4.88",
    port: "22/tcp",
    vulnerability_name: "XZ Utils Liblzma Upstream Backdoor Injection",
    cvss_score: 10.0,
    threat_level: "Critical",
    cve_list: ["CVE-2024-3094"],
    epss_probability: 0.784,
    epss_percentile: 0.962,
    is_cisa_kev: true,
    fair_vulnerability_probability: 0.812,
    description: "Malicious code discovered in upstream liblzma tarballs allowing unauthorized SSH authentication bypass.",
    solution: "Downgrade xz-utils packages to 5.4.6 and rotate administrative host keys.",
    scanner_source: "OpenVAS XML",
  },
];

export default function TechnicalSOCPage() {
  const router = useRouter();
  const [findings, setFindings] = useState<EnrichedFinding[]>(INITIAL_FINDINGS);
  const [selectedFinding, setSelectedFinding] = useState<EnrichedFinding | null>(INITIAL_FINDINGS[0]);
  const [searchQuery, setSearchQuery] = useState("");
  const [severityFilter, setSeverityFilter] = useState("ALL");
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatusMsg, setUploadStatusMsg] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement | null>(null);

  const filteredFindings = findings.filter((f) => {
    const matchesSearch =
      f.vulnerability_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.asset_ip.toLowerCase().includes(searchQuery.toLowerCase()) ||
      f.cve_list.some((cve) => cve.toLowerCase().includes(searchQuery.toLowerCase()));

    const matchesSeverity =
      severityFilter === "ALL" ||
      (severityFilter === "KEV" && f.is_cisa_kev) ||
      (severityFilter === "CRITICAL" && f.cvss_score >= 9.0) ||
      (severityFilter === "HIGH" && f.cvss_score >= 7.0 && f.cvss_score < 9.0);

    return matchesSearch && matchesSeverity;
  });

  const totalFindings = findings.length;
  const criticalCount = findings.filter((f) => f.cvss_score >= 9.0).length;
  const kevCount = findings.filter((f) => f.is_cisa_kev).length;
  const avgFairVuln =
    totalFindings > 0
      ? Math.round(
          (findings.reduce((acc, f) => acc + f.fair_vulnerability_probability, 0) / totalFindings) * 100
        )
      : 0;

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    setUploadStatusMsg(`Ingesting & enriching ${file.name}...`);

    const formData = new FormData();
    formData.append("file", file);
    formData.append("scanner_type", "auto");
    formData.append("is_internet_facing", "true");

    try {
      const response = await fetch("http://127.0.0.1:8000/api/v1/ingestion/upload-scan", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`Status ${response.status}`);
      const result = await response.json();

      if (result.findings && result.findings.length > 0) {
        setFindings(result.findings);
        setSelectedFinding(result.findings[0]);
        setUploadStatusMsg(`Ingested ${result.total_findings_parsed} findings from ${result.detected_scanner}!`);
      }
    } catch (err: any) {
      setUploadStatusMsg(`Upload failed: ${err.message || "FastAPI connection error"}`);
    } finally {
      setIsUploading(false);
      setTimeout(() => setUploadStatusMsg(null), 5000);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const handlePushToExecutiveSimulation = () => {
    if (findings.length === 0) return;
    const bridgePayload = {
      scanner_source: findings[0]?.scanner_source || "Ingested Scan",
      total_findings: totalFindings,
      mean_fair_vuln_prob: avgFairVuln / 100,
      critical_count: criticalCount,
      kev_count: kevCount,
      top_vulnerability: selectedFinding?.vulnerability_name || findings[0]?.vulnerability_name,
      target_asset_name: selectedFinding?.asset_ip || "Core Production Cluster",
    };
    sessionStorage.setItem("active_scan_telemetry", JSON.stringify(bridgePayload));
    router.push("/dashboard?source=scan_ingestion");
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-cyan-500/10 border border-cyan-500/30 rounded-xl">
            <Cpu className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h1 className="text-xl font-bold tracking-tight text-slate-100">
                Technical SOC Telemetry & Threat Ingestion
              </h1>
              <span className="text-[10px] px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 font-mono">
                OpenVAS / Nessus / EPSS / CISA KEV
              </span>
            </div>
            <p className="text-xs text-slate-400">
              Automated Vulnerability Normalization, Exploit Scoring & Asset Exposure Mapping
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handlePushToExecutiveSimulation}
            className="flex items-center gap-1.5 px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-slate-950 font-semibold text-xs rounded-lg transition shadow-sm"
          >
            <TrendingUp className="w-3.5 h-3.5" />
            <span>Sync to Executive FAIR Model</span>
          </button>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept=".xml,.json,.nessus"
            className="hidden"
          />
          <button
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold text-xs rounded-lg transition shadow-sm"
          >
            {isUploading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <UploadCloud className="w-3.5 h-3.5" />}
            <span>{isUploading ? "Enriching..." : "Ingest Scan (XML/JSON)"}</span>
          </button>

          <Link
            href="/dashboard"
            className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 border border-slate-700 hover:bg-slate-800 text-xs font-medium rounded-lg text-slate-300 transition"
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Executive View</span>
          </Link>
        </div>
      </header>

      {uploadStatusMsg && (
        <div className="p-3 bg-cyan-950/40 border border-cyan-500/40 rounded-xl text-xs font-mono text-cyan-300 flex items-center gap-2">
          <RefreshCw className={`w-3.5 h-3.5 ${isUploading ? "animate-spin" : ""}`} />
          <span>{uploadStatusMsg}</span>
        </div>
      )}

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Total Ingested Findings</span>
            <Layers className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-100 mt-2">{totalFindings} Findings</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>CISA KEV Weaponized</span>
            <Flame className="w-4 h-4 text-rose-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-2">{kevCount} Weaponized</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Critical Severity (CVSS ≥ 9.0)</span>
            <AlertOctagon className="w-4 h-4 text-red-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-red-400 mt-2">{criticalCount} Critical</div>
        </div>

        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span>Mean FAIR Vulnerability Probability</span>
            <ShieldAlert className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-2">{avgFairVuln}%</div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
            <div className="flex items-center gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
                <input
                  type="text"
                  placeholder="Search CVE, Asset IP..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 focus:outline-none focus:border-cyan-500"
                />
              </div>

              <select
                value={severityFilter}
                onChange={(e) => setSeverityFilter(e.target.value)}
                className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300"
              >
                <option value="ALL">All</option>
                <option value="KEV">CISA KEV</option>
                <option value="CRITICAL">CVSS ≥ 9.0</option>
              </select>
            </div>

            <div className="space-y-2 max-h-[580px] overflow-y-auto pr-1">
              {filteredFindings.map((finding, idx) => {
                const isSelected = selectedFinding?.vulnerability_name === finding.vulnerability_name;
                return (
                  <div
                    key={idx}
                    onClick={() => setSelectedFinding(finding)}
                    className={`p-3.5 rounded-xl border cursor-pointer transition space-y-1.5 ${
                      isSelected
                        ? "bg-cyan-950/30 border-cyan-500/50 shadow-sm"
                        : "bg-slate-950/60 border-slate-800/80 hover:border-slate-700"
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2">
                      <span className="text-xs font-mono font-bold text-slate-200">
                        {finding.asset_ip}:{finding.port}
                      </span>
                      <div className="flex items-center gap-1.5">
                        {finding.is_cisa_kev && (
                          <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-rose-500/20 text-rose-400 border border-rose-500/30">
                            KEV
                          </span>
                        )}
                        <span className="text-[9px] font-mono font-bold px-1.5 py-0.2 rounded bg-red-500/10 text-red-400 border border-red-500/30">
                          CVSS {finding.cvss_score.toFixed(1)}
                        </span>
                      </div>
                    </div>

                    <div className="text-xs font-semibold text-slate-200 line-clamp-1">
                      {finding.vulnerability_name}
                    </div>

                    <div className="flex items-center justify-between text-[11px] text-slate-400 font-mono">
                      <span>{finding.cve_list.join(", ") || "No CVE Mapped"}</span>
                      <span className="text-cyan-400">
                        Vuln Prob: {(finding.fair_vulnerability_probability * 100).toFixed(1)}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="lg:col-span-7 flex flex-col gap-4">
          {selectedFinding ? (
            <>
              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-800 gap-2">
                  <div>
                    <span className="text-xs font-mono px-2 py-0.5 bg-slate-800 text-cyan-400 rounded">
                      {selectedFinding.asset_ip}:{selectedFinding.port}
                    </span>
                    <h2 className="text-base font-bold text-slate-100 mt-1">{selectedFinding.vulnerability_name}</h2>
                  </div>
                  <div className="text-right">
                    <div className="text-xs font-mono text-slate-400">FAIR Likelihood</div>
                    <div className="text-xl font-bold font-mono text-amber-400">
                      {(selectedFinding.fair_vulnerability_probability * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="text-xs text-slate-300 leading-relaxed bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                  {selectedFinding.description}
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] text-slate-500">CVSS v3.1</span>
                    <div className="text-lg font-bold font-mono text-slate-100 mt-0.5">{selectedFinding.cvss_score.toFixed(1)}</div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] text-slate-500">EPSS 30-Day</span>
                    <div className="text-lg font-bold font-mono text-cyan-400 mt-0.5">{(selectedFinding.epss_probability * 100).toFixed(2)}%</div>
                  </div>
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] text-slate-500">CISA KEV</span>
                    <div className="text-lg font-bold font-mono text-rose-400 mt-0.5">{selectedFinding.is_cisa_kev ? "WEAPONIZED" : "NOT LISTED"}</div>
                  </div>
                </div>
              </div>

              <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-3">
                <div className="p-3.5 bg-slate-950/80 border border-cyan-900/40 rounded-xl space-y-1.5">
                  <div className="flex items-center gap-2 text-xs font-semibold text-emerald-400">
                    <CheckCircle2 className="w-4 h-4" />
                    <span>Vendor Solution</span>
                  </div>
                  <p className="text-xs text-slate-300 font-mono">{selectedFinding.solution}</p>
                </div>

                <div className="flex flex-wrap gap-2 pt-1">
                  {selectedFinding.cve_list.map((cve, i) => (
                    <a
                      key={i}
                      href={`https://nvd.nist.gov/vuln/detail/${cve}`}
                      target="_blank"
                      rel="noreferrer"
                      className="flex items-center gap-1 text-xs font-mono px-2 py-0.5 bg-slate-900 border border-slate-700 hover:border-cyan-500 text-cyan-300 rounded transition"
                    >
                      <span>{cve}</span>
                      <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  ))}
                </div>
              </div>
            </>
          ) : null}
        </div>
      </section>
    </div>
  );
}