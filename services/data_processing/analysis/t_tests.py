"""
t_tests.py — Feature Function 3.1 (AGEARC spec 3.1a, 3.1b, 3.1c)

Three t-test types:
  3.1a  one_sample    — compare a variable mean against a fixed reference value
  3.1b  independent   — Welch's t-test for two unrelated groups
  3.1c  paired        — paired (repeated-measures) t-test on two columns
"""

import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.power import TTestPower, TTestIndPower


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_t_tests(df: pd.DataFrame, analysis_input: dict) -> dict:
    """
    Dispatch to the appropriate t-test based on analysis_input['test_type'].

    Parameters
    ----------
    df              : raw DataFrame (may contain NaNs)
    analysis_input  : dict with keys described in module docstring

    Returns
    -------
    dict — full result payload, or {'error': ..., 'warnings': [...]} on failure
    """
    try:
        test_type = analysis_input.get("test_type", "")
        if test_type == "one_sample":
            return _one_sample(df, analysis_input)
        elif test_type == "independent":
            return _independent(df, analysis_input)
        elif test_type == "paired":
            return _paired(df, analysis_input)
        else:
            raise ValueError(
                f"Unknown test_type '{test_type}'. "
                "Expected 'one_sample', 'independent', or 'paired'."
            )
    except Exception as exc:
        msg = str(exc)
        return {
            "error": msg,
            "warnings": [{"level": "error", "message": msg, "code": "COMPUTATION_ERROR"}],
        }


# ---------------------------------------------------------------------------
# 3.1a — One-sample t-test
# ---------------------------------------------------------------------------

def _one_sample(df: pd.DataFrame, ai: dict) -> dict:
    col = ai["variable_col"]
    ref = float(ai["reference_value"])
    alpha = float(ai.get("alpha", 0.05))
    ci_level = float(ai.get("ci_level", 0.95))

    data = df[col].dropna().astype(float)
    n = int(len(data))
    if n < 2:
        raise ValueError(
            f"Column '{col}' has fewer than 2 non-null observations (found {n})."
        )

    mean = float(data.mean())
    std = float(data.std(ddof=1))
    mean_diff = mean - ref
    df_val = n - 1

    t_stat, p_value = stats.ttest_1samp(data, popmean=ref)
    t_stat = float(t_stat)
    p_value = float(p_value)

    # CIs for the mean difference at ci_level and 0.99
    se = std / np.sqrt(n)
    ci_95_lower, ci_95_upper = _ci_from_t(mean_diff, se, df_val, ci_level)
    ci_99_lower, ci_99_upper = _ci_from_t(mean_diff, se, df_val, 0.99)

    # Effect size
    cohens_d = mean_diff / std if std > 0 else 0.0
    effect_interp = _interpret_effect(abs(cohens_d))

    # Power
    power_obj = TTestPower()
    observed_power = float(
        power_obj.solve_power(
            effect_size=abs(cohens_d),
            nobs=n,
            alpha=alpha,
            alternative="two-sided",
        )
        if cohens_d != 0
        else 0.0
    )
    required_n = _required_n_one_sample(power_obj, abs(cohens_d), alpha)

    # Assumption checks
    normality = _shapiro(data, label=col)
    assumption_checks = {"normality": normality}

    # Warnings
    warnings = []
    if n < 10:
        warnings.append(_warn("warning", f"Sample size is small (n={n}). Results may be unreliable.", "SMALL_N"))
    if normality["p_value"] < 0.05:
        warnings.append(_warn("warning", "Shapiro-Wilk normality test failed (p < 0.05). T-test assumes normality.", "NORMALITY_FAIL"))
    if abs(cohens_d) < 0.2 and p_value < alpha:
        warnings.append(_warn("info", "The effect is statistically significant but very small in practical terms (|d| < 0.2).", "SMALL_EFFECT"))
    if observed_power < 0.80 and p_value >= alpha:
        warnings.append(_warn(
            "warning",
            f"This result may be non-significant because the sample is too small to detect a real effect "
            f"(power = {observed_power:.0%}). Recommend ≥80% power.",
            "LOW_POWER",
        ))

    interpretation = _build_interpretation(
        test_type="one_sample",
        p_value=p_value,
        cohens_d=cohens_d,
        power=observed_power,
        alpha=alpha,
        ci_lower=ci_95_lower,
        ci_upper=ci_95_upper,
        n=n,
        ci_level=ci_level,
    )

    return {
        "test_type": "one_sample",
        "n": n,
        "mean": round(mean, 6),
        "reference_value": ref,
        "mean_diff": round(mean_diff, 6),
        "t_statistic": round(t_stat, 6),
        "degrees_of_freedom": df_val,
        "p_value": round(p_value, 6),
        "ci_lower": round(ci_95_lower, 6),
        "ci_upper": round(ci_95_upper, 6),
        "ci_99_lower": round(ci_99_lower, 6),
        "ci_99_upper": round(ci_99_upper, 6),
        "cohens_d": round(cohens_d, 6),
        "effect_size_interpretation": effect_interp,
        "observed_power": round(observed_power, 6),
        "required_n_for_80_power": required_n,
        "warnings": warnings,
        "interpretation": interpretation,
        "assumption_checks": assumption_checks,
    }


