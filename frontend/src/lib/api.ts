const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000/api/v1";

export interface ScenarioPayload {
  scenario_id: string;
  name: string;
  tef_low: number;
  tef_high: number;
  vuln_prob: number;
  primary_loss: { low: number; mode: number; high: number };
  secondary_loss_prob: number;
  secondary_loss: { low: number; mode: number; high: number };
}

export interface ControlPayload {
  control_id: string;
  name: string;
  category: string;
  cost: number;
  risk_reduction_delta: number;
  framework_mapping: string[];
  mandatory: boolean;
}

export interface OptimizationPayload {
  budget_limit: number;
  baseline_eal: number;
  candidate_controls: ControlPayload[];
}

export async function runFairSimulation(payload: ScenarioPayload) {
  const res = await fetch(`${API_BASE_URL}/risk/simulate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Simulation failed: ${res.statusText}`);
  return res.json();
}

export async function optimizeBudget(payload: OptimizationPayload) {
  const res = await fetch(`${API_BASE_URL}/optimizer/optimize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`Optimization failed: ${res.statusText}`);
  return res.json();
}
