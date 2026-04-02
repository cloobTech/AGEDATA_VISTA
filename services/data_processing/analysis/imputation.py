"""
Imputation analysis — Phase 6B.

Strategies
----------
mean / median / most_frequent
    sklearn SimpleImputer.  Fills each column independently using the column's
    mean, median, or most-frequent value (mode).  Fast, interpretable, and
    appropriate when data are missing completely at random (MCAR).

knn
    sklearn KNNImputer.  Imputes each missing value using the mean of the
    k nearest non-missing neighbours in feature space (Euclidean distance by
    default).  More accurate than simple statistics when missing values are not
    MCAR, but O(n²) in memory — capped at 50 000 rows for safety.

mice
    sklearn IterativeImputer (MICE — Multiple Imputation by Chained Equations).
    Models each column as a function of the others, iterating until convergence.
    The gold standard for missing-at-random (MAR) data, but considerably slower
    than the univariate strategies.  Capped at 50 000 rows.

ffill / bfill
    Pandas forward-fill / backward-fill.  Propagates the last (or next) known
    value along the row axis.  Only sensible for ordered data (time series,
    sequential records); invalid for randomly ordered tabular data.

Return value
------------
A report containing per-column imputation statistics (n_missing_before,
n_missing_after, strategy, fill_value for simple methods) and a preview of
the first ``preview_rows`` rows of the imputed DataFrame.
"""

from typing import Dict, Any
import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession

from schemas.data_processing import AnalysisInput
from services.data_processing.report import crud

_SKLEARN_STRATEGIES = {"mean", "median", "most_frequent"}
_PANDAS_STRATEGIES  = {"ffill", "bfill"}
_HEAVY_STRATEGIES   = {"knn", "mice"}
_HEAVY_ROW_CAP      = 50_000


def _impute(data: pd.DataFrame, target_cols: list[str], strategy: str,
            knn_neighbors: int, mice_max_iter: int) -> tuple[pd.DataFrame, dict]:
    """Return (imputed_df, per_col_stats)."""
    working = data[target_cols].copy()

    # Collect baseline missing counts
    missing_before = working.isnull().sum().to_dict()

    if strategy in _SKLEARN_STRATEGIES:
        from sklearn.impute import SimpleImputer
        imputer = SimpleImputer(strategy=strategy)
        imputed_array = imputer.fit_transform(working)
        imputed_df = pd.DataFrame(imputed_array, columns=target_cols, index=working.index)

        # statistics_dict: fill value per column (first row of imputer.statistics_)
        stats_vals = dict(zip(target_cols, imputer.statistics_.tolist()))

    elif strategy == "knn":
        from sklearn.impute import KNNImputer
        if len(working) > _HEAVY_ROW_CAP:
            working = working.iloc[:_HEAVY_ROW_CAP]
        imputer = KNNImputer(n_neighbors=knn_neighbors)
        imputed_array = imputer.fit_transform(working)
        imputed_df = pd.DataFrame(imputed_array, columns=target_cols, index=working.index)
        stats_vals = {c: None for c in target_cols}  # no single fill-value for KNN

    elif strategy == "mice":
        from sklearn.experimental import enable_iterative_imputer  # noqa: F401
        from sklearn.impute import IterativeImputer
        if len(working) > _HEAVY_ROW_CAP:
            working = working.iloc[:_HEAVY_ROW_CAP]
        imputer = IterativeImputer(max_iter=mice_max_iter, random_state=42)
        imputed_array = imputer.fit_transform(working)
        imputed_df = pd.DataFrame(imputed_array, columns=target_cols, index=working.index)
        stats_vals = {c: None for c in target_cols}

    elif strategy == "ffill":
        imputed_df = working.ffill()
        stats_vals = {c: None for c in target_cols}

    elif strategy == "bfill":
        imputed_df = working.bfill()
        stats_vals = {c: None for c in target_cols}

    else:
        raise ValueError(f"Unknown imputation strategy '{strategy}'")

    missing_after = imputed_df.isnull().sum().to_dict()

    per_col_stats: dict[str, dict] = {}
    for col in target_cols:
        per_col_stats[col] = {
            "n_missing_before": int(missing_before.get(col, 0)),
            "n_missing_after":  int(missing_after.get(col, 0)),
            "n_imputed":        int(missing_before.get(col, 0)) - int(missing_after.get(col, 0)),
            "fill_value":       (
                float(stats_vals[col])
                if stats_vals.get(col) is not None and not isinstance(stats_vals[col], str)
                else stats_vals.get(col)
            ),
        }

    return imputed_df, per_col_stats


async def perform_imputation_analysis(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession,
) -> Dict[str, Any]:
    inp = inputs.analysis_input  # typed as ImputationInput by select_analysis

    missing_cols = [c for c in inp.target_cols if c not in data.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in dataset: {missing_cols}")

    # Only impute numeric columns for sklearn strategies; ffill/bfill work on any type.
    strategy = inp.strategy.value
    if strategy in (_SKLEARN_STRATEGIES | _HEAVY_STRATEGIES):
        non_numeric = [
            c for c in inp.target_cols
            if not pd.api.types.is_numeric_dtype(data[c])
        ]
        if non_numeric:
            raise ValueError(
                f"Strategy '{strategy}' requires numeric columns; "
                f"non-numeric columns selected: {non_numeric}. "
                "Use 'most_frequent' for categorical columns, or 'ffill'/'bfill' for any type."
            )

    imputed_df, per_col_stats = _impute(
        data,
        inp.target_cols,
        strategy,
        inp.knn_neighbors,
        inp.mice_max_iter,
    )

    # Merge imputed columns back into the original frame
    result_df = data.copy()
    for col in inp.target_cols:
        if col in imputed_df.columns:
            result_df.loc[imputed_df.index, col] = imputed_df[col]

    # Replace any remaining numpy scalars so the preview is JSON-serialisable
    preview = (
        result_df.head(inp.preview_rows)
        .replace({np.nan: None})
        .to_dict(orient="records")
    )

    total_imputed = sum(s["n_imputed"] for s in per_col_stats.values())

    summary = {
        "strategy":      strategy,
        "target_cols":   inp.target_cols,
        "total_imputed": total_imputed,
        "per_column":    per_col_stats,
        "preview_rows":  len(preview),
        "note": (
            "Preview contains the first {:,} rows of the imputed dataset. "
            "Columns not listed in target_cols are unchanged.".format(len(preview))
        ),
    }
    if strategy == "knn":
        summary["knn_neighbors"] = inp.knn_neighbors
    elif strategy == "mice":
        summary["mice_max_iter"] = inp.mice_max_iter

    report_obj = {
        "visualizations": {},
        "project_id":     inputs.project_id,
        "summary":        summary,
        "preview":        preview,
        "title":          inputs.title,
        "analysis_group": inputs.analysis_group,
    }
    return await crud.create_report(report_obj, session=session)
