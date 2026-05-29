"""
Non-Parametric Statistical Tests  (AGEARC spec Features 3.3a–3.3d)

Implements:
  3.3a  Mann-Whitney U test
  3.3b  Wilcoxon Signed-Rank test
  3.3c  Kruskal-Wallis H test  (with Dunn post-hoc)
  3.3d  Friedman test          (with pairwise Wilcoxon post-hoc)

Entry point: run_nonparametric_tests(df, analysis_input) → dict
"""

from __future__ import annotations

import itertools
import logging
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.multitest import multipletests

log = logging.getLogger(__name__)

# ── helpers ──────────────────────────────────────────────────────────────────


def _sf(x) -> float | None:
    """Safe float: rounds to 6 dp, returns None for NaN/inf."""
    try:
        v = float(x)
        if v != v or abs(v) == float("inf"):
            return None
        return round(v, 6)
    except Exception:
        return None


def _warn(level: str, message: str, code: str) -> dict:
    return {"level": level, "message": message, "code": code}


def _effect_interp_r(abs_r: float) -> str:
    if abs_r < 0.1:
        return "small"
    if abs_r < 0.3:
        return "medium"
    return "large"


def _bootstrap_hl_ci(diffs: np.ndarray, n_boot: int = 1000, seed: int = 42) -> tuple[float, float]:
    """Bootstrap 95% CI for the Hodges-Lehmann estimator (median of diffs)."""
    rng = np.random.default_rng(seed)
    estimates = np.array([
        np.median(rng.choice(diffs, size=len(diffs), replace=True))
        for _ in range(n_boot)
    ])
    return float(np.percentile(estimates, 2.5)), float(np.percentile(estimates, 97.5))


def _apply_correction(p_values: list[float], method: str) -> list[float]:
    """Return corrected p-values using statsmodels multipletests."""
    if len(p_values) == 0:
        return []
    sm_method = "bonferroni" if method == "bonferroni" else "fdr_bh"
    _, p_adj, _, _ = multipletests(p_values, method=sm_method)
    return [float(p) for p in p_adj]


# ── 3.3a  Mann-Whitney U ─────────────────────────────────────────────────────


