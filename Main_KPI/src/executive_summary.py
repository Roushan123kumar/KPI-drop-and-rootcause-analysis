import pandas as pd


class ExecutiveSummary:

    def __init__(self, kpis, df, drops, root_result=None):
        self.kpis        = kpis
        self.df          = df
        self.drops       = drops
        self.root_result = root_result

    def generate(self):
        latest   = self.kpis.iloc[-1]
        previous = self.kpis.iloc[-2] if len(self.kpis) >= 2 else latest

        def pct_change(new, old):
            return ((new - old) / old * 100) if old != 0 else 0

        sales_change  = pct_change(latest["sales"],  previous["sales"])
        profit_change = pct_change(latest["profit"], previous["profit"])
        orders_change = pct_change(latest["orders"], previous["orders"])

        # NEW: Check for recent critical drops (Last 3 Months)
        recent_drop = False
        if not self.drops.empty:
            # Convert recent periods to strings for comparison
            recent_periods = self.kpis.tail(3)["year_month"].astype(str).tolist()
            # If any month in our 'drops' list matches the last 3 months of data
            recent_drop = any(str(d) in recent_periods for d in self.drops["year_month"])

        # UPDATED STATUS LOGIC
        if sales_change > 0 and profit_change > 0 and not recent_drop:
            overall_status = "🟢 Business is Growing"
            status_color   = "green"
        elif sales_change < -10 or profit_change < -10 or recent_drop:
            # Even if the current month is okay, we flag 'Red' if a drop just happened
            overall_status = "🔴 Business Requires Attention (Recent KPI Drop Detected)"
            status_color   = "red"
        else:
            overall_status = "🟡 Business is Recovering/Stable"
            status_color   = "orange"

        top_region   = self.df.groupby("region")["sales"].sum().idxmax()   if "region"   in self.df.columns else "N/A"
        top_category = self.df.groupby("category")["sales"].sum().idxmax() if "category" in self.df.columns else "N/A"

        drop_status = (
            f"🚨 Critical Drop identified in {self.drops.iloc[-1]['year_month']}"
            if not self.drops.empty else "✅ No recent KPI drops"
        )

        root_cause = (
            f"{self.root_result['category']} → {self.root_result['sub_category']} → {self.root_result['region']}"
            if self.root_result else "No current issues"
        )

        return {
            "overall_status": overall_status,
            "status_color":   status_color,
            "latest_sales":   latest["sales"],
            "latest_profit":  latest["profit"],
            "latest_orders":  latest["orders"],
            "sales_change":   sales_change,
            "profit_change":  profit_change,
            "orders_change":  orders_change,
            "top_region":     top_region,
            "top_category":   top_category,
            "drop_status":    drop_status,
            "root_cause":     root_cause,
            "period":         str(latest["year_month"])
        }