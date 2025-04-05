import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from services.data_processing.visualization import descriptive_analysis
from services.data_processing.report.crud import create_report
from schemas.data_progressing import DescriptiveAnalysisInput


async def perform_descriptive_analysis(df: pd.DataFrame, inputs: DescriptiveAnalysisInput, session: AsyncSession) -> dict:
    """
    Perform descriptive analysis on a given DataFrame.

    :param df: Input DataFrame
    :return: Dictionary containing summary statistics and visualizations
    """

    # Check if the DataFrame is empty
    if df.empty:
        raise ValueError("The DataFrame is empty. Cannot perform analysis.")

    # Check if there are numeric columns
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    if numeric_columns.any():
        describe = df.describe(include=[np.number]).to_dict()
    else:
        describe = {}  # Fallback if no numeric columns are present

    summary = {
        "head": df.head().to_dict(),
        "describe": describe,
        "missing_values": df.isnull().sum().to_dict(),
        "data_types": df.dtypes.astype(str).to_dict(),
        "mean": df.mean(numeric_only=True).to_dict(),
        "median": df.median(numeric_only=True).to_dict(),
        "mode": df.mode().iloc[0].to_dict(),
        "min": df.min(numeric_only=True).to_dict(),
        "max": df.max(numeric_only=True).to_dict(),
        "count": df.count().to_dict(),
        "percentile_25": df.quantile(0.25, numeric_only=True).to_dict(),
        "percentile_50": df.quantile(0.50, numeric_only=True).to_dict(),
        "percentile_75": df.quantile(0.75, numeric_only=True).to_dict(),
        "variance": df.var(numeric_only=True).to_dict(),
        "standard_deviation": df.std(numeric_only=True).to_dict(),
        "skewness": df.skew(numeric_only=True).to_dict(),
        "kurtosis": df.kurt(numeric_only=True).to_dict(),
        "correlation_matrix": df.corr(numeric_only=True).to_dict(),
        "unique_values": {col: df[col].nunique() for col in df.columns},
        "value_counts": {col: df[col].value_counts().to_dict() for col in df.select_dtypes(include=['object']).columns},
        "file_id": inputs.file_id
    }

    report_obj = {}
    report_obj['project_id'] = inputs.project_id
    report_obj['summary'] = summary
    report_obj['title'] = inputs.title

    # Generate visualizations
    if inputs.generate_visualizations:
        # Standardize column names to lowercase
        # df.columns = df.columns.str.lower()
        descriptive_visualizations = inputs.descriptive_visualizations
        visualization_list = inputs.visualization_list
        visualizations = descriptive_analysis.generate_descriptive_visualizations(
            df, descriptive_visualizations, visualization_list)
        report_obj['visualizations'] = visualizations

    report = await create_report(data=report_obj, session=session)
    return report


