import pandas as pd
import numpy as np
from io import BytesIO


def generate_synthetic_time_series_csv(n_periods: int = 100, freq: str = 'D') -> bytes:
    """
    Generate synthetic time series data with trend and seasonality as a CSV file (in bytes).
    
    :param n_periods: Number of time periods (default: 100)
    :param freq: Frequency of the time series (e.g., 'D' for daily, 'M' for monthly)
    :return: CSV data as bytes
    """
    rng = pd.date_range(start='2023-01-01', periods=n_periods, freq=freq)
    
    # Simulate components
    trend = np.linspace(10, 100, n_periods)
    seasonal = 10 * np.sin(2 * np.pi * np.arange(n_periods) / 12)
    noise = np.random.normal(scale=5, size=n_periods)

    # Combine components
    values = trend + seasonal + noise

    df = pd.DataFrame({
        "date": rng,
        "value": values
    })

    # Save as CSV
    output = BytesIO()
    df.to_csv(output, index=False)

    return output.getvalue()


csv_data = generate_synthetic_time_series_csv()
with open("sample_time_series.csv", "wb") as f:
    f.write(csv_data)
