# ==================================================
# PAGE 1 — LIVE DASHBOARD
# Sections: Executive Summary, Comparison, Alerts,
# Thresholds, Trend, Dashboard Viz, Advanced Viz,
# Animated Playback, Live Simulation
# ==================================================
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import numpy as np
import time
import tempfile
import os
from matplotlib.patches import Patch

# ==================================================
# AUTH CHECK
# ==================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.switch_page("app.py")

# ==================================================
# IMPORTS
# ==================================================
from src.data_preparation  import DataPreparation
from src.kpi_engine        import KPIEngine
from src.drop_detection    import DropDetector
from src.comparison_engine import ComparisonEngine
from src.simulation_engine import SimulationEngine
from src.alert_engine      import AlertEngine
from src.executive_summary import ExecutiveSummary
from src.root_cause        import RootCauseAnalyzer

try:
    from src.audit_logger import log_event
except Exception:
    def log_event(*args, **kwargs): pass

# ==================================================
# ROLE + TITLE
# ==================================================
role     = st.session_state.get("role",     "Viewer")
username = st.session_state.get("username", "user")

st.title("📊 KPI Intelligence System — Live Dashboard")
st.sidebar.write(f"👤 **{username}** ({role})")

if st.sidebar.button("🚪 Logout"):
    log_event(role, "Logout", "User logged out")
    st.session_state.logged_in = False
    st.session_state.role      = None
    st.session_state.username  = None
    st.switch_page("app.py")

# ==================================================
# SESSION STATE
# ==================================================
if "sim_running"  not in st.session_state: st.session_state.sim_running  = False
if "sim_index"    not in st.session_state: st.session_state.sim_index    = 0
if "sim_all_fake" not in st.session_state: st.session_state.sim_all_fake = None
if "anim_running" not in st.session_state: st.session_state.anim_running = False
if "anim_index"   not in st.session_state: st.session_state.anim_index   = 1
if "anim_done"    not in st.session_state: st.session_state.anim_done    = False
if "live_df"      not in st.session_state: st.session_state.live_df      = None

# ==================================================
# DATA SOURCE — SINGLE SOURCE OF TRUTH
# ==================================================

# 1. Pull the data directly from the Global Memory (Session State)
# This ensures that if you uploaded a file in app.py or Admin.py, it persists here.
if st.session_state.get("main_df") is not None:
    df = st.session_state.main_df
else:
    # Fallback only if memory is empty (e.g., direct URL access)
    @st.cache_data
    def load_default_data():
        prep = DataPreparation("data/train_prepared.csv")
        return prep.prepare()
    df = load_default_data()
    st.session_state.main_df = df

# 2. Sync Logic: Detect if a new dataset was uploaded elsewhere
# We track the "last_uploaded" name to see if we need to reset the dashboard view.
if "current_dashboard_file" not in st.session_state:
    st.session_state.current_dashboard_file = st.session_state.get("last_uploaded")

if st.session_state.current_dashboard_file != st.session_state.get("last_uploaded"):
    # NEW DATA DETECTED (from Admin Panel or App Setup)
    # Reset simulation and animation to prevent them from using old data
    st.session_state.live_df = None
    st.session_state.sim_running = False
    st.session_state.sim_index = 0
    st.session_state.anim_running = False
    st.session_state.anim_done = False
    st.session_state.current_dashboard_file = st.session_state.get("last_uploaded")
    st.rerun() 

# 3. Sidebar Information
st.sidebar.header("📂 Data Source")
if st.session_state.get("last_uploaded"):
    st.sidebar.success(f"✅ Active: {st.session_state.last_uploaded}")
else:
    st.sidebar.info("✅ Active: Demo Dataset")

