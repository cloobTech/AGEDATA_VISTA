from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_progressing import AnalysisInput
import pandas as pd
import numpy as np
from services.data_processing.visualization.gradient_boosting_plot import (
    generate_gb_classification_plots,
    generate_gb_regression_plots,
    generate_feature_importance
)
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    mean_squared_error, r2_score,
    roc_auc_score
)
from services.data_processing.analysis.train_gradient_boosting import train_gradient_boosting
from services.data_processing.report import crud


async def perform_gradient_boosting_analysis(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input

    try:
        X = data[input.feature_cols]
        y = data[input.target_col]

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
                "precision": precision_score(results["y_test"], results["y_pred"], average='weighted'),
                "recall": recall_score(results["y_test"], results["y_pred"], average='weighted'),
                "roc_auc": roc_auc_score(results["y_test"], results["y_proba"]) if results["y_proba"] is not None else None
            }
        else:
            metrics = {
                "mse": mean_squared_error(results["y_test"], results["y_pred"]),
                "rmse": np.sqrt(mean_squared_error(results["y_test"], results["y_pred"])),
                "r2": r2_score(results["y_test"], results["y_pred"])
            }

        # Generate visualizations
        if inputs.generate_visualizations:
            visualizations = {}
            if input.task_type == "classification":
                visualizations.update(generate_gb_classification_plots(
                    results["y_test"], results["y_pred"], results["y_proba"]
                ))
            else:
                visualizations.update(generate_gb_regression_plots(
                    results["y_test"], results["y_pred"]
                ))

            visualizations.update(generate_feature_importance(
                results["model"], input.feature_cols
            ))

        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {"metrics": metrics,
                        "model_type": input.model_type.value,
                        "feature_importance": dict(zip(
                            input.feature_cols,
                            results["model"].feature_importances_.tolist()
                        ))},
            'title': getattr(inputs, 'title', "Gradient Boosting Analysis Report"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)
        return report

    except Exception as e:
        raise ValueError(
            f"Gradient boosting analysis failed: {str(e)}")
