import pandas as pd
import numpy as np
import time


class SimulationEngine:

    def __init__(self, df):
        self.df = df.copy()
        self.df["order_date"] = pd.to_datetime(self.df["order_date"])

    # ==================================================
    # GENERATE FAKE ORDERS BASED ON EXISTING PATTERNS
    # ==================================================
    def generate_fake_orders(self, n=20):

        # Learn patterns from existing data
        avg_sales       = self.df["sales"].mean()
        std_sales       = self.df["sales"].std()
        avg_profit_rate = (self.df["profit"] / self.df["sales"]).mean()

        categories   = self.df["category"].unique()   if "category"   in self.df.columns else ["General"]
        regions      = self.df["region"].unique()     if "region"     in self.df.columns else ["North"]
        segments     = self.df["segment"].unique()    if "segment"    in self.df.columns else ["Consumer"]
        ship_modes   = self.df["ship_mode"].unique()  if "ship_mode"  in self.df.columns else ["Standard"]
        sub_cats     = self.df["sub_category"].unique() if "sub_category" in self.df.columns else ["General"]

        last_date = self.df["order_date"].max()

        fake_orders = []

        for i in range(n):
            sales  = max(10, np.random.normal(avg_sales, std_sales))
            profit = sales * np.random.normal(avg_profit_rate, 0.05)

            fake_orders.append({
                "order_id":     f"SIM-{1000 + i}",
                "order_date":   last_date + pd.Timedelta(days=i + 1),
                "sales":        round(sales, 2),
                "profit":       round(profit, 2),
                "category":     np.random.choice(categories),
                "sub_category": np.random.choice(sub_cats),
                "region":       np.random.choice(regions),
                "segment":      np.random.choice(segments),
                "ship_mode":    np.random.choice(ship_modes),
                "quantity":     np.random.randint(1, 10),
                "discount":     round(np.random.uniform(0, 0.4), 2),
                "simulated":    True
            })

        return pd.DataFrame(fake_orders)

    # ==================================================
    # MERGE FAKE ORDERS INTO EXISTING DATA
    # ==================================================
    def merge_simulation(self, fake_df):
        combined = pd.concat([self.df, fake_df], ignore_index=True)
        combined = combined.sort_values("order_date").reset_index(drop=True)
        return combined