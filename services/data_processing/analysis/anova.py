import statsmodels.api as sm
from statsmodels.formula.api import ols
from typing import Dict, Any, List
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from scipy.stats import levene, shapiro, t as t_dist, f as f_dist
from services.data_processing.report import crud
from services.data_processing.helper.preprocessor import sanitise_result
from services.data_processing.visualization.anova import generate_anova_visualizations
from schemas.data_processing import AnalysisInput  # Adjust import as needed


async def perform_anova(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession) -> Dict[str, Any]:
    """
    Perform ANOVA analysis using StatsModels.

    :param data: Input DataFrame
    :param input: Analysis input containing parameters
    :param session: Database session
    :return: Dictionary with ANOVA results and visualizations
    """
    inputs = input.analysis_input

    # Validate required parameters
    if not hasattr(inputs, 'factor_cols') or not inputs.factor_cols:
        raise ValueError("ANOVA requires factor_cols parameter")
    if not hasattr(inputs, 'value_col') or not inputs.value_col:
        raise ValueError("ANOVA requires value_col parameter")

    # Validate group sizes — exclude small groups if user confirmed, else raise structured error
    exclude_small_groups = getattr(inputs, 'exclude_small_groups', False)
    excluded_groups: dict = {}
    for factor in inputs.factor_cols:
        if factor in data.columns:
            group_counts = data.groupby(factor).size()
            small = group_counts[group_counts < 2]
            if not small.empty:
                if exclude_small_groups:
                    excluded_groups[factor] = small.to_dict()
                    # Filter rows belonging to excluded groups
                    data = data[~data[factor].isin(small.index)]
                else:
                    raise ValueError(
                        f"Factor '{factor}' has groups with fewer than 2 observations: "
                        f"{small.to_dict()}. Each group needs at least 2 samples for ANOVA."
                    )

    if data.empty:
        raise ValueError(
            "After excluding small groups, no data remains. "
            "Cannot perform ANOVA on an empty dataset."
        )

    # Prepare the formula for ANOVA
    formula = f"{inputs.value_col} ~ "

    # Handle different types of ANOVA
    if len(inputs.factor_cols) == 1:
        # One-way ANOVA
        formula += f"C({inputs.factor_cols[0]})"
    else:
        # Multi-way ANOVA with interactions
        factors = [f"C({factor})" for factor in inputs.factor_cols]
        formula += " + ".join(factors)

        # Add interaction terms if requested
        if getattr(inputs, 'include_interactions', False):
            formula += " + " + " + ".join([f"{factors[i]}:{factors[j]}"
                                           for i in range(len(factors))
                                           for j in range(i+1, len(factors))])

    # Fit the model
    model = ols(formula, data=data).fit()

    # Perform ANOVA
    anova_table = sm.stats.anova_lm(model, typ=2)  # Using Type II ANOVA

    # Prepare response
    response_content = {
        **({"excluded_groups": excluded_groups,
            "excluded_groups_note": (
                "The following groups were automatically excluded because they had "
                "fewer than 2 observations, as confirmed by the user: "
                + str(excluded_groups)
            )} if excluded_groups else {}),
        "anova_table": anova_table.to_dict(),
        "model_summary": str(model.summary()),
        "formula": formula,
        "residuals": model.resid.tolist(),
        "fitted_values": model.fittedvalues.tolist()
    }

    # Levene test for homogeneity of variance
    if len(inputs.factor_cols) == 1:
        groups = [group[inputs.value_col].dropna().values
                  for _, group in data.groupby(inputs.factor_cols[0])]
        if all(len(g) >= 2 for g in groups):
            lev_stat, lev_p = levene(*groups)
            response_content["levene_test"] = {
                "statistic": float(lev_stat),
                "p_value": float(lev_p)
            }
            if lev_p < 0.05:
                response_content["levene_warning"] = (
                    "Variance homogeneity assumption may be violated "
                    f"(Levene p={lev_p:.4f} < 0.05). Consider Welch's ANOVA."
                )

    # --- One-way enhancements: Welch's ANOVA, omega², CIs, power ---
    if len(inputs.factor_cols) == 1:
        try:
            _welch_results = _run_welch_anova(data, inputs.value_col, inputs.factor_cols[0])
            response_content.update(_welch_results)
        except Exception as exc:
            response_content["welch_anova_error"] = str(exc)

        try:
            _ci_results = _group_confidence_intervals(data, inputs.value_col, inputs.factor_cols[0])
            response_content["ci_95_per_group"] = _ci_results
        except Exception as exc:
            response_content["ci_95_per_group_error"] = str(exc)

        try:
            _omega = _compute_omega_squared(anova_table)
            response_content.update(_omega)
        except Exception as exc:
            response_content["omega_squared_error"] = str(exc)

        try:
            _power = _compute_observed_power_and_required_n(anova_table, data, inputs.factor_cols[0])
            response_content.update(_power)
        except Exception as exc:
            response_content["power_error"] = str(exc)

    # Shapiro-Wilk test on residuals
    if len(model.resid) >= 3:
        sw_stat, sw_p = shapiro(model.resid)
        response_content["shapiro_wilk_test"] = {
            "statistic": float(sw_stat),
            "p_value": float(sw_p)
        }
        if sw_p < 0.05:
            response_content["normality_warning"] = (
                "Residuals may not be normally distributed "
                f"(Shapiro-Wilk p={sw_p:.4f} < 0.05)."
            )

    # Phase 5K: post-hoc Tukey HSD when one-way ANOVA is significant
    if len(inputs.factor_cols) == 1:
        f_pvalue = None
        try:
            anova_pr = anova_table.get("PR(>F)", {})
            factor_key = next(
                (k for k in anova_pr.index if k != 'Residual'), None
            ) if hasattr(anova_pr, 'index') else None
            if factor_key:
                f_pvalue = float(anova_table.loc[factor_key, 'PR(>F)'])
        except Exception:
            pass
        if f_pvalue is not None and f_pvalue < 0.05:
            try:
                from statsmodels.stats.multicomp import pairwise_tukeyhsd
                pooled_values = data[inputs.value_col].dropna().values
                pooled_groups = data.loc[data[inputs.value_col].notna(), inputs.factor_cols[0]].values
                tukey = pairwise_tukeyhsd(endog=pooled_values, groups=pooled_groups, alpha=0.05)
                summary = tukey.summary()
                # Extract results as lists
                response_content["post_hoc_tukey"] = {
                    "mean_diffs":  [float(x) for x in tukey.meandiffs],
                    "p_adj":       [float(x) for x in tukey.pvalues],
                    "reject_h0":   [bool(x) for x in tukey.reject],
                    "conf_lower":  [float(x) for x in tukey.confint[:, 0]],
                    "conf_upper":  [float(x) for x in tukey.confint[:, 1]],
                }
                response_content["post_hoc_note"] = (
                    "Tukey HSD post-hoc test performed at α=0.05. "
                    "reject_h0=True means the group pair means differ significantly."
                )
            except Exception as exc:
                response_content["post_hoc_note"] = f"Post-hoc Tukey HSD failed: {exc}"

        # Games-Howell post-hoc (default when variances unequal)
        if f_pvalue is not None and f_pvalue < 0.05:
            try:
                _lev_p = response_content.get("levene_test", {}).get("p_value", 1.0)
                _gh_results = _run_games_howell(data, inputs.value_col, inputs.factor_cols[0])
                response_content["posthoc_games_howell"] = _gh_results
                response_content["posthoc_method_used"] = (
                    "Games-Howell" if _lev_p < 0.05 else "Tukey HSD"
                )
            except Exception as exc:
                response_content["posthoc_games_howell_error"] = str(exc)

    # 5K also: run Tukey for any significant factor in multi-way ANOVA
    # (limited to one factor at a time for interpretability)

    # --- Two-way: interaction plot data ---
    if len(inputs.factor_cols) == 2:
        try:
            _ip = _build_interaction_plot_data(
                data, inputs.value_col, inputs.factor_cols[0], inputs.factor_cols[1], anova_table
            )
            response_content["interaction_plot_data"] = _ip
        except Exception as exc:
            response_content["interaction_plot_data_error"] = str(exc)

    # Phase 5L: correct partial eta² calculation
    effect_sizes = calculate_effect_sizes(anova_table, model)
    response_content["effect_sizes"] = effect_sizes

    visualizations = {}

    # Generate visualization
    if input.generate_visualizations:
        visualizations = generate_anova_visualizations(
            data=data,
            model=model,
            factor_cols=inputs.factor_cols,
            value_col=inputs.value_col
        )

    # Create report object (similar to your regression function)
    report_obj = {
        "visualizations": visualizations,
        'project_id': input.project_id,
        'summary': sanitise_result(response_content),
        'title': input.title,
        'analysis_group': input.analysis_group
    }

    # Create and store report if needed
    report = await crud.create_report(report_obj, session=session)
    return report


