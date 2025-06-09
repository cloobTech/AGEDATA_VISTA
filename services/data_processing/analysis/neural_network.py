from typing import Dict, Any, Union
from keras import Input
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.data_processing import AnalysisInput
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    roc_auc_score,
    mean_squared_error, r2_score
)
import pandas as pd
import numpy as np
from services.data_processing.analysis.build_and_train_neural_networks import NeuralNetworkTrainer, DataType
from services.data_processing.visualization.neural_network_plot import (
    generate_nn_training_plots,
    generate_nn_confusion_matrix,
    generate_nn_roc_curve,
    generate_nn_feature_importance
)
from services.data_processing.report import crud
from utils.save_to_supabase import save_model_to_supabase


async def perform_neural_network_analysis(
    # Updated to accept either DataFrame or image directory path
    data: Union[pd.DataFrame, str],
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input

    try:
        # Initialize the trainer
        trainer = NeuralNetworkTrainer(config=input.config)

        # Train the model (handles both tabular and image data)
        if input.config.data_type == DataType.TABULAR:
            # For tabular data
            X = data[input.feature_cols]
            y = data[input.target_col]
            results = trainer.train(X, y)
        else:
            # For image data (data parameter should be the image directory path)
            results = trainer.train(data)
            # For images, feature_cols/target_col aren't needed as labels come from directory structure

        # Calculate metrics (updated to handle both data types)
        metrics = {}
        if input.task_type == "classification":
            # For image data, we need to get test data from generator
            if input.config.data_type == DataType.IMAGE:
                y_test = []
                y_pred = []
                test_gen = results["generator"]
                for i in range(len(test_gen)):
                    x, y = test_gen[i]
                    y_test.extend(y)
                    y_pred.extend(results["model"].predict(x).argmax(axis=1))
                y_test = np.array(y_test)
                y_pred = np.array(y_pred)
            else:
                y_test = results["y_test"]
                y_pred = results["y_pred"]

            metrics = {
                "accuracy": accuracy_score(y_test, y_pred),
                "precision_micro": precision_score(y_test, y_pred, average='micro'),
                "precision_macro": precision_score(y_test, y_pred, average='macro'),
                "precision_weighted": precision_score(y_test, y_pred, average='weighted'),
                "recall_micro": recall_score(y_test, y_pred, average='micro'),
                "recall_macro": recall_score(y_test, y_pred, average='macro'),
                "recall_weighted": recall_score(y_test, y_pred, average='weighted')
            }

            if (input.config.data_type == DataType.TABULAR and
                len(np.unique(y_test)) == 2 and
                    "y_proba" in results):
                metrics["roc_auc"] = roc_auc_score(y_test, results["y_proba"])

        else:  # Regression
            metrics = {
                "mse": mean_squared_error(results["y_test"], results["y_pred"]),
                "rmse": np.sqrt(mean_squared_error(results["y_test"], results["y_pred"])),
                "r2": r2_score(results["y_test"], results["y_pred"])
            }

        # Upload model to Supabase
        model_upload_result = await save_model_to_supabase(
            model=results["model"],
            model_name=f"{inputs.title or 'neural_net'}_{inputs.project_id}",
        )

        # Prepare model summary
        model_summary = {
            "architecture": [layer.get_config() for layer in results["model"].layers],
            "input_shape": results["model"].input_shape,
            "output_shape": results["model"].output_shape,
            "class_names": results["class_names"],
            "training_epochs": len(results["history"]["loss"]),
            "model_info": model_upload_result,
            "data_type": input.config.data_type.value
        }

        # Generate visualizations (updated for both data types)
        visualizations = {}
        if inputs.generate_visualizations:
            visualizations.update(
                generate_nn_training_plots(results["history"]))

            if input.task_type == "classification":
                # For images, use the collected y_test/y_pred from generator
                conf_matrix_data = {
                    "y_test": y_test if input.config.data_type == DataType.IMAGE else results["y_test"],
                    "y_pred": y_pred if input.config.data_type == DataType.IMAGE else results["y_pred"],
                    "class_names": results["class_names"]
                }
                visualizations.update(
                    generate_nn_confusion_matrix(**conf_matrix_data))

                if (input.config.data_type == DataType.TABULAR and
                    len(np.unique(y_test)) == 2 and
                        "y_proba" in results):
                    visualizations.update(generate_nn_roc_curve(
                        results["y_test"], results["y_proba"]))

            # Feature importance only for tabular data
            if input.config.data_type == DataType.TABULAR:
                visualizations.update(generate_nn_feature_importance(
                    results["model"], input.feature_cols))

        # Create report
        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {
                "metrics": metrics,
                "model_summary": model_summary
            },
            'title': getattr(inputs, 'title', "Neural Network Report"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance"),
            'data_type': input.config.data_type.value
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"Neural network analysis failed: {str(e)}")
