"""
Statistical Precondition Tests
Runs automatically when a dataset is selected.
Results guide analysis selection and are shown to the user.

Tests included:
  Normality:
    1. Shapiro-Wilk test
    2. Fisher's Exact test (for independence/contingency)
    3. Normal Q-Q plot data
    4. Kolmogorov-Smirnov test (one-sample, against normal)

  Time Series Stationarity:
    1. Augmented Dickey-Fuller (ADF) test
    2. KPSS test
"""
import numpy as np
import pandas as pd
import logging
from typing import List, Dict, Any, Optional
from scipy import stats

log = logging.getLogger(__name__)


# ── Helpers ──────────────────────────────────────────────────────────────────

def _interpret_p(p: float, alpha: float = 0.05) -> dict:
    """Standard p-value interpretation."""
    significant = bool(p < alpha)
    return {
        'p_value':     round(float(p), 6),
        'alpha':       alpha,
        'significant': significant,
        'verdict':     'reject H₀' if significant else 'fail to reject H₀',
    }


def _safe_float(x) -> Optional[float]:
    try:
        v = float(x)
        return None if (v != v or abs(v) == float('inf')) else round(v, 6)
    except Exception:
        return None


def _label(significant: bool, test_name: str) -> str:
    """Human-readable verdict for a test."""
    verdicts = {
        'shapiro':  ('NOT normal',     'Normal'),
        'ks':       ('NOT normal',     'Normal'),
        'adf':      ('Stationary',     'NOT stationary (has unit root)'),
        'kpss':     ('NOT stationary', 'Stationary'),
    }
    if test_name in verdicts:
        true_label, false_label = verdicts[test_name]
        return true_label if significant else false_label
    return 'Significant' if significant else 'Not significant'


# ── Normality Tests ───────────────────────────────────────────────────────────

def shapiro_wilk(series: pd.Series) -> dict:
    """
    Shapiro-Wilk normality test.
    H₀: data is normally distributed.
    Best for n < 5000. Sensitive to ties.
    """
    clean = series.dropna().astype(float)
    n = len(clean)

    if n < 3:
        return {
            'test':   'Shapiro-Wilk',
            'status': 'skipped',
            'reason': f'Requires ≥ 3 observations (got {n})',
        }

    n_tested = min(n, 5000)
    sample = clean if n <= 5000 else clean.sample(5000, random_state=42)
    stat, p = stats.shapiro(sample.values)

    interp = _interpret_p(p)
    # Phase 5B: clear note when sampling is applied
    note = (
        f"Note: Shapiro-Wilk applied to a random sample of {n_tested} "
        f"from {n} observations. For large n, consider Anderson-Darling or Lilliefors."
        if n > 5000 else ""
    )

    result = {
        'test':        'Shapiro-Wilk',
        'statistic':   _safe_float(stat),
        'p_value':     _safe_float(p),
        'n':           int(n),
        'n_tested':    int(n_tested),
        'significant': interp['significant'],
        'verdict':     _label(interp['significant'], 'shapiro'),
        'interpretation': (
            f"p={'<0.001' if p < 0.001 else f'{p:.4f}'} — "
            f"{'Evidence against normality' if interp['significant'] else 'No evidence against normality'}. "
            f"{'Data likely NOT normally distributed.' if interp['significant'] else 'Data may be normally distributed.'}"
        ),
        'recommendation': (
            'Consider non-parametric tests or data transformation (log, sqrt, Box-Cox).'
            if interp['significant']
            else 'Parametric tests (t-test, ANOVA, regression) are appropriate.'
        ),
    }
    if note:
        result['note'] = note

    # Phase 5B: add Anderson-Darling for large samples (n > 2000)
    if n > 2000:
        try:
            ad = stats.anderson(clean.values, dist='norm')
            result['anderson_darling'] = {
                'statistic':     _safe_float(ad.statistic),
                'critical_values': {
                    f'{sl}%': _safe_float(cv)
                    for sl, cv in zip(ad.significance_level, ad.critical_values)
                },
                'note': 'Anderson-Darling is more powerful than Shapiro-Wilk for n > 2000.',
            }
        except Exception:
            pass

    return result


