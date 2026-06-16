# ==================================================
# PAGE 4 — ADMIN PANEL
# Refactored for Global State & Data Management
# ==================================================
import streamlit as st
import pandas as pd
import tempfile
import os

# Internal Engine Imports
from src.data_preparation  import DataPreparation
from src.comparison_engine import ComparisonEngine
from src.alert_engine      import AlertEngine
from src.kpi_engine        import KPIEngine

# Try to import logger, fallback to dummy if not found
try:
    from src.audit_logger import log_event
except Exception:
    def log_event(*args, **kwargs): pass

# ==================================================
# AUTH + ROLE GUARD
# ==================================================
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("⚠️ Please login first")
    st.switch_page("app.py")

role = st.session_state.get("role", "Viewer")

# Only Admins can access this page
if role != "Admin":
    st.error("🔒 Access Denied: This page is restricted to Administrators.")
    st.stop()

# ==================================================
# DATA SOURCE — SINGLE SOURCE OF TRUTH
# ==================================================
# Pull the active dataset from global memory
if st.session_state.get("main_df") is None:
    st.warning("⚠️ No dataset detected. Please load data on the Dashboard or Setup page.")
    st.stop()

df = st.session_state.main_df

st.title("⚙️ Admin Control Panel")
st.sidebar.write(f"👤 **{st.session_state.username}** (Administrator)")

# Dataset badge
if st.session_state.get("last_uploaded"):
    st.sidebar.success(f"📄 Active: {st.session_state.last_uploaded}")
else:
    st.sidebar.info("📄 Active: Demo data")

if st.sidebar.button("🚪 Logout"):
    log_event(role, "Logout", "Admin logged out")
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.switch_page("app.py")

# ==================================================
# SECTION 1: GLOBAL DATA MANAGEMENT
# ==================================================
st.header("📂 Global Dataset Override")
st.markdown("Replacing the dataset here will update **all pages** (Analysis, Recommendations, Dashboard) instantly.")

# Robust file uploader for messy data
new_file = st.file_uploader("Upload new CSV or Excel", type=["csv", "xlsx", "xls"])

if new_file is not None:
    # Check if this is a new file to avoid redundant re-runs
    if st.session_state.get("last_uploaded") != new_file.name:
        with st.spinner("Processing & Standardizing Data..."):
            try:
                suffix = os.path.splitext(new_file.name)[1]
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(new_file.getvalue())
                    tmp_path = tmp.name

                # Use DataPreparation to handle missing cells/columns
                prep = DataPreparation(tmp_path)
                st.session_state.main_df = prep.prepare()
                st.session_state.last_uploaded = new_file.name
                
                log_event(role, "Dataset Override", f"File: {new_file.name}")
                st.success(f"✅ Successfully updated global memory with {new_file.name}")
                
                # Force UI propagation across all pages
                st.rerun() 
            except Exception as e:
                st.error(f"❌ Critical processing error: {e}")

# ==================================================
# SECTION 2: EMAIL ALERT CONFIGURATION
# ==================================================
st.header("📧 Email Alert Settings")
col1, col2 = st.columns(2)

# These values can be tied to session_state if you want them to persist
sender_email = col1.text_input("Sender Gmail", value="pro411937@gmail.com")
app_password = col1.text_input("App Password", value="qzhlzmcwabyznztl", type="password")
target_email = col2.text_input("Alert Receiver", value="roushanjsr2033@gmail.com")

if st.button("📤 Send Test Alert"):
    alert_engine = AlertEngine({
        "email": {"sender": sender_email, "password": app_password, "receiver": target_email}
    })
    success, msg = alert_engine.send_email("📊 System Test", "Admin triggered a manual test alert.")
    if success:
        st.success("✅ Test email sent!")
    else:
        st.error(f"❌ Failed: {msg}")

# ==================================================
# SECTION 3: SYSTEM AUDIT LOGS
# ==================================================
st.header("📜 System Audit Logs")
try:
    if os.path.exists("logs/audit_logs.csv"):
        logs_df = pd.read_csv("logs/audit_logs.csv")
        st.dataframe(logs_df.sort_values("timestamp", ascending=False), hide_index=True)
        
        if st.button("🗑️ Clear All Logs"):
            os.remove("logs/audit_logs.csv")
            st.success("Logs cleared.")
            st.rerun()
    else:
        st.info("ℹ️ No logs found yet.")
except Exception as e:
    st.caption("Log system currently unavailable.")

# ==================================================
# SECTION 4: ACTIVE DATA PREVIEW
# ==================================================
st.header("📊 Active Data Snapshot")
st.caption("A quick look at the 'Single Source of Truth' currently in memory.")

c1, c2, c3 = st.columns(3)
c1.metric("Rows", len(df))
c2.metric("Columns", len(df.columns))
c3.metric("Memory Source", "Global State" if st.session_state.get("dataset_ready") else "Local File")

st.dataframe(df.head(5), hide_index=True)