import pandas as pd
import numpy as np

class DataPreparation:
    def __init__(self, filepath):
        self.filepath = filepath

    def prepare(self):
        # Updated loading logic to handle "Buffer Overflow" and malformed files
        try:
            # engine='python' is slower but much more robust for messy/broken CSVs
            df = pd.read_csv(
                self.filepath, 
                encoding='utf-8', 
                engine='python', 
                on_bad_lines='skip'
            )
        except Exception:
            # Fallback for latin1 encoding if utf-8 fails
            df = pd.read_csv(
                self.filepath, 
                encoding='latin1', 
                engine='python', 
                on_bad_lines='skip'
            )

        # 1. Clean Column Names
        df.columns = (
            df.columns
            .str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("-", "_")
        )
        
        
        # 2. Broad Business Alias Mapping 
        # Maps diverse business terms (SaaS, Retail, B2B) to standard internal keys
        column_aliases = {
            "order_date":   ["date", "order_date", "timestamp", "transaction_date", "invoice_date", "created_at"],
            "ship_date":    ["ship_date", "shipdate", "shipping_date", "shipped_date"],
            "order_id":     ["order_id", "orderid", "id", "order_no", "order_number", "invoice_no", "ref"],
            "sales":        ["sales", "revenue", "sale_amount", "total_sales", "amount", "turnover", "mrr"],
            "profit":       ["profit", "net_profit", "profit_amount", "earnings", "margin", "net_income"],
            "category":     ["category", "cat", "product_category", "dept", "department", "industry"],
            "sub_category": ["sub_category", "subcategory", "sub_cat", "product_sub_category", "class"],
            "region":       ["region", "area", "zone", "territory", "location", "city", "state", "branch"],
            "quantity":     ["quantity", "qty", "units", "quantity_ordered", "count", "vol"],
            "segment":      ["segment", "customer_segment", "market", "group"]
        }

        for target_col, possible_names in column_aliases.items():
            if target_col not in df.columns:
                for alias in possible_names:
                    if alias in df.columns:
                        df.rename(columns={alias: target_col}, inplace=True)
                        break

        # 3. Critical Data Recovery (Prevents Collapse)
        
        # Date Handling: If no date column is found, attempt to find any column containing 'date'
        if "order_date" not in df.columns:
            date_cols = [c for c in df.columns if 'date' in c or 'time' in c]
            if date_cols:
                df.rename(columns={date_cols[0]: "order_date"}, inplace=True)
            else:
                # If still missing, we cannot track 'drops' over time, so we must raise an error
                raise KeyError("❌ Critical Error: No date column found. Please include a 'Date' column.")

        # Numeric Recovery: Sales and Profit
        if "sales" not in df.columns:
            df["sales"] = 0.0
        else:
            df["sales"] = pd.to_numeric(df["sales"], errors='coerce').fillna(0.0)

        if "profit" not in df.columns:
            # Fallback: Assume a generic 15% profit margin if data is missing
            df["profit"] = df["sales"] * 0.15
        else:
            df["profit"] = pd.to_numeric(df["profit"], errors='coerce').fillna(0.0)

        # Categorical Recovery: Defaults for missing business segments
        for col in ["category", "sub_category", "region", "segment"]:
            if col not in df.columns:
                df[col] = "General"

        # 4. Standardizing and Derived Columns
        
        # Convert to datetime with 'coerce' to turn malformed dates into NaT (Not a Time)
        df["order_date"] = pd.to_datetime(df["order_date"], errors='coerce')
        df = df.dropna(subset=["order_date"]) # Only drop rows where date is completely unreadable

        # Year-Month for KPI trend analysis
        df["year_month"] = df["order_date"].dt.to_period("M")

        # Ensure Order IDs exist for unique transaction tracking
        if "order_id" not in df.columns:
            df["order_id"] = ["ID-" + str(i).zfill(6) for i in range(len(df))]

        # Shipping Days calculation
        if "ship_date" in df.columns:
            df["ship_date"] = pd.to_datetime(df["ship_date"], errors='coerce')
            df["shipping_days"] = (df["ship_date"] - df["order_date"]).dt.days.fillna(0)
        else:
            df["shipping_days"] = 0

        # 5. Final Cleaning
        # Remove duplicate IDs to prevent artificial inflation of sales figures
        df = df.drop_duplicates(subset=["order_id"])
        
        # Reset index to maintain order after drops
        df = df.reset_index(drop=True)

        return df

    def save(self, df, output_path="data/prepared_data.csv"):
        df.to_csv(output_path, index=False)
        print(f"✅ Data Preparation Complete.")
        print(f"📊 Processed {df.shape[0]} rows and {df.shape[1]} columns.")