# ---------------------------------------------------------------------------
# 3.1b — Independent samples t-test (Welch's, always)
# ---------------------------------------------------------------------------

def _independent(df: pd.DataFrame, ai: dict) -> dict:
    group_col = ai["group_col"]
    outcome_col = ai["outcome_col"]
    alpha = float(ai.get("alpha", 0.05))
    ci_level = float(ai.get("ci_level", 0.95))

    clean = df[[group_col, outcome_col]].dropna()
    groups = clean[group_col].unique()
    if len(groups) != 2:
        raise ValueError(
            f"Independent t-test requires exactly 2 groups in '{group_col}', "
            f"but found: {list(groups)}."
        )

    g1_name, g2_name = str(groups[0]), str(groups[1])
    g1 = clean.loc[clean[group_col] == groups[0], outcome_col].astype(float).values
    g2 = clean.loc[clean[group_col] == groups[1], outcome_col].astype(float).values

    if len(g1) < 2:
        raise ValueError(f"Group '{g1_name}' has fewer than 2 observations.")
    if len(g2) < 2:
        raise ValueError(f"Group '{g2_name}' has fewer than 2 observations.")

    n1, n2 = int(len(g1)), int(len(g2))
    mean1, mean2 = float(g1.mean()), float(g2.mean())
    std1, std2 = float(g1.std(ddof=1)), float(g2.std(ddof=1))
    mean_diff = mean1 - mean2

    # Welch's t-test (equal_var=False)
    t_stat, p_value = stats.ttest_ind(g1, g2, equal_var=False)
    t_stat = float(t_stat)
    p_value = float(p_value)

    # Welch-Satterthwaite df
    welch_df = float(_welch_df(std1, std2, n1, n2))

    # CI for mean difference
    se_diff = np.sqrt(std1**2 / n1 + std2**2 / n2)
    ci_lower, ci_upper = _ci_from_t(mean_diff, se_diff, welch_df, ci_level)

    # Effect sizes
    pooled_std = np.sqrt((std1**2 + std2**2) / 2)
    cohens_d = float(mean_diff / pooled_std) if pooled_std > 0 else 0.0
    hedges_g = float(cohens_d * (1 - 3 / (4 * (n1 + n2 - 2) - 1)))

    # CLES: P(X1 > X2) via Mann-Whitney U
    u_stat, _ = stats.mannwhitneyu(g1, g2, alternative="greater")
    cles = float(u_stat) / (n1 * n2)

    effect_interp = _interpret_effect(abs(cohens_d))

    # Power
    power_obj = TTestIndPower()
    observed_power = float(
        power_obj.solve_power(
            effect_size=abs(cohens_d),
            nobs1=n1,
            ratio=n2 / n1,
            alpha=alpha,
            alternative="two-sided",
        )
        if cohens_d != 0
        else 0.0
    )
    required_n = _required_n_independent(power_obj, abs(cohens_d), alpha)

    # Assumption checks
    norm_g1 = _shapiro(g1, label=g1_name)
    norm_g2 = _shapiro(g2, label=g2_name)
    levene_stat, levene_p = stats.levene(g1, g2)
    assumption_checks = {
        "normality": {g1_name: norm_g1, g2_name: norm_g2},
        "levene": {
            "statistic": round(float(levene_stat), 6),
            "p_value": round(float(levene_p), 6),
            "equal_variances": bool(levene_p >= 0.05),
            "note": "Welch's test is used regardless of this result.",
        },
    }

    # Warnings
    warnings = []
    max_n, min_n = max(n1, n2), min(n1, n2)
    if min_n > 0 and max_n / min_n > 5:
        warnings.append(_warn(
            "warning",
            f"Extreme sample size imbalance (ratio {max_n / min_n:.1f}:1). "
            "Results may be sensitive to assumption violations.",
            "EXTREME_IMBALANCE",
        ))
    if norm_g1["p_value"] < 0.05:
        warnings.append(_warn("warning", f"Normality failed for group '{g1_name}' (Shapiro-Wilk p < 0.05).", "NORMALITY_FAIL"))
    if norm_g2["p_value"] < 0.05:
        warnings.append(_warn("warning", f"Normality failed for group '{g2_name}' (Shapiro-Wilk p < 0.05).", "NORMALITY_FAIL"))
    if n1 < 10 or n2 < 10:
        small_grp = g1_name if n1 < 10 else g2_name
        warnings.append(_warn("warning", f"Group '{small_grp}' has fewer than 10 observations. Normality cannot be reliably assessed.", "SMALL_N"))
    if abs(cohens_d) < 0.2 and p_value < alpha:
        warnings.append(_warn("info", "The effect is statistically significant but very small in practical terms (|d| < 0.2).", "SMALL_EFFECT"))
    if observed_power < 0.80 and p_value >= alpha:
        warnings.append(_warn(
            "warning",
            f"Low statistical power ({observed_power:.0%}). Sample may be too small to detect a real effect.",
            "LOW_POWER",
        ))

    interpretation = _build_interpretation(
        test_type="independent",
        p_value=p_value,
        cohens_d=cohens_d,
        power=observed_power,
        alpha=alpha,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        n=n1 + n2,
        ci_level=ci_level,
    )

    return {
        "test_type": "independent",
        "group_names": [g1_name, g2_name],
        "group_ns": {g1_name: n1, g2_name: n2},
        "group_means": {g1_name: round(mean1, 6), g2_name: round(mean2, 6)},
        "group_stds": {g1_name: round(std1, 6), g2_name: round(std2, 6)},
        "mean_difference": round(mean_diff, 6),
        "t_statistic": round(t_stat, 6),
        "degrees_of_freedom": round(welch_df, 4),
        "p_value": round(p_value, 6),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "cohens_d": round(cohens_d, 6),
        "hedges_g": round(hedges_g, 6),
        "cles": round(cles, 6),
        "effect_size_interpretation": effect_interp,
        "observed_power": round(observed_power, 6),
        "required_n_for_80_power": required_n,
        "warnings": warnings,
        "interpretation": interpretation,
        "assumption_checks": assumption_checks,
    }