# 4. Admin Shortcut (Optional: Admin can still swap directly here)
if role == "Admin":
    with st.sidebar.expander("🔄 Swap Dataset Locally"):
        uploaded_file = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx", "xls"], key="local_dash_swap")
        if uploaded_file is not None:
            if st.session_state.get("last_uploaded") != uploaded_file.name:
                with st.spinner("Processing..."):
                    suffix = os.path.splitext(uploaded_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                        tmp.write(uploaded_file.getvalue())
                        tmp_path = tmp.name
                    
                    # Robust processing: Handles missing cells/columns
                    prep = DataPreparation(tmp_path)
                    st.session_state.main_df = prep.prepare()
                    st.session_state.last_uploaded = uploaded_file.name
                    
                    # Force reset and reload
                    st.rerun()

# Use live_df if simulation is active, otherwise use the Global DF
current_df = st.session_state.live_df if st.session_state.get("sim_running") else df

# SimulationEngine created based on the CURRENT active data
sim = SimulationEngine(current_df)

# ==================================================
# SIDEBAR SETTINGS
# ==================================================
st.sidebar.header("⚙️ KPI Threshold Settings")

drop_threshold     = st.sidebar.number_input("Drop Alert %",       value=10.0)
sales_threshold    = st.sidebar.number_input("Sales Threshold",    value=500.0)
profit_threshold   = st.sidebar.number_input("Profit Threshold",   value=15000.0)
orders_threshold   = st.sidebar.number_input("Orders Threshold",   value=100.0)
margin_threshold   = st.sidebar.number_input("Margin Threshold %", value=20.0)
shipping_threshold = st.sidebar.number_input("Shipping Threshold", value=3.0)

st.sidebar.header("🎮 Playback & Simulation Speed")
anim_speed = st.sidebar.selectbox(
    "History Playback Speed",
    ["Slow (0.8s)", "Medium (0.4s)", "Fast (0.1s)"]
)
anim_map   = {"Slow (0.8s)": 0.8, "Medium (0.4s)": 0.4, "Fast (0.1s)": 0.1}
anim_delay = anim_map[anim_speed]

sim_speed  = st.sidebar.selectbox(
    "Live Simulation Speed",
    ["Slow (2s)", "Medium (1s)", "Fast (0.5s)"]
)
sim_map   = {"Slow (2s)": 2.0, "Medium (1s)": 1.0, "Fast (0.5s)": 0.5}
sim_delay = sim_map[sim_speed]

# ==================================================
# ALERT ENGINE
# ==================================================
alert_engine = AlertEngine({
    "email": {
        "sender":   "pro411937@gmail.com",
        "password": "qzhlzmcwabyznztl",
        "receiver": "roushanjsr2033@gmail.com"
    }
})

# ==================================================
# HELPER — CALCULATE KPIs FROM ANY DATAFRAME
# ==================================================
def get_kpis(data):
    engine = KPIEngine(data)
    kpis   = engine.calculate_monthly_kpis()
    return kpis.sort_values("year_month").reset_index(drop=True)

# Use live_df if simulation is running else use original df
current_df = st.session_state.live_df if st.session_state.live_df is not None else df.copy()
kpis       = get_kpis(current_df)

if len(kpis) == 0:
    st.warning("⚠️ No KPI data available")
    st.stop()

latest = kpis.iloc[-1]

# ==================================================
# ANOMALY + ROOT CAUSE — done early for exec summary
# ==================================================
detector      = DropDetector(kpis)
drops         = detector.detect_drops()
problem_month = drops.iloc[-1]["year_month"] if not drops.empty else None
root_result   = None
root_analyzer = None

if problem_month:
    root_analyzer = RootCauseAnalyzer(df)
    root_result   = root_analyzer.full_root_cause(problem_month)

# ==================================================
# SECTION 2 — EXECUTIVE SUMMARY
# Shows overall business health at a glance
# ==================================================
st.header("📋 Executive Summary")

try:
    exec_gen = ExecutiveSummary(kpis, df, drops, root_result)
    summary  = exec_gen.generate()

    if summary["status_color"] == "green":
        st.success(f"### {summary['overall_status']}")
    elif summary["status_color"] == "red":
        st.error(f"### {summary['overall_status']}")
    else:
        st.warning(f"### {summary['overall_status']}")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📅 Period",        summary["period"])
    c2.metric("💰 Latest Sales",  f"${summary['latest_sales']:,.0f}",  f"{summary['sales_change']:+.1f}%")
    c3.metric("📈 Latest Profit", f"${summary['latest_profit']:,.0f}", f"{summary['profit_change']:+.1f}%")
    c4.metric("📦 Latest Orders", f"{summary['latest_orders']:,.0f}",  f"{summary['orders_change']:+.1f}%")

    c5, c6, c7 = st.columns(3)
    c5.info(f"🏆 Top Region: **{summary['top_region']}**")
    c6.info(f"🛍️ Top Category: **{summary['top_category']}**")
    c7.info(f"🔍 Root Cause: **{summary['root_cause']}**")

    if "🚨" in summary["drop_status"]:
        st.error(summary["drop_status"])
    else:
        st.success(summary["drop_status"])

except Exception as e:
    st.warning(f"Executive summary error: {e}")

# ==================================================
# SECTION 3 — HISTORICAL DATA COMPARISON
# Daily / Weekly / Monthly comparison cards
# ==================================================
st.header("📊 Historical Data Comparison")

comparison_engine = ComparisonEngine(current_df)
col1, col2, col3  = st.columns(3)

def render_comparison(col, data, pct, label, period):
    if data is None:
        col.warning(f"Not enough data for {period}")
        return
    previous = data.iloc[-2][label]
    latest_v = data.iloc[-1][label]
    col.metric(period, f"{pct:.2f}%")
    fig, ax = plt.subplots()
    ax.bar(data["order_date"].astype(str), data[label], color="steelblue")
    ax.set_title(f"{period} Comparison")
    col.pyplot(fig)
    plt.close(fig)
    if pct < -drop_threshold:
        col.error(f"🚨 {period} Drop Detected")
    else:
        col.success("✅ Normal Movement")
    col.dataframe(
        pd.DataFrame({
            "":      ["Previous", "Latest", "Change %"],
            "Sales": [f"{previous:,.2f}", f"{latest_v:,.2f}", f"{pct:+.2f}%"]
        }),
        hide_index=True
    )

data_d, pct_d = comparison_engine.daily_comparison("sales")
data_w, pct_w = comparison_engine.weekly_comparison("sales")
data_m, pct_m = comparison_engine.monthly_comparison("sales")

render_comparison(col1, data_d, pct_d, "sales", "Today vs Yesterday")
render_comparison(col2, data_w, pct_w, "sales", "This Week vs Last Week")
render_comparison(col3, data_m, pct_m, "sales", "This Month vs Last Month")

# ==================================================
# SECTION 4 — REAL-TIME ALERTS
# Only Admin and Analyst can see alerts
# ==================================================
if role == "Viewer":
    st.info("👁️ You have Viewer access — alerts, simulation and advanced features are restricted")

if role != "Viewer":
    st.header("🔔 Real-Time Alerts")

    triggered_alerts = []

    if data_d is not None and pct_d < -drop_threshold:
        triggered_alerts.append(f"🚨 Daily Sales Drop: {pct_d:.2f}%")
        log_event("System", "KPI Drop", f"Daily: {pct_d:.2f}%")
    if data_w is not None and pct_w < -drop_threshold:
        triggered_alerts.append(f"🚨 Weekly Sales Drop: {pct_w:.2f}%")
        log_event("System", "KPI Drop", f"Weekly: {pct_w:.2f}%")
    if data_m is not None and pct_m < -drop_threshold:
        triggered_alerts.append(f"🚨 Monthly Sales Drop: {pct_m:.2f}%")
        log_event("System", "KPI Drop", f"Monthly: {pct_m:.2f}%")

    if triggered_alerts:
        for a in triggered_alerts:
            st.error(a)
    else:
        st.success("✅ No alerts triggered")

    # Only Admin can send email
    if triggered_alerts and role == "Admin":
        if st.button("📤 Send Email Alert"):
            success, msg = alert_engine.send_email(
                "🚨 KPI Alert", "\n".join(triggered_alerts)
            )
            if success:
                st.success("✅ Email sent!")
            else:
                st.error(f"❌ Failed: {msg}")

# ==================================================
# SECTION 5 — THRESHOLD ALERTS
# ==================================================
st.subheader("🚨 Threshold Alerts")

threshold_alerts = []
if latest['sales']             < sales_threshold:    threshold_alerts.append("⚠️ Sales below threshold")
if latest['profit']            < profit_threshold:   threshold_alerts.append("⚠️ Profit below threshold")
if latest['orders']            < orders_threshold:   threshold_alerts.append("⚠️ Orders below threshold")
if latest['profit_margin_%']   < margin_threshold:   threshold_alerts.append("⚠️ Margin below threshold")
if latest['avg_shipping_days'] > shipping_threshold: threshold_alerts.append("⚠️ Shipping too slow")

if threshold_alerts:
    for a in threshold_alerts:
        st.warning(a)
else:
    st.success("✅ All KPIs above threshold")

# ==================================================
# SECTION 6 — KPI THRESHOLD TABLE
# ==================================================
st.subheader("🎯 KPI Threshold Comparison Table")

def check_status(value, threshold, reverse=False):
    if reverse:
        return "🟢 GOOD" if value <= threshold else "🔴 BAD"
    return "🟢 GOOD" if value >= threshold else "🔴 BAD"

st.dataframe(pd.DataFrame({
    "KPI":           ["Sales", "Profit", "Margin %", "Orders", "Shipping Days"],
    "Current Value": [
        round(latest['sales'], 2),
        round(latest['profit'], 2),
        round(latest['profit_margin_%'], 2),
        round(latest['orders'], 2),
        round(latest['avg_shipping_days'], 2)
    ],
    "Threshold": [
        sales_threshold, profit_threshold,
        margin_threshold, orders_threshold, shipping_threshold
    ],
    "Status": [
        check_status(latest['sales'],             sales_threshold),
        check_status(latest['profit'],            profit_threshold),
        check_status(latest['profit_margin_%'],   margin_threshold),
        check_status(latest['orders'],            orders_threshold),
        check_status(latest['avg_shipping_days'], shipping_threshold, reverse=True)
    ]
}), hide_index=True)

# ==================================================
# SECTION 7 — TREND VISUALIZATION
# ==================================================
st.subheader("📊 Sales & Profit Trend")

fig, ax = plt.subplots(figsize=(12, 5))
ax.plot(kpis["year_month"].astype(str), kpis["sales"],
        label="Sales",  color="steelblue", linewidth=2)
ax.plot(kpis["year_month"].astype(str), kpis["profit"],
        label="Profit", color="green",     linewidth=2)
ax.set_xlabel("Month")
ax.set_ylabel("Amount ($)")
ax.set_title("Monthly Sales & Profit Trend", fontweight='bold')
ax.legend()
ax.tick_params(axis='x', rotation=45)
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption("📊 Tracks monthly Sales and Profit over time to reveal growth patterns and downturns.")

# ==================================================
# ANIMATED KPI PLAYBACK — Stock Market Style
# Builds chart month by month like a stock ticker
# ==================================================
st.header("📈 KPI History Playback — Stock Market Style")
st.caption("Watch KPI data build month by month from start to end")

color_map = {
    "sales":             "steelblue",
    "profit":            "green",
    "orders":            "orange",
    "profit_margin_%":   "purple",
    "avg_shipping_days": "brown"
}

pc1, pc2, pc3, pc4 = st.columns(4)

anim_metric = pc1.selectbox(
    "KPI to Animate",
    ["sales", "profit", "orders", "profit_margin_%", "avg_shipping_days"],
    key="anim_metric_select"
)
line_color = color_map.get(anim_metric, "steelblue")

pc2.markdown("<br>", unsafe_allow_html=True)
if pc2.button("▶️ Play History"):
    st.session_state.anim_running = True
    st.session_state.anim_index   = 1
    st.session_state.anim_done    = False

pc3.markdown("<br>", unsafe_allow_html=True)
if pc3.button("⏹️ Stop Playback"):
    st.session_state.anim_running = False
    st.session_state.anim_index   = 1

pc4.markdown("<br>", unsafe_allow_html=True)
if pc4.button("⏭️ Skip to End"):
    st.session_state.anim_running = False
    st.session_state.anim_index   = len(kpis)
    st.session_state.anim_done    = True

anim_placeholder = st.empty()

# --------------------------------------------------
# ANIMATION LOOP
# --------------------------------------------------
if st.session_state.anim_running:
    idx = st.session_state.anim_index

    if idx <= len(kpis):
        kpis_partial     = kpis.iloc[:idx].copy()
        kpis_partial_str = kpis_partial["year_month"].astype(str)
        kpis_full_str    = kpis["year_month"].astype(str)

        with anim_placeholder.container():

            current_period = str(kpis_partial["year_month"].iloc[-1])
            current_value  = kpis_partial[anim_metric].iloc[-1]

            # Metric row
            m1, m2, m3 = st.columns(3)
            m1.metric("📅 Period", current_period)
            m2.metric(
                f"📊 {anim_metric.replace('_',' ').title()}",
                f"{current_value:,.2f}"
            )
            if len(kpis_partial) > 1:
                prev_val = kpis_partial[anim_metric].iloc[-2]
                chg      = ((current_value - prev_val) / prev_val * 100) if prev_val != 0 else 0
                if chg < 0:
                    m3.error(f"📉 {chg:+.2f}% vs last month")
                else:
                    m3.success(f"📈 {chg:+.2f}% vs last month")

            # Chart — line grows + MoM bars below
            fig, axes = plt.subplots(2, 1, figsize=(14, 8))
            fig.suptitle(
                f"📊 {anim_metric.replace('_',' ').title()} — {current_period}",
                fontsize=16, fontweight='bold'
            )

            # Top: line chart building up month by month
            axes[0].plot(
                range(len(kpis_partial)),
                kpis_partial[anim_metric],
                color=line_color, linewidth=2.5,
                marker='o', markersize=4
            )
            axes[0].fill_between(
                range(len(kpis_partial)),
                kpis_partial[anim_metric],
                alpha=0.2, color=line_color
            )
            # Red dot on the latest point
            axes[0].scatter(
                [len(kpis_partial) - 1],
                [kpis_partial[anim_metric].iloc[-1]],
                color='red', s=120, zorder=6
            )
            axes[0].set_xlim(-0.5, len(kpis) - 0.5)
            axes[0].set_xticks(range(len(kpis_full_str)))
            axes[0].set_xticklabels(
                kpis_full_str, rotation=45, ha='right', fontsize=7
            )
            axes[0].set_ylabel(anim_metric.replace('_', ' ').title())
            axes[0].grid(True, alpha=0.3)

            # Bottom: MoM % change bars
            if len(kpis_partial) > 1:
                mom        = kpis_partial[anim_metric].pct_change() * 100
                bar_colors = ['red' if v < 0 else 'green' for v in mom.fillna(0)]
                axes[1].bar(
                    range(len(kpis_partial)),
                    mom, color=bar_colors, alpha=0.8
                )
                axes[1].axhline(0, color='black', linewidth=0.8)
                axes[1].set_xlim(-0.5, len(kpis) - 0.5)
                axes[1].set_xticks(range(len(kpis_full_str)))
                axes[1].set_xticklabels(
                    kpis_full_str, rotation=45, ha='right', fontsize=7
                )
                axes[1].set_ylabel("MoM % Change")
                axes[1].grid(axis='y', alpha=0.3)
                axes[1].legend(handles=[
                    Patch(facecolor='green', label='Growth'),
                    Patch(facecolor='red',   label='Drop')
                ])

            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

            # Progress bar
            st.progress(
                idx / len(kpis),
                text=f"📅 {idx} of {len(kpis)} months"
            )

        st.session_state.anim_index += 1
        time.sleep(anim_delay)
        st.rerun()

    else:
        # Playback done — auto start live simulation
        st.session_state.anim_running = False
        st.session_state.anim_done    = True

        if not st.session_state.sim_running and role != "Viewer":
            fake_all = sim.generate_fake_orders(n=200)
            st.session_state.sim_all_fake = fake_all
            st.session_state.sim_index    = 0
            st.session_state.sim_running  = True
            st.session_state.live_df      = df.copy()

        st.rerun()

else:
    # Static preview when not animating
    with anim_placeholder.container():
        if st.session_state.anim_done:
            st.success("✅ Playback complete — live simulation running below")
        else:
            st.info("👆 Click **▶️ Play History** to watch KPI data build month by month")

        fig, ax = plt.subplots(figsize=(14, 5))
        ax.plot(
            kpis["year_month"].astype(str),
            kpis[anim_metric],
            color=line_color, linewidth=2,
            marker='o', markersize=3
        )
        ax.fill_between(
            kpis["year_month"].astype(str),
            kpis[anim_metric],
            alpha=0.2, color=line_color
        )
        ax.set_title(
            f"{anim_metric.replace('_',' ').title()} — Full History Preview",
            fontweight='bold'
        )
        ax.set_ylabel(anim_metric.replace('_', ' ').title())
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True, alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)
        st.caption("📈 Full historical view of the selected KPI — use Play History to watch it build month by month.")

