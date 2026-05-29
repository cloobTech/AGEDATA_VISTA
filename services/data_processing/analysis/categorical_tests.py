"""
categorical_tests.py — AGEARC spec Features 3.4a–3.4c

Implements three categorical association tests:
  3.4a  Chi-square test of independence
  3.4b  Fisher's exact test (2×2 only)
  3.4c  McNemar test for paired categorical data

Entry point: run_categorical_tests(df, analysis_input) -> dict
"""

import math
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, fisher_exact, binom
from statsmodels.stats.contingency_tables import Table2x2
from typing import Any


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def run_categorical_tests(df: pd.DataFrame, analysis_input: dict) -> dict:
    """
    Dispatch to the appropriate categorical test.

    Parameters
    ----------
    df : pd.DataFrame
    analysis_input : dict
        Required keys: test_type, col1, col2
        Optional key:  alpha (default 0.05)

    Returns
    -------
    dict with test results, or {"error": ..., "warnings": [...]} on failure.
    """
    test_type = analysis_input.get("test_type", "")
    col1 = analysis_input.get("col1")
    col2 = analysis_input.get("col2")
    alpha = float(analysis_input.get("alpha", 0.05))

    # --- column presence check ---
    missing = [c for c in (col1, col2) if c not in df.columns]
    if missing:
        return {
            "error": f"Column(s) not found in dataframe: {missing}",
            "warnings": [],
        }

    # Drop rows where either column is NaN
    subset = df[[col1, col2]].dropna()
    if subset.empty:
        return {
            "error": "No rows remain after dropping NaN values in col1 and col2.",
            "warnings": [],
        }

    if test_type == "chi_square":
        return _chi_square(subset, col1, col2, alpha)
    elif test_type == "fisher_exact":
        return _fisher_exact(subset, col1, col2, alpha)
    elif test_type == "mcnemar":
        return _mcnemar(subset, col1, col2, alpha)
    else:
        return {
            "error": (
                f"Unknown test_type '{test_type}'. "
                "Must be one of: chi_square, fisher_exact, mcnemar."
            ),
            "warnings": [],
        }


# ---------------------------------------------------------------------------
# 3.4a  Chi-square test of independence
# ---------------------------------------------------------------------------