def calculate_effect_sizes(anova_table, model) -> Dict[str, Any]:
    """Calculate eta² and partial eta² for each factor.

    Phase 5L: the previous implementation only computed total eta² (SS_factor /
    SS_total).  Partial eta² is the standard APA 7th-ed effect size for ANOVA:
        partial η² = SS_factor / (SS_factor + SS_error)
    It is NOT the same as η² in multi-factor designs and should be labelled
    separately to avoid misinterpretation.
    """
    effect_sizes: Dict[str, Any] = {}
    total_ss = anova_table['sum_sq'].sum()
    ss_residual = (
        float(anova_table.loc['Residual', 'sum_sq'])
        if 'Residual' in anova_table.index else float('nan')
    )

    for factor in anova_table.index:
        if factor == 'Residual':
            continue
        ss_factor = float(anova_table.loc[factor, 'sum_sq'])
        # Total η² — straightforward but misleading in multi-factor designs
        effect_sizes[f"{factor}_eta_sq"] = round(ss_factor / total_ss, 6)
        # Partial η² — correct APA metric
        denominator = ss_factor + ss_residual
        effect_sizes[f"{factor}_partial_eta_sq"] = (
            round(ss_factor / denominator, 6) if denominator > 0 else float('nan')
        )

    effect_sizes["note"] = (
        "partial_eta_sq = SS_factor / (SS_factor + SS_error) — "
        "APA 7th Ed. recommended effect size for ANOVA. "
        "eta_sq = SS_factor / SS_total — provided for completeness."
    )
    return effect_sizes


