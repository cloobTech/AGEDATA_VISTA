"""
Resampling analysis — Phase 6A.

Three methods are provided:

bootstrap
    Repeatedly resample the target column *with replacement* (B times), compute
    the chosen statistic on each resample, and derive a percentile confidence
    interval.  The percentile bootstrap is model-free and valid for any
    statistic without assuming normality.

monte_carlo
    Fit Normal(μ, σ) to the target column, then draw B synthetic samples of
    the same size from that distribution and compute the statistic on each.
    This simulates the sampling distribution under the normality assumption,
    letting the user compare it against the bootstrap result.

permutation
    Given two groups identified by group_col + group_values, permute the group
    labels B times and record the difference in group means (or other
    statistic) each time.  The empirical p-value is the proportion of permuted
    differences whose absolute value ≥ the observed absolute difference
    (two-tailed).  This is a non-parametric test of the null hypothesis that
    both groups are drawn from the same distribution.
"""

from typing import Dict, Any
import numpy as np
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.data_processing import AnalysisInput
from services.data_processing.report import crud

_RNG = np.random.default_rng(42)  # reproducible; seeded once per worker load


def _compute_statistic(arr: np.ndarray, statistic: str) -> float:
    if statistic == "mean":
        return float(np.mean(arr))
    if statistic == "median":
        return float(np.median(arr))
    if statistic == "std":
        return float(np.std(arr, ddof=1))
    if statistic == "variance":
        return float(np.var(arr, ddof=1))
    raise ValueError(f"Unknown statistic '{statistic}'")


def _bootstrap(values: np.ndarray, statistic: str,
               n_iterations: int, ci_level: float) -> Dict[str, Any]:
    observed = _compute_statistic(values, statistic)
    draws = np.array([
        _compute_statistic(_RNG.choice(values, size=len(values), replace=True), statistic)
        for _ in range(n_iterations)
    ])
    alpha = 1.0 - ci_level
    ci_lo = float(np.percentile(draws, 100 * alpha / 2))
    ci_hi = float(np.percentile(draws, 100 * (1 - alpha / 2)))
    return {
        "method": "bootstrap",
        "statistic": statistic,
        "observed_value": observed,
        "n_iterations": n_iterations,
        "ci_level": ci_level,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "bootstrap_mean":   float(np.mean(draws)),
        "bootstrap_std":    float(np.std(draws, ddof=1)),
        "bootstrap_p5":     float(np.percentile(draws, 5)),
        "bootstrap_p95":    float(np.percentile(draws, 95)),
        "interpretation": (
            f"Bootstrap {int(ci_level * 100)}% CI for the {statistic}: "
            f"[{ci_lo:.4f}, {ci_hi:.4f}]. "
            "Constructed from {:,} resamples with replacement; "
            "no distributional assumption is made.".format(n_iterations)
        ),
    }


def _monte_carlo(values: np.ndarray, statistic: str,
                 n_iterations: int, ci_level: float) -> Dict[str, Any]:
    mu    = float(np.mean(values))
    sigma = float(np.std(values, ddof=1))
    observed = _compute_statistic(values, statistic)
    draws = np.array([
        _compute_statistic(
            _RNG.normal(loc=mu, scale=sigma, size=len(values)), statistic
        )
        for _ in range(n_iterations)
    ])
    alpha = 1.0 - ci_level
    ci_lo = float(np.percentile(draws, 100 * alpha / 2))
    ci_hi = float(np.percentile(draws, 100 * (1 - alpha / 2)))
    return {
        "method": "monte_carlo",
        "statistic": statistic,
        "observed_value": observed,
        "fitted_mean":  mu,
        "fitted_std":   sigma,
        "n_iterations": n_iterations,
        "ci_level": ci_level,
        "ci_lower": ci_lo,
        "ci_upper": ci_hi,
        "mc_mean": float(np.mean(draws)),
        "mc_std":  float(np.std(draws, ddof=1)),
        "interpretation": (
            f"Monte Carlo {int(ci_level * 100)}% CI for the {statistic} under "
            f"Normal(μ={mu:.4f}, σ={sigma:.4f}): [{ci_lo:.4f}, {ci_hi:.4f}]. "
            "The observed value {:.4f} is {} the CI.".format(
                observed,
                "inside" if ci_lo <= observed <= ci_hi else "outside"
            )
        ),
    }


