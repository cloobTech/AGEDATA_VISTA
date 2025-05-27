from typing import Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, roc_auc_score, confusion_matrix, roc_curve
from sklearn.model_selection import train_test_split
import pandas as pd
from services.data_processing.visualization.logistic_plot import generate_logistic_regression_plot
from services.data_processing.report import crud
from schemas.data_progressing import AnalysisInput


async def perform_logistic_regression(
    data: pd.DataFrame,
    inputs: AnalysisInput,
    session: AsyncSession
) -> Dict[str, Any]:
    input = inputs.analysis_input

    try:
        X = data[input.feature_cols]
        y = data[input.target_col]

        # Check if multi-class classification
        if len(y.unique()) > 2:
            # For multi-class problems, some solvers require specific settings
            if input.solver in ['liblinear']:
                raise ValueError(
                    "liblinear solver doesn't support multinomial loss")
            if input.penalty == 'none' and input.solver in ['lbfgs', 'newton-cg']:
                raise ValueError(
                    f"Solver {input.solver} doesn't support penalty='none'")

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=input.test_size, random_state=42, stratify=y
        )

        model = LogisticRegression(
            penalty=input.penalty,
            solver=input.solver,
            max_iter=input.max_iter,
            multi_class=input.multi_class  # Now using the corrected parameter
        )
        model.fit(X_train, y_train)

        y_pred = model.predict(X_test)

        # Handle probabilities differently for binary vs multi-class
        if len(model.classes_) == 2:
            y_proba = model.predict_proba(X_test)[:, 1]
            roc_auc = roc_auc_score(y_test, y_proba)
        else:
            y_proba = None
            roc_auc = None

        metrics = {
            "classification_report": classification_report(y_test, y_pred, output_dict=True),
            "confusion_matrix": confusion_matrix(y_test, y_pred).tolist()
        }

        if roc_auc is not None:
            metrics["roc_auc_score"] = roc_auc

        visualizations = {}
        if inputs.generate_visualizations:
            visualizations = generate_logistic_regression_plot(
                y_test,
                y_pred,
                y_proba if y_proba is not None else model.predict_proba(
                    X_test),
                len(model.classes_)
            )

        report = await crud.create_report({
            'project_id': inputs.project_id,
            "visualizations": visualizations,
            "summary": {
                "model": "Logistic Regression",
                "metrics": metrics,
                "coefficients": dict(zip(input.feature_cols, model.coef_[0].tolist()))
                if len(model.classes_) == 2
                else {cls: dict(zip(input.feature_cols, coef.tolist()))
                      for cls, coef in zip(model.classes_, model.coef_)}
            },
            'title': getattr(inputs, 'title', "Logistic Regression"),
            'analysis_group': getattr(inputs, 'analysis_group', "advance")
        }, session=session)

        return report

    except Exception as e:
        raise ValueError(f"Logistic Regression failed: {str(e)}")
