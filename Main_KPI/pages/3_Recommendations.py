# ==================================================
# PAGE 3 — RECOMMENDATIONS & AI EXPLAINER
# Refactored for Global State & Robust AI Insights
# ==================================================
import streamlit as st
import pandas as pd

# Internal Engine Imports
from src.kpi_engine         import KPIEngine
from src.drop_detection     import DropDetector
from src.root_cause         import RootCauseAnalyzer
from src.pipeline_inspector import PipelineInspector
from src.executive_summary  import ExecutiveSummary
from src.ai_explainer       import AIExplainer
from src.llm_explainer      import LLMExplainer  # Groq/Llama 3.1 Integration

# ==================================================
# AUTH + DATASET GUARD
# ==================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.switch_page("app.py")

# Single Source of Truth: Reference the data uploaded in app.py
if st.session_state.get("main_df") is None:
    st.warning("⚠️ No dataset detected. Please complete setup in the Dashboard.")
    st.switch_page("app.py")

df = st.session_state.main_df
role = st.session_state.get("role", "Viewer")

st.title("🧠 Recommendations & AI Explainer")
st.sidebar.write(f"👤 **{st.session_state.username}** ({role})")

# Dataset Identification
if st.session_state.get("last_uploaded"):
    st.sidebar.success(f"📄 Dataset: {st.session_state.last_uploaded}")
else:
    st.sidebar.info("📄 Dataset: Demo data")

if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("app.py")

# ==================================================
# SIDEBAR THRESHOLDS (User-adjustable)
# ==================================================
st.sidebar.header("⚙️ Threshold Settings")
sales_threshold    = st.sidebar.number_input("Sales Goal",      value=500.0)
profit_threshold   = st.sidebar.number_input("Min Profit",      value=15000.0)
orders_threshold   = st.sidebar.number_input("Min Orders",      value=100.0)
margin_threshold   = st.sidebar.number_input("Min Margin %",   value=20.0)
shipping_threshold = st.sidebar.number_input("Max Ship Days",   value=3.0)

# ==================================================
# DATA PROCESSING
# ==================================================
# Use engines to analyze the active session data
kpi_engine = KPIEngine(df)
kpis       = kpi_engine.calculate_monthly_kpis().sort_values("year_month").reset_index(drop=True)
latest     = kpis.iloc[-1]
detector   = DropDetector(kpis)
drops      = detector.detect_drops()

# Root Cause Isolation
problem_month = drops.iloc[-1]["year_month"] if not drops.empty else None
root_result   = None
if problem_month:
    root_analyzer = RootCauseAnalyzer(df)
    root_result   = root_analyzer.full_root_cause(problem_month)

# Pipeline Health Check (Detecting "Messy" Data Gaps)
inspector    = PipelineInspector(df)
inspection   = inspector.full_inspection()
gaps_df      = inspection["gaps"]
zero_df      = inspection["zero_orders"]
cat_drops_df = inspection["category_drops"]

# ==================================================
# SECTION 1: EXECUTIVE SUMMARY
# ==================================================
st.header("📋 Executive Summary")
try:
    exec_gen = ExecutiveSummary(kpis, df, drops, root_result)
    summary  = exec_gen.generate()

    # Visual indicators based on business health
    if summary["status_color"] == "green":
        st.success(f"### {summary['overall_status']}")
    elif summary["status_color"] == "red":
        st.error(f"### {summary['overall_status']}")
    else:
        st.warning(f"### {summary['overall_status']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Period",  summary["period"])
    c2.metric("💰 Sales",   f"${summary['latest_sales']:,.0f}",  f"{summary['sales_change']:+.1f}%")
    c3.metric("📈 Profit",  f"${summary['latest_profit']:,.0f}", f"{summary['profit_change']:+.1f}%")
    c4.metric("📦 Orders",  f"{summary['latest_orders']:,.0f}",  f"{summary['orders_change']:+.1f}%")

    st.info(f"🔍 **Root Cause of Performance Variance:** {summary['root_cause']}")
except Exception as e:
    st.warning("Could not summarize data. Check for valid numeric columns.")

# ==================================================
# SECTION 2: AI DROP EXPLAINER (Groq Powered)
# ==================================================
st.header("🤖 AI Analysis (Llama 3.1)")
st.caption("Deep-dive explanation into why your KPIs are behaving this way.")

if not drops.empty and root_result:
    # Prepare summary for the AI
    kpi_summary = {
        "latest_sales":         round(float(latest["sales"]), 2),
        "latest_profit":        round(float(latest["profit"]), 2),
        "latest_orders":        round(float(latest["orders"]), 2),
        "latest_margin":        round(float(latest["profit_margin_%"]), 2),
        "latest_shipping_days": round(float(latest["avg_shipping_days"]), 2),
    }

    if st.button("🤖 Generate AI Explanation"):
        with st.spinner("Llama 3.1 is analyzing your business data..."):
            try:
                # Primary: Advanced AI Explanation
                llm = LLMExplainer()
                explanation = llm.explain(kpi_summary, root_result, drops)
                st.info(f"🤖 **AI Analysis Output:**\n\n{explanation}")
            except Exception as e:
                # Fallback: Template-based explanation if API fails
                st.warning("⚠️ AI API connection failed. Using local pattern-matcher...")
                fallback    = AIExplainer()
                explanation = fallback.explain_drop(kpi_summary, root_result, drops)
                st.info(f"📊 **Local Engine Analysis:**\n\n{explanation}")
else:
    st.success("✅ No KPI drops detected. Your data shows stable or positive growth.")

# ==================================================
# SECTION 3: SMART RECOMMENDATIONS
# ==================================================
st.header("🧠 Actionable Business Insights")
st.caption("Automated suggestions based on your data thresholds.")

recs = []
# Threshold-based alerts
if latest['sales']             < sales_threshold:
    recs.append("📉 **Increase Sales Velocity:** Your sales are below the target. Consider flash sales or targeted email marketing.")
if latest['profit_margin_%']   < margin_threshold:
    recs.append("📊 **Margin Recovery:** Your profit margin is thin. Review product pricing and reduce non-essential discounts.")
if latest['avg_shipping_days'] > shipping_threshold:
    recs.append("🚚 **Logistics Optimization:** Shipping is taking longer than target. Check for warehouse delays in the affected regions.")
if not gaps_df.empty:
    recs.append(f"🖥️ **Fix Data Gaps:** Detected {len(gaps_df)} periods of missing orders. This could be an app crash or API failure.")

if recs:
    for r in recs:
        st.warning(r)
else:
    st.success("✨ All KPIs are performing above your set thresholds. No immediate action required.")