def _mann_whitney(df: pd.DataFrame, inp: dict) -> dict:
    outcome_col = inp["outcome_col"]
    group_col = inp["group_col"]
    alpha = float(inp.get("alpha", 0.05))

    if outcome_col not in df.columns or group_col not in df.columns:
        return {"error": f"Columns '{outcome_col}' or '{group_col}' not found."}

    clean = df[[outcome_col, group_col]].dropna()
    groups = clean[group_col].unique()
    if len(groups) != 2:
        return {"error": f"Mann-Whitney requires exactly 2 groups; found {len(groups)}."}

    g1_label, g2_label = str(groups[0]), str(groups[1])
    x1 = clean.loc[clean[group_col] == groups[0], outcome_col].values.astype(float)
    x2 = clean.loc[clean[group_col] == groups[1], outcome_col].values.astype(float)
    n1, n2 = len(x1), len(x2)

    if n1 < 2 or n2 < 2:
        return {"error": "Each group must have at least 2 observations."}

    warnings: list[dict] = []

    # Choose exact vs asymptotic
    use_exact = (n1 < 25) and (n2 < 25)
    p_method = "exact" if use_exact else "asymptotic"
    try:
        res = stats.mannwhitneyu(x1, x2, alternative="two-sided", method=p_method)
        u_stat = float(res.statistic)
        p_value = float(res.pvalue)
    except Exception as exc:
        # Fallback to asymptotic if exact fails (e.g. ties)
        res = stats.mannwhitneyu(x1, x2, alternative="two-sided", method="asymptotic")
        u_stat = float(res.statistic)
        p_value = float(res.pvalue)
        p_method = "asymptotic"
        warnings.append(_warn("info", f"Exact method failed ({exc}); used asymptotic.", "MW_EXACT_FALLBACK"))

    # Z approximation:  U ~ N(n1*n2/2, sqrt(n1*n2*(n1+n2+1)/12))
    mu_u = n1 * n2 / 2.0
    sigma_u = np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12.0)
    z_approx = (u_stat - mu_u) / sigma_u if sigma_u > 0 else float("nan")

    # Effect sizes
    rank_biserial_r = 1.0 - (2.0 * u_stat / (n1 * n2))
    cles = u_stat / (n1 * n2)

    # Hodges-Lehmann estimator: median of all pairwise x1 - x2 differences
    pairwise_diffs = np.array([a - b for a in x1 for b in x2])
    hl_estimate = float(np.median(pairwise_diffs))
    hl_ci_lower, hl_ci_upper = _bootstrap_hl_ci(pairwise_diffs)

    abs_r = abs(rank_biserial_r)
    effect_interp = _effect_interp_r(abs_r)

    if n1 < 5 or n2 < 5:
        warnings.append(_warn("warning", "Very small group size(s); results may be unreliable.", "MW_SMALL_N"))
    if abs_r < 0.1:
        warnings.append(_warn("info", "Effect size is small (|r| < 0.1).", "MW_SMALL_EFFECT"))

    dominant = g1_label if u_stat > (n1 * n2 / 2) else g2_label
    direction = "stochastically dominates" if u_stat != n1 * n2 / 2 else "shows no stochastic dominance over"
    significant = p_value < alpha

    interpretation = {
        "main_finding": (
            f"{'Significant' if significant else 'No significant'} difference between '{g1_label}' "
            f"and '{g2_label}' (U={u_stat:.4f}, p={p_value:.4f}). "
            f"'{dominant}' {direction} the other group."
        ),
        "effect_size_meaning": (
            f"Rank-biserial r = {rank_biserial_r:.4f} ({effect_interp} effect). "
            f"Common Language Effect Size = {cles:.4f}: in {cles*100:.1f}% of random pairs, "
            f"'{g1_label}' scores higher than '{g2_label}'."
        ),
        "key_caveat": (
            "Mann-Whitney tests stochastic dominance (whether one group's values tend to be larger), "
            "NOT simply a difference in medians. A significant result means one distribution tends to "
            "produce higher values, which does not necessarily imply a median shift."
        ),
    }

    return {
        "test_type": "mann_whitney",
        "group_names": [g1_label, g2_label],
        "group_ns": {g1_label: n1, g2_label: n2},
        "group_medians": {g1_label: _sf(np.median(x1)), g2_label: _sf(np.median(x2))},
        "u_statistic": _sf(u_stat),
        "z_approximation": _sf(z_approx),
        "p_value": _sf(p_value),
        "p_method": p_method,
        "rank_biserial_r": _sf(rank_biserial_r),
        "cles": _sf(cles),
        "hodges_lehmann_estimate": _sf(hl_estimate),
        "hl_ci_lower": _sf(hl_ci_lower),
        "hl_ci_upper": _sf(hl_ci_upper),
        "effect_size_interpretation": effect_interp,
        "alpha": alpha,
        "significant": significant,
        "warnings": warnings,
        "interpretation": interpretation,
    }


# ── 3.3b  Wilcoxon Signed-Rank ───────────────────────────────────────────────


