from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import AnalysisInput
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    roc_auc_score,
    mean_squared_error, r2_score
)
import pandas as pd
import numpy as np
from services.data_processing.analysis.build_and_train_neural_networks import train_neural_network
from services.data_processing.visualization.neural_network_plot import (
    generate_nn_training_plots,
    generate_nn_confusion_matrix,
    generate_nn_roc_curve,
    generate_nn_feature_importance
)
from services.data_processing.report import crud


async def perform_neural_network_analysis(
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
        results = train_neural_network(
            X, y,
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
            if len(np.unique(y)) == 2 and results["y_proba"] is not None:
                metrics["roc_auc"] = roc_auc_score(
                    results["y_test"], results["y_proba"])
        else:
            metrics = {
                "mse": mean_squared_error(results["y_test"], results["y_pred"]),
                "rmse": np.sqrt(mean_squared_error(results["y_test"], results["y_pred"])),
                "r2": r2_score(results["y_test"], results["y_pred"])
            }

        # Generate visualizations
        visualizations = {}
        if inputs.generate_visualizations:
            visualizations.update(
                generate_nn_training_plots(results["history"]))

            if input.task_type == "classification":
                visualizations.update(generate_nn_confusion_matrix(
                    results["y_test"], results["y_pred"], results["class_names"]))

                if len(np.unique(y)) == 2 and results["y_proba"] is not None:
                    visualizations.update(generate_nn_roc_curve(
                        results["y_test"], results["y_proba"]))

            visualizations.update(generate_nn_feature_importance(
                results["model"], input.feature_cols))

        # Create report
        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {
                "metrics": metrics,

                "model_summary": {
                    "architecture": [layer.get_config() for layer in results["model"].layers],
                    "input_shape": results["model"].input_shape,
                    "output_shape": results["model"].output_shape,
                    "class_names": results["class_names"],
                    "training_epochs": len(results["history"]["loss"])
                }
            },
            'title': getattr(inputs, 'title', "Neural Network Report"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"Neural network analysis failed: {str(e)}")