# ==================================================
# SECTION 11 — DASHBOARD VISUALIZATION
# All KPI graphs with drop highlights
# ==================================================
st.header("📊 Dashboard Visualization")

# Add drop flags for coloring
kpis["sales_drop"]    = kpis["sales"].diff() < 0
kpis["profit_drop"]   = kpis["profit"].diff() < 0
kpis["orders_drop"]   = kpis["orders"].diff() < 0
kpis["margin_drop"]   = kpis["profit_margin_%"].diff() < 0
kpis["shipping_drop"] = kpis["avg_shipping_days"].diff() > 0
kpis_str = kpis["year_month"].astype(str)

# --------------------------------------------------
# Graph 2 — Bar Charts with Drop Highlights
# --------------------------------------------------
st.subheader("📊 Monthly KPI Bar Charts (Red = Drop Month)")

fig, axes = plt.subplots(2, 2, figsize=(16, 10))
fig.suptitle("Monthly KPI Comparison", fontsize=16, fontweight='bold')

def plot_bar(ax, x, y, drop_mask, title, ylabel, color):
    ax.bar(x, y, color=['red' if d else color for d in drop_mask])
    ax.set_title(title, fontweight='bold')
    ax.set_ylabel(ylabel)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', alpha=0.3)
    ax.legend(handles=[
        Patch(facecolor=color, label='Normal'),
        Patch(facecolor='red', label='Drop')
    ])

