class KPIEngine:

    def __init__(self, df):
        self.df = df

    def calculate_monthly_kpis(self):

        kpis = (
            self.df.groupby("year_month")
            .agg({
                "sales": "sum",
                "profit": "sum",
                "order_id": "count",
                "shipping_days": "mean"
            })
            .reset_index()
        )

        # Rename columns
        kpis.rename(columns={
            "order_id": "orders",
            "shipping_days": "avg_shipping_days"
        }, inplace=True)

        # Profit Margin
        kpis["profit_margin_%"] = (
            kpis["profit"] / kpis["sales"]
        ) * 100

        # Sales Growth %
        kpis["sales_growth_%"] = kpis["sales"].pct_change() * 100

        return kpis