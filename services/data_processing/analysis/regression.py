from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler
import numpy as np
import pandas as pd
from services.data_processing.report import crud
from services.data_processing.visualization.regression_analysis import (
    linear_regression_plot,
    decision_tree_plot,
)
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import RegressionInput, AnalysisInput


async def perform_regression(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession):
    """
    Perform regression using scikit-learn.

    :param regression_type: Type of regression ('linear', 'decision_tree', 'logistic')
    :param data: Input DataFrame
    :param features_col: List of feature columns
    :param label_col: Target column
    :return: Trained regression model and performance metrics
    """

    inputs: RegressionInput = input.analysis_input

    # Validate columns exist
    missing_features = [c for c in inputs.features_col if c not in data.columns]
    if missing_features:
        raise ValueError(f"Feature columns not found in DataFrame: {missing_features}")
    if inputs.label_col not in data.columns:
        raise ValueError(f"Label column '{inputs.label_col}' not found in DataFrame")
    if len(data) < 20:
        import warnings
        warnings.warn(f"Only {len(data)} observations. Linear regression results may be unreliable for small samples.")

    X = data[inputs.features_col].values
    y = data[inputs.label_col].values

    # Split data into training and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42)

    # Initialize and train the regression model
    if inputs.regression_type == 'linear':
        result = perform_linear_regression(
            X_train, X_test, y_train, y_test, input)
    elif inputs.regression_type == 'decision_tree':
        result = perform_decision_tree_regression(
            X_train, X_test, y_train, y_test, input)
    elif inputs.regression_type == 'logistic':
        result = perform_logistic_regression(
            X_train, X_test, y_train, y_test, input)
    else:
        raise ValueError(
            f"Unsupported regression type: {inputs.regression_type}. Use 'linear', 'decision_tree', or 'logistic'.")

    report_obj = {}
    report_obj["visualizations"] = result.pop("visualizations", {})
    report_obj['project_id'] = input.project_id
    report_obj['summary'] = result
    report_obj['title'] = input.title
    report_obj['analysis_group'] = input.analysis_group

    # Create Visualization

    # Create a report
    report = await crud.create_report(report_obj, session=session)
    return report


