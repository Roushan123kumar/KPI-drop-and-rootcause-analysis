import pandas as pd


class PipelineInspector:

    def __init__(self, df):
        self.df = df.copy()
        self.df["order_date"] = pd.to_datetime(self.df["order_date"])

    # ==================================================
    # 1️⃣ DATA GAP DETECTION (Possible App Crash)
    # ==================================================
    def detect_data_gaps(self):
        """
        Finds missing dates in order_date.
        A gap of 2+ days with no orders = possible app crash / pipeline failure.
        """
        daily_orders = (
            self.df.groupby("order_date")["sales"]
            .sum()
            .reset_index()
            .sort_values("order_date")
        )

        # Full date range
        full_range = pd.date_range(
            start=daily_orders["order_date"].min(),
            end=daily_orders["order_date"].max(),
            freq="D"
        )

        # Missing dates
        missing_dates = full_range.difference(daily_orders["order_date"])

        if len(missing_dates) == 0:
            return pd.DataFrame(), 0

        # Group consecutive missing dates into gap periods
        gaps = []
        gap_start = missing_dates[0]
        gap_end = missing_dates[0]

        for i in range(1, len(missing_dates)):
            if (missing_dates[i] - missing_dates[i - 1]).days == 1:
                gap_end = missing_dates[i]
            else:
                gaps.append({
                    "Gap Start": gap_start.date(),
                    "Gap End": gap_end.date(),
                    "Missing Days": (gap_end - gap_start).days + 1,
                    "Possible Cause": "⚠️ App Crash / Pipeline Failure"
                })
                gap_start = missing_dates[i]
                gap_end = missing_dates[i]

        # Append last gap
        gaps.append({
            "Gap Start": gap_start.date(),
            "Gap End": gap_end.date(),
            "Missing Days": (gap_end - gap_start).days + 1,
            "Possible Cause": "⚠️ App Crash / Pipeline Failure"
        })

        return pd.DataFrame(gaps), len(missing_dates)

    # ==================================================
    # 2️⃣ ZERO ORDER DETECTION (Possible Stock-Out)
    # ==================================================
    def detect_zero_order_days(self):
        """
        Finds dates where total orders were 0 or near 0.
        Possible stock-out or system issue.
        """
        # FIX: count rows per date instead of summing "orders" column
        daily_orders = (
            self.df.groupby("order_date")
            .size()
            .reset_index(name="orders")
            .sort_values("order_date")
        )

        # Days with 0 or 1 orders
        zero_days = daily_orders[daily_orders["orders"] <= 1].copy()
        zero_days["order_date"] = zero_days["order_date"].dt.date
        zero_days["Possible Cause"] = "📦 Possible Stock-Out / System Issue"
        zero_days.columns = ["Date", "Orders", "Possible Cause"]

        return zero_days

    # ==================================================
    # 3️⃣ SUDDEN CATEGORY DROP (Specific Product Affected)
    # ==================================================
    def detect_category_drops(self, threshold=-20.0):
        """
        Detects sudden month-over-month drops per category.
        Default threshold: -20% drop triggers alert.
        """
        if "category" not in self.df.columns:
            return pd.DataFrame()

        # Add year_month
        df = self.df.copy()
        df["year_month"] = df["order_date"].dt.to_period("M")

        cat_monthly = (
            df.groupby(["year_month", "category"])["sales"]
            .sum()
            .reset_index()
            .sort_values(["category", "year_month"])
        )

        # Pct change per category
        cat_monthly["pct_change"] = (
            cat_monthly.groupby("category")["sales"]
            .pct_change() * 100
        )

        # Filter drops below threshold
        drops = cat_monthly[cat_monthly["pct_change"] < threshold].copy()
        drops["year_month"] = drops["year_month"].astype(str)
        drops["pct_change"] = drops["pct_change"].round(2)
        drops["Possible Cause"] = "🛒 Product/Category Demand Drop or Stock-Out"
        drops.columns = ["Month", "Category", "Sales", "Drop %", "Possible Cause"]

        return drops.sort_values("Drop %")

    # ==================================================
    # 4️⃣ COMBINED SUMMARY
    # ==================================================
    def full_inspection(self, category_threshold=-20.0):
        gaps_df, total_missing = self.detect_data_gaps()
        zero_df = self.detect_zero_order_days()
        cat_drops_df = self.detect_category_drops(category_threshold)

        return {
            "gaps": gaps_df,
            "total_missing_days": total_missing,
            "zero_orders": zero_df,
            "category_drops": cat_drops_df
        }