def _wilcoxon(df: pd.DataFrame, inp: dict) -> dict:
    col1 = inp["col1"]
    col2 = inp["col2"]
    alpha = float(inp.get("alpha", 0.05))

    if col1 not in df.columns or col2 not in df.columns:
        return {"error": f"Columns '{col1}' or '{col2}' not found."}

    clean = df[[col1, col2]].dropna()
    n = len(clean)
    if n < 4:
        return {"error": f"Wilcoxon requires at least 4 complete pairs; found {n}."}

    x1 = clean[col1].values.astype(float)
    x2 = clean[col2].values.astype(float)

    warnings: list[dict] = []
    diffs = x2 - x1

    # Ties check
    nonzero_diffs = diffs[diffs != 0]
    has_ties = len(nonzero_diffs) < len(diffs)
    use_exact = (n < 25) and not has_ties
    p_method = "exact" if use_exact else "asymptotic"

    if has_ties:
        warnings.append(_warn("info", "Tied differences present; asymptotic p-value used.", "WSR_TIES"))

    try:
        mode_arg = "exact" if use_exact else "approx"
        w_res = stats.wilcoxon(x1, x2, alternative="two-sided", method=mode_arg)
        w_stat = float(w_res.statistic)
        p_value = float(w_res.pvalue)
    except Exception as exc:
        w_res = stats.wilcoxon(x1, x2, alternative="two-sided", method="approx")
        w_stat = float(w_res.statistic)
        p_value = float(w_res.pvalue)
        p_method = "asymptotic"
        warnings.append(_warn("info", f"Exact method failed ({exc}); used asymptotic.", "WSR_EXACT_FALLBACK"))

    # Z approximation from normal approximation of W
    n_nz = len(nonzero_diffs) if len(nonzero_diffs) > 0 else n
    mu_w = n_nz * (n_nz + 1) / 4.0
    sigma_w = np.sqrt(n_nz * (n_nz + 1) * (2 * n_nz + 1) / 24.0)
    z_approx = (w_stat - mu_w) / sigma_w if sigma_w > 0 else float("nan")

    r_effect = z_approx / np.sqrt(n) if n > 0 else float("nan")
    effect_interp = _effect_interp_r(abs(r_effect))

    # Hodges-Lehmann pseudomedian: median of (d_i + d_j)/2 for all i <= j
    # This is exact for signed-rank; we use Walsh averages of differences
    d = diffs
    walsh_avgs = np.array([(d[i] + d[j]) / 2.0 for i in range(len(d)) for j in range(i, len(d))])
    hl_pseudomedian = float(np.median(walsh_avgs))
    hl_ci_lower, hl_ci_upper = _bootstrap_hl_ci(diffs)

    if n < 10:
        warnings.append(_warn("warning", "Small sample size (n < 10); results may be unreliable.", "WSR_SMALL_N"))

    significant = p_value < alpha
    direction = "increased" if np.median(diffs) > 0 else ("decreased" if np.median(diffs) < 0 else "unchanged")

    interpretation = {
        "main_finding": (
            f"{'Significant' if significant else 'No significant'} difference between paired "
            f"'{col1}' and '{col2}' (W={w_stat:.4f}, p={p_value:.4f}). "
            f"'{col2}' values tend to be {direction} relative to '{col1}'."
        ),
        "effect_size_meaning": (
            f"r = {r_effect:.4f} ({effect_interp} effect based on |r|). "
            f"Hodges-Lehmann pseudomedian shift: {hl_pseudomedian:.4f}."
        ),
        "key_caveat": (
            "Wilcoxon signed-rank tests the symmetry of the difference distribution around zero, "
            "not just the sign of differences. Requires paired observations measured on the same subjects."
        ),
    }

    return {
        "test_type": "wilcoxon",
        "n_pairs": n,
        "median_col1": _sf(float(np.median(x1))),
        "median_col2": _sf(float(np.median(x2))),
        "w_statistic": _sf(w_stat),
        "z_approximation": _sf(z_approx),
        "p_value": _sf(p_value),
        "p_method": p_method,
        "r_effect_size": _sf(r_effect),
        "effect_size_interpretation": effect_interp,
        "hodges_lehmann_pseudomedian": _sf(hl_pseudomedian),
        "hl_ci_lower": _sf(hl_ci_lower),
        "hl_ci_upper": _sf(hl_ci_upper),
        "alpha": alpha,
        "significant": significant,
        "warnings": warnings,
        "interpretation": interpretation,
    }


# ── 3.3c  Kruskal-Wallis ────────────────────────────────────────────────────


