import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

# Generate a dataset with 100 rows
df = pd.DataFrame({
    "Employee_ID": np.arange(1, 101),  # Unique IDs for employees
    "Age": np.random.randint(22, 60, 100),  # Random ages between 22 and 60
    "Salary": np.random.randint(40000, 120000, 100),  # Random salaries between 40k and 120k
    "Department": np.random.choice(["IT", "HR", "Finance", "Marketing", "Operations"], 100),  # Random departments
    "Performance_Score": np.random.randint(1, 10, 100),  # Random performance scores between 1 and 10
    "Work_Hours": np.random.randint(30, 50, 100),  # Random work hours between 30 and 50
    "Joining_Date": pd.date_range(start="2015-01-01", periods=100, freq="ME"),  # Monthly end joining dates
    "Gender": np.random.choice(["Male", "Female"], 100)  # Random genders
})

# Save the dataset to a CSV file (optional)
df.to_csv("dataset.csv", index=False)
# Save the dataset to an Excel file
df.to_excel("dataset.xlsx", index=False)

print("Dataset saved as 'synthetic_dataset.xlsx'")

# Display the first few rows of the dataset
print(df.head())