def perform_linear_regression(X_train, X_test, y_train, y_test, input):
    """Phase 5H: switched from sklearn LinearRegression to statsmodels OLS
    to obtain full inferential statistics (p-values, CIs, F-test, AIC/BIC,
    residual normality).  sklearn gave point estimates only.
    """
    import statsmodels.api as sm
    from scipy.stats import shapiro as _shapiro
    from statsmodels.stats.outliers_influence import variance_inflation_factor
    from statsmodels.stats.stattools import durbin_watson
    from statsmodels.stats.diagnostic import het_breuschpagan

    X_train_c = sm.add_constant(X_train, has_constant='add')
    X_test_c  = sm.add_constant(X_test,  has_constant='add')
    ols_model = sm.OLS(y_train, X_train_c).fit()

    y_pred = ols_model.predict(X_test_c)

    # Residual normality p-value (Shapiro-Wilk on training residuals)
    resid = ols_model.resid
    _, resid_sw_p = _shapiro(resid[:min(len(resid), 5000)])

    feature_names = ['const'] + list(input.analysis_input.features_col)
    predictor_names = list(input.analysis_input.features_col)
    ci = np.asarray(ols_model.conf_int())  # normalise: ndarray when X is numpy, DataFrame when X is pandas

    # ── Standardised (beta) coefficients ──────────────────────────────────────
    X_std = StandardScaler().fit_transform(X_train)
    y_std = (y_train - y_train.mean()) / y_train.std()
    lr_std = LinearRegression().fit(X_std, y_std)
    beta_coefficients = dict(zip(predictor_names, lr_std.coef_.tolist()))

    # ── MAE ───────────────────────────────────────────────────────────────────
    mae = float(mean_absolute_error(y_test, y_pred))

    # ── VIF & Tolerance ───────────────────────────────────────────────────────
    X_df = pd.DataFrame(X_train, columns=predictor_names)
    X_with_const = sm.add_constant(X_df)
    vif_data = {}
    for i, col in enumerate(X_df.columns):
        vif_data[col] = float(variance_inflation_factor(X_with_const.values, i + 1))
    tolerance = {col: float(1.0 / v) if v != 0 else None for col, v in vif_data.items()}

    # ── Condition Index ───────────────────────────────────────────────────────
    eigenvalues = np.linalg.eigvalsh(X_with_const.values.T @ X_with_const.values)
    eigenvalues = np.maximum(eigenvalues, 0.0)  # guard against tiny negative floats
    condition_index = np.sqrt(eigenvalues.max() / np.where(eigenvalues > 0, eigenvalues, np.inf))
    max_condition_index = float(condition_index.max())

    # ── Residual diagnostics ──────────────────────────────────────────────────
    fitted_values = ols_model.fittedvalues
    residuals = ols_model.resid
    n, p = X_df.shape

    mse = float((residuals ** 2).sum() / (n - p - 1))
    std_residuals = (residuals / np.sqrt(mse)).tolist()

    influence = ols_model.get_influence()
    hat_values = influence.hat_matrix_diag
    leverage_threshold = 2 * (p + 1) / n
    high_leverage = [int(i) for i, h in enumerate(hat_values) if h > leverage_threshold]

    cooks_d = influence.cooks_distance[0]
    cooks_threshold = 4 / n
    influential_obs = [int(i) for i, d in enumerate(cooks_d) if d > cooks_threshold]

    studentized = influence.resid_studentized_external
    outlier_obs = [int(i) for i, r in enumerate(studentized) if abs(r) > 2.5]

    dffits = influence.dffits[0]
    dffits_threshold = 2 * np.sqrt((p + 1) / n)
    dffits_flagged = [int(i) for i, d in enumerate(dffits) if abs(d) > dffits_threshold]

    # ── PRESS statistic ───────────────────────────────────────────────────────
    press = float(np.sum((residuals / (1 - hat_values)) ** 2))

    # ── Durbin-Watson ─────────────────────────────────────────────────────────
    dw_stat = float(durbin_watson(residuals))
    if dw_stat < 1.5:
        dw_interpretation = "positive_autocorrelation"
    elif dw_stat > 2.5:
        dw_interpretation = "negative_autocorrelation"
    else:
        dw_interpretation = "no_autocorrelation"

    # ── Breusch-Pagan ─────────────────────────────────────────────────────────
    bp_lm, bp_p, bp_f, bp_fp = het_breuschpagan(residuals, ols_model.model.exog)
    breusch_pagan = {
        "lm_statistic": float(bp_lm),
        "p_value":      float(bp_p),
        "significant":  bool(bp_p < 0.05),
    }

    # ── Observations-per-predictor ────────────────────────────────────────────
    n_obs_per_pred = n / p if p > 0 else None

    # ── Assemble warnings list ────────────────────────────────────────────────
    warnings_list = []

    for col, v in vif_data.items():
        if v > 10:
            warnings_list.append({
                "level":   "error",
                "message": f"VIF for {col} = {v:.2f}. Serious multicollinearity — results are unreliable.",
                "code":    "CRITICAL_VIF",
            })
        elif v > 5:
            warnings_list.append({
                "level":   "warning",
                "message": f"VIF for {col} = {v:.2f}. Coefficients may be unstable.",
                "code":    "HIGH_VIF",
            })

    if max_condition_index > 30:
        warnings_list.append({
            "level":   "warning",
            "message": f"Condition index = {max_condition_index:.2f}. Near-collinearity detected.",
            "code":    "HIGH_CONDITION_INDEX",
        })

    if breusch_pagan["significant"]:
        warnings_list.append({
            "level":   "warning",
            "message": f"Breusch-Pagan p = {bp_p:.4f}. Heteroscedasticity detected — OLS standard errors may be invalid.",
            "code":    "HETEROSCEDASTICITY",
        })

    if n_obs_per_pred is not None:
        if n_obs_per_pred < 5:
            warnings_list.append({
                "level":   "error",
                "message": f"Only {n_obs_per_pred:.1f} observations per predictor. Model is likely overfit.",
                "code":    "CRITICAL_OVERFIT",
            })
        elif n_obs_per_pred < 10:
            warnings_list.append({
                "level":   "warning",
                "message": f"Only {n_obs_per_pred:.1f} observations per predictor. Results may not generalise.",
                "code":    "POTENTIAL_OVERFIT",
            })

    response_content = {
        "RMSE":           float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "MAE":            mae,
        "R2":             float(r2_score(y_test, y_pred)),
        "r_squared":      float(ols_model.rsquared),
        "adj_r_squared":  float(ols_model.rsquared_adj),
        "f_statistic":    float(ols_model.fvalue),
        "f_pvalue":       float(ols_model.f_pvalue),
        "n_observations": int(ols_model.nobs),
        "aic":            float(ols_model.aic),
        "bic":            float(ols_model.bic),
        "coefficients":   dict(zip(feature_names, ols_model.params.tolist())),
        "beta_coefficients": beta_coefficients,
        "std_errors":     dict(zip(feature_names, ols_model.bse.tolist())),
        "t_statistics":   dict(zip(feature_names, ols_model.tvalues.tolist())),
        "p_values":       dict(zip(feature_names, ols_model.pvalues.tolist())),
        "conf_intervals_95": {
            feat: [float(ci[i, 0]), float(ci[i, 1])]
            for i, feat in enumerate(feature_names)
        },
        "residuals_normality_sw_p": float(resid_sw_p),
        "vif":            vif_data,
        "tolerance":      tolerance,
        "condition_index_max": max_condition_index,
        "press":          press,
        "durbin_watson": {
            "statistic":      dw_stat,
            "interpretation": dw_interpretation,
        },
        "breusch_pagan":  breusch_pagan,
        "n_obs_per_predictor": float(n_obs_per_pred) if n_obs_per_pred is not None else None,
        "residual_diagnostics": {
            "std_residuals":   std_residuals,
            "high_leverage":   high_leverage,
            "influential_obs": influential_obs,
            "outlier_obs":     outlier_obs,
            "dffits_flagged":  dffits_flagged,
        },
        "warnings": warnings_list,
    }

    if input.generate_visualizations:
        response_content["visualizations"] = linear_regression_plot(
            X_test, y_test, y_pred, input.analysis_input.features_col)
    else:
        response_content["visualizations"] = {}
    return response_content


