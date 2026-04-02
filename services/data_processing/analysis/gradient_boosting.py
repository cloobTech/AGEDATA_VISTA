import logging
import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import AnalysisInput
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, classification_report, confusion_matrix,
    mean_squared_error, r2_score,
)
from services.data_processing.visualization.gradient_boosting_plot import (
    generate_gb_classification_plots,
    generate_gb_regression_plots,
    generate_feature_importance
)
from services.data_processing.analysis.train_gradient_boosting import train_gradient_boosting
from services.data_processing.report import crud
from services.data_processing.model_store.model_store import save_sklearn_model

from sklearn.preprocessing import LabelEncoder

_log = logging.getLogger(__name__)


async def perform_gradient_boosting_analysis(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input

    try:
        X = data[input.feature_cols]
        y = data[input.target_col]

        # Encode string labels to numerical values
        if input.task_type == "classification" and y.dtype == object:
            le = LabelEncoder()
            y = le.fit_transform(y)
            class_names = le.classes_.tolist()
        else:
            class_names = None

        # Train model
        results = train_gradient_boosting(
            X, y,
            model_type=input.model_type,
            config=input.config,
            test_size=input.test_size,
            task_type=input.task_type
        )

        # Phase 5P + 5R: F1, AUC, classification report, baseline comparison
        metrics = {}
        if input.task_type == "classification":
            y_t, y_p = results["y_test"], results["y_pred"]
            y_proba = results.get("y_proba")

            # AUC-ROC — binary vs multiclass
            try:
                if y_proba is not None:
                    n_cls = y_proba.shape[1] if hasattr(y_proba, 'shape') and y_proba.ndim > 1 else 2
                    if n_cls == 2:
                        _proba_pos = y_proba[:, 1] if hasattr(y_proba, 'ndim') and y_proba.ndim > 1 else y_proba
                        auc = float(roc_auc_score(y_t, _proba_pos))
                        auc_note = "Binary AUC-ROC"
                    else:
                        auc = float(roc_auc_score(y_t, y_proba, multi_class='ovr', average='macro'))
                        auc_note = "Macro OvR AUC (multiclass)"
                else:
                    auc, auc_note = None, "AUC unavailable"
            except Exception:
                auc, auc_note = None, "AUC computation failed"

            metrics = {
                "accuracy":           float(accuracy_score(y_t, y_p)),
                "precision_macro":    float(precision_score(y_t, y_p, average='macro',    zero_division=0)),
                "precision_weighted": float(precision_score(y_t, y_p, average='weighted', zero_division=0)),
                "recall_macro":       float(recall_score(y_t, y_p,    average='macro',    zero_division=0)),
                "recall_weighted":    float(recall_score(y_t, y_p,    average='weighted', zero_division=0)),
                "f1_macro":           float(f1_score(y_t, y_p,        average='macro',    zero_division=0)),
                "f1_weighted":        float(f1_score(y_t, y_p,        average='weighted', zero_division=0)),
                "classification_report": classification_report(y_t, y_p, output_dict=True, zero_division=0),
                "confusion_matrix":   confusion_matrix(y_t, y_p).tolist(),
            }
            if auc is not None:
                metrics["roc_auc"] = auc
                metrics["roc_auc_note"] = auc_note

            from sklearn.dummy import DummyClassifier
            dummy = DummyClassifier(strategy="most_frequent")
            dummy.fit(results["X_train"], results["y_train"])
            baseline_acc = float(dummy.score(results["X_test"], y_t))
            metrics["baseline"] = {
                "strategy": "majority class",
                "accuracy": baseline_acc,
                "note": f"Model ({metrics['accuracy']:.3f}) vs majority-class baseline ({baseline_acc:.3f})",
            }
        else:
            metrics = {
                "mse":  float(mean_squared_error(results["y_test"], results["y_pred"])),
                "rmse": float(np.sqrt(mean_squared_error(results["y_test"], results["y_pred"]))),
                "r2":   float(r2_score(results["y_test"], results["y_pred"])),
            }
            from sklearn.dummy import DummyRegressor
            dummy = DummyRegressor(strategy="mean")
            dummy.fit(results["X_train"], results["y_train"])
            metrics["baseline"] = {
                "strategy": "mean prediction",
                "r2": float(dummy.score(results["X_test"], results["y_test"])),
            }

        # Generate visualizations (always — frontend always wants them)
        visualizations = {}
        if input.task_type == "classification":
            visualizations.update(generate_gb_classification_plots(
                results["y_test"],
                results["y_pred"],
                results.get("y_proba"),
                class_names=class_names
            ))
        else:
            visualizations.update(generate_gb_regression_plots(
                results["y_test"], results["y_pred"]
            ))

        visualizations.update(generate_feature_importance(
            results["model"], input.feature_cols
        ))

        # Save model bundle non-blocking
        model_storage_path = None
        try:
            storage_id = f"gb_{inputs.project_id}_{uuid.uuid4().hex[:8]}"
            bundle = {
                "model": results["model"],
                "scaler": results.get("scaler"),
                "feature_cols": list(input.feature_cols),
                "task_type": input.task_type,
            }
            model_storage_path = save_sklearn_model(bundle, storage_id)
        except Exception as exc:
            _log.warning("GB model save failed (non-fatal): %s", exc)

        # Create report
        report_obj = {
            "visualizations": visualizations,
            "summary": {
                "metrics": metrics,
                "analysis_type": "gradient_boosting",
                "model_type": input.model_type,
                "feature_cols": list(input.feature_cols),
                "model_storage_path": model_storage_path,
                "feature_importance": dict(zip(
                    input.feature_cols,
                    results["model"].feature_importances_.tolist()
                )),
                "class_names": class_names
            },
            "project_id": inputs.project_id,
            "title": inputs.title,
            "analysis_group": inputs.analysis_group
        }

        report = await crud.create_report(report_obj, session=session)
        return report

    except Exception as e:
        raise ValueError(f"Gradient boosting analysis failed: {str(e)}")
