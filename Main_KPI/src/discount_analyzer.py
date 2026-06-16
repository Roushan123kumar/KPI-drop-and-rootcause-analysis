import pandas as pd
import numpy as np


class DiscountAnalyzer:

    def __init__(self, df):
        self.df = df.copy()

    # ==================================================
    # DISCOUNT VS PROFIT ANALYSIS
    # ==================================================
    def discount_vs_profit(self):
        if "discount" not in self.df.columns:
            return pd.DataFrame()

        # Bucket discounts into ranges
        self.df["discount_bucket"] = pd.cut(
            self.df["discount"],
            bins=[-0.01, 0.05, 0.10, 0.20, 0.30, 0.40, 1.0],
            labels=["0-5%", "5-10%", "10-20%", "20-30%", "30-40%", "40%+"]
        )

        result = (
            self.df.groupby("discount_bucket", observed=True)
            .agg(
                total_sales=("sales",   "sum"),
                total_profit=("profit", "sum"),
                avg_margin=("profit_margin_%", "mean"),
                order_count=("order_id", "count")
            )
            .reset_index()
        )

        result["profit_per_order"] = result["total_profit"] / result["order_count"]
        return result

    # ==================================================
    # TOP DISCOUNTED PRODUCTS LOSING PROFIT
    # ==================================================
    def top_loss_products(self, top_n=10):
        if "discount" not in self.df.columns:
            return pd.DataFrame()

        product_col = "product_name" if "product_name" in self.df.columns else "sub_category"

        result = (
            self.df.groupby(product_col)
            .agg(
                total_sales=("sales",    "sum"),
                total_profit=("profit",  "sum"),
                avg_discount=("discount","mean")
            )
            .reset_index()
        )

        # Products with high discount and low/negative profit
        result = result[result["avg_discount"] > 0.1]
        result = result.sort_values("total_profit").head(top_n)
        return result

    # ==================================================
    # DISCOUNT IMPACT SUMMARY
    # ==================================================
    def impact_summary(self):
        if "discount" not in self.df.columns:
            return {}

        high_discount = self.df[self.df["discount"] > 0.2]
        low_discount  = self.df[self.df["discount"] <= 0.2]

        return {
            "high_discount_avg_profit": high_discount["profit"].mean(),
            "low_discount_avg_profit":  low_discount["profit"].mean(),
            "high_discount_orders":     len(high_discount),
            "low_discount_orders":      len(low_discount),
            "total_profit_lost":        high_discount[high_discount["profit"] < 0]["profit"].sum()
        }