# ---------------------------------------------------------------------------
# 3.1c — Paired t-test
# ---------------------------------------------------------------------------

def _paired(df: pd.DataFrame, ai: dict) -> dict:
    col1 = ai["col1"]
    col2 = ai["col2"]
    alpha = float(ai.get("alpha", 0.05))
    ci_level = float(ai.get("ci_level", 0.95))

    clean = df[[col1, col2]].dropna()
    n_pairs = int(len(clean))
    if n_pairs < 2:
        raise ValueError(
            f"Paired t-test requires at least 2 complete pairs, but found {n_pairs}."
        )

    vals1 = clean[col1].astype(float).values
    vals2 = clean[col2].astype(float).values
    differences = vals2 - vals1

    mean1 = float(vals1.mean())
    mean2 = float(vals2.mean())
    mean_diff = float(differences.mean())
    std_diff = float(differences.std(ddof=1))
    df_val = n_pairs - 1

    t_stat, p_value = stats.ttest_rel(vals1, vals2)
    t_stat = float(t_stat)
    p_value = float(p_value)

    # CI for mean difference
    se_diff = std_diff / np.sqrt(n_pairs)
    ci_lower, ci_upper = _ci_from_t(mean_diff, se_diff, df_val, ci_level)

    # Effect size: Cohen's d_z
    cohens_d_z = float(mean_diff / std_diff) if std_diff > 0 else 0.0

    # Pearson correlation between the two columns
    r_paired, r_p = stats.pearsonr(vals1, vals2)
    r_paired = float(r_paired)

    effect_interp = _interpret_effect(abs(cohens_d_z))

    # Power (treat as one-sample on the differences)
    power_obj = TTestPower()
    observed_power = float(
        power_obj.solve_power(
            effect_size=abs(cohens_d_z),
            nobs=n_pairs,
            alpha=alpha,
            alternative="two-sided",
        )
        if cohens_d_z != 0
        else 0.0
    )
    required_n = _required_n_one_sample(power_obj, abs(cohens_d_z), alpha)

    # Assumption check: normality of DIFFERENCES (not individual cols)
    norm_diff = _shapiro(differences, label="differences")
    assumption_checks = {"normality": norm_diff}

    # Warnings
    warnings = []
    if n_pairs < 10:
        warnings.append(_warn("warning", f"Small number of pairs (n={n_pairs}). Results may be unreliable.", "SMALL_N"))
    if norm_diff["p_value"] < 0.05:
        warnings.append(_warn(
            "warning",
            "Shapiro-Wilk normality test failed on the difference scores (p < 0.05). "
            "The paired t-test assumes normality of the differences.",
            "NORMALITY_FAIL",
        ))
    if r_paired < -0.3:
        warnings.append(_warn(
            "warning",
            f"The correlation between paired measurements is negative (r = {r_paired:.3f}). "
            "Pairing is counterproductive. Consider using the independent samples t-test instead.",
            "NEGATIVE_CORRELATION",
        ))
    if abs(cohens_d_z) < 0.2 and p_value < alpha:
        warnings.append(_warn("info", "The effect is statistically significant but very small in practical terms (|d_z| < 0.2).", "SMALL_EFFECT"))
    if observed_power < 0.80 and p_value >= alpha:
        warnings.append(_warn(
            "warning",
            f"Low statistical power ({observed_power:.0%}). Sample may be too small to detect a real effect.",
            "LOW_POWER",
        ))

    interpretation = _build_interpretation(
        test_type="paired",
        p_value=p_value,
        cohens_d=cohens_d_z,
        power=observed_power,
        alpha=alpha,
        ci_lower=ci_lower,
        ci_upper=ci_upper,
        n=n_pairs,
        ci_level=ci_level,
    )

    return {
        "test_type": "paired",
        "n_pairs": n_pairs,
        "mean_col1": round(mean1, 6),
        "mean_col2": round(mean2, 6),
        "mean_difference": round(mean_diff, 6),
        "std_difference": round(std_diff, 6),
        "t_statistic": round(t_stat, 6),
        "degrees_of_freedom": df_val,
        "p_value": round(p_value, 6),
        "ci_lower": round(ci_lower, 6),
        "ci_upper": round(ci_upper, 6),
        "cohens_d_z": round(cohens_d_z, 6),
        "r_paired": round(r_paired, 6),
        "effect_size_interpretation": effect_interp,
        "observed_power": round(observed_power, 6),
        "required_n_for_80_power": required_n,
        "warnings": warnings,
        "interpretation": interpretation,
        "assumption_checks": assumption_checks,
    }