plot_bar(axes[0,0], kpis_str, kpis["sales"],           kpis["sales_drop"],  "Sales by Month",  "Sales ($)",  "steelblue")
plot_bar(axes[0,1], kpis_str, kpis["profit"],          kpis["profit_drop"], "Profit by Month", "Profit ($)", "green")
plot_bar(axes[1,0], kpis_str, kpis["orders"],          kpis["orders_drop"], "Orders by Month", "Orders",     "orange")
plot_bar(axes[1,1], kpis_str, kpis["profit_margin_%"], kpis["margin_drop"], "Margin by Month", "Margin (%)", "purple")
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption("📊 Monthly bar charts for each KPI — red bars highlight months where the KPI dropped vs the previous month.")

# --------------------------------------------------
# Graph 3 — Area Charts
# --------------------------------------------------
st.subheader("📉 Cumulative Area Charts")

fig, axes = plt.subplots(1, 2, figsize=(16, 5))
fig.suptitle("Cumulative Trends", fontsize=16, fontweight='bold')

axes[0].fill_between(kpis_str, kpis["sales"],  alpha=0.4, color="steelblue")
axes[0].plot(kpis_str, kpis["sales"],  color="steelblue", linewidth=2)
axes[0].set_title("Sales Area Chart",  fontweight='bold')
axes[0].set_ylabel("Sales ($)")
axes[0].tick_params(axis='x', rotation=45)
axes[0].grid(True, alpha=0.3)