def kolmogorov_smirnov(series: pd.Series) -> dict:
    """
    Lilliefors-corrected Kolmogorov-Smirnov test for normality.

    Phase 5A: replaced the naive one-sample KS test (stats.kstest against
    'norm' with estimated µ/σ) with the Lilliefors correction from statsmodels.
    The naive KS test is anti-conservative when parameters are estimated from
    the data; Lilliefors corrects the critical values for this.

    H₀: data is normally distributed.
    """
    from statsmodels.stats.diagnostic import lilliefors as _lilliefors

    clean = series.dropna().astype(float)
    n = len(clean)

    if n < 5:
        return {
            'test':   'Lilliefors (corrected KS)',
            'status': 'skipped',
            'reason': f'Requires ≥ 5 observations (got {n})',
        }

    if float(clean.std()) == 0:
        return {
            'test':   'Lilliefors (corrected KS)',
            'status': 'skipped',
            'reason': 'Zero variance — all values are identical',
        }

    stat, p = _lilliefors(clean.values, dist='norm')
    interp = _interpret_p(p)

    return {
        'test':        'Lilliefors (corrected KS for estimated parameters)',
        'statistic':   _safe_float(stat),
        'p_value':     _safe_float(p),
        'n':           int(n),
        'significant': interp['significant'],
        'verdict':     _label(interp['significant'], 'ks'),
        'interpretation': (
            f"D={stat:.4f}, p={'<0.001' if p < 0.001 else f'{p:.4f}'} — "
            f"{'Significant deviation from normality (Lilliefors p ≤ 0.05).' if interp['significant'] else 'Data appears normally distributed (Lilliefors p > 0.05).'}"
        ),
        'recommendation': (
            'Distribution deviates from normal. Verify with Q-Q plot.'
            if interp['significant']
            else 'Distribution is consistent with normality.'
        ),
    }


def fishers_exact(df: pd.DataFrame, col1: str, col2: str) -> dict:
    """
    Fisher's Exact test for independence between two categorical columns.
    H₀: the two variables are independent.
    """
    try:
        if col1 not in df.columns or col2 not in df.columns:
            return {
                'test':   "Fisher's Exact",
                'status': 'skipped',
                'reason': f'Columns not found: {col1}, {col2}',
            }

        ct = pd.crosstab(df[col1].astype(str), df[col2].astype(str))
        rows, cols = ct.shape

        if rows < 2 or cols < 2:
            return {
                'test':   "Fisher's Exact",
                'status': 'skipped',
                'reason': 'Need at least 2 categories in each column',
            }

        if rows == 2 and cols == 2:
            # Phase 6D: auto-trigger Fisher's Exact when any expected cell count < 5
            # (Cochran 1954 rule). Chi-squared is appropriate when all expected counts ≥ 5;
            # Fisher's Exact is required for sparse 2×2 tables to preserve the nominal α.
            _, _, _, expected = stats.chi2_contingency(ct.values, correction=False)
            use_fisher = bool((expected < 5).any())

            if use_fisher:
                odds_ratio, p = stats.fisher_exact(ct.values)
                interp = _interpret_p(p)
                min_expected = float(expected.min())
                return {
                    'test':        "Fisher's Exact (auto-triggered: expected cell < 5)",
                    'statistic':   _safe_float(odds_ratio),
                    'p_value':     _safe_float(p),
                    'odds_ratio':  _safe_float(odds_ratio),
                    'table_shape': [int(rows), int(cols)],
                    'min_expected_count': min_expected,
                    'fisher_trigger': True,
                    'significant': interp['significant'],
                    'verdict':     'Dependent' if interp['significant'] else 'Independent',
                    'interpretation': (
                        f"Fisher's Exact used (min expected cell={min_expected:.2f} < 5). "
                        f"Odds ratio={odds_ratio:.4f}, p={'<0.001' if p < 0.001 else f'{p:.4f}'} — "
                        f"{'Variables are dependent (associated).' if interp['significant'] else 'No significant association.'}"
                    ),
                    'recommendation': (
                        f"'{col1}' and '{col2}' are statistically associated. Account for this in analysis."
                        if interp['significant']
                        else f"'{col1}' and '{col2}' appear independent."
                    ),
                }
            else:
                # All expected counts ≥ 5 → Pearson Chi-squared is appropriate
                chi2, p, dof, _ = stats.chi2_contingency(ct.values)
                interp = _interpret_p(p)
                min_expected = float(expected.min())
                return {
                    'test':        'Chi-squared (Pearson)',
                    'statistic':   _safe_float(chi2),
                    'p_value':     _safe_float(p),
                    'dof':         int(dof),
                    'table_shape': [int(rows), int(cols)],
                    'min_expected_count': min_expected,
                    'fisher_trigger': False,
                    'significant': interp['significant'],
                    'verdict':     'Dependent' if interp['significant'] else 'Independent',
                    'interpretation': (
                        f"Chi-squared used (min expected cell={min_expected:.2f} ≥ 5). "
                        f"χ²={chi2:.4f}, df={dof}, p={'<0.001' if p < 0.001 else f'{p:.4f}'} — "
                        f"{'Significant association.' if interp['significant'] else 'No significant association.'}"
                    ),
                    'recommendation': (
                        f"'{col1}' and '{col2}' are statistically associated."
                        if interp['significant']
                        else f"'{col1}' and '{col2}' appear independent."
                    ),
                }
        else:
            # >2×2: Chi-squared is the standard test. Fisher's Exact generalisation
            # (Barnard / Freeman-Halton) is not implemented here.
            chi2, p, dof, expected = stats.chi2_contingency(ct.values)
            interp = _interpret_p(p)
            return {
                'test':        'Chi-squared',
                'statistic':   _safe_float(chi2),
                'p_value':     _safe_float(p),
                'dof':         int(dof),
                'table_shape': [int(rows), int(cols)],
                'significant': interp['significant'],
                'verdict':     'Dependent' if interp['significant'] else 'Independent',
                'interpretation': (
                    f"χ²={chi2:.4f}, df={dof}, p={'<0.001' if p < 0.001 else f'{p:.4f}'} — "
                    f"{'Significant association.' if interp['significant'] else 'No significant association.'}"
                ),
                'recommendation': (
                    'Variables are statistically associated.'
                    if interp['significant']
                    else 'Variables appear independent.'
                ),
            }
    except Exception as e:
        return {'test': "Fisher's Exact", 'status': 'error', 'error': str(e)}


