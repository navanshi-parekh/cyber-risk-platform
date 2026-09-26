"use client";

import React, { useState, useEffect, useCallback } from "react";
import dynamic from "next/dynamic";
import {
  ShieldAlert,
  TrendingDown,
  ShieldCheck,
  Layers,
  RefreshCw,
  Server,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  DollarSign,
  History,
  TrendingUp,
} from "lucide-react";
import { formatINR } from "@/lib/utils";

const ReactECharts = dynamic(() => import("echarts-for-react"), {
  ssr: false,
  loading: () => (
    <div className="flex items-center justify-center h-48 text-xs text-slate-500">
      Loading Plot...
    </div>
  ),
});

const DEFAULT_SCENARIO = {
  scenario_id: "SCEN-RANSOMWARE-01",
  name: "Core Banking Cluster Ransomware Exposure",
  tef_low: 0.5,
  tef_high: 3.0,
  vuln_prob: 0.65,
  primary_loss: { low: 500000, mode: 1500000, high: 4000000 },
  secondary_loss_prob: 0.40,
  secondary_loss: { low: 1000000, mode: 3000000, high: 8000000 },
};

const FALLBACK_CONTROLS = [
  { control_id: "CTRL-01", name: "Deploy EDR on Core DB Cluster", category: "Endpoint", cost: 800000, risk_reduction_delta: 1200000, framework_mapping: ["RBI Sec 3.2", "NIST CSF DE.CM"], mandatory: false },
  { control_id: "CTRL-02", name: "Enforce Multi-Factor Authentication (MFA)", category: "IAM", cost: 200000, risk_reduction_delta: 700000, framework_mapping: ["SEBI CSCRF 4.1", "ISO 27001 A.9"], mandatory: true },
  { control_id: "CTRL-03", name: "Deploy Web Application Firewall (WAF)", category: "Network", cost: 500000, risk_reduction_delta: 600000, framework_mapping: ["ISO 27001 A.12", "PCI-DSS 6.6"], mandatory: false },
  { control_id: "CTRL-04", name: "Automated Patch Automation Engine", category: "Vulnerability", cost: 400000, risk_reduction_delta: 550000, framework_mapping: ["RBI Sec 5.1"], mandatory: false },
  { control_id: "CTRL-05", name: "Employee Security & Anti-Phishing Training", category: "Human Layer", cost: 150000, risk_reduction_delta: 300000, framework_mapping: ["NIST CSF PR.AT"], mandatory: false },
];

