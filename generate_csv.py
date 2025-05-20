import pandas as pd
import random
from datetime import datetime, timedelta


# Generate 100 rows of data
start_date = datetime(2023, 1, 1)
data = {
    "date": [(start_date + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(100)],
    # Random sales values between 200 and 500
    "sales": [random.randint(200, 500) for _ in range(100)]
}

# Create a DataFrame
df = pd.DataFrame(data)

# Save to CSV
df.to_csv("sales_data.csv", index=False)

print("CSV file 'sales_data.csv' created successfully!")
