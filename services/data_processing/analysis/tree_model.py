from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import AnalysisInput
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    confusion_matrix, mean_squared_error, r2_score
)
from services.data_processing.analysis.train_tree_model import train_tree_model
from services.data_processing.visualization.tree_model import (
    generate_tree_confusion_matrix,
    generate_feature_importance,
    generate_regression_plots
)
from services.data_processing.report import crud


async def perform_tree_analysis(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:

    input = inputs.analysis_input
    try:
        X = data[input.feature_cols]
        y = data[input.target_col]

        # Train model
        results = train_tree_model(
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
                "confusion_matrix": confusion_matrix(results["y_test"], results["y_pred"]).tolist()
            }
        else:
            metrics = {
                "mse": mean_squared_error(results["y_test"], results["y_pred"]),
                "rmse": np.sqrt(mean_squared_error(results["y_test"], results["y_pred"])),
                "r2": r2_score(results["y_test"], results["y_pred"])
            }

        # Generate visualizations
        visualizations = {}
        if inputs.generate_visualizations:
            if input.task_type == "classification":
                visualizations.update(generate_tree_confusion_matrix(
                    results["y_test"], results["y_pred"]
                ))
            else:
                visualizations.update(generate_regression_plots(
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
                        "task_type": input.task_type,
                        "feature_importance": dict(zip(
                            input.feature_cols,
                            results["model"].feature_importances_.tolist()
                        ))},
            'title': getattr(inputs, 'title', "Logistic Regression"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)
        return report

    except Exception as e:
        raise ValueError(f"Tree model analysis failed: {str(e)}")