# ---------------------------------------------------------------------------
# Helper: Welch's one-way ANOVA
# ---------------------------------------------------------------------------

def _run_welch_anova(data: pd.DataFrame, value_col: str, factor_col: str) -> Dict[str, Any]:
    """Run Welch's one-way ANOVA. Tries pingouin first, falls back to manual."""
    try:
        import pingouin as pg
        result = pg.welch_anova(data=data, dv=value_col, between=factor_col)
        return {
            "welch_anova": {
                "F": float(result["F"].iloc[0]),
                "p_value": float(result["p-unc"].iloc[0]),
                "ddof1": float(result["ddof1"].iloc[0]),
                "ddof2": float(result["ddof2"].iloc[0]),
                "eta_sq": float(result["np2"].iloc[0]) if "np2" in result.columns else None,
                "method": "pingouin.welch_anova",
            }
        }
    except ImportError:
        pass

    # Manual Welch's F
    groups = data.groupby(factor_col)[value_col].apply(lambda x: x.dropna().values)
    k = len(groups)
    ms = np.array([g.mean() for g in groups])
    ss = np.array([g.std(ddof=1) ** 2 for g in groups])
    ns = np.array([len(g) for g in groups])

    # Guard: need at least 2 obs per group
    if np.any(ns < 2) or np.any(ss == 0):
        return {"welch_anova_note": "Skipped: one or more groups have < 2 obs or zero variance."}

    ws = ns / ss
    W = ws.sum()
    grand_mean_w = (ws * ms).sum() / W
    numerator = (ws * (ms - grand_mean_w) ** 2).sum()
    lambda_ = (2 * (k - 2) / (k ** 2 - 1)) * ((1 - ws / W) ** 2 / (ns - 1)).sum()
    F_welch = numerator / ((k - 1) * (1 + lambda_))
    df1 = k - 1
    df2 = (k ** 2 - 1) / (3 * ((1 - ws / W) ** 2 / (ns - 1)).sum())
    p_value = float(1 - f_dist.cdf(F_welch, df1, df2))

    return {
        "welch_anova": {
            "F": round(float(F_welch), 6),
            "p_value": p_value,
            "df1": df1,
            "df2": round(df2, 4),
            "method": "manual (pingouin unavailable)",
        }
    }