def perform_decision_tree_regression(X_train, X_test, y_train, y_test, input):
    """Phase 5I: added cost-complexity pruning + 5-fold cross-validation to
    prevent overfitting. Unpruned Decision Trees memorise training data;
    selecting the best ccp_alpha via CV chooses the simplest tree whose
    performance does not deteriorate.
    """
    from sklearn.model_selection import cross_val_score

    # Cost-complexity pruning path
    dt_full = DecisionTreeRegressor(random_state=42)
    path = dt_full.cost_complexity_pruning_path(X_train, y_train)
    # Clamp alphas to [0, inf) — floating-point arithmetic can produce tiny negatives
    raw_alphas = [max(0.0, float(a)) for a in path.ccp_alphas[:-1]]
    # Cap at 20 evenly-spaced candidates to bound CV computation time
    if len(raw_alphas) > 20:
        idx = np.linspace(0, len(raw_alphas) - 1, 20, dtype=int)
        alphas = [raw_alphas[i] for i in idx]
    else:
        alphas = raw_alphas

    if len(alphas) > 0:
        # Select alpha that maximises CV R² on training data
        cv_scores = [
            cross_val_score(
                DecisionTreeRegressor(ccp_alpha=a, random_state=42),
                X_train, y_train, cv=min(5, len(y_train)), scoring='r2'
            ).mean()
            for a in alphas
        ]
        best_alpha = float(alphas[np.argmax(cv_scores)])
    else:
        best_alpha = 0.0

    model = DecisionTreeRegressor(ccp_alpha=best_alpha, random_state=42)
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    final_cv = cross_val_score(model, X_train, y_train, cv=min(5, len(y_train)), scoring='r2')

    response_content = {
        "RMSE":              float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "R2":                float(r2_score(y_test, y_pred)),
        "tree_depth":        int(model.get_depth()),
        "num_leaves":        int(model.get_n_leaves()),
        "ccp_alpha":         float(best_alpha),
        "cv_r2_mean":        float(final_cv.mean()),
        "cv_r2_std":         float(final_cv.std()),
        "Feature Importances": model.feature_importances_.tolist(),
    }
    if input.generate_visualizations:
        feature_names = input.analysis_input.features_col
        response_content["visualizations"] = decision_tree_plot(
            X_test, y_test, y_pred, feature_names)
    else:
        response_content["visualizations"] = {}
    return response_content


def perform_logistic_regression(X_train, X_test, y_train, y_test, input):
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)

    response_content = {
        "Coefficients": model.coef_.tolist(),
        "Intercept": model.intercept_.tolist(),
        "Score": float(model.score(X_test_scaled, y_test))
    }
    return response_content
