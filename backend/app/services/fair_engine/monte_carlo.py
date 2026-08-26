"""
FAIR (Factor Analysis of Information Risk) Quantitative Monte Carlo Simulation Engine.
Implements vectorized stochastic sampling across 10,000 iterations to calculate
Expected Annual Loss (EAL), Value-at-Risk (VaR), and Loss Exceedance Curves.
Uses pure NumPy for zero-dependency portability.
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
import numpy as np


@dataclass
class LossParameters:
    """Confidence bounds (10th percentile and 90th percentile) for lognormal loss estimation."""
    low: float      # 10th percentile loss estimate in ₹ / $
    mode: float     # Most likely loss estimate
    high: float     # 90th percentile loss estimate in ₹ / $
    confidence: float = 0.90


@dataclass
class ScenarioInput:
    """Inputs representing a single threat-asset scenario under the Open FAIR framework."""
    scenario_id: str
    name: str
    # Frequency parameters (Annual events)
    tef_low: float      # Threat Event Frequency (low estimate events/year)
    tef_high: float     # Threat Event Frequency (high estimate events/year)
    vuln_prob: float    # Vulnerability (0.0 to 1.0 - probability of exploit given contact)
    
    # Primary Loss Magnitude (Direct forensics, downtime, recovery)
    primary_loss: LossParameters
    
    # Secondary Loss (Regulatory fines, litigation, churn)
    secondary_loss_prob: float  # Probability of secondary loss triggering (0.0 to 1.0)
    secondary_loss: LossParameters


@dataclass
class SimulationResult:
    """Structured output containing statistical aggregates and plot-ready curve coordinates."""
    scenario_id: str
    scenario_name: str
    iterations: int
    mean_eal: float              # Expected Annual Loss (Mean)
    median_loss: float           # 50th percentile
    std_dev: float
    min_loss: float
    max_loss: float
    var_90: float                # 90% Value-at-Risk
    var_95: float                # 95% Value-at-Risk
    var_99: float                # 99% Value-at-Risk
    loss_exceedance_curve: List[Dict[str, float]]  # Coordinates for UI curves
    histogram_bins: List[Dict[str, Any]]           # Binned frequencies for charts
    simulated_losses: Optional[np.ndarray] = field(default=None, repr=False)


class FairMonteCarloEngine:
    """
    Vectorized FAIR quantitative simulation engine.
    Utilizes lognormal distributions calibrated to 90% confidence intervals.
    """

    def __init__(self, iterations: int = 10000, random_seed: Optional[int] = 42):
        self.iterations = iterations
        self.rng = np.random.default_rng(random_seed)

    @staticmethod
    def _fit_lognormal_params(low: float, high: float, confidence: float = 0.90) -> Tuple[float, float]:
        """
        Calculates mu and sigma for a lognormal distribution.
        For a two-tailed 90% confidence interval, Z ≈ 1.644853.
        """
        if low <= 0 or high <= 0 or low >= high:
            raise ValueError(f"Invalid confidence bounds: low={low}, high={high}. Values must be positive and low < high.")
        
        # Standard Z-score for 90% Confidence Interval
        z = 1.6448536269514722

        log_low = np.log(low)
        log_high = np.log(high)

        mu = (log_low + log_high) / 2.0
        sigma = (log_high - log_low) / (2.0 * z)

        return float(mu), float(sigma)

    def _sample_poisson_or_lognormal_frequency(self, tef_low: float, tef_high: float, vuln_prob: float) -> np.ndarray:
        """Simulates annual Loss Event Frequency (LEF) using a Poisson process."""
        mu_tef, sigma_tef = self._fit_lognormal_params(max(tef_low, 0.01), max(tef_high, 0.02))
        annual_tef = self.rng.lognormal(mean=mu_tef, sigma=sigma_tef, size=self.iterations)
        
        sampled_lambda = annual_tef * np.clip(vuln_prob, 0.0, 1.0)
        lef_events = self.rng.poisson(lam=sampled_lambda)
        return lef_events

    def _sample_loss_magnitude(self, loss_params: LossParameters, event_counts: np.ndarray) -> np.ndarray:
        """Samples financial loss magnitude per event iteration."""
        mu, sigma = self._fit_lognormal_params(loss_params.low, loss_params.high, loss_params.confidence)
        
        total_losses = np.zeros(self.iterations, dtype=np.float64)
        active_indices = np.where(event_counts > 0)[0]
        
        for idx in active_indices:
            num_events = int(event_counts[idx])
            event_losses = self.rng.lognormal(mean=mu, sigma=sigma, size=num_events)
            total_losses[idx] = np.sum(event_losses)

        return total_losses

    def run_scenario(self, scenario: ScenarioInput) -> SimulationResult:
        """Executes 10,000 Monte Carlo iterations for a single risk scenario."""
        # 1. Simulate Loss Event Frequency (LEF)
        lef_events = self._sample_poisson_or_lognormal_frequency(
            tef_low=scenario.tef_low,
            tef_high=scenario.tef_high,
            vuln_prob=scenario.vuln_prob,
        )

        # 2. Simulate Primary Loss Magnitude (PLM)
        primary_losses = self._sample_loss_magnitude(scenario.primary_loss, lef_events)

        # 3. Simulate Secondary Loss Magnitude (SLM)
        secondary_trigger = self.rng.binomial(n=1, p=np.clip(scenario.secondary_loss_prob, 0.0, 1.0), size=self.iterations)
        secondary_events = np.where(secondary_trigger == 1, lef_events, 0)
        secondary_losses = self._sample_loss_magnitude(scenario.secondary_loss, secondary_events)

        # 4. Total Annual Loss
        total_losses = primary_losses + secondary_losses

        # 5. Summary Statistics
        mean_eal = float(np.mean(total_losses))
        median_loss = float(np.median(total_losses))
        std_dev = float(np.std(total_losses))
        min_loss = float(np.min(total_losses))
        max_loss = float(np.max(total_losses))

        # VaR Percentiles
        var_90 = float(np.percentile(total_losses, 90))
        var_95 = float(np.percentile(total_losses, 95))
        var_99 = float(np.percentile(total_losses, 99))

        # 6. Loss Exceedance Curve (LEC) Coordinates
        sorted_losses = np.sort(total_losses)
        exceedance_probs = 1.0 - (np.arange(1, self.iterations + 1) / self.iterations)

        sample_indices = np.linspace(0, self.iterations - 1, num=50, dtype=int)
        loss_exceedance_curve = [
            {
                "loss": round(float(sorted_losses[i]), 2),
                "exceedance_probability": round(float(exceedance_probs[i]) * 100.0, 2),
            }
            for i in sample_indices
        ]

        # 7. Distribution Histogram
        hist_counts, bin_edges = np.histogram(total_losses, bins=30)
        histogram_bins = [
            {
                "bin_start": round(float(bin_edges[i]), 2),
                "bin_end": round(float(bin_edges[i + 1]), 2),
                "count": int(hist_counts[i]),
                "percentage": round(float(hist_counts[i] / self.iterations * 100.0), 2),
            }
            for i in range(len(hist_counts))
        ]

        return SimulationResult(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            iterations=self.iterations,
            mean_eal=round(mean_eal, 2),
            median_loss=round(median_loss, 2),
            std_dev=round(std_dev, 2),
            min_loss=round(min_loss, 2),
            max_loss=round(max_loss, 2),
            var_90=round(var_90, 2),
            var_95=round(var_95, 2),
            var_99=round(var_99, 2),
            loss_exceedance_curve=loss_exceedance_curve,
            histogram_bins=histogram_bins,
            simulated_losses=total_losses,
        )

    def run_portfolio(self, scenarios: List[ScenarioInput]) -> Dict[str, Any]:
        """Runs simulations across a portfolio of scenarios."""
        results: List[SimulationResult] = []
        portfolio_losses = np.zeros(self.iterations, dtype=np.float64)

        for scenario in scenarios:
            res = self.run_scenario(scenario)
            results.append(res)
            if res.simulated_losses is not None:
                portfolio_losses += res.simulated_losses

        total_mean_eal = float(np.mean(portfolio_losses))
        portfolio_var_95 = float(np.percentile(portfolio_losses, 95))
        portfolio_var_99 = float(np.percentile(portfolio_losses, 99))

        sorted_portfolio = np.sort(portfolio_losses)
        exceedance_probs = 1.0 - (np.arange(1, self.iterations + 1) / self.iterations)
        sample_indices = np.linspace(0, self.iterations - 1, num=50, dtype=int)

        portfolio_lec = [
            {
                "loss": round(float(sorted_portfolio[i]), 2),
                "exceedance_probability": round(float(exceedance_probs[i]) * 100.0, 2),
            }
            for i in sample_indices
        ]

        return {
            "iterations": self.iterations,
            "total_eal": round(total_mean_eal, 2),
            "portfolio_var_95": round(portfolio_var_95, 2),
            "portfolio_var_99": round(portfolio_var_99, 2),
            "portfolio_exceedance_curve": portfolio_lec,
            "scenarios": results,
        }