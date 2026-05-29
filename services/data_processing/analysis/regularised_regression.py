import numpy as np
import pandas as pd
from sklearn.linear_model import RidgeCV, LassoCV, ElasticNetCV, Ridge, Lasso, ElasticNet
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
import warnings as py_warnings


def run_regularised_regression(df, analysis_input):
    try:
        # Extract params (handle both dict and object)
        if hasattr(analysis_input, 'analysis_input'):
            inp = analysis_input.analysis_input
        else:
            inp = analysis_input

        outcome_col = inp.get("outcome_col")
        feature_cols = inp.get("feature_cols", [])
        model_type = inp.get("model_type", "lasso")
        l1_ratio = inp.get("l1_ratio", 0.5)
        cv_folds = inp.get("cv_folds", 5)

        data = df[[outcome_col] + feature_cols].dropna()
        y = data[outcome_col].values
        X_raw = data[feature_cols].values

        # Always standardise (required for regularised regression)
        scaler = StandardScaler()
        X = scaler.fit_transform(X_raw)

        # Lambda/alpha values to search
        alphas = np.logspace(-4, 4, 100)

        # Fit with cross-validation
        cv = KFold(n_splits=cv_folds, shuffle=True, random_state=42)

        if model_type == "ridge":
            model_cv = RidgeCV(alphas=alphas, cv=cv)
            model_cv.fit(X, y)
            optimal_alpha = model_cv.alpha_
            final_model = Ridge(alpha=optimal_alpha)
        elif model_type == "lasso":
            model_cv = LassoCV(alphas=alphas, cv=cv, max_iter=10000, random_state=42)
            model_cv.fit(X, y)
            optimal_alpha = model_cv.alpha_
            final_model = Lasso(alpha=optimal_alpha, max_iter=10000)
        else:  # elastic_net
            model_cv = ElasticNetCV(alphas=alphas, l1_ratio=l1_ratio, cv=cv, max_iter=10000, random_state=42)
            model_cv.fit(X, y)
            optimal_alpha = model_cv.alpha_
            final_model = ElasticNet(alpha=optimal_alpha, l1_ratio=l1_ratio, max_iter=10000)

        final_model.fit(X, y)

        # Coefficients
        coef_table = []
        for name, coef in zip(feature_cols, final_model.coef_):
            coef_table.append({
                "predictor": name,
                "coefficient": round(float(coef), 6),
                "selected": bool(abs(coef) > 1e-6),  # Non-zero (Lasso selection)
            })

        # Selected variables (Lasso)
        selected_variables = [c["predictor"] for c in coef_table if c["selected"]]

        # Cross-validated performance (honest estimate)
        cv_r2_scores = cross_val_score(final_model, X, y, cv=cv, scoring='r2')
        cv_r2_mean = float(np.mean(cv_r2_scores))
        cv_r2_std = float(np.std(cv_r2_scores))

        # Training performance
        y_pred = final_model.predict(X)
        train_r2 = float(r2_score(y, y_pred))
        train_rmse = float(np.sqrt(mean_squared_error(y, y_pred)))
        train_mae = float(mean_absolute_error(y, y_pred))

        # CV plot data (error vs lambda)
        cv_plot_data = []
        if model_type in ["lasso", "elastic_net"] and hasattr(model_cv, 'alphas_'):
            alphas_used = model_cv.alphas_
            mse_path = model_cv.mse_path_.mean(axis=1)
            for a, mse in zip(alphas_used, mse_path):
                cv_plot_data.append({"log_lambda": round(float(np.log10(a)), 4), "cv_mse": round(float(mse), 4)})

        # Coefficient trace plot data (top 20 alphas for readability)
        trace_plot_data = {"alphas": [], "feature_names": feature_cols, "coefficients": []}
        trace_alphas = np.logspace(-4, 2, 30)
        trace_coefs = []
        for a in trace_alphas:
            if model_type == "ridge":
                m = Ridge(alpha=a).fit(X, y)
            elif model_type == "lasso":
                m = Lasso(alpha=a, max_iter=10000).fit(X, y)
            else:
                m = ElasticNet(alpha=a, l1_ratio=l1_ratio, max_iter=10000).fit(X, y)
            trace_coefs.append(m.coef_.tolist())
        trace_plot_data["alphas"] = np.log10(trace_alphas).round(2).tolist()
        trace_plot_data["coefficients"] = trace_coefs

        warnings_list = [
            {"level": "info", "message": "All predictors were standardised before fitting. Coefficients are in standardised units.", "code": "STANDARDISED"},
            {"level": "info", "message": "P-values are not reported for regularised regression — coefficients are intentionally shrunk toward zero.", "code": "NO_PVALUES"},
        ]

        overfitting_gap = train_r2 - cv_r2_mean
        if overfitting_gap > 0.1:
            warnings_list.append({"level": "warning", "message": f"Training R² ({train_r2:.3f}) is substantially higher than cross-validated R² ({cv_r2_mean:.3f}). Possible overfitting.", "code": "OVERFIT_GAP"})

        return {
            "model_type": model_type,
            "n": int(len(data)),
            "n_predictors": len(feature_cols),
            "n_selected": len(selected_variables),
            "optimal_lambda": round(float(optimal_alpha), 6),
            "log10_optimal_lambda": round(float(np.log10(optimal_alpha)), 4),
            "l1_ratio": l1_ratio if model_type == "elastic_net" else None,
            "cv_folds": cv_folds,
            "coefficient_table": coef_table,
            "selected_variables": selected_variables,
            "intercept": round(float(final_model.intercept_), 6),
            "train_r2": round(train_r2, 4),
            "train_rmse": round(train_rmse, 4),
            "train_mae": round(train_mae, 4),
            "cv_r2_mean": round(cv_r2_mean, 4),
            "cv_r2_std": round(cv_r2_std, 4),
            "cv_plot_data": cv_plot_data,
            "trace_plot_data": trace_plot_data,
            "standardisation_note": "All predictors were automatically standardised (mean=0, std=1) before fitting. This is required for regularised regression.",
            "warnings": warnings_list,
            "interpretation": {
                "main_finding": f"{model_type.replace('_', ' ').title()} regression selected {len(selected_variables)} of {len(feature_cols)} predictors at optimal λ = {optimal_alpha:.4f}. Cross-validated R² = {cv_r2_mean:.3f}.",
                "honest_performance": f"The honest performance estimate (cross-validated R²) is {cv_r2_mean:.3f} ± {cv_r2_std:.3f}.",
                "key_caveat": "Coefficients are shrunk and cannot be interpreted as ordinary regression coefficients. Do not report p-values.",
            },
        }

    except Exception as e:
        return {
            "error": True,
            "message": str(e),
            "model_type": analysis_input.get("model_type") if isinstance(analysis_input, dict) else getattr(analysis_input, "model_type", None),
        }