# ---------------------------------------------------------------------------
# Helper: per-group 95% CIs
# ---------------------------------------------------------------------------

def _group_confidence_intervals(data: pd.DataFrame, value_col: str, factor_col: str) -> Dict[str, List[float]]:
    """Return {group_label: [lower, upper]} for 95% CI around each group mean."""
    ci: Dict[str, List[float]] = {}
    for label, grp in data.groupby(factor_col):
        vals = grp[value_col].dropna().values
        n = len(vals)
        if n < 2:
            ci[str(label)] = [float("nan"), float("nan")]
            continue
        mean = vals.mean()
        se = vals.std(ddof=1) / np.sqrt(n)
        margin = float(t_dist.ppf(0.975, df=n - 1)) * se
        ci[str(label)] = [round(mean - margin, 6), round(mean + margin, 6)]
    return ci


# ---------------------------------------------------------------------------
# Helper: omega² (unbiased effect size)
# ---------------------------------------------------------------------------

def _interpret_omega_sq(omega: float) -> str:
    if omega < 0.01:
        return "small"
    if omega < 0.14:
        return "medium"
    return "large"


def _compute_omega_squared(anova_table) -> Dict[str, Any]:
    """Compute omega² alongside eta² for one-way ANOVA table."""
    try:
        factor_key = next(k for k in anova_table.index if k != "Residual")
    except StopIteration:
        return {}

    ss_between = float(anova_table.loc[factor_key, "sum_sq"])
    df_between = float(anova_table.loc[factor_key, "df"])
    ss_residual = float(anova_table.loc["Residual", "sum_sq"])
    df_residual = float(anova_table.loc["Residual", "df"])
    ms_within = ss_residual / df_residual if df_residual > 0 else float("nan")
    ss_total = ss_between + ss_residual
    k = df_between + 1  # number of groups

    omega_sq = (ss_between - (k - 1) * ms_within) / (ss_total + ms_within)
    omega_sq = float(omega_sq)

    return {
        "omega_squared": round(omega_sq, 6),
        "omega_squared_interpretation": _interpret_omega_sq(omega_sq) if not np.isnan(omega_sq) else "undefined",
    }


# ---------------------------------------------------------------------------
# Helper: observed power and required N
# ---------------------------------------------------------------------------

def _compute_observed_power_and_required_n(anova_table, data: pd.DataFrame, factor_col: str) -> Dict[str, Any]:
    """Estimate observed power and required N for 80% power."""
    try:
        from statsmodels.stats.power import FTestAnovaPower
        power_analysis = FTestAnovaPower()

        try:
            factor_key = next(k for k in anova_table.index if k != "Residual")
        except StopIteration:
            return {}

        ss_between = float(anova_table.loc[factor_key, "sum_sq"])
        ss_residual = float(anova_table.loc["Residual", "sum_sq"])
        df_between = float(anova_table.loc[factor_key, "df"])
        df_residual = float(anova_table.loc["Residual", "df"])
        ms_within = ss_residual / df_residual if df_residual > 0 else float("nan")
        k = int(df_between + 1)
        n_per_group = int(data.groupby(factor_col).size().mean())
        n_total = int(data[factor_col].notna().sum())

        # Cohen's f from omega²
        omega = (ss_between - (k - 1) * ms_within) / (ss_between + ss_residual + ms_within)
        if omega <= 0 or np.isnan(omega):
            return {"observed_power_note": "Could not compute: omega² <= 0."}
        cohens_f = np.sqrt(omega / (1 - omega))

        observed_power = float(power_analysis.power(
            effect_size=cohens_f, nobs=n_total, alpha=0.05, k_groups=k
        ))
        required_n_per_group = float(power_analysis.solve_power(
            effect_size=cohens_f, power=0.80, alpha=0.05, k_groups=k
        ))

        return {
            "observed_power": round(observed_power, 4),
            "cohens_f": round(float(cohens_f), 4),
            "required_n_for_80_power": int(np.ceil(required_n_per_group)),
        }
    except Exception as exc:
        return {"observed_power_error": str(exc)}


# ---------------------------------------------------------------------------
# Helper: Games-Howell post-hoc
# ---------------------------------------------------------------------------

