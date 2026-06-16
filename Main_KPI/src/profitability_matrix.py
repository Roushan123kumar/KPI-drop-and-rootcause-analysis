import pandas as pd
import numpy as np


class ProfitabilityMatrix:

    def __init__(self, df):
        self.df = df.copy()

    def generate(self):

        product_col = "sub_category" if "sub_category" in self.df.columns else "category"

        result = (
            self.df.groupby(product_col)
            .agg(
                total_sales=("sales",  "sum"),
                total_profit=("profit","sum"),
                orders=("order_id",    "count")
            )
            .reset_index()
        )

        # Median splits for quadrants
        sales_median  = result["total_sales"].median()
        profit_median = result["total_profit"].median()

        # Assign quadrant
        def assign_quadrant(row):
            high_sales  = row["total_sales"]  >= sales_median
            high_profit = row["total_profit"] >= profit_median

            if high_sales and high_profit:
                return "⭐ Star"
            elif high_sales and not high_profit:
                return "❓ Question Mark"
            elif not high_sales and high_profit:
                return " Cash Cow"
            else:
                return " Dog"

        result["quadrant"] = result.apply(assign_quadrant, axis=1)
        result = result.rename(columns={product_col: "product"})

        return result, sales_median, profit_median