import pandas as pd
import numpy as np
from services.data_processing.visualization import descriptive_analysis

# Set random seed for reproducibility

def test_visulaization():
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

    # Display first few rows
    print(df.head(20))

    summary = descriptive_analysis.generate_visualizations(df)

    return summary

