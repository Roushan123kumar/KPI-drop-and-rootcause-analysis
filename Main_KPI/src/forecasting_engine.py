import pandas as pd
import numpy as np
#for forecasting
from sklearn.linear_model import LinearRegression


class ForecastingEngine:

    def __init__(self, kpis):
        self.kpis = kpis.copy()

    def forecast(self, metric="sales", periods=3):

        df = self.kpis[["year_month", metric]].dropna().copy()
        df["index"] = range(len(df))

        X = df[["index"]].values
        y = df[metric].values

        model = LinearRegression()
        model.fit(X, y)

        # Predict future periods
        future_indices = np.array([[len(df) + i] for i in range(periods)])
        future_values  = model.predict(future_indices)

        # Generate future month labels
        last_month    = pd.Period(str(df["year_month"].iloc[-1]), freq="M")  # FIX: ensure it's a proper Period
        future_months = pd.period_range(start=last_month + 1, periods=periods, freq="M")

        forecast_df = pd.DataFrame({
            "year_month":            future_months.astype(str),
            f"{metric}_forecast":   future_values.round(2)
        })

        # Historical fit
        df["fitted"]       = model.predict(X).round(2)
        df["year_month"]   = df["year_month"].astype(str)  # FIX: ensure str for safe downstream use

        return df, forecast_df, model.coef_[0]