def _dunn_posthoc(data: pd.Series, groups: pd.Series, group_labels: list, correction: str) -> list[dict]:
    """
    Manual Dunn's test.
    z_{ij} = (R_i_bar - R_j_bar) / sqrt((N*(N+1)/12) * (1/n_i + 1/n_j))
    where R_i_bar are mean ranks computed on the combined pooled ranking.
    """
    combined = pd.DataFrame({"value": data, "group": groups})
    combined["rank"] = combined["value"].rank(method="average")
    N = len(combined)

    group_stats: dict[str, dict] = {}
    for g in group_labels:
        subset_ranks = combined.loc[combined["group"] == g, "rank"]
        group_stats[g] = {
            "mean_rank": float(subset_ranks.mean()),
            "n": int(len(subset_ranks)),
        }

    pairs = list(itertools.combinations(group_labels, 2))
    p_unadj: list[float] = []
    z_stats: list[float] = []

    for g1, g2 in pairs:
        n_i = group_stats[g1]["n"]
        n_j = group_stats[g2]["n"]
        r_i = group_stats[g1]["mean_rank"]
        r_j = group_stats[g2]["mean_rank"]
        se = np.sqrt((N * (N + 1) / 12.0) * (1.0 / n_i + 1.0 / n_j))
        z = (r_i - r_j) / se if se > 0 else float("nan")
        z_stats.append(z)
        p = float(2.0 * (1.0 - stats.norm.cdf(abs(z)))) if not np.isnan(z) else float("nan")
        p_unadj.append(p)

    valid_mask = [not np.isnan(p) for p in p_unadj]
    valid_ps = [p for p, v in zip(p_unadj, valid_mask) if v]
    if valid_ps:
        adj_valid = _apply_correction(valid_ps, correction)
        adj_iter = iter(adj_valid)
        p_adj_all = [next(adj_iter) if v else float("nan") for v in valid_mask]
    else:
        p_adj_all = p_unadj

    results = []
    for (g1, g2), z, p_raw, p_adj in zip(pairs, z_stats, p_unadj, p_adj_all):
        results.append({
            "group1": str(g1),
            "group2": str(g2),
            "z_stat": _sf(z),
            "p_value_unadjusted": _sf(p_raw),
            "p_value_adjusted": _sf(p_adj),
            "significant": bool(not np.isnan(p_adj) and p_adj < 0.05),
        })
    return results


def _kruskal_wallis(df: pd.DataFrame, inp: dict) -> dict:
    outcome_col = inp["outcome_col"]
    group_col = inp["group_col"]
    alpha = float(inp.get("alpha", 0.05))
    correction = inp.get("posthoc_correction", "bonferroni")

    if outcome_col not in df.columns or group_col not in df.columns:
        return {"error": f"Columns '{outcome_col}' or '{group_col}' not found."}

    clean = df[[outcome_col, group_col]].dropna()
    group_labels = sorted(clean[group_col].unique(), key=str)
    k = len(group_labels)

    if k < 2:
        return {"error": f"Kruskal-Wallis requires at least 2 groups; found {k}."}

    warnings: list[dict] = []
    group_arrays = [
        clean.loc[clean[group_col] == g, outcome_col].values.astype(float)
        for g in group_labels
    ]

    small_groups = [str(g) for g, arr in zip(group_labels, group_arrays) if len(arr) < 5]
    if small_groups:
        warnings.append(_warn("warning",
            f"Groups {small_groups} have fewer than 5 observations; test power may be low.",
            "KW_SMALL_GROUP"))

    h_stat, p_value = stats.kruskal(*group_arrays)
    h_stat = float(h_stat)
    p_value = float(p_value)

    n_total = len(clean)
    df_val = k - 1

    # Eta-squared: (H - k + 1) / (n - k)
    denom_eta = n_total - k
    eta_sq = (h_stat - k + 1) / denom_eta if denom_eta > 0 else float("nan")

    if eta_sq < 0.01:
        effect_interp = "small"
    elif eta_sq < 0.06:
        effect_interp = "medium"
    else:
        effect_interp = "large"

    group_ns = {str(g): int(len(arr)) for g, arr in zip(group_labels, group_arrays)}
    group_medians = {str(g): _sf(float(np.median(arr))) for g, arr in zip(group_labels, group_arrays)}

    # Dunn post-hoc
    posthoc_dunn = _dunn_posthoc(
        clean[outcome_col], clean[group_col], group_labels, correction
    )

    if p_value >= alpha:
        warnings.append(_warn("info",
            "Overall test is not significant; post-hoc results should be interpreted cautiously.",
            "KW_NONSIG_POSTHOC"))

    significant = p_value < alpha
    dominant_group = max(group_medians, key=lambda g: group_medians[g] or float("-inf"))

    interpretation = {
        "main_finding": (
            f"{'Significant' if significant else 'No significant'} difference across {k} groups "
            f"(H({df_val})={h_stat:.4f}, p={p_value:.4f}). "
            + (f"'{dominant_group}' has the highest median." if significant else "")
        ),
        "effect_size_meaning": (
            f"Eta-squared = {_sf(eta_sq)} ({effect_interp} effect). "
            f"Approximately {(eta_sq or 0)*100:.1f}% of rank variance is explained by group membership."
        ),
        "key_caveat": (
            "Kruskal-Wallis tests whether the distributions differ broadly (shape, spread, or location), "
            "not exclusively medians. A significant result does not pinpoint which groups differ — "
            "use the Dunn post-hoc comparisons for that."
        ),
    }

    return {
        "test_type": "kruskal_wallis",
        "n_groups": k,
        "group_ns": group_ns,
        "group_medians": group_medians,
        "h_statistic": _sf(h_stat),
        "degrees_of_freedom": df_val,
        "p_value": _sf(p_value),
        "eta_squared": _sf(eta_sq),
        "effect_size_interpretation": effect_interp,
        "posthoc_dunn": posthoc_dunn,
        "posthoc_correction": correction,
        "alpha": alpha,
        "significant": significant,
        "warnings": warnings,
        "interpretation": interpretation,
    }