# ---------------------------------------------------------------------------
# Interpretation builder
# ---------------------------------------------------------------------------

def _build_interpretation(
    test_type: str,
    p_value: float,
    cohens_d: float,
    power: float,
    alpha: float,
    ci_lower: float,
    ci_upper: float,
    n: int,
    ci_level: float = 0.95,
) -> dict:
    """Build plain-English interpretation dict for any t-test type."""

    # main_finding
    if p_value < alpha:
        if test_type == "one_sample":
            desc = "The sample mean differs significantly from the reference value."
        elif test_type == "independent":
            desc = "The two groups have significantly different means."
        else:
            desc = "The paired measurements differ significantly."
        main_finding = f"The result is statistically significant (p = {p_value:.4f}). {desc}"
    else:
        main_finding = f"No significant effect was detected (p = {p_value:.4f})."

    # effect_size_meaning
    abs_d = abs(cohens_d)
    if abs_d < 0.2:
        es_label = "negligible effect"
    elif abs_d < 0.5:
        es_label = "small effect"
    elif abs_d < 0.8:
        es_label = "medium effect"
    else:
        es_label = "large effect"
    effect_size_meaning = (
        f"The observed Cohen's d of {cohens_d:.3f} represents a {es_label} "
        f"(benchmarks: 0.2 = small, 0.5 = medium, 0.8 = large)."
    )

    # ci_meaning
    ci_pct = f"{ci_level * 100:.0f}"
    ci_meaning = (
        f"We are {ci_pct}% confident the true mean difference lies between "
        f"{ci_lower:.3f} and {ci_upper:.3f}."
    )

    # power_note
    if power < 0.80:
        power_note = (
            f"With the current sample (n={n}), statistical power was {power:.0%}. "
            "Recommend ≥80% power."
        )
    else:
        power_note = f"Statistical power is adequate ({power:.0%} ≥ 80%)."

    # key_caveat
    if test_type == "independent":
        key_caveat = (
            "This test assumes each observation is from a different independent individual. "
            "Observational data only shows association, not causation."
        )
    elif test_type == "paired":
        key_caveat = (
            "The normality assumption applies to the difference scores, not individual columns. "
            "Observational data only shows association, not causation."
        )
    else:
        key_caveat = "Observational data only shows association, not causation."

    return {
        "main_finding": main_finding,
        "effect_size_meaning": effect_size_meaning,
        "ci_meaning": ci_meaning,
        "power_note": power_note,
        "key_caveat": key_caveat,
    }


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _shapiro(data, label: str = "") -> dict:
    """Run Shapiro-Wilk; gracefully handle n < 3 or n > 5000."""
    arr = np.asarray(data, dtype=float)
    arr = arr[~np.isnan(arr)]
    n = len(arr)
    if n < 3:
        return {
            "label": label,
            "statistic": None,
            "p_value": None,
            "normal": None,
            "note": f"Shapiro-Wilk requires n ≥ 3 (n={n}).",
        }
    if n > 5000:
        # scipy shapiro is unreliable above 5000; subsample
        rng = np.random.default_rng(seed=42)
        arr = rng.choice(arr, size=5000, replace=False)
        note = "Shapiro-Wilk run on random subsample of 5000 (n > 5000)."
    else:
        note = ""
    stat, p = stats.shapiro(arr)
    return {
        "label": label,
        "statistic": round(float(stat), 6),
        "p_value": round(float(p), 6),
        "normal": bool(p >= 0.05),
        "note": note,
    }