axes[1].fill_between(kpis_str, kpis["profit"], alpha=0.4, color="green")
axes[1].plot(kpis_str, kpis["profit"], color="green",     linewidth=2)
axes[1].set_title("Profit Area Chart", fontweight='bold')
axes[1].set_ylabel("Profit ($)")
axes[1].tick_params(axis='x', rotation=45)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption("📉 Area charts show the cumulative volume of Sales and Profit over time, making overall growth or decline easy to spot.")

# --------------------------------------------------
# Graph 4 — Donut Charts
# --------------------------------------------------
st.subheader("🥧 Sales Breakdown by Category & Region")

col1, col2 = st.columns(2)

if "category" in df.columns:
    cat_sales = df.groupby("category")["sales"].sum()
    fig, ax   = plt.subplots(figsize=(7, 7))
    ax.pie(cat_sales, labels=cat_sales.index, autopct='%1.1f%%',
           startangle=140, wedgeprops=dict(width=0.5))
    ax.set_title("Sales by Category", fontweight='bold')
    col1.pyplot(fig)
    plt.close(fig)

if "region" in df.columns:
    region_sales = df.groupby("region")["sales"].sum()
    fig, ax      = plt.subplots(figsize=(7, 7))
    ax.pie(region_sales, labels=region_sales.index, autopct='%1.1f%%',
           startangle=140, wedgeprops=dict(width=0.5))
    ax.set_title("Sales by Region", fontweight='bold')
    col2.pyplot(fig)
    plt.close(fig)

st.caption("🥧 Donut charts show what share of total sales comes from each product category and geographic region.")

# --------------------------------------------------
# Graph 6 — Top Affected KPIs
# --------------------------------------------------
st.subheader("🏆 Top Affected KPIs — Worst Drop Ever")

kpi_drops = {
    "Sales":           kpis["sales"].pct_change().min() * 100,
    "Profit":          kpis["profit"].pct_change().min() * 100,
    "Orders":          kpis["orders"].pct_change().min() * 100,
    "Profit Margin %": kpis["profit_margin_%"].pct_change().min() * 100,
    "Shipping Days":   kpis["avg_shipping_days"].pct_change().max() * 100
}