def _run_games_howell(data: pd.DataFrame, value_col: str, factor_col: str) -> List[Dict[str, Any]]:
    """Pairwise Games-Howell comparisons. Tries pingouin first, falls back to manual."""
    try:
        import pingouin as pg
        result = pg.pairwise_gameshowell(data=data, dv=value_col, between=factor_col)
        rows = []
        for _, row in result.iterrows():
            rows.append({
                "group1": str(row["A"]),
                "group2": str(row["B"]),
                "mean_diff": float(row["mean(A)"] - row["mean(B)"]) if "mean(A)" in row else float(row.get("diff", float("nan"))),
                "ci_lower": float(row["hedges_g"]) if False else float(row.get("lower", float("nan"))),  # will be overridden below
                "ci_upper": float(row.get("upper", float("nan"))),
                "p_value": float(row["pval"]),
                "significant": bool(row["pval"] < 0.05),
                "hedges_g": float(row.get("hedges_g", float("nan"))),
            })
            # pingouin column names vary by version; patch CI if present
            if "lower" in row and "upper" in row:
                rows[-1]["ci_lower"] = float(row["lower"])
                rows[-1]["ci_upper"] = float(row["upper"])
        return rows
    except ImportError:
        pass

    # Manual Games-Howell
    group_stats = {}
    for label, grp in data.groupby(factor_col):
        vals = grp[value_col].dropna().values
        if len(vals) >= 2:
            group_stats[str(label)] = {
                "mean": vals.mean(),
                "var": vals.std(ddof=1) ** 2,
                "n": len(vals),
            }

    labels = list(group_stats.keys())
    rows = []
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            a, b = labels[i], labels[j]
            ma, mb = group_stats[a]["mean"], group_stats[b]["mean"]
            va, vb = group_stats[a]["var"], group_stats[b]["var"]
            na, nb = group_stats[a]["n"], group_stats[b]["n"]

            se_diff = np.sqrt(va / na + vb / nb)
            if se_diff == 0:
                continue
            t_stat = (ma - mb) / se_diff
            df_ij = (va / na + vb / nb) ** 2 / (
                (va / na) ** 2 / (na - 1) + (vb / nb) ** 2 / (nb - 1)
            )
            p_value = float(2 * t_dist.sf(abs(t_stat), df=df_ij))

            # 95% CI
            margin = float(t_dist.ppf(0.975, df=df_ij)) * se_diff
            mean_diff = ma - mb

            # Cohen's d (pooled)
            pooled_sd = np.sqrt(((na - 1) * va + (nb - 1) * vb) / (na + nb - 2))
            cohens_d = (ma - mb) / pooled_sd if pooled_sd > 0 else float("nan")

            rows.append({
                "group1": a,
                "group2": b,
                "mean_diff": round(float(mean_diff), 6),
                "ci_lower": round(float(mean_diff - margin), 6),
                "ci_upper": round(float(mean_diff + margin), 6),
                "p_value": p_value,
                "significant": p_value < 0.05,
                "cohens_d": round(float(cohens_d), 4),
            })
    return rows


# ---------------------------------------------------------------------------
# Helper: two-way interaction plot data
# ---------------------------------------------------------------------------

def _build_interaction_plot_data(
    data: pd.DataFrame,
    value_col: str,
    factor_a: str,
    factor_b: str,
    anova_table,
) -> Dict[str, Any]:
    """Build cell-means dict for interaction plot and detect significant interaction."""
    cell_means: Dict[str, Dict[str, float]] = {}
    cell_ns: Dict[str, Dict[str, int]] = {}

    for level_a, grp_a in data.groupby(factor_a):
        cell_means[str(level_a)] = {}
        cell_ns[str(level_a)] = {}
        for level_b, grp_ab in grp_a.groupby(factor_b):
            vals = grp_ab[value_col].dropna()
            cell_means[str(level_a)][str(level_b)] = round(float(vals.mean()), 6) if len(vals) else float("nan")
            cell_ns[str(level_a)][str(level_b)] = len(vals)

    # Check if interaction term is in anova_table
    interaction_key = None
    for idx in anova_table.index:
        if ":" in str(idx):
            interaction_key = idx
            break

    interaction_p = float("nan")
    interaction_significant = False
    if interaction_key and "PR(>F)" in anova_table.columns:
        try:
            interaction_p = float(anova_table.loc[interaction_key, "PR(>F)"])
            interaction_significant = interaction_p < 0.05
        except Exception:
            pass

    result: Dict[str, Any] = {
        "factor_a": factor_a,
        "factor_b": factor_b,
        "cell_means": cell_means,
        "cell_ns": cell_ns,
        "interaction_p_value": interaction_p if not np.isnan(interaction_p) else None,
        "interaction_significant": interaction_significant,
    }
    if interaction_significant:
        result["interaction_warning"] = (
            f"A significant interaction was detected (p={interaction_p:.4f}). "
            f"The effect of [{factor_a}] depends on the level of [{factor_b}]. "
            "Main effects must not be interpreted without examining the interaction plot."
        )
    return result