def _ci_from_t(estimate: float, se: float, df: float, level: float) -> tuple:
    """Confidence interval for an estimate using the t-distribution."""
    t_crit = float(stats.t.ppf((1 + level) / 2, df=df))
    return estimate - t_crit * se, estimate + t_crit * se


def _welch_df(s1: float, s2: float, n1: int, n2: int) -> float:
    """Welch-Satterthwaite degrees of freedom."""
    v1, v2 = s1**2 / n1, s2**2 / n2
    return (v1 + v2) ** 2 / (v1**2 / (n1 - 1) + v2**2 / (n2 - 1))


def _interpret_effect(abs_d: float) -> str:
    if abs_d < 0.2:
        return "negligible"
    elif abs_d < 0.5:
        return "small"
    elif abs_d < 0.8:
        return "medium"
    return "large"


def _warn(level: str, message: str, code: str) -> dict:
    return {"level": level, "message": message, "code": code}


def _required_n_one_sample(power_obj: TTestPower, effect_size: float, alpha: float) -> int:
    """Required n for 80% power, one-sample / paired design."""
    if effect_size == 0:
        return 0
    try:
        n = power_obj.solve_power(
            effect_size=effect_size,
            power=0.80,
            alpha=alpha,
            alternative="two-sided",
        )
        return int(np.ceil(n))
    except Exception:
        return 0


def _required_n_independent(power_obj: TTestIndPower, effect_size: float, alpha: float) -> int:
    """Required n per group for 80% power, independent design."""
    if effect_size == 0:
        return 0
    try:
        n = power_obj.solve_power(
            effect_size=effect_size,
            power=0.80,
            alpha=alpha,
            ratio=1.0,
            alternative="two-sided",
        )
        return int(np.ceil(n))
    except Exception:
        return 0
