"""
poisson_regression.py — AGEARC spec Feature 3.6d

Implements Poisson regression with automatic overdispersion detection and
Negative Binomial fallback, plus zero-inflation flagging.

Entry point: run_poisson_regression(df, analysis_input) -> dict
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import chi2


def run_poisson_regression(df: pd.DataFrame, analysis_input) -> dict:
    """
    Fit a Poisson GLM and return coefficients, IRRs, goodness-of-fit stats,
    overdispersion diagnostics, and (if overdispersed) a Negative Binomial fit.

    Parameters
    ----------
    df : pd.DataFrame
    analysis_input : dict or object with .analysis_input attribute
        outcome_col  : str   — non-negative integer count column
        feature_cols : list[str] — predictor columns
        alpha        : float — significance level (default 0.05)

    Returns
    -------
    dict with model results, or {"error": ..., "traceback": ...} on failure.
    """
    try:
        # ── resolve analysis_input ────────────────────────────────────────────
        if isinstance(analysis_input, dict):
            inp = analysis_input
        elif hasattr(analysis_input, "analysis_input"):
            raw = analysis_input.analysis_input
            inp = raw if isinstance(raw, dict) else (
                raw.__dict__ if hasattr(raw, "__dict__") else {}
            )
        else:
            inp = analysis_input.__dict__ if hasattr(analysis_input, "__dict__") else {}

        outcome_col = inp.get("outcome_col")
        feature_cols = inp.get("feature_cols", [])
        alpha = float(inp.get("alpha", 0.05))

        # ── input validation ──────────────────────────────────────────────────
        if not outcome_col:
            return {"error": "outcome_col is required."}
        if not feature_cols:
            return {"error": "feature_cols must be a non-empty list."}

        missing_cols = [c for c in [outcome_col] + feature_cols if c not in df.columns]
        if missing_cols:
            return {"error": f"Column(s) not found in dataframe: {missing_cols}"}

        data = df[[outcome_col] + feature_cols].dropna()
        if data.empty:
            return {"error": "No rows remain after dropping NaN values."}

        y = data[outcome_col]

        if (y < 0).any():
            return {"error": f"outcome_col '{outcome_col}' contains negative values. Poisson regression requires non-negative counts."}
        if not np.issubdtype(y.dtype, np.number):
            return {"error": f"outcome_col '{outcome_col}' must be numeric."}

        X = sm.add_constant(data[feature_cols], has_constant="add")

        # ── fit Poisson GLM ───────────────────────────────────────────────────
        poisson_model = sm.GLM(y, X, family=sm.families.Poisson()).fit()

        # ── coefficient table with IRR ────────────────────────────────────────
        def _coef_table(model_result) -> list[dict]:
            rows = []
            for name, coef, se, z, p in zip(
                model_result.params.index,
                model_result.params,
                model_result.bse,
                model_result.tvalues,
                model_result.pvalues,
            ):
                irr = np.exp(coef)
                rows.append({
                    "predictor": name,
                    "log_coeff": round(float(coef), 4),
                    "std_error": round(float(se), 4),
                    "z_value": round(float(z), 4),
                    "p_value": round(float(p), 4),
                    "irr": round(float(irr), 4),
                    "irr_ci_lower": round(float(np.exp(coef - 1.96 * se)), 4),
                    "irr_ci_upper": round(float(np.exp(coef + 1.96 * se)), 4),
                    "significant": bool(p < alpha),
                })
            return rows

        coef_table = _coef_table(poisson_model)

        # ── goodness of fit ───────────────────────────────────────────────────
        pearson_chi2 = poisson_model.pearson_chi2
        df_resid = poisson_model.df_resid
        pearson_chi2_pvalue = float(chi2.sf(pearson_chi2, df_resid))
        overdispersion_statistic = float(pearson_chi2 / df_resid) if df_resid > 0 else None
        overdispersed = overdispersion_statistic is not None and overdispersion_statistic > 1.5

        # ── Negative Binomial fallback (if overdispersed) ─────────────────────
        neg_binom_result = None
        if overdispersed:
            try:
                nb_model = sm.GLM(y, X, family=sm.families.NegativeBinomial()).fit()
                neg_binom_result = {
                    "aic": round(float(nb_model.aic), 4),
                    "bic": round(float(nb_model.bic), 4),
                    "log_likelihood": round(float(nb_model.llf), 4),
                    "coefficient_table": _coef_table(nb_model),
                }
            except Exception as nb_exc:
                neg_binom_result = {"error": str(nb_exc)}

        # ── zero-inflation check ──────────────────────────────────────────────
        observed_zero_pct = float((y == 0).mean() * 100)
        predicted_zeros = np.exp(-np.exp(X @ poisson_model.params))
        predicted_zero_pct = float(predicted_zeros.mean() * 100)
        zero_inflation = observed_zero_pct > (predicted_zero_pct * 1.5)

        # ── warnings ─────────────────────────────────────────────────────────
        warnings: list[dict] = []
        if overdispersed:
            warnings.append({
                "level": "warning",
                "message": (
                    f"Overdispersion detected (Pearson chi²/df = "
                    f"{overdispersion_statistic:.2f}). "
                    "Negative Binomial model has been fitted automatically."
                ),
                "code": "OVERDISPERSION",
            })
        if zero_inflation:
            warnings.append({
                "level": "warning",
                "message": (
                    f"Excess zeros detected ({observed_zero_pct:.1f}% observed vs "
                    f"{predicted_zero_pct:.1f}% predicted). Consider Zero-Inflated "
                    "Poisson or Zero-Inflated Negative Binomial."
                ),
                "code": "ZERO_INFLATION",
            })

        return {
            "model_type": "negative_binomial" if overdispersed else "poisson",
            "n": int(len(data)),
            "n_predictors": len(feature_cols),
            "aic": round(float(poisson_model.aic), 4),
            "bic": round(float(poisson_model.bic), 4),
            "log_likelihood": round(float(poisson_model.llf), 4),
            "deviance": round(float(poisson_model.deviance), 4),
            "pearson_chi_squared": round(float(pearson_chi2), 4),
            "pearson_chi2_p_value": round(pearson_chi2_pvalue, 4),
            "degrees_of_freedom_residual": int(df_resid),
            "overdispersion_statistic": (
                round(overdispersion_statistic, 4) if overdispersion_statistic is not None else None
            ),
            "overdispersed": overdispersed,
            "zero_inflation_flag": zero_inflation,
            "observed_zero_pct": round(observed_zero_pct, 2),
            "predicted_zero_pct": round(predicted_zero_pct, 2),
            "coefficient_table": coef_table,
            "negative_binomial": neg_binom_result,
            "recommended_model": "negative_binomial" if overdispersed else "poisson",
            "warnings": warnings,
            "interpretation": {
                "main_finding": (
                    f"The Poisson model"
                    f"{'(overdispersed — Negative Binomial fitted)' if overdispersed else ''}"
                    f" was fitted with {len(feature_cols)} predictor(s) on {len(data)} observations."
                ),
                "irr_note": (
                    "IRR (Incidence Rate Ratio) = exp(coefficient). "
                    "IRR > 1 means the predictor increases the event rate; "
                    "IRR < 1 means it decreases it."
                ),
                "key_caveat": (
                    "Overdispersion inflates false positives in Poisson regression. "
                    "Always check the overdispersion statistic (Pearson chi²/df)."
                ),
            },
        }

    except Exception as exc:
        import traceback
        return {
            "error": f"Poisson regression failed: {str(exc)}",
            "traceback": traceback.format_exc(),
        }
