import pandas as pd
import numpy as np
from scipy import stats as scipy_stats
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.visualization import descriptive_analysis
from services.data_processing.report import crud
from services.data_processing.helper.preprocessor import sanitise_result
from schemas.data_processing import DescriptiveAnalysisInput, AnalysisInput


def _safe_mode(df: pd.DataFrame) -> dict:
    """Return mode row as dict, handling columns that are all-NaN (DEFECT-25)."""
    try:
        mode_df = df.mode()
        if mode_df.empty:
            return {}
        return {col: (mode_df[col].iloc[0] if not mode_df[col].isna().all() else None)
                for col in mode_df.columns}
    except Exception:
        return {}


async def perform_descriptive_analysis(df: pd.DataFrame, inputs: AnalysisInput, session: AsyncSession) -> dict:
    """
    Perform descriptive analysis on a given DataFrame.

    :param df: Input DataFrame
    :return: Dictionary containing summary statistics and visualizations
    """

    # Check if the DataFrame is empty
    if df.empty:
        raise ValueError("The DataFrame is empty. Cannot perform analysis.")

    # Check if there are numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if numeric_columns.any():
        describe = df.describe(include=[np.number]).to_dict()
    else:
        describe = {}  # Fallback if no numeric columns are present

    # ------------------------------------------------------------------ #
    # Pre-computations for new metrics (added surgically)                  #
    # ------------------------------------------------------------------ #

    # Per-column extended stats for numeric columns
    _cv: dict = {}
    _percentiles: dict = {
        "p01": {}, "p05": {}, "p10": {}, "p90": {}, "p95": {}, "p99": {}
    }
    _iqr: dict = {}
    _range: dict = {}
    _interpretation_flags: dict = {}

    for col in numeric_columns:
        try:
            col_data = df[col].dropna().values
            n = len(col_data)
            if n == 0:
                continue

            _mean = float(np.nanmean(col_data))
            _std  = float(np.nanstd(col_data, ddof=1)) if n > 1 else 0.0
            _min  = float(np.nanmin(col_data))
            _max  = float(np.nanmax(col_data))
            _q25  = float(np.nanpercentile(col_data, 25))
            _q75  = float(np.nanpercentile(col_data, 75))

            # CV
            _cv[col] = (_std / _mean * 100) if _mean != 0 else None

            # Extra percentiles
            for pct, key in [(1, "p01"), (5, "p05"), (10, "p10"),
                             (90, "p90"), (95, "p95"), (99, "p99")]:
                _percentiles[key][col] = float(np.nanpercentile(col_data, pct))

            # IQR and Range
            _iqr[col]   = _q75 - _q25
            _range[col] = _max - _min

            # Interpretation flags
            flags = []
            try:
                _skew = float(scipy_stats.skew(col_data, bias=False)) if n >= 3 else 0.0
                _kurt = float(scipy_stats.kurtosis(col_data, bias=False)) if n >= 4 else 0.0

                if abs(_skew) > 1.0:
                    flags.append(
                        f"Highly skewed (|skew| > 1.0). The mean may not represent the "
                        f"typical value. Consider using the median."
                    )
                elif abs(_skew) > 0.5:
                    flags.append(
                        f"Moderate skew detected (|skew| = {_skew:.2f}). Check distribution "
                        f"shape before parametric tests."
                    )

                if _kurt > 3:
                    flags.append(
                        f"Heavy tails detected (excess kurtosis = {_kurt:.2f}). More extreme "
                        f"values than a normal distribution."
                    )
            except Exception:
                pass

            if n > 1000:
                flags.append(
                    f"Large sample (n={n}): statistical tests of normality are "
                    f"hypersensitive — rely on Q-Q plots and distribution shape, "
                    f"not p-values alone."
                )

            _interpretation_flags[col] = flags

        except Exception:
            pass

    # Spearman correlation matrix and Pearson p-values
    _spearman_corr: dict = {}
    _pearson_pvalues: dict = {}
    _correlation_warnings: list = []
    try:
        num_df = df[numeric_columns].copy()
        if num_df.shape[1] >= 2:
            spearman_matrix, _ = scipy_stats.spearmanr(num_df, nan_policy="omit")
            cols_list = list(num_df.columns)
            if num_df.shape[1] == 2:
                # spearmanr returns a scalar when n_vars == 2
                _spearman_corr = {
                    cols_list[0]: {cols_list[0]: 1.0, cols_list[1]: float(spearman_matrix)},
                    cols_list[1]: {cols_list[0]: float(spearman_matrix), cols_list[1]: 1.0},
                }
            else:
                _spearman_corr = {
                    cols_list[i]: {
                        cols_list[j]: float(spearman_matrix[i, j])
                        for j in range(len(cols_list))
                    }
                    for i in range(len(cols_list))
                }

            # Pearson p-values and correlation warnings
            for i, ci in enumerate(cols_list):
                _pearson_pvalues[ci] = {}
                for j, cj in enumerate(cols_list):
                    if i == j:
                        _pearson_pvalues[ci][cj] = 0.0
                    elif j > i:
                        try:
                            valid = num_df[[ci, cj]].dropna()
                            if len(valid) >= 3:
                                r_val, p_val = scipy_stats.pearsonr(valid[ci], valid[cj])
                                _pearson_pvalues[ci][cj] = float(p_val)
                                _pearson_pvalues.setdefault(cj, {})[ci] = float(p_val)
                                if abs(r_val) > 0.80:
                                    _correlation_warnings.append(
                                        f"High correlation between {ci} and {cj} "
                                        f"(r = {r_val:.3f}). Using both in the same "
                                        f"regression may produce unstable results."
                                    )
                            else:
                                _pearson_pvalues[ci][cj] = None
                                _pearson_pvalues.setdefault(cj, {})[ci] = None
                        except Exception:
                            _pearson_pvalues[ci][cj] = None
                            _pearson_pvalues.setdefault(cj, {})[ci] = None
    except Exception:
        pass

    # Frequency distributions
    _freq_distributions: dict = {}

    # Continuous columns
    for col in numeric_columns:
        try:
            col_data = df[col].dropna()
            n = len(col_data)
            if n == 0:
                continue
            values = col_data.values.astype(float)
            min_val = float(np.nanmin(values))
            max_val = float(np.nanmax(values))
            q25_fd  = float(np.nanpercentile(values, 25))
            q75_fd  = float(np.nanpercentile(values, 75))
            iqr_val = q75_fd - q25_fd

            if n >= 4 and iqr_val > 0:
                bin_width = 2 * iqr_val / (n ** (1 / 3))
            elif max_val != min_val:
                bin_width = (max_val - min_val) / 10
            else:
                bin_width = 0

            if bin_width > 0 and max_val != min_val:
                n_bins = int((max_val - min_val) / bin_width)
                n_bins = max(5, min(n_bins, 50))
            else:
                n_bins = 10

            counts, bin_edges = np.histogram(values, bins=n_bins)
            counts_list = counts.tolist()
            total = sum(counts_list) or 1
            rel_freq = [c / total for c in counts_list]
            cum_freq = list(np.cumsum(rel_freq))

            # Near-zero variance flag: single value > 80% of non-null rows
            _mode_count = int(pd.Series(values).value_counts().iloc[0]) if n > 0 else 0
            near_zero = (_mode_count / n) > 0.80 if n > 0 else False

            _freq_distributions[col] = {
                "bin_edges": [round(float(e), 6) for e in bin_edges.tolist()],
                "counts": counts_list,
                "relative_frequency": [round(r, 6) for r in rel_freq],
                "cumulative_frequency": [round(c, 6) for c in cum_freq],
                "near_zero_variance": near_zero,
            }
        except Exception:
            pass

    # Categorical/object columns
    for col in df.select_dtypes(include=["object", "category"]).columns:
        try:
            vc = df[col].value_counts(dropna=True)
            total_cat = vc.sum() or 1
            categories = vc.index.tolist()
            counts_cat = vc.values.tolist()
            percentages = [round(c / total_cat * 100, 4) for c in counts_cat]
            mode_val = str(categories[0]) if categories else None
            near_zero_cat = (counts_cat[0] / total_cat) > 0.80 if counts_cat else False
            _freq_distributions[col] = {
                "categories": [str(c) for c in categories],
                "counts": counts_cat,
                "percentages": percentages,
                "mode": mode_val,
                "near_zero_variance": near_zero_cat,
            }
        except Exception:
            pass

    # ------------------------------------------------------------------ #
    # End pre-computations                                                 #
    # ------------------------------------------------------------------ #

    summary = {
        "head": df.head().to_dict(),
        "describe": describe,
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "mean": df.mean(numeric_only=True).to_dict(),
        "median": df.median(numeric_only=True).to_dict(),
        "mode": _safe_mode(df),
        "min": df.min(numeric_only=True).to_dict(),
        "max": df.max(numeric_only=True).to_dict(),
        "count": df.count().to_dict(),
        "percentile_25": df.quantile(0.25, numeric_only=True).to_dict(),
        "percentile_50": df.quantile(0.50, numeric_only=True).to_dict(),
        "percentile_75": df.quantile(0.75, numeric_only=True).to_dict(),
        "percentile_01": _percentiles["p01"],
        "percentile_05": _percentiles["p05"],
        "percentile_10": _percentiles["p10"],
        "percentile_90": _percentiles["p90"],
        "percentile_95": _percentiles["p95"],
        "percentile_99": _percentiles["p99"],
        "iqr": _iqr,
        "range": _range,
        "cv": _cv,
        "variance": df.var(numeric_only=True).to_dict(),
        "standard_deviation": df.std(numeric_only=True).to_dict(),
        "skewness": df.skew(numeric_only=True).to_dict(),
        # Phase 5D: label kurtosis convention — Fisher's excess kurtosis (normal = 0)
        "kurtosis": df.kurt(numeric_only=True).to_dict(),
        "kurtosis_type": "excess (Fisher's definition; normal distribution = 0)",
        "interpretation_flags": _interpretation_flags,
        # Phase 5E: disclose correlation method and caveat
        "correlation_matrix": df.corr(method="pearson", numeric_only=True).to_dict(),
        "correlation_method": "pearson",
        "correlation_method_note": (
            "Pearson correlation assumes bivariate normality and linear relationships. "
            "For non-normal or ordinal data, use Spearman or Kendall."
        ),
        "spearman_correlation": _spearman_corr,
        "correlation_pvalues": _pearson_pvalues,
        "correlation_warnings": _correlation_warnings,
        "unique_values": {col: df[col].nunique() for col in df.columns},
        "value_counts": {col: df[col].value_counts().to_dict() for col in df.select_dtypes(include=['object']).columns},
        "frequency_distributions": _freq_distributions,
        "file_id": inputs.file_id
    }

    report_obj = {}
    report_obj['project_id'] = inputs.project_id
    report_obj['summary'] = sanitise_result(summary)
    report_obj['title'] = inputs.title
    report_obj['visualizations'] = {}
    report_obj['analysis_group'] = inputs.analysis_group

    # Generate visualizations
    if inputs.generate_visualizations:
        descriptive_inputs = inputs.analysis_input
        if not isinstance(descriptive_inputs, DescriptiveAnalysisInput):
            raise ValueError(
                "Invalid analysis input type. Expected DescriptiveAnalysisInput.")
        descriptive_visualizations = descriptive_inputs.descriptive_visualizations
        visualization_list = descriptive_inputs.visualization_list
        visualizations = descriptive_analysis.generate_descriptive_visualizations(
            df, descriptive_visualizations, visualization_list)
        report_obj['visualizations'] = visualizations

    report = await crud.create_report(report_obj, session=session)
    return report