# ── 3.3d  Friedman ──────────────────────────────────────────────────────────


def _friedman(df: pd.DataFrame, inp: dict) -> dict:
    repeated_cols = inp.get("repeated_cols") or []
    alpha = float(inp.get("alpha", 0.05))
    correction = inp.get("posthoc_correction", "bonferroni")

    missing = [c for c in repeated_cols if c not in df.columns]
    if missing:
        return {"error": f"Columns not found: {missing}"}
    if len(repeated_cols) < 3:
        return {"error": "Friedman requires at least 3 repeated-measure columns."}

    clean = df[repeated_cols].dropna()
    n_subjects = len(clean)
    n_conditions = len(repeated_cols)

    if n_subjects < 3:
        return {"error": f"Friedman requires at least 3 complete rows; found {n_subjects}."}

    warnings: list[dict] = []

    # scipy.stats.friedmanchisquare takes *args (one array per condition)
    arrays = [clean[col].values.astype(float) for col in repeated_cols]
    chi2_stat, p_value = stats.friedmanchisquare(*arrays)
    chi2_stat = float(chi2_stat)
    p_value = float(p_value)

    df_val = n_conditions - 1

    # Kendall's W
    kendalls_w = chi2_stat / (n_subjects * df_val) if (n_subjects * df_val) > 0 else float("nan")

    if kendalls_w < 0.1:
        effect_interp = "weak"
    elif kendalls_w < 0.3:
        effect_interp = "moderate"
    else:
        effect_interp = "strong"

    condition_medians = {col: _sf(float(np.median(clean[col].values))) for col in repeated_cols}

    # Pairwise Wilcoxon post-hoc
    pairs = list(itertools.combinations(repeated_cols, 2))
    p_unadj: list[float] = []
    w_stats: list[float] = []

    for c1, c2 in pairs:
        d = clean[c1].values - clean[c2].values
        nonzero = d[d != 0]
        if len(nonzero) < 4:
            w_stats.append(float("nan"))
            p_unadj.append(float("nan"))
            continue
        try:
            w_res = stats.wilcoxon(clean[c1].values, clean[c2].values,
                                   alternative="two-sided", method="approx")
            w_stats.append(float(w_res.statistic))
            p_unadj.append(float(w_res.pvalue))
        except Exception as exc:
            log.warning("Wilcoxon post-hoc failed for (%s, %s): %s", c1, c2, exc)
            w_stats.append(float("nan"))
            p_unadj.append(float("nan"))

    valid_mask = [not np.isnan(p) for p in p_unadj]
    valid_ps = [p for p, v in zip(p_unadj, valid_mask) if v]
    if valid_ps:
        adj_valid = _apply_correction(valid_ps, correction)
        adj_iter = iter(adj_valid)
        p_adj_all = [next(adj_iter) if v else float("nan") for v in valid_mask]
    else:
        p_adj_all = p_unadj

    posthoc_wilcoxon = []
    for (c1, c2), w, p_raw, p_adj in zip(pairs, w_stats, p_unadj, p_adj_all):
        posthoc_wilcoxon.append({
            "col1": c1,
            "col2": c2,
            "w_statistic": _sf(w),
            "p_value_unadjusted": _sf(p_raw),
            "p_value_adjusted": _sf(p_adj),
            "significant": bool(not np.isnan(p_adj) and p_adj < alpha),
        })

    if n_subjects < 10:
        warnings.append(_warn("warning",
            f"Small number of subjects (n={n_subjects}); Friedman test power may be low.",
            "FRIED_SMALL_N"))

    if p_value >= alpha:
        warnings.append(_warn("info",
            "Overall Friedman test is not significant; post-hoc results should be interpreted cautiously.",
            "FRIED_NONSIG_POSTHOC"))

    significant = p_value < alpha
    best_condition = max(condition_medians, key=lambda c: condition_medians[c] or float("-inf"))

    interpretation = {
        "main_finding": (
            f"{'Significant' if significant else 'No significant'} differences across {n_conditions} "
            f"repeated conditions (χ²({df_val})={chi2_stat:.4f}, p={p_value:.4f}, n={n_subjects} subjects). "
            + (f"'{best_condition}' has the highest median." if significant else "")
        ),
        "effect_size_meaning": (
            f"Kendall's W = {_sf(kendalls_w)} ({effect_interp} concordance). "
            "W ranges from 0 (no agreement in rankings) to 1 (perfect agreement)."
        ),
        "key_caveat": (
            "Friedman tests whether at least one condition's distribution differs from the others. "
            "It does not indicate which specific pair differs — use the pairwise Wilcoxon post-hoc "
            "results (with correction) for that. Assumes the same subjects appear in all conditions."
        ),
    }

    return {
        "test_type": "friedman",
        "n_subjects": n_subjects,
        "n_conditions": n_conditions,
        "condition_medians": condition_medians,
        "chi_square_statistic": _sf(chi2_stat),
        "degrees_of_freedom": df_val,
        "p_value": _sf(p_value),
        "kendalls_w": _sf(kendalls_w),
        "effect_size_interpretation": effect_interp,
        "posthoc_wilcoxon": posthoc_wilcoxon,
        "posthoc_correction": correction,
        "alpha": alpha,
        "significant": significant,
        "warnings": warnings,
        "interpretation": interpretation,
    }


