import pandas as pd

class DropDetector:

    def __init__(self, kpis):
        self.kpis = kpis

    def detect_drops(self, threshold=-10):

        drops = []

        for _, row in self.kpis.iterrows():
            if pd.notna(row["sales_growth_%"]) and row["sales_growth_%"] < threshold:
                drops.append({
                    "year_month": row["year_month"],
                    "kpi": "sales",
                    "drop_%": row["sales_growth_%"]
                })

        return pd.DataFrame(drops)