def qq_plot_data(series: pd.Series) -> dict:
    """
    Normal Q-Q plot data — theoretical quantiles vs sample quantiles.
    Returns data points for Plotly rendering on the frontend.
    """
    clean = series.dropna().astype(float)
    n = len(clean)

    if n < 4:
        return {
            'test':   'Normal Q-Q Plot',
            'status': 'skipped',
            'reason': f'Requires ≥ 4 observations (got {n})',
        }

    sample = clean if n <= 1000 else clean.sample(1000, random_state=42)
    sample_sorted = np.sort(sample.values)

    theoretical = stats.norm.ppf(
        np.linspace(1 / (len(sample_sorted) + 1),
                    len(sample_sorted) / (len(sample_sorted) + 1),
                    len(sample_sorted))
    )

    mu, sigma = float(sample_sorted.mean()), float(sample_sorted.std())
    sample_std = (sample_sorted - mu) / sigma if sigma > 0 else sample_sorted - mu

    slope, intercept, r_value, _, _ = stats.linregress(theoretical, sample_std)
    r_squared = float(r_value ** 2)

    if r_squared >= 0.99:
        normality = 'Excellent — very close to normal'
    elif r_squared >= 0.97:
        normality = 'Good — approximately normal'
    elif r_squared >= 0.95:
        normality = 'Fair — mild deviation from normal'
    else:
        normality = 'Poor — significant deviation from normal'

    # Phase 5C: Q-Q plot is exploratory only — no formal pass/fail verdict.
    # Using "Normal" / "NOT normal" labels here is statistically incorrect
    # because R² is descriptive, not a hypothesis test.
    return {
        'test':            'Normal Q-Q Plot',
        'r_squared':       _safe_float(r_squared),
        'slope':           _safe_float(slope),
        'intercept':       _safe_float(intercept),
        'n':               int(n),
        'n_plotted':       int(len(sample_sorted)),
        'normality_fit':   normality,
        'qq_interpretation': (
            f"Q-Q R²={r_squared:.4f} — {normality} (exploratory only; "
            "Q-Q plots are visual guides, not formal normality tests)."
        ),
        'interpretation': (
            f"Q-Q R²={r_squared:.4f} — {normality}. "
            "Q-Q plots provide visual evidence only; use Shapiro-Wilk or Lilliefors for formal testing."
        ),
        'recommendation': (
            'Visual inspection suggests departure from normality. Corroborate with Shapiro-Wilk / Lilliefors.'
            if r_squared < 0.95
            else 'Visual inspection is consistent with normality. Confirm with formal normality tests.'
        ),
        'plot_data': {
            'theoretical_quantiles': theoretical.tolist(),
            'sample_quantiles':      sample_std.tolist(),
            'reference_line': {
                'x': [float(theoretical.min()), float(theoretical.max())],
                'y': [
                    float(slope * theoretical.min() + intercept),
                    float(slope * theoretical.max() + intercept),
                ],
            },
        },
    }


