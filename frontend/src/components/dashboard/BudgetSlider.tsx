"use client";

import React from "react";
import { formatINR } from "@/lib/utils";
import { ShieldCheck, TrendingDown, DollarSign } from "lucide-react";

interface BudgetSliderProps {
  currentBudget: number;
  minBudget: number;
  maxBudget: number;
  step: number;
  totalSpend: number;
  baselineEal: number;
  residualEal: number;
  portfolioRosi: number;
  onBudgetChange: (newBudget: number) => void;
  isLoading?: boolean;
}

export const BudgetSlider: React.FC<BudgetSliderProps> = ({
  currentBudget,
  minBudget,
  maxBudget,
  step,
  totalSpend,
  baselineEal,
  residualEal,
  portfolioRosi,
  onBudgetChange,
  isLoading = false,
}) => {
  const riskMitigated = Math.max(0, baselineEal - residualEal);

  return (
    <div className="w-full bg-slate-900 border border-slate-800 rounded-xl p-5 flex flex-col gap-5">
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-sm font-semibold text-slate-200">
            Security Investment Optimizer
          </h3>
          <p className="text-xs text-slate-400">
            Adjust budget constraint to compute optimal control allocation
          </p>
        </div>
        <div className="text-right">
          <div className="text-xs text-slate-400 font-medium">Allocated Budget</div>
          <div className="text-xl font-bold font-mono text-cyan-400">
            {formatINR(currentBudget)}
          </div>
        </div>
      </div>

      <div className="flex flex-col gap-2">
        <input
          type="range"
          min={minBudget}
          max={maxBudget}
          step={step}
          value={currentBudget}
          disabled={isLoading}
          onChange={(e) => onBudgetChange(Number(e.target.value))}
          className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-cyan-400 disabled:opacity-50"
        />
        <div className="flex justify-between text-xs font-mono text-slate-400">
          <span>{formatINR(minBudget)}</span>
          <span>{formatINR((maxBudget + minBudget) / 2)}</span>
          <span>{formatINR(maxBudget)}</span>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-3 border-t border-slate-800 pt-4">
        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <DollarSign className="w-3.5 h-3.5 text-cyan-400" />
            <span>Optimal Spend</span>
          </div>
          <div className="text-base font-bold font-mono text-slate-200 mt-1">
            {formatINR(totalSpend)}
          </div>
        </div>

        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <TrendingDown className="w-3.5 h-3.5 text-emerald-400" />
            <span>Risk Reduced</span>
          </div>
          <div className="text-base font-bold font-mono text-emerald-400 mt-1">
            {formatINR(riskMitigated)}
          </div>
        </div>

        <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
          <div className="flex items-center gap-1.5 text-xs text-slate-400">
            <ShieldCheck className="w-3.5 h-3.5 text-amber-400" />
            <span>Projected ROSI</span>
          </div>
          <div className="text-base font-bold font-mono text-amber-400 mt-1">
            {portfolioRosi.toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};
