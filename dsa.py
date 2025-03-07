from services.data_processing.regression import perform_regression
from services.data_processing.data_loader import load_data
from services.data_processing.spark_session import get_spark_session
from io import BytesIO

# Create a Spark session
spk = get_spark_session()

# Read the CSV file
with open("regression_sample.csv", "rb") as f:
    csv_file = BytesIO(f.read())

csv_df = load_data(spk, csv_file, "regression_sample.csv")
csv_df.show()

# Perform regression analysis
features_col = ["feature1", "feature2", "feature3"]
label_col = "target"
model = perform_regression(csv_df, features_col, label_col)

# Print the model summary
training_summary = model.summary
print(f"RMSE: {training_summary.rootMeanSquaredError}")
print(f"R2: {training_summary.r2}")

# Optionally, print additional details from the summary
print(f"Coefficients: {model.coefficients}")
print(f"Intercept: {model.intercept}")