import pandas as pd
import re
from statsmodels.tsa.statespace.sarimax import SARIMAX

class EmissionForecastAgent:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path, engine='openpyxl')
        self.df.columns = [col.strip().lower().replace(" ", "_") for col in self.df.columns]
        self._parse_dates()

    def _parse_dates(self):
        for col in self.df.columns:
            if 'date' in col or 'time' in col:
                self.df[col] = pd.to_datetime(self.df[col])
                self.df.set_index(col, inplace=True)
                return
        raise ValueError("No valid date column found.")

    def parse_query(self, query: str):
        query = query.lower().replace(" ", "_")
        emission_types = ['co2', 'methane', 'scope_1', 'scope_2', 'scope_3']
        forecast_periods = re.findall(r"(?:for|next|over|in)?_?(\d+)[-_]?year", query)
        years = int(forecast_periods[0]) if forecast_periods else 5
        matched_emissions = [et for et in emission_types if et in query]
        if not matched_emissions:
            raise ValueError("Could not determine emission type from query.")
        return matched_emissions, years

    def forecast(self, emission_type: str, years: int = 5):
        matching_cols = [col for col in self.df.columns if emission_type in col]
        if not matching_cols:
            raise ValueError(f"No column found for emission type '{emission_type}'")

        target_col = matching_cols[0]
        ts = self.df[target_col].resample('MS').mean().ffill()

        if 'revenue_forecast' not in self.df.columns:
            raise ValueError("The 'revenue_forecast' column is missing for exogenous forecasting.")

        revenue_ts = self.df['revenue_forecast'].resample('MS').mean().ffill()
        min_len = min(len(ts), len(revenue_ts))
        ts, revenue_ts = ts.iloc[:min_len], revenue_ts.iloc[:min_len]

        model = SARIMAX(ts, exog=revenue_ts, order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
        model_fit = model.fit(disp=False)

        future_revenue = revenue_ts[-12:].mean()
        future_exog = pd.Series([future_revenue] * (years * 12), index=pd.date_range(start=ts.index[-1] + pd.offsets.MonthBegin(), periods=years * 12, freq='MS'))
        forecast = model_fit.forecast(steps=years * 12, exog=future_exog)
        return ts, forecast

    def generate_summary(self):
        numeric_df = self.df.select_dtypes(include='number')
        if numeric_df.empty:
            raise ValueError("No numeric emissions data found to summarize.")
        return numeric_df.describe().T[["mean", "std", "min", "max"]].round(2)

    def generate_prompt(self, emission_type: str, years: int, forecast, summary_df):
        summary_markdown = summary_df.to_markdown() if isinstance(summary_df, pd.DataFrame) else "No summary available."
        return f"""
You are a senior environmental analyst reviewing historical and forecasted emissions data.

## Summary of Uploaded Emissions Data:
{summary_markdown}

## Forecast Task:
The user has requested a {years}-year forecast for {emission_type.upper()} emissions.

## Sample Forecast (First 12 Months):
{forecast.head(12).tolist()}

Please generate a concise, insight-driven report covering:

### 📈 Emissions Forecast Overview
- Trend direction and stability across the forecasted period
- Any volatility, recovery signs, or anomalies

### 🌀 Seasonality & Anomalies
- Seasonal effects and unexpected spikes or dips
- Operational or environmental triggers

### ⚠️ Key Drivers Behind Patterns
- Operational, regulatory, or energy source explanations

### ✅ Recommendations
- Specific actions to mitigate emissions, optimize energy use, and improve sustainability
- Strategic suggestions tailored to future actions
"""

    def get_data_snapshot(self):
        return self.df.head(100).to_markdown()
