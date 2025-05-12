from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from services.data_processing.report import crud
from schemas.data_progressing import AnalysisInput
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.visualization.pca import generate_pca_visualizations
import pandas as pd
from typing import Dict, Any


async def perform_pca_analysis(data: pd.DataFrame, input: AnalysisInput, session: AsyncSession) -> Dict[str, Any]:
    """
    Perform PCA analysis with Plotly visualizations exported as JSON.
    """
    inputs = input.analysis_input

    # Validate required parameters
    if not hasattr(inputs, 'numeric_cols') or not inputs.numeric_cols:
        raise ValueError("PCA requires numeric_cols parameter")

    # Prepare data
    X = data[inputs.numeric_cols].dropna()
    feature_names = inputs.numeric_cols  # Store feature names

    # Scale data if requested
    if getattr(inputs, 'scale_data', True):
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
    else:
        X_scaled = X.values

    # Perform PCA
    n_components = getattr(inputs, 'n_components', None)
    pca = PCA(n_components=n_components)
    principal_components = pca.fit_transform(X_scaled)

    # Create results DataFrame
    pc_cols = [f"PC{i+1}" for i in range(principal_components.shape[1])]
    pca_df = pd.DataFrame(principal_components, columns=pc_cols)

    # Add metadata if available
    if hasattr(inputs, 'color_col') and inputs.color_col in data.columns:
        pca_df[inputs.color_col] = data[inputs.color_col].values
    if hasattr(inputs, 'hover_col') and inputs.hover_col in data.columns:
        pca_df[inputs.hover_col] = data[inputs.hover_col].values

    # Prepare response
    response_content = {
        "explained_variance_ratio": list(pca.explained_variance_ratio_),
        "components": pd.DataFrame(pca.components_,
                                   columns=feature_names,
                                   index=pc_cols).to_dict(),
        "singular_values": list(pca.singular_values_),
        "n_components": pca.n_components_,
        "scale_data": getattr(inputs, 'scale_data', True)
    }

    visualizations = {}

    # Generate visualizations if requested
    if input.generate_visualizations:
        visualizations = generate_pca_visualizations(
            pca_df=pca_df,
            pca_model=pca,
            feature_names=feature_names,
            color_col=getattr(inputs, 'color_col', None),
            hover_col=getattr(inputs, 'hover_col', None)
        )

    # Create report object
    report_obj = {
        "visualizations": visualizations,
        'project_id': input.project_id,
        'summary': response_content,
        'title': input.title,
        'analysis_group': input.analysis_group
    }

    # Create and store report
    report = await crud.create_report(report_obj, session=session)
    return report
