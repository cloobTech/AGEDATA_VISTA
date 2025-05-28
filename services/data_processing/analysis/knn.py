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
from services.data_processing.analysis.train_knn import train_knn
from services.data_processing.visualization.knn_plot import (
    generate_knn_confusion_matrix,
    generate_knn_decision_boundary,
    generate_knn_metrics_plot,
    generate_knn_elbow_curve
)
from services.data_processing.report import crud


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
                "rmse": np.sqrt(mean_squared_error(results["y_test"], results["y_pred"])),
                "r2": r2_score(results["y_test"], results["y_pred"])
            }

        # Generate visualizations
        visualizations = {}
        if inputs.generate_visualizations:
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
            "metrics": metrics,
            "summary": {"model_params": {
                "n_neighbors": input.config.n_neighbors,
                "algorithm": input.config.algorithm.value,
                "weights": input.config.weights.value,
                "effective_metric": results["model"].effective_metric_
            }},
            'title': getattr(inputs, 'title', "Support Vector Machine Analysis Report"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"KNN analysis failed: {str(e)}")
