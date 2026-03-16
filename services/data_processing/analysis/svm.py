import logging
import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import AnalysisInput
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    mean_squared_error,
    r2_score
)
import pandas as pd
import numpy as np
from services.data_processing.report import crud
from services.data_processing.analysis.train_svm import train_svm
from services.data_processing.visualization.svm import (
    generate_svm_confusion_matrix,
    generate_svm_decision_boundary,
    generate_svm_metrics_plot
)
from services.data_processing.model_store.model_store import save_sklearn_model

_log = logging.getLogger(__name__)


async def perform_svm_analysis(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input
    try:
        # Prepare data
        X = data[input.feature_cols]
        y = data[input.target_col]

        # Train model (train_svm also applies prepare_X + StandardScaler internally)
        results = train_svm(
            X, y,
            config=input.config,
            test_size=input.test_size,
            task_type=input.task_type
        )

        # Calculate metrics
        if input.task_type == "classification":
            metrics = {
                "accuracy": accuracy_score(results["y_test"], results["y_pred"]),
                "precision_micro": precision_score(results["y_test"], results["y_pred"], average='micro'),
                "precision_macro": precision_score(results["y_test"], results["y_pred"], average='macro'),
                "precision_weighted": precision_score(results["y_test"], results["y_pred"], average='weighted'),
                "recall_micro": recall_score(results["y_test"], results["y_pred"], average='micro'),
                "recall_macro": recall_score(results["y_test"], results["y_pred"], average='macro'),
                "recall_weighted": recall_score(results["y_test"], results["y_pred"], average='weighted')
            }
        else:
            metrics = {
                "mse": mean_squared_error(results["y_test"], results["y_pred"]),
                "rmse": float(np.sqrt(mean_squared_error(results["y_test"], results["y_pred"]))),
                "r2": r2_score(results["y_test"], results["y_pred"])
            }

        # Generate visualizations (always — frontend always wants them)
        visualizations = {}
        if input.task_type == "classification":
            visualizations.update(generate_svm_confusion_matrix(
                results["y_test"], results["y_pred"]))

            if len(input.feature_cols) == 2:
                visualizations.update(generate_svm_decision_boundary(
                    results["model"], results["X_test"], results["y_test"]))

        visualizations.update(generate_svm_metrics_plot(metrics))

        # Save sklearn model bundle non-blocking
        model_storage_path = None
        try:
            storage_id = f"svm_{inputs.project_id}_{uuid.uuid4().hex[:8]}"
            bundle = {
                "model": results["model"],
                "scaler": results.get("scaler"),
                "feature_cols": list(input.feature_cols),
                "task_type": input.task_type,
            }
            model_storage_path = save_sklearn_model(bundle, storage_id)
        except Exception as exc:
            _log.warning("SVM model save failed (non-fatal): %s", exc)

        # Support vectors: store only first 20 + total count to avoid oversized JSON
        sv_model = results["model"]
        if hasattr(sv_model, "support_vectors_"):
            n_support_vectors = int(len(sv_model.support_vectors_))
            support_vectors_sample = sv_model.support_vectors_[:20].tolist()
            n_support = sv_model.n_support_.tolist() if input.task_type == "classification" else None
        else:
            n_support_vectors = 0
            support_vectors_sample = None
            n_support = None

        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {
                "metrics": metrics,
                "analysis_type": "svm",
                "feature_cols": list(input.feature_cols),
                "model_storage_path": model_storage_path,
                "model_params": {
                    "kernel": input.config.kernel.value,
                    "n_support_vectors": n_support_vectors,
                    "support_vectors_sample": support_vectors_sample,
                    "n_support": n_support,
                }
            },
            'title': getattr(inputs, 'title', "Support Vector Machine Analysis Report"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"SVM analysis failed: {str(e)}")
