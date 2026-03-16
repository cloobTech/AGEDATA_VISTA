import logging
import uuid
from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import AnalysisInput
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
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

        # Calculate metrics
        metrics = {}
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
