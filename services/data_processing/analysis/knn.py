import logging
import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import AnalysisInput
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report,
    confusion_matrix,
    mean_squared_error,
    r2_score,
)
import pandas as pd
import numpy as np
from services.data_processing.analysis.train_knn import train_knn
from services.data_processing.visualization.knn_plot import (
    generate_knn_confusion_matrix,
    generate_knn_decision_boundary,
    generate_knn_metrics_plot,
    generate_knn_elbow_curve
)
from services.data_processing.report import crud
from services.data_processing.model_store.model_store import save_sklearn_model

_log = logging.getLogger(__name__)


async def perform_knn_analysis(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input

    try:
        # Prepare data
        X = data[input.feature_cols]
        y = data[input.target_col]

        # Train model
        results = train_knn(
            X, y,
            config=input.config,
            test_size=input.test_size,
            task_type=input.task_type
        )

        # Phase 5P + 5R: F1, AUC, classification report, and baseline
        if input.task_type == "classification":
            y_t, y_p = results["y_test"], results["y_pred"]
            try:
                y_proba = results["model"].predict_proba(results["X_test"])
                n_cls = y_proba.shape[1]
                if n_cls == 2:
                    auc = float(roc_auc_score(y_t, y_proba[:, 1]))
                    auc_note = "Binary AUC-ROC"
                else:
                    auc = float(roc_auc_score(y_t, y_proba, multi_class='ovr', average='macro'))
                    auc_note = "Macro OvR AUC (multiclass)"
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

        # Phase 7A: save model bundle non-blocking
        model_storage_path = None
        try:
            storage_id = f"knn_{inputs.project_id}_{uuid.uuid4().hex[:8]}"
            bundle = {
                "model":        results["model"],
                "scaler":       results.get("scaler"),
                "feature_cols": list(input.feature_cols),
                "task_type":    input.task_type,
            }
            model_storage_path = save_sklearn_model(bundle, storage_id)
        except Exception as exc:
            _log.warning("KNN model save failed (non-fatal): %s", exc)

        # Generate visualizations (always — frontend always wants them)
        visualizations = {}
        if input.task_type == "classification":
            visualizations.update(generate_knn_confusion_matrix(
                results["y_test"], results["y_pred"]))

            if len(input.feature_cols) == 2:
                visualizations.update(generate_knn_decision_boundary(
                    results["model"], results["X_test"], results["y_test"], input.feature_cols))

            visualizations.update(generate_knn_elbow_curve(
                results["X_train"], results["y_train"]))

        visualizations.update(generate_knn_metrics_plot(metrics))

        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {
                "metrics": metrics,
                "analysis_type": "knn",
                "model_storage_path": model_storage_path,
                "model_params": {
                    "n_neighbors": input.config.n_neighbors,
                    "algorithm": input.config.algorithm.value,
                    "weights": input.config.weights.value,
                    "effective_metric": results["model"].effective_metric_
                }
            },
            'title': getattr(inputs, 'title', "KNN Analysis Report"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"KNN analysis failed: {str(e)}")