def _permutation(values_a: np.ndarray, values_b: np.ndarray,
                 statistic: str, n_iterations: int) -> Dict[str, Any]:
    observed_a = _compute_statistic(values_a, statistic)
    observed_b = _compute_statistic(values_b, statistic)
    observed_diff = abs(observed_a - observed_b)

    combined = np.concatenate([values_a, values_b])
    na = len(values_a)
    null_diffs = np.empty(n_iterations)
    for i in range(n_iterations):
        perm = _RNG.permutation(combined)
        null_diffs[i] = abs(
            _compute_statistic(perm[:na], statistic) -
            _compute_statistic(perm[na:], statistic)
        )

    p_value = float(np.mean(null_diffs >= observed_diff))
    return {
        "method": "permutation",
        "statistic": statistic,
        "group_a_stat": observed_a,
        "group_b_stat": observed_b,
        "observed_difference": float(observed_a - observed_b),
        "observed_abs_difference": observed_diff,
        "n_iterations": n_iterations,
        "p_value": p_value,
        "significant": p_value < 0.05,
        "null_diff_mean": float(np.mean(null_diffs)),
        "null_diff_p95":  float(np.percentile(null_diffs, 95)),
        "interpretation": (
            f"Two-tailed permutation test for difference in {statistic}: "
            f"observed |Δ| = {observed_diff:.4f}, p = {p_value:.4f}. "
            + ("Statistically significant difference (p < 0.05)."
               if p_value < 0.05
               else "No statistically significant difference (p ≥ 0.05).")
        ),
    }


async def perform_resampling_analysis(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession,
) -> Dict[str, Any]:
    inp = inputs.analysis_input  # already typed as ResamplingInput by select_analysis

    col = inp.target_col
    if col not in data.columns:
        raise ValueError(f"Column '{col}' not found in the dataset.")

    values = data[col].dropna().to_numpy(dtype=float)
    if len(values) < 10:
        raise ValueError(
            f"Column '{col}' has only {len(values)} non-null values; "
            "at least 10 are required for resampling."
        )

    method    = inp.method.value
    statistic = inp.statistic
    B         = inp.n_iterations
    ci_level  = inp.ci_level

    if method == "bootstrap":
        result = _bootstrap(values, statistic, B, ci_level)

    elif method == "monte_carlo":
        result = _monte_carlo(values, statistic, B, ci_level)

    elif method == "permutation":
        if not inp.group_col or not inp.group_values or len(inp.group_values) != 2:
            raise ValueError(
                "Permutation test requires 'group_col' and exactly two 'group_values'."
            )
        gc = inp.group_col
        gv = inp.group_values
        if gc not in data.columns:
            raise ValueError(f"Group column '{gc}' not found in the dataset.")
        group_a = data.loc[data[gc].astype(str) == str(gv[0]), col].dropna().to_numpy(dtype=float)
        group_b = data.loc[data[gc].astype(str) == str(gv[1]), col].dropna().to_numpy(dtype=float)
        if len(group_a) < 5 or len(group_b) < 5:
            raise ValueError(
                f"Each group must have at least 5 observations; "
                f"got {len(group_a)} ('{gv[0]}') and {len(group_b)} ('{gv[1]}')."
            )
        result = _permutation(group_a, group_b, statistic, B)
        result["group_a_label"] = str(gv[0])
        result["group_b_label"] = str(gv[1])
        result["group_a_n"] = len(group_a)
        result["group_b_n"] = len(group_b)
    else:
        raise ValueError(f"Unknown resampling method '{method}'")

    result["target_col"] = col
    result["n_observations"] = len(values)

    report_obj = {
        "visualizations": {},
        "project_id":     inputs.project_id,
        "summary":        result,
        "title":          inputs.title,
        "analysis_group": inputs.analysis_group,
    }
    return await crud.create_report(report_obj, session=session)