# ── Time Series Stationarity Tests ────────────────────────────────────────────

def augmented_dickey_fuller(series: pd.Series) -> dict:
    """
    ADF test for unit root.
    H₀: unit root present (NOT stationary). Reject → stationary.
    """
    from statsmodels.tsa.stattools import adfuller

    clean = series.dropna().astype(float)
    n = len(clean)

    if n < 20:
        return {
            'test':   'Augmented Dickey-Fuller',
            'status': 'skipped',
            'reason': f'Requires ≥ 20 observations (got {n})',
        }

    try:
        result = adfuller(clean.values, autolag='AIC')
        adf_stat, p, lags_used, n_obs, crit_vals, _ = result
        interp = _interpret_p(p)

        return {
            'test':            'Augmented Dickey-Fuller (ADF)',
            'statistic':       _safe_float(adf_stat),
            'p_value':         _safe_float(p),
            'lags_used':       int(lags_used),
            'n_obs':           int(n_obs),
            'critical_values': {
                '1%':  _safe_float(crit_vals.get('1%')),
                '5%':  _safe_float(crit_vals.get('5%')),
                '10%': _safe_float(crit_vals.get('10%')),
            },
            'significant':    interp['significant'],
            'verdict':        _label(interp['significant'], 'adf'),
            'is_stationary':  interp['significant'],
            'interpretation': (
                f"ADF={adf_stat:.4f}, p={'<0.001' if p < 0.001 else f'{p:.4f}'} — "
                f"{'Reject H₀: Series appears STATIONARY.' if interp['significant'] else 'Fail to reject H₀: Series may have a UNIT ROOT (non-stationary).'}"
            ),
            'recommendation': (
                'Series is stationary. ARIMA, regression on time series are appropriate.'
                if interp['significant']
                else 'Series is non-stationary. Apply differencing (d≥1) before ARIMA. Consider KPSS to confirm.'
            ),
        }
    except Exception as e:
        return {'test': 'Augmented Dickey-Fuller', 'status': 'error', 'error': str(e)}


def kpss_test(series: pd.Series, regression: str = 'c') -> dict:
    """
    KPSS test for stationarity.
    H₀: series IS stationary. Reject → non-stationary.
    """
    from statsmodels.tsa.stattools import kpss

    clean = series.dropna().astype(float)
    n = len(clean)

    if n < 20:
        return {
            'test':   'KPSS',
            'status': 'skipped',
            'reason': f'Requires ≥ 20 observations (got {n})',
        }

    try:
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            kpss_stat, p, lags, crit_vals = kpss(
                clean.values, regression=regression, nlags='auto'
            )

        interp = _interpret_p(p)
        reg_label = 'level' if regression == 'c' else 'trend'

        return {
            'test':            f'KPSS ({reg_label} stationarity)',
            'statistic':       _safe_float(kpss_stat),
            'p_value':         _safe_float(p),
            'lags_used':       int(lags),
            'regression':      regression,
            'critical_values': {
                '10%':  _safe_float(crit_vals.get('10%')),
                '5%':   _safe_float(crit_vals.get('5%')),
                '2.5%': _safe_float(crit_vals.get('2.5%')),
                '1%':   _safe_float(crit_vals.get('1%')),
            },
            'significant':   interp['significant'],
            'verdict':       _label(interp['significant'], 'kpss'),
            'is_stationary': not interp['significant'],
            'interpretation': (
                f"KPSS={kpss_stat:.4f}, p={'<0.001' if p < 0.001 else f'{p:.4f}'} — "
                f"{'Reject H₀: Series is NOT stationary (' + reg_label + ').' if interp['significant'] else 'Fail to reject H₀: Series appears STATIONARY (' + reg_label + ').'}"
            ),
            'recommendation': (
                f'Series lacks {reg_label} stationarity. Differencing or detrending required.'
                if interp['significant']
                else f'Series has {reg_label} stationarity. Suitable for time series models.'
            ),
        }
    except Exception as e:
        return {'test': 'KPSS', 'status': 'error', 'error': str(e)}


