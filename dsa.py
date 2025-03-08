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

"""
DEV_ENV=dev
SECRET_KEY=super_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=520
REFRESH_TOKEN_EXPIRE_DAYS=30
EMAIL_CONFIG_USERNAME=belkid98@gmail.com
EMAIL_CONFIG_PASSWORD=jdlcelwnuzcpfoil
DATABASE_URL=sqlite+aiosqlite:///db.sqlite3
CLOUDINARY_CLOUD_NAME=ddheqirld
CLOUDINARY_API_KEY=933716352435599
CLOUDINARY_API_SECRET=5M6gHwz0lRJqw0HPfFpVY_EGKU4
GOOGLE_CLIENT_ID=448662846551-qvhe4c4l0v1uremqkkbpj3235lddq69r.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
FRONTEND_URL=http://localhost:3000
"""