st.dataframe(pd.DataFrame({
    "KPI":            list(kpi_drops.keys()),
    "Worst Drop (%)": [f"{v:.2f}%" for v in kpi_drops.values()]
}).sort_values("Worst Drop (%)"), hide_index=True)

fig, ax = plt.subplots(figsize=(10, 5))
ax.barh(
    list(kpi_drops.keys()),
    list(kpi_drops.values()),
    color=['red' if v < 0 else 'green' for v in kpi_drops.values()]
)
ax.axvline(0, color='black', linewidth=0.8)
ax.set_title("Worst % Drop Per KPI", fontweight='bold')
ax.set_xlabel("% Change")
ax.grid(axis='x', alpha=0.3)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption("🏆 Ranks each KPI by its single worst month-over-month drop — red bars indicate KPIs that suffered a decline, green bars indicate overall gains.")


# ==================================================
# SECTION 12 — ADVANCED KPI VISUALIZATIONS
# ==================================================
st.header("📊 Advanced KPI Visualizations")

# --------------------------------------------------
# Sales vs Profit Scatter
# --------------------------------------------------
st.subheader("💹 Sales vs Profit — Margin Health Check")

fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(
    kpis["sales"], kpis["profit"],
    c=kpis["profit_margin_%"], cmap="RdYlGn", s=100, zorder=5
)
for i, row in kpis.iterrows():
    ax.annotate(
        str(row["year_month"]),
        (row["sales"], row["profit"]),
        textcoords="offset points", xytext=(6, 4), fontsize=7, alpha=0.7
    )
plt.colorbar(scatter, ax=ax, label="Profit Margin %")
ax.set_title("Sales vs Profit (Color = Profit Margin)", fontweight='bold')
ax.set_xlabel("Sales ($)")
ax.set_ylabel("Profit ($)")
ax.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig)
plt.close(fig)
st.caption("🔴 Red = high sales but low margin — pricing or discount issue")

# --------------------------------------------------
# Sub-Category Drop Bar Chart
# --------------------------------------------------
st.subheader("🛍️ Sub-Category Sales Drop Detection")

if "sub_category" in df.columns:
    df_copy = df.copy()
    df_copy["year_month"] = pd.to_datetime(df_copy["order_date"]).dt.to_period("M")
    subcat_monthly = (
        df_copy.groupby(["year_month","sub_category"])["sales"]
        .sum().reset_index()
        .sort_values(["sub_category","year_month"])
    )
    subcat_monthly["pct_change"] = (
        subcat_monthly.groupby("sub_category")["sales"].pct_change() * 100
    )
    worst_subcat = (
        subcat_monthly.groupby("sub_category")["pct_change"]
        .min().reset_index().sort_values("pct_change")
    )

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(
        worst_subcat["sub_category"],
        worst_subcat["pct_change"],
        color=['red' if v < -20 else 'orange' if v < 0 else 'green'
               for v in worst_subcat["pct_change"]]
    )
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_title("Worst Month-over-Month Drop per Sub-Category", fontweight='bold')
    ax.set_xlabel("Drop %")
    ax.grid(axis='x', alpha=0.3)
    ax.legend(handles=[
        Patch(facecolor='red',    label='Drop > 20%'),
        Patch(facecolor='orange', label='Drop 0-20%'),
        Patch(facecolor='green',  label='Growth')
    ])
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)
    st.caption("🛍️ Shows which product sub-categories experienced the steepest single-month sales drop — red bars indicate severe declines exceeding 20%.")

# --------------------------------------------------
# Region-Wise Performance
# --------------------------------------------------
st.subheader("🌍 Region-Wise Sales Performance")

if "region" in df.columns:
    df_copy = df.copy()
    df_copy["year_month"] = pd.to_datetime(df_copy["order_date"]).dt.to_period("M")
    region_monthly = (
        df_copy.groupby(["year_month","region"])["sales"]
        .sum().reset_index().sort_values(["region","year_month"])
    )
    region_monthly["pct_change"] = (
        region_monthly.groupby("region")["sales"].pct_change() * 100
    )
    region_total = (
        df_copy.groupby("region")["sales"].sum()
        .reset_index().sort_values("sales", ascending=True)
    )
    worst_region = (
        region_monthly.groupby("region")["pct_change"]
        .min().reset_index().sort_values("pct_change")
    )

    col1, col2 = st.columns(2)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(
        region_total["region"], region_total["sales"],
        color=plt.cm.RdYlGn([i/len(region_total) for i in range(len(region_total))])
    )
    ax.set_title("Total Sales by Region", fontweight='bold')
    ax.set_xlabel("Sales ($)")
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    col1.pyplot(fig)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(
        worst_region["region"], worst_region["pct_change"],
        color=['red' if v < -20 else 'orange' if v < 0 else 'green'
               for v in worst_region["pct_change"]]
    )
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_title("Worst Drop % by Region", fontweight='bold')
    ax.set_xlabel("Drop %")
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    col2.pyplot(fig)
    plt.close(fig)
    st.caption("🌍 Left: total sales contribution by region. Right: each region's worst single-month sales drop, highlighting where performance risk is highest.")