# ── Phase 6C: combined stationarity wrapper ───────────────────────────────────

def run_stationarity_tests(series: pd.Series, regression: str = 'c') -> dict:
    """Always run ADF + KPSS together and add a four-way consensus.

    Returning only ADF *or* only KPSS is insufficient:
    - ADF H₀: unit root (non-stationary). Reject → stationary.
    - KPSS H₀: series is stationary. Reject → non-stationary.
    Their combined result disambiguates four distinct cases:

    ADF stat, KPSS stat   → confirmed stationary; no differencing needed.
    ADF stat, KPSS non-st → trend-stationary: mean is constant but variance/
                             trend may not be; detrend before modelling.
    ADF non-st, KPSS stat → possible structural break or the series is
                             level-stationary with a unit-root regime change;
                             re-run ADF with trend, or apply first difference
                             and re-test.
    ADF non-st, KPSS non-st → both agree non-stationary; apply d≥1 differencing.
    """
    adf_result  = augmented_dickey_fuller(series)
    kpss_result = kpss_test(series, regression=regression)

    adf_s  = adf_result.get('is_stationary')
    kpss_s = kpss_result.get('is_stationary')

    if adf_s is None or kpss_s is None:
        # One or both tests were skipped/errored — no consensus possible
        consensus = "Consensus unavailable (one or both tests did not complete)."
        differencing = None
        d_suggestion = None
    elif adf_s and kpss_s:
        consensus    = "Both ADF and KPSS agree: series is STATIONARY."
        differencing = False
        d_suggestion = "No differencing needed. Suitable for ARIMA(p,0,q)."
    elif adf_s and not kpss_s:
        consensus    = (
            "Contradiction: ADF finds no unit root (stationary) but KPSS rejects "
            "level stationarity. The series is likely TREND-STATIONARY — it has no "
            "stochastic trend but its mean changes over time."
        )
        differencing = False
        d_suggestion = (
            "Detrend the series (subtract a fitted linear trend or use 'ct' regression "
            "in KPSS) rather than differencing."
        )
    elif not adf_s and kpss_s:
        consensus    = (
            "Contradiction: ADF fails to reject the unit root but KPSS does not reject "
            "level stationarity. Possible structural break or regime change. "
            "Re-run ADF with trend (regression='ct') or apply one difference and re-test."
        )
        differencing = None
        d_suggestion = (
            "Apply one difference (d=1) as a precaution, then re-run both tests. "
            "If the differenced series passes both, use ARIMA(p,1,q)."
        )
    else:  # not adf_s and not kpss_s
        consensus    = "Both ADF and KPSS agree: series is NON-STATIONARY."
        differencing = True
        d_suggestion = (
            "Apply first differencing (d=1). Re-run both tests after differencing. "
            "If still non-stationary, try d=2 before considering seasonal differencing."
        )

    return {
        "adf":               adf_result,
        "kpss":              kpss_result,
        "consensus":         consensus,
        "differencing_needed": differencing,
        "differencing_suggestion": d_suggestion,
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def run_precondition_tests(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    run_time_series: bool = True,
    run_normality: bool = True,
    max_columns: int = 10,
    fisher_pairs: Optional[List[tuple]] = None,
) -> dict:
    """
    Run all precondition tests on a DataFrame.
    Returns a structured result with per-column and overall findings.
    """
    from services.data_processing.helper.preprocessor import sanitise_result

    if df is None or df.empty:
        return {'status': 'error', 'error': 'Empty dataset'}

    numeric_cols = [c for c in df.columns
                    if str(df[c].dtype) in ('int64', 'float64', 'int32', 'float32')]
    if columns:
        numeric_cols = [c for c in columns
                        if c in df.columns and
                        str(df[c].dtype) in ('int64', 'float64', 'int32', 'float32')]

    test_cols = numeric_cols[:max_columns]

    cat_cols = [c for c in df.columns
                if df[c].dtype == object and df[c].nunique() <= 20
                and c not in numeric_cols]

    normality_results    = {}
    stationarity_results = {}
    fishers_results      = []

    # ── Normality tests ──────────────────────────────────────────────────────
    if run_normality:
        for col in test_cols:
            series = df[col]
            col_results = {}
            for name, fn in [
                ('shapiro_wilk',       lambda s: shapiro_wilk(s)),
                ('kolmogorov_smirnov', lambda s: kolmogorov_smirnov(s)),
                ('qq_plot',            lambda s: qq_plot_data(s)),
            ]:
                try:
                    col_results[name] = fn(series)
                except Exception as e:
                    col_results[name] = {'test': name, 'error': str(e)}
            normality_results[col] = col_results

    # ── Fisher's Exact ───────────────────────────────────────────────────────
    if run_normality and len(cat_cols) >= 2:
        pairs = fisher_pairs or [
            (cat_cols[i], cat_cols[j])
            for i in range(min(3, len(cat_cols)))
            for j in range(i + 1, min(3, len(cat_cols)))
        ]
        for col1, col2 in pairs[:5]:
            result = fishers_exact(df, col1, col2)
            result['columns'] = [col1, col2]
            fishers_results.append(result)

    # ── Stationarity tests (Phase 6C: always run ADF+KPSS together) ─────────
    if run_time_series and len(df) >= 20:
        for col in test_cols[:5]:
            try:
                stationarity_results[col] = run_stationarity_tests(df[col], regression='c')
            except Exception as e:
                stationarity_results[col] = {'error': str(e)}

    # ── Overall votes ────────────────────────────────────────────────────────
    normal_votes     = []
    stationary_votes = []

    for col, tests in normality_results.items():
        sw = tests.get('shapiro_wilk', {})
        ks = tests.get('kolmogorov_smirnov', {})
        qq = tests.get('qq_plot', {})
        votes = []
        if 'significant' in sw: votes.append(not sw['significant'])
        if 'significant' in ks: votes.append(not ks['significant'])
        if 'r_squared' in qq:   votes.append(qq.get('r_squared', 0) >= 0.97)
        if votes:
            normal_votes.append(sum(votes) / len(votes) >= 0.5)

    for col, tests in stationarity_results.items():
        adf_r  = tests.get('adf', {})
        kpss_r = tests.get('kpss', {})
        adf_s  = adf_r.get('is_stationary')
        kpss_s = kpss_r.get('is_stationary')
        if adf_s is not None and kpss_s is not None:
            stationary_votes.append(adf_s and kpss_s)
        elif adf_s is not None:
            stationary_votes.append(adf_s)
        elif kpss_s is not None:
            stationary_votes.append(kpss_s)

    overall_normal     = (sum(normal_votes) / len(normal_votes) >= 0.5
                          if normal_votes else None)
    overall_stationary = (sum(stationary_votes) / len(stationary_votes) >= 0.5
                          if stationary_votes else None)

    analysis_recs = _build_analysis_recommendations(
        overall_normal, overall_stationary,
        len(numeric_cols), len(cat_cols), len(df)
    )

    summary = {
        'n_rows':             int(len(df)),
        'n_numeric_columns':  int(len(numeric_cols)),
        'n_categorical_cols': int(len(cat_cols)),
        'n_columns_tested':   int(len(test_cols)),
        'overall_normal':     overall_normal,
        'overall_stationary': overall_stationary,
        'normality_pct': (
            round(sum(normal_votes) / len(normal_votes) * 100)
            if normal_votes else None
        ),
        'stationarity_pct': (
            round(sum(stationary_votes) / len(stationary_votes) * 100)
            if stationary_votes else None
        ),
    }

    result = {
        'status':                   'success',
        'summary':                  summary,
        'normality':                normality_results,
        'stationarity':             stationarity_results,
        'fishers_exact':            fishers_results,
        'overall': {
            'is_normal':       overall_normal,
            'is_stationary':   overall_stationary,
            'recommendations': analysis_recs['general'],
        },
        'analysis_recommendations': analysis_recs,
    }

    return sanitise_result(result)


def _build_analysis_recommendations(
    is_normal: Optional[bool],
    is_stationary: Optional[bool],
    n_numeric: int,
    n_categorical: int,
    n_rows: int,
) -> dict:
    recommended     = []
    with_caution    = []
    not_recommended = []
    general         = []

    if is_normal is True:
        general.append('✓ Data is approximately normal — parametric tests are appropriate.')
        recommended.extend([
            {'type': 'regression',          'reason': 'Assumes normality of residuals — satisfied'},
            {'type': 'anova',               'reason': 'Assumes normality within groups — satisfied'},
            {'type': 'correlation',         'reason': 'Pearson correlation is valid for normal data'},
            {'type': 'pca',                 'reason': 'Works well with normal data'},
            {'type': 'logistic_regression', 'reason': 'Valid regardless, but residuals behave better'},
            {'type': 'neural_network',      'reason': 'Scaling will work well with normal inputs'},
        ])
        with_caution.extend([
            {'type': 'knn', 'reason': 'Distance-based — normalise first'},
            {'type': 'svm', 'reason': 'Scale-sensitive — standardise first'},
        ])
    elif is_normal is False:
        general.append('⚠ Data is NOT normally distributed — prefer non-parametric or robust methods.')
        recommended.extend([
            {'type': 'correlation',       'reason': 'Use Spearman or Kendall instead of Pearson'},
            {'type': 'clustering',        'reason': 'Does not assume normality'},
            {'type': 'gradient_boosting', 'reason': 'Tree-based — distribution-free'},
            {'type': 'tree_model',        'reason': 'No distributional assumptions'},
            {'type': 'knn',               'reason': 'No distributional assumptions'},
        ])
        with_caution.extend([
            {'type': 'regression', 'reason': 'Check residuals — may need transformation'},
            {'type': 'anova',      'reason': 'Consider Kruskal-Wallis instead'},
        ])
        not_recommended.append({
            'type':   'regression (without transformation)',
            'reason': 'Normality assumption violated — transform data first',
        })
        general.append('💡 Consider: log transform, sqrt transform, or Box-Cox transformation.')

    if is_stationary is True:
        general.append('✓ Time series data is stationary — ARIMA(p,0,q) is appropriate.')
        recommended.extend([
            {'type': 'arima',                    'reason': 'Stationary — no differencing needed (d=0)'},
            {'type': 'acf_pacf',                 'reason': 'Use to determine ARIMA(p,q) orders'},
            {'type': 'exponential_smoothing',     'reason': 'Appropriate for stationary series'},
            {'type': 'moving_average',            'reason': 'Valid for stationary series'},
            {'type': 'time_series_decomposition', 'reason': 'Decomposition meaningful on stationary series'},
        ])
    elif is_stationary is False:
        general.append('⚠ Time series is NON-STATIONARY — differencing required before ARIMA.')
        recommended.extend([
            {'type': 'arima',    'reason': 'Use d≥1 for differencing (e.g. ARIMA(p,1,q))'},
            {'type': 'acf_pacf', 'reason': 'Check ACF of differenced series to determine orders'},
        ])
        with_caution.extend([
            {'type': 'moving_average',            'reason': 'Trend will dominate — detrend first'},
            {'type': 'exponential_smoothing',      'reason': 'Use Holt-Winters for trend/seasonality'},
            {'type': 'time_series_decomposition',  'reason': 'Useful but apply to differenced series'},
        ])
        general.append('💡 Apply first-order differencing. Re-test stationarity after.')

    if n_rows < 30:
        not_recommended.append({
            'type':   'neural_network',
            'reason': f'Only {n_rows} rows — neural networks need ≥100 samples',
        })
        not_recommended.append({
            'type':   'svm',
            'reason': f'Only {n_rows} rows — results may be unreliable',
        })
    elif n_rows > 10000:
        not_recommended.append({
            'type':   'svm',
            'reason': f'{n_rows:,} rows — SVM is too slow (O(n²)). Use Gradient Boosting.',
        })

    if n_numeric >= 3:
        recommended.append({
            'type':   'pca',
            'reason': f'{n_numeric} numeric columns — dimensionality reduction may help',
        })
        recommended.append({
            'type':   'canonical_correlation',
            'reason': 'Multiple numeric variables — test for multivariate relationships',
        })

    if n_categorical >= 2:
        recommended.append({
            'type':   'anova',
            'reason': 'Categorical grouping variables available for group comparison',
        })

    return {
        'recommended':      recommended,
        'with_caution':     with_caution,
        'not_recommended':  not_recommended,
        'general':          general,
    }
