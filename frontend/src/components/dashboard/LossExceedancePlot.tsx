"use client";

import React from "react";
import dynamic from "next/dynamic";
import { formatINR } from "@/lib/utils";

// Disable SSR for ECharts so it only evaluates in the browser
const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false });

interface LECPoint {
  loss: number;
  exceedance_probability: number;
}

interface LossExceedancePlotProps {
  data: LECPoint[];
  var95: number;
  meanEal: number;
}

export function LossExceedancePlot({
  data,
  var95,
  meanEal,
}: LossExceedancePlotProps) {
  const chartData = (data || []).map((d) => [d.loss, d.exceedance_probability]);

  const option = {
    backgroundColor: "transparent",
    tooltip: {
      trigger: "axis",
      backgroundColor: "#1e293b",
      borderColor: "#334155",
      textStyle: { color: "#f8fafc" },
      formatter: (params: any) => {
        const item = params?.[0];
        if (!item) return "";
        const lossVal = item.value[0];
        const probVal = item.value[1];
        return `
          <div style="font-family:sans-serif; font-size:12px;">
            <div style="font-weight:600; color:#cbd5e1;">FAIR Loss Exceedance</div>
            <div style="margin-top:4px;">Monetary Loss: <span style="font-family:monospace; color:#34d399; font-weight:bold;">${formatINR(lossVal)}</span></div>
            <div>Probability: <span style="font-family:monospace; color:#22d3ee; font-weight:bold;">${Number(probVal).toFixed(1)}%</span></div>
          </div>
        `;
      },
    },
    grid: {
      left: "4%",
      right: "4%",
      bottom: "10%",
      top: "12%",
      containLabel: true,
    },
    xAxis: {
      type: "value",
      name: "Financial Loss (INR)",
      nameLocation: "middle",
      nameGap: 30,
      nameTextStyle: { color: "#94a3b8", fontSize: 11 },
      axisLine: { lineStyle: { color: "#334155" } },
      splitLine: { lineStyle: { color: "#1e293b" } },
      axisLabel: {
        color: "#94a3b8",
        formatter: (val: number) => formatINR(val),
      },
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
      axisLabel: {
        color: "#94a3b8",
        formatter: "{value}%",
      },
    },
    series: [
      {
        name: "Loss Exceedance Curve",
        type: "line",
        smooth: true,
        showSymbol: false,
        data: chartData,
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
              xAxis: var95,
              lineStyle: { color: "#ef4444", type: "dashed", width: 2 },
              label: {
                show: true,
                formatter: `95% VaR: ${formatINR(var95)}`,
                color: "#f87171",
                position: "insideEndTop",
              },
            },
            {
              xAxis: meanEal,
              lineStyle: { color: "#f59e0b", type: "dotted", width: 2 },
              label: {
                show: true,
                formatter: `Mean EAL: ${formatINR(meanEal)}`,
                color: "#fbbf24",
                position: "insideStartTop",
              },
            },
          ],
        },
      },
    ],
  };

  return (
    <div className="w-full h-80 bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between">
      <div className="flex items-center justify-between border-b border-slate-800 pb-2">
        <h3 className="text-sm font-semibold text-slate-200">
          Loss Exceedance Curve (10,000 Monte Carlo Iterations)
        </h3>
        <div className="flex gap-4 text-xs font-mono">
          <span className="text-amber-400">● Expected Annual Loss</span>
          <span className="text-red-400">■ 95% Value-at-Risk</span>
        </div>
      </div>
      <ReactECharts option={option} style={{ height: "240px", width: "100%" }} />
    </div>
  );
}

export default LossExceedancePlot;