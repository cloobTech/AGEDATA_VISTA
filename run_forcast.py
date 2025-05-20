import pandas as pd
from schemas.data_progressing import ForecastInput, SARIMAXConfig, ProphetConfig
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio
from services.data_processing.analysis.forecasting import perform_forecasting

# Sample DataFrame
data = {
    "date": [
        "2023-01-01", "2023-01-02", "2023-01-03", "2023-01-04", "2023-01-05",
        "2023-01-06", "2023-01-07", "2023-01-08", "2023-01-09", "2023-01-10"
    ],
    "sales": [200, 220, 250, 270, 300, 320, 310, 330, 340, 360],
    "promotion": [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # Example external variable
}

df = pd.DataFrame(data)
# df['date'] = pd.to_datetime(df['date'])
# df.set_index('date', inplace=True)

# # Reset the index to make 'date' a regular column
# df.reset_index(inplace=True)

# Define the SARIMAX configuration
sarimax_config = SARIMAXConfig(
    order=[1, 1, 1],  # ARIMA (p, d, q)
    seasonal_order=[1, 1, 0, 12],  # SARIMA (P, D, Q, s)
    enforce_stationarity=True,
    enforce_invertibility=True
)

# Define the Prophet configuration
prophet_config = ProphetConfig(
    seasonality_mode="additive",  # Can be "additive" or "multiplicative"
    yearly_seasonality=True,
    weekly_seasonality=True,
    daily_seasonality=False,
    changepoint_prior_scale=0.05  # Controls flexibility of trend changes
)

forecast_input = ForecastInput(
    time_col='date',
    value_col='sales',
    forecast_steps=5,
    model_type='prophet',
    prophet=prophet_config
)

# Create a mock AsyncSession


class MockAsyncSession:
    async def commit(self):
        pass

    async def close(self):
        pass

    async def rollback(self):
        pass


async def main():
    session = MockAsyncSession()
    # Perform forecasting
    result = await perform_forecasting(df, forecast_input, session)
    print(result)
    await session.close()

# Run the main function
if __name__ == "__main__":
    asyncio.run(main())