# ── dispatcher ───────────────────────────────────────────────────────────────

_DISPATCH = {
    "mann_whitney":   _mann_whitney,
    "wilcoxon":       _wilcoxon,
    "kruskal_wallis": _kruskal_wallis,
    "friedman":       _friedman,
}


def run_nonparametric_tests(df: pd.DataFrame, analysis_input: dict) -> dict:
    """
    Entry point for all non-parametric tests (AGEARC 3.3a–3.3d).

    Parameters
    ----------
    df : pd.DataFrame
        The dataset to analyse.
    analysis_input : dict
        Must contain ``test_type`` plus test-specific fields; see module docstring.

    Returns
    -------
    dict
        Test results or ``{"error": str}`` on failure.
    """
    if not isinstance(analysis_input, dict):
        try:
            analysis_input = dict(analysis_input)
        except Exception:
            return {"error": "analysis_input must be a dict."}

    test_type = analysis_input.get("test_type", "")
    if test_type not in _DISPATCH:
        return {
            "error": (
                f"Unknown test_type '{test_type}'. "
                f"Must be one of: {sorted(_DISPATCH)}."
            )
        }

    if not isinstance(df, pd.DataFrame):
        return {"error": "df must be a pandas DataFrame."}

    if df.empty:
        return {"error": "DataFrame is empty."}

    try:
        return _DISPATCH[test_type](df, analysis_input)
    except Exception as exc:
        log.exception("run_nonparametric_tests failed for test_type='%s'", test_type)
        return {"error": f"Test execution failed: {exc}"}