def _chi_square(df: pd.DataFrame, col1: str, col2: str, alpha: float) -> dict:
    table = pd.crosstab(df[col1], df[col2])
    n = int(table.values.sum())
    n_rows, n_cols = table.shape

    chi2, p_value, dof, expected_arr = chi2_contingency(table, correction=False)

    expected_df = pd.DataFrame(expected_arr, index=table.index, columns=table.columns)

    # --- warnings ---
    warnings: list[dict] = []
    valid = True

    if (expected_arr < 1).any():
        valid = False
        warnings.append({
            "level": "error",
            "message": (
                "Chi-square is invalid — expected cell frequency < 1. "
                "Use Fisher's Exact Test or collapse categories."
            ),
            "code": "EXPECTED_FREQ_ZERO",
        })

    n_cells = expected_arr.size
    n_low = int((expected_arr < 5).sum())
    if n_low > 0:
        pct = round(100 * n_low / n_cells, 1)
        warnings.append({
            "level": "warning",
            "message": (
                f"Chi-square may be unreliable — {pct}% of cells have expected "
                "frequency < 5. Consider Fisher's Exact Test."
            ),
            "code": "EXPECTED_FREQ_LOW",
        })

    # --- effect sizes ---
    cramers_v = float(math.sqrt(chi2 / (n * min(n_rows - 1, n_cols - 1)))) if n > 0 and min(n_rows - 1, n_cols - 1) > 0 else float("nan")

    result: dict[str, Any] = {
        "test_type": "chi_square",
        "chi_square_statistic": round(float(chi2), 6),
        "degrees_of_freedom": int(dof),
        "p_value": round(float(p_value), 6),
        "n": n,
        "cramers_v": round(cramers_v, 6),
        "valid": valid,
    }

    # 2×2 extras
    if n_rows == 2 and n_cols == 2:
        phi = float(math.sqrt(chi2 / n)) if n > 0 else float("nan")
        result["phi"] = round(phi, 6)

        a, b, c, d = (
            int(table.iloc[0, 0]),
            int(table.iloc[0, 1]),
            int(table.iloc[1, 0]),
            int(table.iloc[1, 1]),
        )
        if b * c > 0:
            or_val = (a * d) / (b * c)
            log_or = math.log(or_val)
            se_log_or = math.sqrt(1/a + 1/b + 1/c + 1/d) if all(v > 0 for v in (a, b, c, d)) else float("nan")
            z = 1.959964  # 97.5th percentile of normal
            result["odds_ratio"] = round(or_val, 6)
            result["or_ci_lower"] = round(math.exp(log_or - z * se_log_or), 6) if not math.isnan(se_log_or) else float("nan")
            result["or_ci_upper"] = round(math.exp(log_or + z * se_log_or), 6) if not math.isnan(se_log_or) else float("nan")
        else:
            result["odds_ratio"] = float("inf") if b == 0 or c == 0 else float("nan")
            result["or_ci_lower"] = float("nan")
            result["or_ci_upper"] = float("nan")

    # --- contingency tables ---
    result["contingency_table"] = _df_to_nested_dict(table)
    result["expected_table"] = _df_to_nested_dict(expected_df.round(4))

    row_pct = table.div(table.sum(axis=1), axis=0) * 100
    col_pct = table.div(table.sum(axis=0), axis=1) * 100
    total_pct = table / n * 100

    result["row_percentages"] = _df_to_nested_dict(row_pct.round(2))
    result["col_percentages"] = _df_to_nested_dict(col_pct.round(2))
    result["total_percentages"] = _df_to_nested_dict(total_pct.round(2))

    # --- standardised residuals ---
    std_resid_arr = (table.values - expected_arr) / np.sqrt(expected_arr)
    std_resid_df = pd.DataFrame(std_resid_arr, index=table.index, columns=table.columns)
    result["standardised_residuals"] = _df_to_nested_dict(pd.DataFrame(
        np.round(std_resid_arr, 4), index=table.index, columns=table.columns
    ))

    notable_cells = []
    for row_label in table.index:
        for col_label in table.columns:
            residual = float(std_resid_df.loc[row_label, col_label])
            if abs(residual) > 2:
                notable_cells.append({
                    "row": str(row_label),
                    "col": str(col_label),
                    "residual": round(residual, 4),
                    "direction": "over" if residual > 0 else "under",
                })
    result["notable_cells"] = notable_cells

    result["warnings"] = warnings
    result["interpretation"] = _interpret_chi_square(chi2, p_value, alpha, cramers_v, n_rows, n_cols, valid)

    return result


# ---------------------------------------------------------------------------
# 3.4b  Fisher's exact test
# ---------------------------------------------------------------------------

def _fisher_exact(df: pd.DataFrame, col1: str, col2: str, alpha: float) -> dict:
    table = pd.crosstab(df[col1], df[col2])
    n_rows, n_cols = table.shape

    if n_rows != 2 or n_cols != 2:
        return {
            "error": (
                f"Fisher's Exact Test requires a 2×2 contingency table. "
                f"Got {n_rows}×{n_cols}. Ensure col1 and col2 each have exactly 2 categories."
            ),
            "warnings": [],
        }

    n = int(table.values.sum())
    arr = table.values  # shape (2, 2)

    # Two-tailed and one-tailed (less direction)
    _, p_two = fisher_exact(arr, alternative="two-sided")
    _, p_one = fisher_exact(arr, alternative="less")

    # Odds ratio and exact CI via statsmodels Table2x2
    sm_table = Table2x2(arr)
    or_val = float(sm_table.oddsratio)
    or_ci = sm_table.oddsratio_confint(alpha=0.05, method="exact")
    or_ci_lower = float(or_ci[0])
    or_ci_upper = float(or_ci[1])

    warnings: list[dict] = []
    # Fisher is appropriate when expected counts are low — no error, but note if
    # the table is larger than 2×2 (already caught above).

    result: dict[str, Any] = {
        "test_type": "fisher_exact",
        "p_value_two_tailed": round(float(p_two), 6),
        "p_value_one_tailed": round(float(p_one), 6),
        "odds_ratio": round(or_val, 6),
        "or_ci_lower": round(or_ci_lower, 6),
        "or_ci_upper": round(or_ci_upper, 6),
        "n": n,
        "contingency_table": _df_to_nested_dict(table),
        "warnings": warnings,
        "interpretation": _interpret_fisher(p_two, alpha, or_val, or_ci_lower, or_ci_upper),
    }
    return result


