import pandas as pd


class ComparisonEngine:

    def __init__(self, df):
        # Make a copy so original dataframe is not modified
        self.df = df.copy()

        # Convert order_date column to datetime
        self.df["order_date"] = pd.to_datetime(self.df["order_date"])

        # Sort by date (important for correct comparison)
        self.df = self.df.sort_values("order_date")

    # ==================================================
    # INTERNAL METHOD (Used by daily, weekly, monthly)
    # ==================================================
    def _compare(self, freq, metric):

        grouped = (
            self.df
            .groupby(pd.Grouper(key="order_date", freq=freq))[metric]
            .sum()
            .reset_index()
            .sort_values("order_date")
        )

        # FIX: Return tuple (None, 0.0) instead of bare None
        if len(grouped) < 2:
            return None, 0.0

        last_two = grouped.tail(2).copy()

        new_value = last_two.iloc[-1][metric]
        old_value = last_two.iloc[-2][metric]

        # FIX: Standard percent change (positive = gain, negative = drop)
        # FIX: Handle old_value == 0 edge case explicitly
        if old_value == 0:
            percent_change = float("inf") if new_value > 0 else 0.0
        else:
            percent_change = ((new_value - old_value) / old_value) * 100

        return last_two, percent_change

    # ==================================================
    # PUBLIC METHODS
    # ==================================================

    # 🔹 Daily comparison
    def daily_comparison(self, metric="sales"):
        return self._compare("D", metric)

    # 🔹 Weekly comparison
    def weekly_comparison(self, metric="sales"):
        return self._compare("W", metric)

    # 🔹 Monthly comparison
    def monthly_comparison(self, metric="sales"):
        return self._compare("ME", metric)

    # ==================================================
    # RAW VALUE COMPARISON (No grouping)
    # ==================================================
    def raw_comparison(self, metric="sales"):

        if len(self.df) < 2:
            return None, 0

        latest = self.df.iloc[-1][metric]
        previous = self.df.iloc[-2][metric]

        # FIX: Consistent formula with _compare + zero division guard
        if previous == 0:
            percent_change = float("inf") if latest > 0 else 0.0
        else:
            percent_change = ((latest - previous) / previous) * 100

        return {
            "latest": latest,
            "previous": previous,
            "percent_change": percent_change
        }