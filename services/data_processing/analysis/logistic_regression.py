from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report, roc_auc_score, confusion_matrix, roc_curve,
    auc, precision_recall_curve, average_precision_score,
)
from sklearn.model_selection import train_test_split
from sklearn.utils import resample
import pandas as pd
import numpy as np
import statsmodels.api as sm
from scipy.stats import chi2
from services.data_processing.visualization.logistic_plot import generate_logistic_regression_plot
from services.data_processing.report import crud
from schemas.data_processing import AnalysisInput


async def perform_logistic_regression(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input

    try:
        X = data[input.feature_cols]
        y = data[input.target_col]

        # Validate target classes
        if y.nunique() < 2:
            raise ValueError(
                f"Target column must have at least 2 unique classes, "
                f"found only {y.nunique()}: {y.unique().tolist()}"
            )

        # Check if multi-class classification
        if len(y.unique()) > 2:
            # For multi-class problems, some solvers require specific settings
            if input.solver in ['liblinear']:
                raise ValueError(
                    "liblinear solver doesn't support multinomial loss")
            if input.penalty == 'none' and input.solver in ['lbfgs', 'newton-cg']:
                raise ValueError(
                    f"Solver {input.solver} doesn't support penalty='none'")

        # Use stratify only when all classes have >= 2 samples
        _class_counts = y.value_counts()
        _stratify = y if (_class_counts >= 2).all() else None
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=input.test_size, random_state=42, stratify=_stratify
        )

        model = LogisticRegression(
            penalty=input.penalty if input.penalty != 'none' else None,
            solver=input.solver,
            max_iter=input.max_iter,
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)
        y_proba_all = model.predict_proba(X_test)

        # Phase 5J: compute AUC-ROC for both binary and multiclass
        if len(model.classes_) == 2:
            y_proba = y_proba_all[:, 1]
            roc_auc = float(roc_auc_score(y_test, y_proba))
            roc_auc_note = "Binary AUC-ROC"
        else:
            y_proba = y_proba_all
            try:
                roc_auc = float(roc_auc_score(
                    y_test, y_proba, multi_class='ovr', average='macro'
                ))
                roc_auc_note = "Macro-averaged One-vs-Rest AUC for multiclass"
            except Exception:
                roc_auc = None
                roc_auc_note = "AUC not computable (check class representation in test set)"

        metrics = {
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist(),
        }

        if roc_auc is not None:
            metrics["roc_auc_score"] = roc_auc
            metrics["roc_auc_note"] = roc_auc_note

        visualizations = {}
        if inputs.generate_visualizations:
            visualizations = generate_logistic_regression_plot(
                y_test,
                y_pred,
                y_proba_all,
                len(model.classes_)
            )

        # ------------------------------------------------------------------ #
        # AGEARC 3.6c — full inference block (binary only)                    #
        # ------------------------------------------------------------------ #
        inference = {}
        warnings_list = []

        if len(model.classes_) == 2:
            X_df = pd.DataFrame(X, columns=input.feature_cols)
            y_series = pd.Series(y.values if hasattr(y, 'values') else y, name=input.target_col)

            X_sm = sm.add_constant(X_df, has_constant='add')
            logit_model = sm.Logit(y_series, X_sm)
            sm_result = logit_model.fit(disp=False, maxiter=200)

            # --- coefficient table with odds ratios ---
            coef_table = []
            for name, coef, se, z, p in zip(
                sm_result.params.index,
                sm_result.params,
                sm_result.bse,
                sm_result.tvalues,
                sm_result.pvalues,
            ):
                or_val = float(np.exp(coef))
                or_ci_lower = float(np.exp(coef - 1.96 * se))
                or_ci_upper = float(np.exp(coef + 1.96 * se))
                coef_table.append({
                    "predictor": name,
                    "log_odds": round(float(coef), 4),
                    "std_error": round(float(se), 4),
                    "wald_statistic": round(float(z ** 2), 4),
                    "z_value": round(float(z), 4),
                    "p_value": round(float(p), 4),
                    "odds_ratio": round(or_val, 4),
                    "or_ci_lower": round(or_ci_lower, 4),
                    "or_ci_upper": round(or_ci_upper, 4),
                })

            # --- model fit metrics ---
            log_likelihood = float(sm_result.llf)
            null_log_likelihood = float(sm_result.llnull)
            minus_2ll = round(-2 * log_likelihood, 4)
            aic = round(float(sm_result.aic), 4)
            bic = round(float(sm_result.bic), 4)

            lr_stat = -2 * (null_log_likelihood - log_likelihood)
            lr_df = len(sm_result.params) - 1
            lr_p_value = float(chi2.sf(lr_stat, lr_df))

            n = len(y_series)
            mcfadden_r2 = float(1 - (log_likelihood / null_log_likelihood))
            cox_snell_r2 = float(1 - np.exp(-lr_stat / n))
            nagelkerke_r2 = cox_snell_r2 / float(1 - np.exp(2 * null_log_likelihood / n))

            model_fit = {
                "minus_2_log_likelihood": minus_2ll,
                "aic": aic,
                "bic": bic,
                "log_likelihood": round(log_likelihood, 4),
                "null_log_likelihood": round(null_log_likelihood, 4),
                "likelihood_ratio_test": {
                    "statistic": round(lr_stat, 4),
                    "df": lr_df,
                    "p_value": round(lr_p_value, 4),
                    "significant": lr_p_value < 0.05,
                },
                "pseudo_r_squared": {
                    "mcfadden": round(mcfadden_r2, 4),
                    "cox_snell": round(cox_snell_r2, 4),
                    "nagelkerke": round(nagelkerke_r2, 4),
                    "note": (
                        "Pseudo-R² values are approximations and not directly "
                        "comparable to linear regression R²."
                    ),
                },
            }

            # --- Hosmer-Lemeshow test ---
            probs = sm_result.predict(X_sm)
            try:
                deciles = pd.qcut(probs, q=10, duplicates='drop')
                hl_table = []
                hl_chi2 = 0.0
                for group in sorted(deciles.unique()):
                    mask = deciles == group
                    n_g = int(mask.sum())
                    obs_events = float(y_series[mask].sum())
                    exp_events = float(probs[mask].sum())
                    obs_nonevents = n_g - obs_events
                    exp_nonevents = n_g - exp_events
                    if exp_events > 0 and exp_nonevents > 0:
                        hl_chi2 += (obs_events - exp_events) ** 2 / exp_events
                        hl_chi2 += (obs_nonevents - exp_nonevents) ** 2 / exp_nonevents
                    hl_table.append({
                        "n": n_g,
                        "observed_events": int(obs_events),
                        "expected_events": round(exp_events, 2),
                    })
                hl_df = len(hl_table) - 2
                hl_p = float(chi2.sf(hl_chi2, hl_df))
                hosmer_lemeshow = {
                    "chi2": round(hl_chi2, 4),
                    "df": hl_df,
                    "p_value": round(hl_p, 4),
                    "table": hl_table,
                    "model_well_calibrated": hl_p > 0.05,
                }
            except Exception:
                hosmer_lemeshow = {"error": "Could not compute Hosmer-Lemeshow test"}

            # --- classification table at 0.5 threshold ---
            y_pred_full = (probs >= 0.5).astype(int)
            tn, fp, fn, tp = confusion_matrix(y_series, y_pred_full).ravel()
            sensitivity = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
            specificity = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0
            precision_val = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
            accuracy = float((tp + tn) / n)
            f1 = (
                2 * precision_val * sensitivity / (precision_val + sensitivity)
                if (precision_val + sensitivity) > 0 else 0.0
            )
            balanced_accuracy = (sensitivity + specificity) / 2

            classification_table = {
                "threshold": 0.5,
                "true_positives": int(tp),
                "true_negatives": int(tn),
                "false_positives": int(fp),
                "false_negatives": int(fn),
                "accuracy": round(accuracy, 4),
                "sensitivity": round(sensitivity, 4),
                "specificity": round(specificity, 4),
                "precision": round(precision_val, 4),
                "f1_score": round(f1, 4),
                "balanced_accuracy": round(balanced_accuracy, 4),
            }

            # --- ROC curve + AUC CI + optimal threshold ---
            fpr_vals, tpr_vals, thresholds_vals = roc_curve(y_series, probs)
            roc_auc_full = float(auc(fpr_vals, tpr_vals))

            auc_scores = []
            y_arr = y_series.values
            p_arr = probs.values
            for _ in range(1000):
                y_boot, p_boot = resample(y_arr, p_arr)
                try:
                    auc_scores.append(float(roc_auc_score(y_boot, p_boot)))
                except Exception:
                    pass
            auc_ci_lower = round(float(np.percentile(auc_scores, 2.5)), 4) if auc_scores else None
            auc_ci_upper = round(float(np.percentile(auc_scores, 97.5)), 4) if auc_scores else None

            youden = tpr_vals - fpr_vals
            optimal_idx = int(np.argmax(youden))
            optimal_threshold = round(float(thresholds_vals[optimal_idx]), 4)
            optimal_sensitivity = round(float(tpr_vals[optimal_idx]), 4)
            optimal_specificity = round(float(1 - fpr_vals[optimal_idx]), 4)

            roc_data = {
                "auc": round(roc_auc_full, 4),
                "auc_ci_lower": auc_ci_lower,
                "auc_ci_upper": auc_ci_upper,
                "fpr": [round(float(v), 4) for v in fpr_vals],
                "tpr": [round(float(v), 4) for v in tpr_vals],
                "optimal_threshold": optimal_threshold,
                "optimal_sensitivity": optimal_sensitivity,
                "optimal_specificity": optimal_specificity,
            }

            # --- Precision-Recall curve ---
            prec_vals, rec_vals, _ = precision_recall_curve(y_series, probs)
            pr_auc = round(float(average_precision_score(y_series, probs)), 4)
            pr_curve = {
                "auc": pr_auc,
                "precision": [round(float(v), 4) for v in prec_vals],
                "recall": [round(float(v), 4) for v in rec_vals],
            }

            # --- class imbalance check ---
            minority_pct = float(min(y_series.mean(), 1 - y_series.mean()) * 100)
            class_imbalanced = minority_pct < 20.0
            if class_imbalanced:
                warnings_list.append({
                    "level": "warning",
                    "message": (
                        f"Class imbalance detected — minority class is "
                        f"{minority_pct:.1f}%. Accuracy is misleading. "
                        "Use AUC, F1, and Balanced Accuracy instead."
                    ),
                    "code": "CLASS_IMBALANCE",
                })

            # --- complete separation check ---
            if float(sm_result.bse.max()) > 100:
                warnings_list.append({
                    "level": "warning",
                    "message": (
                        "Possible complete or quasi-complete separation detected. "
                        "Coefficient estimates may be unreliable. Consider "
                        "Firth's penalised logistic regression."
                    ),
                    "code": "COMPLETE_SEPARATION",
                })

            # --- calibration plot data ---
            prob_bins = np.linspace(0, 1, 11)
            calibration_data = []
            for i in range(len(prob_bins) - 1):
                mask = (probs >= prob_bins[i]) & (probs < prob_bins[i + 1])
                if int(mask.sum()) > 0:
                    calibration_data.append({
                        "predicted_mean": round(float(probs[mask].mean()), 4),
                        "observed_proportion": round(float(y_series[mask].mean()), 4),
                        "n": int(mask.sum()),
                    })

            # --- interpretation ---
            primary_metrics = (
                ["auc", "f1_score", "balanced_accuracy"]
                if class_imbalanced
                else ["accuracy", "auc", "sensitivity", "specificity"]
            )
            interpretation = {
                "primary_metrics": primary_metrics,
                "class_imbalanced": class_imbalanced,
                "minority_class_pct": round(minority_pct, 2),
                "model_significant": lr_p_value < 0.05,
                "well_calibrated": hosmer_lemeshow.get("model_well_calibrated"),
                "note": (
                    "Odds ratios are not the same as relative risk. "
                    "When the outcome is common (above 10%), the odds ratio "
                    "overstates the relative risk."
                ),
            }

            inference = {
                "coefficient_table": coef_table,
                "model_fit": model_fit,
                "hosmer_lemeshow": hosmer_lemeshow,
                "classification_table": classification_table,
                "roc_curve": roc_data,
                "precision_recall_curve": pr_curve,
                "calibration_data": calibration_data,
                "interpretation": interpretation,
            }

        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {
                "model": "Logistic Regression",
                "metrics": metrics,
                "coefficients": dict(zip(input.feature_cols, model.coef_[0].tolist()))
                if len(model.classes_) == 2
                else {cls: dict(zip(input.feature_cols, coef.tolist()))
                      for cls, coef in zip(model.classes_, model.coef_)},
                **({"inference": inference} if inference else {}),
                **({"warnings": warnings_list} if warnings_list else {}),
            },
            'title': getattr(inputs, 'title', "Logistic Regression"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"Logistic Regression failed: {str(e)}")