# ---------------------------------------------------------------------------
# 3.4c  McNemar test
# ---------------------------------------------------------------------------

def _mcnemar(df: pd.DataFrame, col1: str, col2: str, alpha: float) -> dict:
    """
    col1 = 'before' measurements, col2 = 'after' measurements.
    Build a 2×2 cross-tabulation of (before, after) paired combinations.
    """
    table = pd.crosstab(df[col1], df[col2])
    n_rows, n_cols = table.shape

    if n_rows != 2 or n_cols != 2:
        return {
            "error": (
                f"McNemar Test requires a 2×2 paired table. "
                f"Got {n_rows}×{n_cols}. Ensure col1 and col2 each have exactly 2 categories."
            ),
            "warnings": [],
        }

    # The 2×2 layout:
    #              after_0   after_1
    #  before_0  [  a          b  ]
    #  before_1  [  c          d  ]
    # Discordant cells: b (0→1) and c (1→0)
    a = int(table.iloc[0, 0])
    b = int(table.iloc[0, 1])
    c = int(table.iloc[1, 0])
    d = int(table.iloc[1, 1])

    n_concordant = a + d
    n_discordant = b + c
    n = a + b + c + d

    # p-value selection
    if n_discordant < 25:
        # Exact binomial: P(X >= max(b,c)) under H0: b=c, p=0.5
        p_value = float(2 * binom.sf(max(b, c) - 1, n_discordant, 0.5))
        p_value = min(p_value, 1.0)
        p_method = "exact_binomial"
        # Chi-square statistic with continuity correction (Yates) for reference
        if n_discordant > 0:
            chi2_stat = ((abs(b - c) - 1) ** 2) / n_discordant
        else:
            chi2_stat = 0.0
    else:
        # Asymptotic with Yates continuity correction
        chi2_stat = ((abs(b - c) - 1) ** 2) / n_discordant if n_discordant > 0 else 0.0
        p_value = float(stats.chi2.sf(chi2_stat, df=1))
        p_method = "asymptotic"

    # Odds ratio = b / c (discordant ratio); CI via log method
    if c > 0:
        or_val = b / c
        log_or = math.log(or_val) if or_val > 0 else float("nan")
        se_log_or = math.sqrt(1 / b + 1 / c) if b > 0 and c > 0 else float("nan")
        z = 1.959964
        or_ci_lower = math.exp(log_or - z * se_log_or) if not math.isnan(se_log_or) else float("nan")
        or_ci_upper = math.exp(log_or + z * se_log_or) if not math.isnan(se_log_or) else float("nan")
    else:
        or_val = float("inf") if b > 0 else float("nan")
        or_ci_lower = float("nan")
        or_ci_upper = float("nan")

    # Marginal proportions: proportion of "positive" category
    # Use iloc[1] index as "positive" (second category alphabetically after crosstab sort)
    prop_before = (b + d) / n if n > 0 else float("nan")   # col1 == category[1]
    prop_after = (c + d) / n if n > 0 else float("nan")    # col2 == category[1]
    prop_change = prop_after - prop_before

    warnings: list[dict] = []
    if n_discordant == 0:
        warnings.append({
            "level": "warning",
            "message": "All paired observations are concordant — McNemar test is trivially non-significant.",
            "code": "NO_DISCORDANT_PAIRS",
        })

    result: dict[str, Any] = {
        "test_type": "mcnemar",
        "n_concordant": n_concordant,
        "n_discordant": n_discordant,
        "chi_square_statistic": round(float(chi2_stat), 6),
        "p_value": round(float(p_value), 6),
        "p_method": p_method,
        "odds_ratio": round(float(or_val), 6) if not math.isnan(float(or_val)) and not math.isinf(float(or_val)) else or_val,
        "or_ci_lower": round(float(or_ci_lower), 6) if not math.isnan(float(or_ci_lower)) else or_ci_lower,
        "or_ci_upper": round(float(or_ci_upper), 6) if not math.isnan(float(or_ci_upper)) else or_ci_upper,
        "proportion_before": round(float(prop_before), 6),
        "proportion_after": round(float(prop_after), 6),
        "proportion_change": round(float(prop_change), 6),
        "contingency_table": _df_to_nested_dict(table),
        "warnings": warnings,
        "interpretation": _interpret_mcnemar(p_value, alpha, or_val, b, c, prop_before, prop_after),
    }
    return result


