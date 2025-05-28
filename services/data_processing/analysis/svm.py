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

        # Train model
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
                "rmse": np.sqrt(mean_squared_error(results["y_test"], results["y_pred"])),
                "r2": r2_score(results["y_test"], results["y_pred"])
            }

        # Generate visualizations
        visualizations = {}
        if inputs.generate_visualizations:

            if input.task_type == "classification":
                visualizations.update(generate_svm_confusion_matrix(
                    results["y_test"], results["y_pred"]))

                if len(input.feature_cols) == 2:
                    visualizations.update(generate_svm_decision_boundary(
                        results["model"], results["X_test"], results["y_test"]))

            visualizations.update(generate_svm_metrics_plot(metrics))

        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {"metrics": metrics,
                        "model_params": {
                            "kernel": input.config.kernel.value,
                            "support_vectors": results["model"].support_vectors_.tolist()
                            if hasattr(results["model"], "support_vectors_") else None,
                            "n_support": results["model"].n_support_.tolist()
                            if input.task_type == "classification" else None
                        }},
            'title': getattr(inputs, 'title', "Support Vector Machine Analysis Report"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"SVM analysis failed: {str(e)}")