export default function DashboardPage() {
  const [simulationData, setSimulationData] = useState<any>(null);
  const [simLoading, setSimLoading] = useState<boolean>(true);
  const [budgetLimit, setBudgetLimit] = useState<number>(1000000);
  const [optimizationData, setOptimizationData] = useState<any>(null);
  const [optLoading, setOptLoading] = useState<boolean>(false);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [candidateControls, setCandidateControls] = useState<any[]>(FALLBACK_CONTROLS);

  const fetchHistory = async () => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/risk/history?limit=6");
      if (res.ok) {
        const data = await res.json();
        setHistoricalData(data.runs || []);
      }
    } catch (err) {
      console.error("History fetch error:", err);
    }
  };

  const triggerOptimization = async (budget: number, baselineEal: number, controls: any[]) => {
    setOptLoading(true);
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/optimizer/optimize", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          budget_limit: budget,
          baseline_eal: baselineEal,
          candidate_controls: controls,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        setOptimizationData(data);
      }
    } catch (err) {
      console.error("Optimization failed:", err);
    } finally {
      setOptLoading(false);
    }
  };

  const fetchSuggestedControls = async (scan: any, baselineEal: number): Promise<any[]> => {
    try {
      const res = await fetch("http://127.0.0.1:8000/api/v1/optimizer/suggest-controls", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          total_findings: scan.total_findings_parsed,
          critical_count: scan.critical_findings_count,
          kev_count: scan.kev_weaponized_count,
          mean_fair_vuln_prob: scan.mean_fair_vuln_prob,
          baseline_eal: baselineEal,
        }),
      });
      if (res.ok) return await res.json();
    } catch (err) {
      console.error("Control suggestion failed:", err);
    }
    return FALLBACK_CONTROLS;
  };

  const executeSimulation = useCallback(async () => {
    setSimLoading(true);
    try {
      // Prefer the server-persisted latest scan (survives across sessions/devices)
      // over the hardcoded demo scenario, so the dashboard reflects real ingested telemetry.
      const scanRes = await fetch("http://127.0.0.1:8000/api/v1/ingestion/latest");
      const latestScan = scanRes.ok ? await scanRes.json() : null;

      let data;
      let controls = FALLBACK_CONTROLS;

      if (latestScan && latestScan.total_findings_parsed > 0) {
        const topFinding = latestScan.findings?.[0];
        const bridgePayload = {
          scanner_source: latestScan.detected_scanner,
          total_findings: latestScan.total_findings_parsed,
          mean_fair_vuln_prob: latestScan.mean_fair_vuln_prob,
          critical_count: latestScan.critical_findings_count,
          kev_count: latestScan.kev_weaponized_count,
          top_vulnerability: topFinding?.vulnerability_name || "Ingested Vulnerability",
          target_asset_name: topFinding?.asset_ip || "Enterprise Core Production Cluster",
        };
        const res = await fetch("http://127.0.0.1:8000/api/v1/risk/simulate-from-scan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(bridgePayload),
        });
        data = await res.json();
        if (data?.mean_eal) {
          controls = await fetchSuggestedControls(latestScan, data.mean_eal);
        }
      } else {
        const res = await fetch("http://127.0.0.1:8000/api/v1/risk/simulate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(DEFAULT_SCENARIO),
        });
        data = await res.json();
      }
      setSimulationData(data);
      setCandidateControls(controls);
      if (data?.mean_eal) {
        triggerOptimization(budgetLimit, data.mean_eal, controls);
      }
      fetchHistory();
    } catch (err) {
      console.error("Simulation failed:", err);
    } finally {
      setSimLoading(false);
    }
  }, [budgetLimit]);

  useEffect(() => {
    executeSimulation();
    fetchHistory();
  }, [executeSimulation]);

  const handleBudgetChange = (newBudget: number) => {
    setBudgetLimit(newBudget);
    if (simulationData?.mean_eal) {
      triggerOptimization(newBudget, simulationData.mean_eal, candidateControls);
    }
  };

  // FAIR Loss Exceedance Curve Option
  const chartPoints = (simulationData?.loss_exceedance_curve || []).map((d: any) => [d.loss, d.exceedance_probability]);
  const lossCurveOption = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: "#1e293b",
      borderColor: "#334155",
      textStyle: { color: "#f8fafc" },
      formatter: (params: any) => {
        const item = params?.[0];
        if (!item) return "";
        return `
          <div style="font-family:sans-serif; font-size:12px;">
            <div style="color:#94a3b8; font-weight:600;">FAIR Loss Exceedance</div>
            <div style="margin-top:4px;">Monetary Loss: <b style="color:#34d399;">${formatINR(item.value[0])}</b></div>
            <div>Probability: <b style="color:#22d3ee;">${Number(item.value[1]).toFixed(1)}%</b></div>
          </div>
        `;
      },
    },
    grid: { left: "4%", right: "4%", bottom: "10%", top: "12%", containLabel: true },
    xAxis: {
      type: "value",
      name: "Financial Loss (INR)",
      nameLocation: "middle",
      nameGap: 30,
      nameTextStyle: { color: "#94a3b8", fontSize: 11 },
      axisLine: { lineStyle: { color: "#334155" } },
      splitLine: { lineStyle: { color: "#1e293b" } },
      axisLabel: { color: "#94a3b8", formatter: (val: number) => formatINR(val) },
    },
    yAxis: {
      type: "value",
      name: "Exceedance Probability (%)",
      nameLocation: "middle",
      nameGap: 35,
      min: 0,
      max: 100,
      nameTextStyle: { color: "#94a3b8", fontSize: 11 },
      axisLine: { lineStyle: { color: "#334155" } },
      splitLine: { lineStyle: { color: "#1e293b" } },
      axisLabel: { color: "#94a3b8", formatter: "{value}%" },
    },
    series: [
      {
        name: "Loss Exceedance Curve",
        type: "line",
        smooth: true,
        showSymbol: false,
        data: chartPoints,
        lineStyle: { width: 3, color: "#06b6d4" },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(6, 182, 212, 0.35)" },
              { offset: 1, color: "rgba(6, 182, 212, 0.0)" },
            ],
          },
        },
        markLine: {
          symbol: ["none", "none"],
          data: [
            {
              xAxis: simulationData?.var_95 || 0,
              lineStyle: { color: "#ef4444", type: "dashed", width: 2 },
              label: {
                show: true,
                formatter: `95% VaR: ${formatINR(simulationData?.var_95 || 0)}`,
                color: "#f87171",
                position: "insideEndTop",
              },
            },
            {
              xAxis: simulationData?.mean_eal || 0,
              lineStyle: { color: "#f59e0b", type: "dotted", width: 2 },
              label: {
                show: true,
                formatter: `Mean EAL: ${formatINR(simulationData?.mean_eal || 0)}`,
                color: "#fbbf24",
                position: "insideStartTop",
              },
            },
          ],
        },
      },
    ],
  };

  // MoM Historical Risk Reduction Trajectory Option
  const historyLabels = historicalData.map((h) => h.timestamp);
  const historyEal = historicalData.map((h) => h.mean_eal);
  const historyVar = historicalData.map((h) => h.var_95);
  const historyResidual = historicalData.map((h) => h.residual_eal);

  const momTrendOption = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: "#0f172a",
      borderColor: "#334155",
      textStyle: { color: "#f8fafc" },
      formatter: (params: any) => {
        let text = `<div style="font-size:11px; font-weight:bold; color:#cbd5e1; margin-bottom:4px;">${params[0].axisValue} Risk Audit</div>`;
        params.forEach((item: any) => {
          text += `<div>${item.marker} ${item.seriesName}: <b style="color:#f1f5f9;">${formatINR(item.value)}</b></div>`;
        });
        return text;
      },
    },
    legend: {
      data: ["Baseline EAL", "95% VaR Exposure", "Residual Post-Control EAL"],
      textStyle: { color: "#94a3b8", fontSize: 10 },
      top: 0,
    },
    grid: { left: "4%", right: "4%", bottom: "10%", top: "18%", containLabel: true },
    xAxis: {
      type: "category",
      data: historyLabels.length > 0 ? historyLabels : ["Month -5", "Month -4", "Month -3", "Month -2", "Month -1", "Current"],
      axisLine: { lineStyle: { color: "#334155" } },
      axisLabel: { color: "#94a3b8", fontSize: 10 },
    },
    yAxis: {
      type: "value",
      splitLine: { lineStyle: { color: "#1e293b" } },
      axisLabel: { color: "#94a3b8", formatter: (val: number) => formatINR(val), fontSize: 10 },
    },
    series: [
      {
        name: "95% VaR Exposure",
        type: "line",
        smooth: true,
        data: historyVar.length > 0 ? historyVar : [18500000, 16200000, 14500000, 13200000, 12300000, 12300000],
        lineStyle: { color: "#f43f5e", width: 2, type: "dashed" },
        itemStyle: { color: "#f43f5e" },
      },
      {
        name: "Baseline EAL",
        type: "line",
        smooth: true,
        data: historyEal.length > 0 ? historyEal : [4500000, 3900000, 3400000, 3100000, 2901400, 2901400],
        lineStyle: { color: "#f59e0b", width: 2.5 },
        itemStyle: { color: "#f59e0b" },
      },
      {
        name: "Residual Post-Control EAL",
        type: "line",
        smooth: true,
        data: historyResidual.length > 0 ? historyResidual : [4500000, 3400000, 2600000, 2100000, 1001400, 1001400],
        lineStyle: { color: "#10b981", width: 3 },
        areaStyle: {
          color: {
            type: "linear",
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: "rgba(16, 185, 129, 0.25)" },
              { offset: 1, color: "rgba(16, 185, 129, 0.0)" },
            ],
          },
        },
        itemStyle: { color: "#10b981" },
      },
    ],
  };

  const riskMitigated = Math.max(0, (simulationData?.mean_eal || 0) - (optimizationData?.residual_eal || 0));

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-900 dark:text-slate-100 p-6 space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div className="flex items-center gap-2.5">
          <div className="p-2 bg-cyan-500/10 border border-cyan-500/30 rounded-lg">
            <ShieldAlert className="w-6 h-6 text-cyan-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Cyber Exposure & Capital Allocation Dashboard
            </h1>
            <p className="text-xs text-slate-600 dark:text-slate-400">
              Open FAIR Quantitative Risk Modeling & MILP Investment Optimizer
            </p>
          </div>
        </div>

        <button
          onClick={executeSimulation}
          disabled={simLoading}
          className="flex items-center gap-2 px-3.5 py-2 bg-slate-100 dark:bg-slate-50 dark:bg-slate-900border border-slate-300 dark:border-slate-700 hover:bg-slate-200 dark:hover:bg-slate-800 text-xs font-medium rounded-lg transition text-slate-700 dark:text-slate-300"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${simLoading ? "animate-spin" : ""}`} />
          <span>Re-run 10k Monte Carlo</span>
        </button>
      </header>

      {/* Top 4 KPI Metric Cards */}
      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="group relative bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl p-4 overflow-hidden transition-all hover:border-amber-500/40 hover:-translate-y-0.5 hover:shadow-[0_8px_30px_-12px_rgba(251,191,36,0.25)]">
          <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-amber-500/0 via-amber-400 to-amber-500/0 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <span>Expected Annual Loss (EAL)</span>
            <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-slate-900 dark:text-slate-900 dark:text-slate-100 mt-2">
            {simLoading ? "Calculating..." : formatINR(simulationData?.mean_eal || 0)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-500 mt-1">Mean stochastic annual exposure</div>
        </div>

        <div className="group relative bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl p-4 overflow-hidden transition-all hover:border-red-500/40 hover:-translate-y-0.5 hover:shadow-[0_8px_30px_-12px_rgba(248,113,113,0.25)]">
          <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-red-500/0 via-red-400 to-red-500/0 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <span>95% Value-at-Risk (VaR)</span>
            <ShieldAlert className="w-4 h-4 text-red-600 dark:text-red-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-red-600 dark:text-red-400 mt-2">
            {simLoading ? "Calculating..." : formatINR(simulationData?.var_95 || 0)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-500 mt-1">1-in-20 year worst-case scenario</div>
        </div>

        <div className="group relative bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl p-4 overflow-hidden transition-all hover:border-emerald-500/40 hover:-translate-y-0.5 hover:shadow-[0_8px_30px_-12px_rgba(52,211,153,0.25)]">
          <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-emerald-500/0 via-emerald-400 to-emerald-500/0 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <span>Residual Risk Exposure</span>
            <TrendingDown className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-600 dark:text-emerald-400 mt-2">
            {optLoading || !optimizationData ? "Optimizing..." : formatINR(optimizationData.residual_eal)}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-500 mt-1">
            {optimizationData ? `Reduced by ${formatINR(optimizationData.total_risk_reduced)}` : "--"}
          </div>
        </div>

        <div className="group relative bg-white dark:bg-slate-900/80 border border-slate-200 dark:border-slate-800 rounded-xl p-4 overflow-hidden transition-all hover:border-cyan-500/40 hover:-translate-y-0.5 hover:shadow-[0_8px_30px_-12px_rgba(34,211,238,0.25)]">
          <div className="absolute inset-x-0 top-0 h-0.5 bg-gradient-to-r from-cyan-500/0 via-cyan-400 to-cyan-500/0 opacity-0 group-hover:opacity-100 transition-opacity" />
          <div className="flex items-center justify-between text-xs text-slate-600 dark:text-slate-400">
            <span>Portfolio ROSI</span>
            <ShieldCheck className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-600 dark:text-cyan-400 mt-2">
            {optLoading || !optimizationData ? "--" : `${optimizationData.portfolio_rosi.toFixed(1)}%`}
          </div>
          <div className="text-xs text-slate-500 dark:text-slate-500 mt-1">Net ROI on security spend</div>
        </div>
      </section>

      {/* Row 1: FAIR Exceedance Curve (7 Cols) + Budget Optimizer (5 Cols) */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 flex flex-col gap-4">
          <div className="w-full h-80 bg-white dark:bg-slate-50 dark:bg-slate-900border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-col justify-between">
            <div className="flex items-center justify-between border-b border-slate-800 pb-2">
              <h3 className="text-sm font-semibold text-slate-200">
                Loss Exceedance Curve (10,000 Monte Carlo Iterations)
              </h3>
              <div className="flex gap-4 text-xs font-mono">
                <span className="text-amber-400">● Expected Annual Loss</span>
                <span className="text-red-400">■ 95% Value-at-Risk</span>
              </div>
            </div>
            {simulationData ? (
              <ReactECharts option={lossCurveOption} style={{ height: "240px", width: "100%" }} />
            ) : (
              <div className="flex items-center justify-center h-48 text-xs text-slate-500">
                Loading Monte Carlo Simulation...
              </div>
            )}
          </div>
        </div>

        <div className="lg:col-span-5 flex flex-col gap-4">
          <div className="w-full bg-white dark:bg-slate-50 dark:bg-slate-900border border-slate-200 dark:border-slate-800 rounded-xl p-5 flex flex-col gap-5">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-semibold text-slate-200">Security Investment Optimizer</h3>
                <p className="text-xs text-slate-600 dark:text-slate-400">0-1 Knapsack MILP budget allocation</p>
              </div>
              <div className="text-right">
                <div className="text-xs text-slate-400 font-medium">Allocated Budget</div>
                <div className="text-xl font-bold font-mono text-cyan-400">{formatINR(budgetLimit)}</div>
              </div>
            </div>

            <input
              type="range"
              min={200000}
              max={2500000}
              step={50000}
              value={budgetLimit}
              disabled={optLoading}
              onChange={(e) => handleBudgetChange(Number(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400"
            />

            <div className="grid grid-cols-3 gap-3 border-t border-slate-800 pt-4">
              <div className="bg-slate-50 dark:bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400">
                  <DollarSign className="w-3.5 h-3.5 text-cyan-400" />
                  <span>Optimal Spend</span>
                </div>
                <div className="text-base font-bold font-mono text-slate-200 mt-1">
                  {formatINR(optimizationData?.total_spend || 0)}
                </div>
              </div>
              <div className="bg-slate-50 dark:bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400">
                  <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
                  <span>Risk Reduced</span>
                </div>
                <div className="text-base font-bold font-mono text-emerald-400 mt-1">
                  {formatINR(riskMitigated)}
                </div>
              </div>
              <div className="bg-slate-50 dark:bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
                <div className="flex items-center gap-1.5 text-xs text-slate-600 dark:text-slate-400">
                  <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
                  <span>Projected ROSI</span>
                </div>
                <div className="text-base font-bold font-mono text-amber-400 mt-1">
                  {optimizationData?.portfolio_rosi ? `${optimizationData.portfolio_rosi.toFixed(1)}%` : "--"}
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Row 2: Month-over-Month Risk Trajectory (7 Cols) + Control Allocation Roadmap (5 Cols) */}
      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Month-over-Month Risk Reduction Trajectory Chart */}
        <div className="lg:col-span-7 bg-white dark:bg-slate-50 dark:bg-slate-900border border-slate-200 dark:border-slate-800 rounded-xl p-5 flex flex-col justify-between">
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-2">
              <History className="w-4 h-4 text-cyan-400" />
              <div>
                <h3 className="text-xs font-bold text-slate-200 uppercase tracking-wider">
                  Historical Risk Reduction Trajectory (MoM Audit Ledger)
                </h3>
                <p className="text-[10px] text-slate-400">
                  Tracking EAL and 95% VaR decline across capital deployment cycles
                </p>
              </div>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-mono">
              -77.7% Net EAL Reduced
            </span>
          </div>

          <div className="py-2">
            <ReactECharts option={momTrendOption} style={{ height: "230px", width: "100%" }} />
          </div>
        </div>

        {/* Control Allocation Roadmap */}
        <div className="lg:col-span-5 bg-white dark:bg-slate-50 dark:bg-slate-900border border-slate-200 dark:border-slate-800 rounded-xl p-4 flex flex-col gap-3">
          <div className="flex items-center justify-between border-b border-slate-800 pb-2">
            <div className="flex items-center gap-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
                Optimal Control Allocation Roadmap
              </h3>
            </div>
            <span className="text-xs text-slate-400 font-mono">
              {optimizationData?.selected_controls?.length || 0} Deployed
            </span>
          </div>

          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {optimizationData?.selected_controls?.map((ctrl: any) => (
              <div
                key={ctrl.control_id}
                className="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-950/70 border border-emerald-950/60 rounded-lg text-xs"
              >
                <div className="flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
                  <div>
                    <div className="font-semibold text-slate-200">{ctrl.name}</div>
                    <div className="text-[10px] text-slate-400">{ctrl.category} • {ctrl.framework_mapping.join(", ")}</div>
                  </div>
                </div>
                <div className="text-right font-mono shrink-0">
                  <div className="text-slate-200 font-bold">{formatINR(ctrl.cost)}</div>
                  <div className="text-[10px] text-emerald-400">-{formatINR(ctrl.risk_reduction_delta)} EAL</div>
                </div>
              </div>
            ))}
            {optimizationData?.deferred_controls?.map((ctrl: any) => (
              <div
                key={ctrl.control_id}
                className="flex items-center justify-between p-2.5 bg-slate-50 dark:bg-slate-950/30 border border-slate-800/40 rounded-lg text-xs opacity-50"
              >
                <div className="flex items-center gap-2">
                  <XCircle className="w-4 h-4 text-slate-500 shrink-0" />
                  <div>
                    <div className="font-medium text-slate-400 line-through">{ctrl.name}</div>
                    <div className="text-[10px] text-slate-500">{ctrl.category} (Deferred)</div>
                  </div>
                </div>
                <div className="text-right font-mono shrink-0">
                  <div className="text-slate-400">{formatINR(ctrl.cost)}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}