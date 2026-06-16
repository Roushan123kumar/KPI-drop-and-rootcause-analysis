# ==================================================
# app.py — ENTRY POINT
# Flow: Login → Upload Dataset → App
# ==================================================
import streamlit as st
import tempfile
import os
import pandas as pd

# 1. Page Configuration (Must be the first Streamlit command)
st.set_page_config(
    page_title="KPI Intelligence System",
    page_icon="📊",
    layout="wide"
)

# --------------------------------------------------
# USER STORE
# --------------------------------------------------
USERS = {
    "admin":   {"password": "admin123",   "role": "Admin"},
    
}

# --------------------------------------------------
# HELPERS
# --------------------------------------------------
from src.data_preparation import DataPreparation

@st.cache_data
def load_default_data():
    """Loads the core demo dataset from the local path."""
    prep = DataPreparation("data/train_prepared.csv")
    return prep.prepare()

def init_session():
    """Initializes the Global Memory (Session State)."""
    defaults = {
        "logged_in": False,
        "role": None,
        "username": None,
        "dataset_ready": False,
        "main_df": None,
        "last_uploaded": None,
        "sim_running": False,
        "sim_index": 0,
        "anim_running": False,
        "anim_done": False,
        "live_df": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Initialize the state immediately
init_session()

# ==================================================
# STAGE 0 — REDIRECTION GUARD
# ==================================================
# If user is logged in AND data is already in memory, skip straight to the app.
if st.session_state.logged_in and st.session_state.dataset_ready and st.session_state.main_df is not None:
    st.switch_page("pages/1_Live_Dashboard.py")

# ==================================================
# STAGE 1 — LOGIN
# ==================================================
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align:center'>📊 KPI Intelligence System</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Login to access your analytics dashboard</p>", unsafe_allow_html=True)
    st.divider()

    col_l, col_m, col_r = st.columns([1, 1.2, 1])
    with col_m:
        st.subheader(" Login")
        username = st.text_input("Username", placeholder="admin")
        password = st.text_input("Password", type="password")

        if st.button("Login →", use_container_width=True, type="primary"):
            user = USERS.get(username.lower())
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username  = username
                st.session_state.role      = user["role"]
                st.rerun()
            else:
                st.error(" Invalid username or password")

        st.caption("Demo credentials — admin/admin123 ")
    st.stop()

# ==================================================
# STAGE 2 — DATASET SETUP
# ==================================================
if not st.session_state.dataset_ready:
    st.markdown(f"<h1 style='text-align:center'> Welcome, {st.session_state.username}!</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;color:gray'>Choose the data you want to analyze across the entire app.</p>", unsafe_allow_html=True)
    st.divider()

    col_l, col_m, col_r = st.columns([1, 2, 1])
    with col_m:
        st.subheader(" Dataset Setup")

        choice = st.radio(
            "Which dataset would you like to use?",
            [" Use the built-in demo dataset", "📤 Upload my own CSV / Excel file"],
            index=0
        )

        if choice == "📤 Upload my own CSV / Excel file":
            uploaded = st.file_uploader(
                "Upload your dataset",
                type=["csv", "xlsx", "xls"],
                help="Requires: order_date, sales, profit, orders (standard business columns)."
            )

            col_a, col_b = st.columns(2)

            if uploaded is not None:
                st.info(f" File ready: **{uploaded.name}**")

                if col_a.button(" Load & Open Dashboard", use_container_width=True, type="primary"):
                    with st.spinner("Processing your custom dataset..."):
                        try:
                            # Save to temp file to allow pandas/DataPreparation to read it
                            suffix = os.path.splitext(uploaded.name)[1]
                            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                                tmp.write(uploaded.getvalue())
                                tmp_path = tmp.name
                            
                            # Standardize and save to Global Memory
                            prep = DataPreparation(tmp_path)
                            st.session_state.main_df       = prep.prepare()
                            st.session_state.last_uploaded = uploaded.name
                            st.session_state.dataset_ready = True
                            
                            # Clean up temp file
                            if os.path.exists(tmp_path):
                                os.remove(tmp_path)
                            
                            st.success(" Dataset loaded into memory!")
                            st.rerun()
                        except Exception as e:
                            st.error(f" Error: {e}")

            if col_b.button("Use demo instead", use_container_width=True):
                st.session_state.main_df       = load_default_data()
                st.session_state.last_uploaded  = "Demo Dataset (data/train_prepared.csv)"
                st.session_state.dataset_ready  = True
                st.rerun()

        else:  # built-in demo choice
            if st.button(" Open Dashboard", use_container_width=True, type="primary"):
                with st.spinner("Loading demo dataset..."):
                    st.session_state.main_df       = load_default_data()
                    st.session_state.last_uploaded  = "Demo Dataset"
                    st.session_state.dataset_ready  = True
                st.rerun()

        st.divider()
        if st.button("Logout", use_container_width=True):
            # Full state wipe
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    st.stop()

# ==================================================
# STAGE 3 — REDIRECT TO APP
# ==================================================
# This only executes if logged_in=True and dataset_ready=True
st.switch_page("pages/1_Live_Dashboard.py")