# ---------------------------------------------------------------------------
# Repeated Measures ANOVA
# ---------------------------------------------------------------------------

async def run_repeated_measures_anova(
    df: pd.DataFrame,
    analysis_input: AnalysisInput,
    session: AsyncSession,
) -> Dict[str, Any]:
    """
    Perform repeated-measures ANOVA.

    analysis_input.analysis_input must expose:
      - repeated_cols: list of column names (3+ time points, wide format)
      - subject_col: optional str (column identifying subjects)
    """
    inputs = analysis_input.analysis_input
    repeated_cols: List[str] = getattr(inputs, "repeated_cols", None)
    subject_col: str = getattr(inputs, "subject_col", None)

    if not repeated_cols or len(repeated_cols) < 3:
        raise ValueError("repeated_measures_anova requires at least 3 columns in repeated_cols.")

    # Validate columns exist
    missing = [c for c in repeated_cols if c not in df.columns]
    if missing:
        raise ValueError(f"repeated_cols not found in data: {missing}")

    response_content: Dict[str, Any] = {"analysis_type": "repeated_measures_anova"}
    warnings: List[str] = []

    # ---- Try pingouin path (long format) ----
    try:
        import pingouin as pg

        # Convert wide → long
        id_col = subject_col if subject_col and subject_col in df.columns else "__subject__"
        if id_col == "__subject__":
            df = df.copy()
            df[id_col] = np.arange(len(df))

        long_df = df[[id_col] + repeated_cols].melt(
            id_vars=id_col, var_name="__time__", value_name="__value__"
        ).dropna(subset=["__value__"])

        rm = pg.rm_anova(data=long_df, dv="__value__", within="__time__", subject=id_col, detailed=True)

        # Mauchly sphericity via pingouin
        spher_result = pg.sphericity(data=long_df, dv="__value__", within="__time__", subject=id_col)
        mauchly_w = float(spher_result[1]) if hasattr(spher_result, "__len__") else float("nan")
        mauchly_p = float(spher_result[2]) if hasattr(spher_result, "__len__") else float("nan")

        sphericity_violated = mauchly_p < 0.05 if not np.isnan(mauchly_p) else False
        if sphericity_violated:
            warnings.append(
                f"Sphericity assumption violated (Mauchly W={mauchly_w:.4f}, p={mauchly_p:.4f}). "
                "Greenhouse-Geisser corrected values are reported."
            )

        # Pull corrected stats from rm table (row 0 = within effect)
        rm_row = rm.iloc[0]
        epsilon_gg = float(rm_row.get("eps", float("nan")))
        f_stat = float(rm_row.get("F", float("nan")))
        df_num = float(rm_row.get("ddof1", float("nan")))
        df_den = float(rm_row.get("ddof2", float("nan")))
        p_unc = float(rm_row.get("p-unc", float("nan")))
        p_gg = float(rm_row.get("p-GG-corr", p_unc))
        p_hf = float(rm_row.get("p-HF-corr", p_unc))
        partial_eta_sq = float(rm_row.get("np2", float("nan")))

        # Pairwise post-hoc with Bonferroni correction
        posthoc_rows: List[Dict[str, Any]] = []
        try:
            ph = pg.pairwise_tests(
                data=long_df, dv="__value__", within="__time__", subject=id_col, padjust="bonf"
            )
            for _, phrow in ph.iterrows():
                posthoc_rows.append({
                    "group1": str(phrow.get("A", "")),
                    "group2": str(phrow.get("B", "")),
                    "mean_diff": float(phrow.get("mean(A)", float("nan"))) - float(phrow.get("mean(B)", float("nan"))) if "mean(A)" in phrow else float("nan"),
                    "p_value_bonf": float(phrow.get("p-corr", float("nan"))),
                    "significant": bool(phrow.get("p-corr", 1.0) < 0.05),
                })
        except Exception as ph_exc:
            warnings.append(f"Post-hoc pairwise failed: {ph_exc}")

        response_content.update({
            "mauchly_w": mauchly_w,
            "mauchly_p_value": mauchly_p,
            "sphericity_violated": sphericity_violated,
            "epsilon_gg": epsilon_gg,
            "epsilon_hf": float(rm_row.get("eps-HF", float("nan"))),
            "f_statistic": f_stat,
            "f_statistic_corrected": f_stat * epsilon_gg if not np.isnan(epsilon_gg) else f_stat,
            "df_corrected": round(df_num * epsilon_gg, 4) if not np.isnan(epsilon_gg) else df_num,
            "df_denominator_corrected": round(df_den * epsilon_gg, 4) if not np.isnan(epsilon_gg) else df_den,
            "p_value_corrected": p_gg,
            "p_value_hf": p_hf,
            "p_value_uncorrected": p_unc,
            "eta_squared": partial_eta_sq,
            "posthoc_wilcoxon": posthoc_rows,
            "warnings": warnings,
            "method": "pingouin.rm_anova",
        })

    except ImportError:
        # Fallback: Friedman test (non-parametric equivalent)
        try:
            from scipy.stats import friedmanchisquare
            arrays = [df[c].dropna().values for c in repeated_cols]
            min_len = min(len(a) for a in arrays)
            arrays = [a[:min_len] for a in arrays]
            stat, p_value = friedmanchisquare(*arrays)
            warnings.append(
                "pingouin not available. Used Friedman test as non-parametric fallback. "
                "Sphericity correction, Mauchly test, and corrected F statistics are unavailable."
            )
            response_content.update({
                "friedman_statistic": float(stat),
                "p_value": float(p_value),
                "warnings": warnings,
                "method": "scipy.stats.friedmanchisquare (fallback)",
            })

            # Pairwise Wilcoxon with Bonferroni
            posthoc_rows = []
            try:
                from scipy.stats import wilcoxon
                from itertools import combinations
                pairs = list(combinations(repeated_cols, 2))
                bonf_alpha = 0.05 / len(pairs)
                for col_a, col_b in pairs:
                    vals_a = df[col_a].dropna().values
                    vals_b = df[col_b].dropna().values
                    n = min(len(vals_a), len(vals_b))
                    w_stat, w_p = wilcoxon(vals_a[:n], vals_b[:n])
                    posthoc_rows.append({
                        "group1": col_a,
                        "group2": col_b,
                        "wilcoxon_statistic": float(w_stat),
                        "p_value_bonf": float(min(w_p * len(pairs), 1.0)),
                        "significant": w_p * len(pairs) < 0.05,
                    })
            except Exception as pw_exc:
                warnings.append(f"Pairwise Wilcoxon failed: {pw_exc}")

            response_content["posthoc_wilcoxon"] = posthoc_rows

        except Exception as fallback_exc:
            response_content["error"] = f"Both pingouin and scipy fallback failed: {fallback_exc}"
            warnings.append(str(fallback_exc))
            response_content["warnings"] = warnings

    # Store report
    report_obj = {
        "visualizations": {},
        "project_id": analysis_input.project_id,
        "summary": sanitise_result(response_content),
        "title": analysis_input.title,
        "analysis_group": analysis_input.analysis_group,
    }
    report = await crud.create_report(report_obj, session=session)
    return report


# ---------------------------------------------------------------------------
# Top-level dispatch (call this instead of perform_anova for new analysis types)
# ---------------------------------------------------------------------------

async def run_anova(
    data: pd.DataFrame,
    analysis_input: AnalysisInput,
    session: AsyncSession,
) -> Dict[str, Any]:
    """Dispatch to the appropriate ANOVA variant based on analysis_type."""
    analysis_type = getattr(analysis_input.analysis_input, "analysis_type", "one_way")
    if analysis_type == "repeated_measures_anova":
        return await run_repeated_measures_anova(data, analysis_input, session)
    return await perform_anova(data, analysis_input, session)
