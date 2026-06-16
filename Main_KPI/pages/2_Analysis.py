# ==================================================
# PAGE 2 — ANALYSIS
# Refactored for Global State & Messy Data Support
# ==================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np

# Internal Engine Imports
from src.kpi_engine           import KPIEngine
from src.drop_detection       import DropDetector
from src.root_cause           import RootCauseAnalyzer
from src.discount_analyzer    import DiscountAnalyzer
from src.profitability_matrix import ProfitabilityMatrix
from src.forecasting_engine   import ForecastingEngine

# ==================================================
# AUTH + DATASET GUARD
# ==================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.switch_page("app.py")

# This is the "Link" that ensures the data you uploaded in app.py persists here
if not st.session_state.get("dataset_ready", False) or st.session_state.get("main_df") is None:
    st.warning("⚠️ No dataset loaded. Please complete setup in the Dashboard first.")
    st.switch_page("app.py")

# ==================================================
# DATA SOURCE — SINGLE SOURCE OF TRUTH
# ==================================================
# Pull the processed dataframe from global memory
df = st.session_state.main_df

role = st.session_state.get("role", "Viewer")
st.title("🔍 KPI Analysis")
st.sidebar.write(f"👤 **{st.session_state.username}** ({role})")

# Display active dataset info
if st.session_state.get("last_uploaded"):
    st.sidebar.success(f"📄 Active: {st.session_state.last_uploaded}")
else:
    st.sidebar.info("📄 Active: Demo Data")

st.sidebar.caption(f"📊 {len(df)} rows loaded and cleaned.")

if st.sidebar.button(" Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("app.py")

# ==================================================
# ENGINE INITIALIZATION
# ==================================================
# These engines consume the 'df' regardless of how many columns were missing
kpi_engine = KPIEngine(df)
kpis       = kpi_engine.calculate_monthly_kpis().sort_values("year_month").reset_index(drop=True)
detector   = DropDetector(kpis)
drops      = detector.detect_drops()

# ==================================================
# SECTION 8 — ANOMALY & ROOT CAUSE
# ==================================================
st.header(" Anomaly Detection Engine")

if drops.empty:
    st.success("No significant KPI drops detected in the current dataset.")
else:
    st.error(" KPI DROP DETECTED")
    st.dataframe(drops, hide_index=True)
    problem_month = drops.iloc[-1]["year_month"]

    st.header("🔍 Root Cause Drill-Down")
    # This analyzer automatically maps to whatever categories exist in the user's file
    root_analyzer = RootCauseAnalyzer(df)
    root_result   = root_analyzer.full_root_cause(problem_month)

    st.info(f"""
    **Automated Findings for {problem_month}:**
    * **Category Impact** → {root_result['category']}
    * **Regional Weakness** → {root_result['region']}
    * **Segment Affected** → {root_result['segment']}
    """)


# ==================================================
# SECTION 14 — PRODUCT PROFITABILITY MATRIX
# ==================================================
st.header(" Product Profitability Matrix (BCG)")

try:
    # Uses median splits to categorize items even if profit is estimated
    pm = ProfitabilityMatrix(df)
    matrix_df, sales_med, profit_med = pm.generate()

    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(" Quadrant Assignments")
        st.dataframe(matrix_df[["product", "quadrant", "total_sales", "total_profit"]].head(10), hide_index=True)

    with col2:
        st.subheader("📊 Matrix View")
        fig, ax = plt.subplots(figsize=(6, 5))
        for q, color in zip(["⭐ Star", "❓ Question Mark", " Cash Cow", " Dog"], ["gold", "orange", "green", "red"]):
            sub = matrix_df[matrix_df["quadrant"] == q]
            ax.scatter(sub["total_sales"], sub["total_profit"], label=q, color=color, s=100)
        
        ax.axvline(sales_med, color='gray', linestyle='--')
        ax.axhline(profit_med, color='gray', linestyle='--')
        ax.set_xlabel("Sales ($)")
        ax.set_ylabel("Profit ($)")
        ax.legend()
        st.pyplot(fig)
        plt.close(fig)
except Exception as e:
    st.warning("Could not generate matrix. Ensure your CSV has valid sales and profit data.")

# ==================================================
# SECTION 15 — FORECASTING
# ==================================================
st.header(" Sales Forecasting")

try:
    # Linear Regression based on the user's uploaded history
    fe = ForecastingEngine(kpis)
    hist_df, fore_df, trend = fe.forecast("sales", periods=3)

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.plot(hist_df["year_month"], hist_df["sales"], label="Actual", color="steelblue")
    ax.plot(fore_df["year_month"], fore_df["sales_forecast"], label="Forecast", color="red", linestyle='--')
    ax.set_title("3-Month Sales Projection")
    ax.legend()
    st.pyplot(fig)
    plt.close(fig)
    
    if trend > 0:
        st.success(f"📈 Projected Growth: Your data suggests an upward trend of ${trend:,.2f} per month.")
    else:
        st.error(f"📉 Projected Decline: Your data suggests a downward trend of ${abs(trend):,.2f} per month.")
except Exception as e:
    st.info("Forecasting requires at least 2 months of historical data.")