# ---------------------------------------------------------------------------
# Interpretation helpers
# ---------------------------------------------------------------------------

def _interpret_chi_square(
    chi2: float, p_value: float, alpha: float,
    cramers_v: float, n_rows: int, n_cols: int, valid: bool,
) -> dict:
    sig = p_value < alpha

    if not valid:
        main = (
            "Chi-square test result is invalid due to expected cell frequencies below 1. "
            "Interpret with caution or use Fisher's Exact Test."
        )
    elif sig:
        main = (
            f"There is a statistically significant association between the two variables "
            f"(χ²={chi2:.4f}, p={p_value:.4f} < α={alpha})."
        )
    else:
        main = (
            f"No statistically significant association was found between the two variables "
            f"(χ²={chi2:.4f}, p={p_value:.4f} ≥ α={alpha})."
        )

    if not math.isnan(cramers_v):
        if cramers_v < 0.1:
            es_meaning = f"Cramér's V = {cramers_v:.4f} indicates a negligible effect size."
        elif cramers_v < 0.3:
            es_meaning = f"Cramér's V = {cramers_v:.4f} indicates a small-to-medium effect size."
        elif cramers_v < 0.5:
            es_meaning = f"Cramér's V = {cramers_v:.4f} indicates a medium-to-large effect size."
        else:
            es_meaning = f"Cramér's V = {cramers_v:.4f} indicates a large effect size."
    else:
        es_meaning = "Effect size (Cramér's V) could not be computed."

    return {
        "main_finding": main,
        "effect_size_meaning": es_meaning,
        "key_caveat": "Observational — association not causation.",
    }


def _interpret_fisher(
    p_two: float, alpha: float, or_val: float,
    or_ci_lower: float, or_ci_upper: float,
) -> dict:
    sig = p_two < alpha

    if sig:
        main = (
            f"Fisher's Exact Test indicates a statistically significant association "
            f"(two-tailed p={p_two:.4f} < α={alpha})."
        )
    else:
        main = (
            f"Fisher's Exact Test found no statistically significant association "
            f"(two-tailed p={p_two:.4f} ≥ α={alpha})."
        )

    if not math.isnan(or_val) and not math.isinf(or_val):
        es_meaning = (
            f"Odds ratio = {or_val:.4f} (95% CI: {or_ci_lower:.4f}–{or_ci_upper:.4f}). "
            "An OR > 1 means the outcome is more likely in the first row category."
        )
    else:
        es_meaning = "Odds ratio could not be computed (zero cell count)."

    return {
        "main_finding": main,
        "effect_size_meaning": es_meaning,
        "key_caveat": "Observational — association not causation.",
    }


def _interpret_mcnemar(
    p_value: float, alpha: float, or_val: float,
    b: int, c: int, prop_before: float, prop_after: float,
) -> dict:
    sig = p_value < alpha
    direction = ""
    if b != c:
        direction = " Proportion increased after intervention." if b > c else " Proportion decreased after intervention."

    if sig:
        main = (
            f"McNemar's test indicates a statistically significant change between "
            f"paired measurements (p={p_value:.4f} < α={alpha}).{direction}"
        )
    else:
        main = (
            f"McNemar's test found no statistically significant change between "
            f"paired measurements (p={p_value:.4f} ≥ α={alpha})."
        )

    if not math.isnan(float(or_val)) and not math.isinf(float(or_val)):
        es_meaning = (
            f"Discordant ratio (b/c) = {float(or_val):.4f}. Values > 1 indicate more "
            "subjects shifted toward the second category after the intervention."
        )
    else:
        es_meaning = "Discordant odds ratio could not be computed."

    return {
        "main_finding": main,
        "effect_size_meaning": es_meaning,
        "key_caveat": "For McNemar, ensure data is genuinely paired.",
    }


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _df_to_nested_dict(df: pd.DataFrame) -> dict:
    """Convert a DataFrame to a nested dict with string keys: {row: {col: value}}."""
    return {
        str(row): {str(col): val for col, val in row_data.items()}
        for row, row_data in df.to_dict(orient="index").items()
    }