# --------------------------------------------------
# Segment Breakdown
# --------------------------------------------------
st.subheader("👥 Segment-Wise Sales & Profit")

if "segment" in df.columns:
    col1, col2 = st.columns(2)

    segment_sales = df.groupby("segment")["sales"].sum()
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(
        segment_sales, labels=segment_sales.index,
        autopct='%1.1f%%', startangle=140,
        wedgeprops=dict(width=0.5),
        colors=["steelblue", "orange", "green"]
    )
    ax.set_title("Sales by Segment", fontweight='bold')
    col1.pyplot(fig)
    plt.close(fig)

    segment_profit = (
        df.groupby("segment")["profit"].sum()
        .reset_index().sort_values("profit", ascending=True)
    )
    fig, ax = plt.subplots(figsize=(7, 5))
    ax.barh(
        segment_profit["segment"], segment_profit["profit"],
        color=['green' if v > 0 else 'red' for v in segment_profit["profit"]]
    )
    ax.axvline(0, color='black', linewidth=0.8)
    ax.set_title("Profit by Segment", fontweight='bold')
    ax.set_xlabel("Profit ($)")
    ax.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    col2.pyplot(fig)
    plt.close(fig)
    st.caption("👥 Compares sales share and total profit across customer segments (Consumer, Corporate, Home Office) to identify the most and least profitable groups.")

# --------------------------------------------------
# Shipping Days vs Sales Scatter
# --------------------------------------------------
st.subheader("🚚 Shipping Days vs Sales — Health Check")

# 1. CLEAN DATA: Remove any NaNs or Infinities that could crash the SVD solver
clean_kpis = kpis.replace([np.inf, -np.inf], np.nan).dropna(subset=["avg_shipping_days", "sales"])

