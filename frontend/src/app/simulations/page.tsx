"use client";

import React, { useState, useMemo } from "react";
import Link from "next/link";
import dynamic from "next/dynamic";
import {
  Sliders,
  TrendingUp,
  AlertTriangle,
  ShieldAlert,
  ShieldCheck,
  RefreshCw,
  LayoutDashboard,
  ArrowRight,
} from "lucide-react";
import { formatINR } from "@/lib/utils";

const ReactECharts = dynamic(() => import("echarts-for-react"), {
  ssr: false,
  loading: () => <div className="flex items-center justify-center h-48 text-xs text-slate-500">Loading Plot...</div>,
});

export default function DynamicSimulationsPage() {
  const baselineEal = 2901400;
  const baselineVar95 = 12300000;

  const [patchDelayDays, setPatchDelayDays] = useState<number>(30);
  const [zeroDayMultiplier, setZeroDayMultiplier] = useState<number>(1.5);
  const [threatContactFrequency, setThreatContactFrequency] = useState<number>(2.0);
  const [mfaBypassExposed, setMfaBypassExposed] = useState<boolean>(false);
  const [unencryptedBackupRisk, setUnencryptedBackupRisk] = useState<boolean>(false);

  const calculatedMetrics = useMemo(() => {
    const delayFactor = 1.0 + (patchDelayDays / 30) * 0.45;
    const threatFactor = (threatContactFrequency / 1.0) * (zeroDayMultiplier / 1.0);
    let penaltyAdder = 0;
    if (mfaBypassExposed) penaltyAdder += 1500000;
    if (unencryptedBackupRisk) penaltyAdder += 2500000;

    const simulatedEal = Math.round(baselineEal * delayFactor * (0.5 + threatFactor * 0.5) + penaltyAdder * 0.25);
    const simulatedVar95 = Math.round(baselineVar95 * delayFactor * (0.6 + threatFactor * 0.4) + penaltyAdder);
    const deltaEal = simulatedEal - baselineEal;
    const deltaVar95 = simulatedVar95 - baselineVar95;

    return {
      simulatedEal,
      simulatedVar95,
      deltaEal,
      deltaVar95,
      riskMultiplier: (simulatedEal / baselineEal).toFixed(2),
    };
  }, [patchDelayDays, zeroDayMultiplier, threatContactFrequency, mfaBypassExposed, unencryptedBackupRisk]);

  const baselineCurve = [
    [100000, 99.5],
    [500000, 92.1],
    [1000000, 78.4],
    [2000000, 56.3],
    [2901400, 42.0],
    [5000000, 24.5],
    [8000000, 11.2],
    [12300000, 5.0],
    [18000000, 1.2],
  ];

  const simulatedCurve = baselineCurve.map(([loss, prob]) => [
    Math.round(loss * Number(calculatedMetrics.riskMultiplier)),
    prob,
  ]);

  const chartOption = {
    backgroundColor: "transparent",
    tooltip: { trigger: "axis", backgroundColor: "#0f172a", borderColor: "#334155", textStyle: { color: "#f8fafc" } },
    legend: { data: ["Baseline", "Simulated What-If"], textStyle: { color: "#94a3b8" } },
    grid: { left: "4%", right: "4%", bottom: "12%", top: "16%", containLabel: true },
    xAxis: {
      type: "value",
      name: "Financial Loss (INR)",
      axisLabel: { color: "#94a3b8", formatter: (val: number) => formatINR(val) },
    },
    yAxis: { type: "value", name: "Exceedance (%)", min: 0, max: 100, axisLabel: { color: "#94a3b8" } },
    series: [
      { name: "Baseline", type: "line", smooth: true, showSymbol: false, data: baselineCurve, lineStyle: { width: 2, color: "#06b6d4", type: "dashed" } },
      { name: "Simulated What-If", type: "line", smooth: true, showSymbol: false, data: simulatedCurve, lineStyle: { width: 3, color: "#f43f5e" } },
    ],
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      <header className="flex flex-col md:flex-row md:items-center justify-between pb-6 border-b border-slate-800 gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 rounded-xl">
            <Sliders className="w-6 h-6 text-rose-400" />
          </div>
          <div>
            <h1 className="text-xl font-bold tracking-tight text-slate-100">
              What-If Dynamic Threat & Scenario Simulator
            </h1>
            <p className="text-xs text-slate-400">Simulate Patch Delays & Exploit Multipliers</p>
          </div>
        </div>

        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 px-3.5 py-2 bg-slate-900 border border-slate-700 hover:bg-slate-800 text-xs font-medium rounded-lg text-slate-300 transition"
        >
          <LayoutDashboard className="w-3.5 h-3.5" />
          <span>Executive View</span>
        </Link>
      </header>

      <section className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400">Simulated EAL</span>
          <div className="text-2xl font-bold font-mono text-rose-400 mt-2">{formatINR(calculatedMetrics.simulatedEal)}</div>
        </div>
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400">Simulated 95% VaR</span>
          <div className="text-2xl font-bold font-mono text-red-400 mt-2">{formatINR(calculatedMetrics.simulatedVar95)}</div>
        </div>
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400">Exposure Multiplier</span>
          <div className="text-2xl font-bold font-mono text-amber-400 mt-2">{calculatedMetrics.riskMultiplier}x</div>
        </div>
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4">
          <span className="text-xs text-slate-400">Baseline EAL</span>
          <div className="text-2xl font-bold font-mono text-slate-200 mt-2">{formatINR(baselineEal)}</div>
        </div>
      </section>

      <section className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-7 bg-slate-900/90 border border-slate-800 rounded-xl p-4 h-[420px]">
          <ReactECharts option={chartOption} style={{ height: "340px", width: "100%" }} />
        </div>

        <div className="lg:col-span-5 bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-5">
          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>Patch Remediation Delay</span>
              <span className="font-mono text-rose-400 font-bold">{patchDelayDays} Days</span>
            </div>
            <input
              type="range"
              min={0}
              max={90}
              step={5}
              value={patchDelayDays}
              onChange={(e) => setPatchDelayDays(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg accent-rose-400"
            />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>Zero-Day Multiplier</span>
              <span className="font-mono text-rose-400 font-bold">{zeroDayMultiplier}x</span>
            </div>
            <input
              type="range"
              min={1.0}
              max={4.0}
              step={0.1}
              value={zeroDayMultiplier}
              onChange={(e) => setZeroDayMultiplier(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg accent-rose-400"
            />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span>Threat Contact Frequency</span>
              <span className="font-mono text-rose-400 font-bold">{threatContactFrequency} ev/yr</span>
            </div>
            <input
              type="range"
              min={0.5}
              max={5.0}
              step={0.5}
              value={threatContactFrequency}
              onChange={(e) => setThreatContactFrequency(Number(e.target.value))}
              className="w-full h-2 bg-slate-800 rounded-lg accent-rose-400"
            />
          </div>
        </div>
      </section>
    </div>
  );
}