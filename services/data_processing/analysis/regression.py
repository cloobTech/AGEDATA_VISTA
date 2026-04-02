from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
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

    X_train_c = sm.add_constant(X_train, has_constant='add')
    X_test_c  = sm.add_constant(X_test,  has_constant='add')
    ols_model = sm.OLS(y_train, X_train_c).fit()

    y_pred = ols_model.predict(X_test_c)

    # Residual normality p-value (Shapiro-Wilk on training residuals)
    resid = ols_model.resid
    _, resid_sw_p = _shapiro(resid[:min(len(resid), 5000)])

    feature_names = ['const'] + list(input.analysis_input.features_col)

    response_content = {
        "RMSE":           float(np.sqrt(mean_squared_error(y_test, y_pred))),
        "R2":             float(r2_score(y_test, y_pred)),
        "r_squared":      float(ols_model.rsquared),
        "adj_r_squared":  float(ols_model.rsquared_adj),
        "f_statistic":    float(ols_model.fvalue),
        "f_pvalue":       float(ols_model.f_pvalue),
        "n_observations": int(ols_model.nobs),
        "aic":            float(ols_model.aic),
        "bic":            float(ols_model.bic),
        "coefficients":   dict(zip(feature_names, ols_model.params.tolist())),
        "std_errors":     dict(zip(feature_names, ols_model.bse.tolist())),
        "t_statistics":   dict(zip(feature_names, ols_model.tvalues.tolist())),
        "p_values":       dict(zip(feature_names, ols_model.pvalues.tolist())),
        "conf_intervals_95": {
            feat: [float(ols_model.conf_int().loc[feat, 0]),
                   float(ols_model.conf_int().loc[feat, 1])]
            for feat in ols_model.conf_int().index
        },
        "residuals_normality_sw_p": float(resid_sw_p),
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
    alphas = path.ccp_alphas[:-1]  # drop the last alpha (trivial root)

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