# 2. VARIANCE CHECK: Polyfit fails if all values are the same (e.g., all shipping days are 0)
if len(clean_kpis) > 1 and clean_kpis["avg_shipping_days"].nunique() > 1:
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        scatter = ax.scatter(
            clean_kpis["avg_shipping_days"], clean_kpis["sales"],
            c=clean_kpis["sales"], cmap="RdYlGn", s=100, zorder=5
        )
        
        # Linear Regression Math
        z = np.polyfit(clean_kpis["avg_shipping_days"], clean_kpis["sales"], 1)
        p = np.poly1d(z)
        
        x_line = np.linspace(clean_kpis["avg_shipping_days"].min(), clean_kpis["avg_shipping_days"].max(), 100)
        ax.plot(x_line, p(x_line), color='red', linestyle='--', linewidth=1.5, label='Trend')
        
        plt.colorbar(scatter, ax=ax, label="Sales ($)")
        ax.set_title("Avg Shipping Days vs Sales", fontweight='bold')
        ax.set_xlabel("Avg Shipping Days")
        ax.set_ylabel("Sales ($)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        plt.close(fig)
    except np.linalg.LinAlgError:
        st.warning("⚠️ Mathematical convergence error: The distribution of your shipping data is too flat to generate a trend line.")
else:
    st.info("ℹ️ Not enough variation in Shipping Days to calculate a trend. This usually happens if 'Ship Date' was missing in your CSV.")

# ==================================================
# SECTION 17 — LIVE ORDER SIMULATION
# Viewer cannot access — Admin and Analyst only
# ==================================================
if role == "Viewer":
    st.info("👁️ Live Simulation is restricted to Admin and Analyst roles")
    st.stop()

st.header("🎲 Live Order Simulation")
st.caption("Fake orders arrive every few seconds — all graphs update in real time")

sc1, sc2, sc3 = st.columns(3)

if sc1.button("▶️ Start Live Simulation"):
    fake_all = sim.generate_fake_orders(n=200)
    st.session_state.sim_all_fake = fake_all
    st.session_state.sim_index    = 0
    st.session_state.sim_running  = True
    st.session_state.live_df      = df.copy()
    st.rerun()

if sc2.button("⏸️ Pause Simulation"):
    st.session_state.sim_running = False

if sc3.button("🔄 Reset Everything"):
    st.session_state.sim_running  = False
    st.session_state.sim_index    = 0
    st.session_state.sim_all_fake = None
    st.session_state.live_df      = None
    st.session_state.anim_done    = False
    st.rerun()

# --------------------------------------------------
# LIVE SIMULATION LOOP
# --------------------------------------------------
if st.session_state.sim_running and st.session_state.sim_all_fake is not None:

    idx      = st.session_state.sim_index
    all_fake = st.session_state.sim_all_fake

    if idx < len(all_fake):

        # Add next 3 orders
        batch_size = 3
        end_idx    = min(idx + batch_size, len(all_fake))
        new_orders = all_fake.iloc[idx:end_idx]

        # Merge into live dataframe
        st.session_state.live_df = pd.concat(
            [st.session_state.live_df, new_orders],
            ignore_index=True
        )
        st.session_state.sim_index = end_idx

        # Recalculate KPIs
        live_kpis   = get_kpis(st.session_state.live_df)
        live_latest = live_kpis.iloc[-1]
        live_str    = live_kpis["year_month"].astype(str)
        total_new   = st.session_state.sim_index

        # Progress bar
        st.progress(
            total_new / len(all_fake),
            text=f"🔴 LIVE — {total_new} new orders added"
        )

        # Live KPI metrics — compare vs original
        st.subheader("📊 Live KPI Metrics")
        orig_kpis = get_kpis(df)
        orig_last = orig_kpis.iloc[-1]

        lc1, lc2, lc3, lc4, lc5 = st.columns(5)
        lc1.metric("💰 Sales",
                   f"${live_latest['sales']:,.0f}",
                   f"{((live_latest['sales']-orig_last['sales'])/orig_last['sales']*100):+.1f}%")
        lc2.metric("📈 Profit",
                   f"${live_latest['profit']:,.0f}",
                   f"{((live_latest['profit']-orig_last['profit'])/orig_last['profit']*100):+.1f}%")
        lc3.metric("📦 Orders",
                   f"{live_latest['orders']:,.0f}",
                   f"{((live_latest['orders']-orig_last['orders'])/orig_last['orders']*100):+.1f}%")
        lc4.metric("📊 Margin",
                   f"{live_latest['profit_margin_%']:,.1f}%",
                   f"{(live_latest['profit_margin_%']-orig_last['profit_margin_%']):+.1f}%")
        lc5.metric("🚚 Shipping",
                   f"{live_latest['avg_shipping_days']:,.1f}d",
                   f"{(live_latest['avg_shipping_days']-orig_last['avg_shipping_days']):+.1f}")

        # Live KPI alerts
        live_alerts = []
        if live_latest['sales']             < sales_threshold:    live_alerts.append("⚠️ Sales below threshold")
        if live_latest['profit']            < profit_threshold:   live_alerts.append("⚠️ Profit below threshold")
        if live_latest['orders']            < orders_threshold:   live_alerts.append("⚠️ Orders below threshold")
        if live_latest['profit_margin_%']   < margin_threshold:   live_alerts.append("⚠️ Margin below threshold")
        if live_latest['avg_shipping_days'] > shipping_threshold: live_alerts.append("⚠️ Shipping too slow")

        if live_alerts:
            for a in live_alerts:
                st.error(a)
        else:
            st.success("✅ All KPIs healthy")

        # Live 6-panel chart
        st.subheader("📈 Live KPI Charts — Updating in Real Time")
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(
            f"🔴 LIVE DASHBOARD — {total_new} new orders added",
            fontsize=16, fontweight='bold', color='red'
        )

        def live_chart(ax, x, y, title, ylabel, color):
            ax.plot(x, y, color=color, linewidth=2, marker='o', markersize=3)
            ax.fill_between(x, y, alpha=0.2, color=color)
            # Red dot on latest point
            ax.scatter([x.iloc[-1]], [y.iloc[-1]], color='red', s=80, zorder=5)
            # Red dots on drop points
            drop_mask = y.diff() < 0
            if drop_mask.any():
                ax.scatter(x[drop_mask], y[drop_mask],
                           color='red', s=40, zorder=4, alpha=0.5)
            ax.set_title(title, fontweight='bold')
            ax.set_ylabel(ylabel)
            ax.tick_params(axis='x', rotation=45, labelsize=6)
            ax.grid(True, alpha=0.3)

        live_chart(axes[0,0], live_str, live_kpis["sales"],             "💰 Sales",         "Sales ($)",  "steelblue")
        live_chart(axes[0,1], live_str, live_kpis["profit"],            "📈 Profit",        "Profit ($)", "green")
        live_chart(axes[0,2], live_str, live_kpis["orders"],            "📦 Orders",        "Orders",     "orange")
        live_chart(axes[1,0], live_str, live_kpis["profit_margin_%"],   "📊 Margin %",      "Margin (%)", "purple")
        live_chart(axes[1,1], live_str, live_kpis["avg_shipping_days"], "🚚 Shipping Days", "Days",       "brown")

        # Last panel: new orders bar chart
        new_daily = new_orders.groupby("order_date")["sales"].sum().reset_index()
        if not new_daily.empty:
            axes[1,2].bar(
                new_daily["order_date"].astype(str),
                new_daily["sales"],
                color='red', alpha=0.7
            )
            axes[1,2].set_title("🔴 New Orders Just Arrived", fontweight='bold')
            axes[1,2].set_ylabel("Sales ($)")
            axes[1,2].tick_params(axis='x', rotation=45, labelsize=6)
            axes[1,2].grid(axis='y', alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

        # Latest orders table
        st.subheader("📋 Latest Arriving Orders")
        st.dataframe(
            new_orders[[
                "order_id", "order_date", "sales", "profit",
                "category", "region", "segment"
            ]],
            hide_index=True
        )

        # Wait then rerun to show next batch
        time.sleep(sim_delay)
        st.rerun()

    else:
        # All orders done — loop back with new batch
        st.session_state.sim_index = 0
        fake_all = sim.generate_fake_orders(n=200)
        st.session_state.sim_all_fake = fake_all
        st.info("🔄 Generating new batch of orders...")
        time.sleep(1)
        st.rerun()

else:
    if not st.session_state.sim_running:
        st.info(
            "👆 Click **▶️ Start Live Simulation** to start, "
            "or click **▶️ Play History** above to watch history "
            "and then auto-start simulation."
        )