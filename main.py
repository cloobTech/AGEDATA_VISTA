from sqlalchemy.ext.asyncio import AsyncSession
import numpy as np
import pandas as pd
from schemas.data_progressing import DescriptiveAnalysisInput
from services.data_processing.analysis.descriptive import perform_descriptive_analysis
from storage import DBStorage as DB
import asyncio
from pprint import pprint


db = DB()


async def reload_db():
    """reload"""
    await db.drop_all()
    await db.reload()
    print('DB reloaded')

# asyncio.run(reload_db())


# Test Plotly


np.random.seed(42)

# Generate a dataset with 100 rows
df = pd.DataFrame({
    "Employee_ID": np.arange(1, 101),
    "Age": np.random.randint(22, 60, 100),
    "Salary": np.random.randint(40000, 120000, 100),
    "Department": np.random.choice(["IT", "HR", "Finance", "Marketing", "Operations"], 100),
    "Performance_Score": np.random.randint(1, 10, 100),
    "Work_Hours": np.random.randint(30, 50, 100),
    "Joining_Date": pd.date_range(start="2015-01-01", periods=100, freq="M"),
    "Gender": np.random.choice(["Male", "Female"], 100)
})

descriptive_visualizations = {
    "pie_chart_input": {
        "names": "Department",
        "title": "Employee Distribution"

    },
    "bar_chart_input": {
        "x": "Department",
        "y": "Salary",
        "title": "Average Salary by Department",
    },
    "line_chart_input": {
        "x": "Salary",
        "y": "Age",
        "title": "Age vs Salary"
    },
    "scatter_plot_input": {
        "x": "Salary",
        "y": "Age",
        "title": "Age vs Salary"
    },
    "heat_map_input": {
        "x": "Department",
        "y": "Salary",
        "title": "Age Distribution"
    },
    "histogram_input": {
        "x": "Department",
        "y": "Salary",
        "title": "Age Distribution"
    }
}

inputs = DescriptiveAnalysisInput(file_id='1', project_id='1', generate_visualizations=True, visualization_list=[
                                  'bar_chart', 'pie_chart', 'line_chart', 'scatter_plot', 'heat_map', 'histogram'], descriptive_visualizations=descriptive_visualizations)


async def test_descriptive_analysis():
    async for session in db.get_session():
        report = await perform_descriptive_analysis(df, inputs, session)
        pprint(report['visualizations'])


asyncio.run(test_descriptive_analysis())
