# app.py
"""
FinRisk Pro – Data-Driven Risk Profiling for Finance
Main Streamlit Application
"""

import os
import sys
import warnings

warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import streamlit as st

# ── Path setup ───────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.constants import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION, DEFAULT_WEIGHTS,
    RISK_COLORS, CREDIT_GRADE_COLORS, DECISION_COLORS,
)
from src.data_loader import load_customer_data, load_customer_data_from_upload
from src.risk_engine import RiskEngine
from src.utils import (
    get_credit_grade, get_risk_category, get_risk_color,
    get_risk_icon, get_decision, df_to_csv_bytes, df_to_excel_bytes,
    fmt_currency,
)
from src.visualization import (
    create_gauge_chart, contribution_chart, radar_chart,
    pie_chart, histogram_chart, correlation_heatmap,
    top_risk_chart, location_risk_chart, scatter_score_credit,
)
from src.preprocessing import compute_risk_factors

# ─────────────────────────────────────────────────────────────────
# Page Config
# ─────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title=f"{APP_TITLE} – Risk Profiling",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────────────────────────

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600;700&family=IBM+Plex+Sans:wght@300;400;500;600;700&display=swap');

  html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background-color: #060d1a !important;
    color: #e2e8f0 !important;
  }

  /* Header */
  .hero-header {
    background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
  }
  .hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 50%, rgba(56,189,248,0.06) 0%, transparent 60%),
                radial-gradient(circle at 70% 50%, rgba(124,58,237,0.06) 0%, transparent 60%);
    pointer-events: none;
  }
  .hero-title {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #38bdf8, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0 0 0.3rem 0;
  }
  .hero-sub {
    font-size: 0.95rem;
    color: #64748b;
    font-family: 'IBM Plex Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .hero-badge {
    display: inline-block;
    background: rgba(56,189,248,0.1);
    border: 1px solid rgba(56,189,248,0.3);
    color: #38bdf8;
    padding: 2px 10px;
    border-radius: 20px;
    font-size: 0.72rem;
    font-family: 'IBM Plex Mono', monospace;
    margin-left: 10px;
    vertical-align: middle;
  }

  /* KPI Cards */
  .kpi-card {
    background: linear-gradient(145deg, #0f172a, #1a2742);
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 1.2rem 1.4rem;
    text-align: center;
    position: relative;
    overflow: hidden;
    transition: border-color 0.3s ease;
  }
  .kpi-card:hover { border-color: #38bdf8; }
  .kpi-label {
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    color: #64748b;
    font-family: 'IBM Plex Mono', monospace;
    margin-bottom: 0.3rem;
  }
  .kpi-value {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'IBM Plex Mono', monospace;
    line-height: 1.1;
  }
  .kpi-sub {
    font-size: 0.75rem;
    color: #475569;
    margin-top: 0.2rem;
  }

  /* Section headers */
  .section-header {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #38bdf8;
    border-left: 3px solid #38bdf8;
    padding-left: 10px;
    margin: 1.5rem 0 1rem 0;
  }

  /* Risk band banner */
  .risk-banner {
    border-radius: 10px;
    padding: 0.8rem 1.2rem;
    font-family: 'IBM Plex Mono', monospace;
    font-weight: 600;
    font-size: 1rem;
    text-align: center;
    margin-bottom: 1rem;
    letter-spacing: 0.05em;
  }

  /* Decision card */
  .decision-card {
    border-radius: 12px;
    padding: 1.5rem;
    text-align: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    letter-spacing: 0.03em;
    border: 2px solid;
    margin-top: 0.5rem;
  }

  /* Explainability */
  .explain-item {
    background: rgba(30,41,59,0.6);
    border-left: 3px solid;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.4rem;
    font-size: 0.87rem;
  }
  .rule-item {
    background: rgba(124,58,237,0.08);
    border-left: 3px solid #7c3aed;
    border-radius: 6px;
    padding: 0.6rem 1rem;
    margin-bottom: 0.4rem;
    font-size: 0.87rem;
    font-family: 'IBM Plex Mono', monospace;
  }

  /* Sidebar */
  section[data-testid="stSidebar"] {
    background: #0a1628 !important;
    border-right: 1px solid #1e3a5f;
  }

  /* Streamlit overrides */
  .stSlider > div > div { background: #1e3a5f; }
  div[data-testid="metric-container"] {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 10px;
    padding: 0.8rem;
  }
  .stDataFrame { border: 1px solid #1e3a5f; border-radius: 8px; }
  .stSelectbox > div > div { background: #0f172a !important; border-color: #1e3a5f !important; }
  .stButton > button {
    background: linear-gradient(135deg, #1e40af, #7c3aed) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.5rem 1.2rem !important;
  }
  .stButton > button:hover { opacity: 0.85 !important; }

  /* Chart containers */
  .chart-box {
    background: #0f172a;
    border: 1px solid #1e3a5f;
    border-radius: 12px;
    padding: 0.5rem;
    margin-bottom: 1rem;
  }

  /* Alert box */
  .alert-box {
    background: rgba(239,68,68,0.08);
    border: 1px solid rgba(239,68,68,0.3);
    border-radius: 8px;
    padding: 0.8rem 1.2rem;
    color: #fca5a5;
    font-size: 0.85rem;
  }

  /* Hide Streamlit default elements */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────
# Session State Init
# ─────────────────────────────────────────────────────────────────

def init_session():
    if "weights" not in st.session_state:
        st.session_state.weights = DEFAULT_WEIGHTS.copy()
    if "df" not in st.session_state:
        st.session_state.df = None
    if "scored_df" not in st.session_state:
        st.session_state.scored_df = None
    if "engine" not in st.session_state:
        st.session_state.engine = RiskEngine(st.session_state.weights)


init_session()


# ─────────────────────────────────────────────────────────────────
# Load Default Data
# ─────────────────────────────────────────────────────────────────

@st.cache_data
def load_default_data():
    path = os.path.join(ROOT, "data", "sample_customers.csv")
    return load_customer_data(path)


# ─────────────────────────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style='text-align:center;padding:1rem 0 0.5rem'>
      <div style='font-family:IBM Plex Mono,monospace;font-size:1.4rem;font-weight:700;
                  background:linear-gradient(135deg,#38bdf8,#818cf8);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>
        🛡️ FinRisk Pro
      </div>
      <div style='font-size:0.7rem;color:#475569;letter-spacing:0.1em;'>v{}</div>
    </div>
    """.format(APP_VERSION), unsafe_allow_html=True)

    st.divider()

    # ── Data Upload ────────────────────────────────────────────────
    st.markdown("**📂 Data Source**")
    uploaded = st.file_uploader(
        "Upload Customer CSV", type=["csv"],
        help="Upload a CSV file with customer financial data",
        label_visibility="collapsed",
    )

    use_sample = st.button("📊 Load Sample Data (120 Customers)", use_container_width=True)

    if uploaded:
        with st.status("🚀 Processing Uploaded Data...", expanded=True) as status:
            try:
                st.write("Reading CSV file...")
                df_raw = load_customer_data_from_upload(uploaded)
                st.session_state.df = df_raw
                
                st.write("Initializing Risk Engine...")
                st.session_state.engine = RiskEngine(st.session_state.weights)
                
                st.write("Batch scoring customers...")
                st.session_state.scored_df = st.session_state.engine.score_all(df_raw)
                
                status.update(label="✅ Data Processed Successfully!", state="complete", expanded=False)
                st.toast(f"Loaded {len(df_raw)} customers", icon="✅")
            except Exception as e:
                status.update(label="❌ Processing Failed", state="error")
                st.error(f"Error: {e}")

    if use_sample:
        with st.spinner("Loading sample dataset..."):
            st.session_state.df = load_default_data()
            st.session_state.scored_df = st.session_state.engine.score_all(st.session_state.df)
            st.success("✅ Sample data loaded!")

    # REMOVED AUTO-LOAD LOGIC HERE

    df = st.session_state.df

    st.divider()

    # ── Customer Selector ──────────────────────────────────────────
    if df is not None:
        st.markdown("**👤 Select Customer**")
        customer_names = df["name"].tolist()
        selected_name = st.selectbox(
            "Customer", options=customer_names, label_visibility="collapsed"
        )
        selected_row = df[df["name"] == selected_name].iloc[0]
    else:
        st.info("Please upload data to select a customer.")
        selected_row = None

    if df is not None:
        st.divider()
        # ── Weight Sliders ─────────────────────────────────────────────
        st.markdown("**⚖️ Adjust Risk Weights**")

        weight_labels = {
            "credit_score":     "Credit Score",
            "payment_history":  "Payment History",
            "monthly_income":   "Monthly Income",
            "debt_ratio":       "Debt Ratio",
            "existing_loans":   "Existing Loans",
            "employment_years": "Employment",
            "fraud_alerts":     "Fraud Alerts",
            "security_flags":   "Security Flags",
        }

        new_weights = {}
        for factor, label in weight_labels.items():
            new_weights[factor] = st.slider(
                label,
                min_value=0.0,
                max_value=0.5,
                value=float(st.session_state.weights.get(factor, DEFAULT_WEIGHTS[factor])),
                step=0.01,
                format="%.2f",
            )

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.weights = DEFAULT_WEIGHTS.copy()
                st.session_state.scored_df = None
                st.rerun()
        with col_r2:
            if st.button("✅ Apply", use_container_width=True):
                st.session_state.weights = new_weights
                st.session_state.engine = RiskEngine(new_weights)
                st.session_state.scored_df = None

        st.divider()

        # ── Filter Controls ────────────────────────────────────────────
        st.markdown("**🔍 Dataset Filters**")
        filter_risk = st.multiselect(
            "Risk Category",
            options=["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
            default=["Low Risk", "Medium Risk", "High Risk", "Critical Risk"],
        )

        st.divider()

        # ── Export ─────────────────────────────────────────────────────
        st.markdown("**📥 Export Results**")
        if st.session_state.scored_df is not None:
            scored = st.session_state.scored_df
            csv_data = df_to_csv_bytes(scored)
            excel_data = df_to_excel_bytes(scored)

            st.download_button(
                "⬇️ Download CSV",
                data=csv_data,
                file_name="risk_report.csv",
                mime="text/csv",
                use_container_width=True,
            )
            st.download_button(
                "⬇️ Download Excel",
                data=excel_data,
                file_name="risk_report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
            )
    else:
        # Show a helpful tip when no data is loaded
        st.info("💡 Tip: Use the 'Load Sample Data' button above to quickly explore the dashboard features.")
        filter_risk = []


# ── Data Processing ─────────────────────────────────────────────

if df is not None:
    engine = st.session_state.engine

    # Ensure we have scored data
    if st.session_state.scored_df is None:
        with st.spinner("Analyzing portfolio risk..."):
            st.session_state.scored_df = engine.score_all(df)

    scored_df = st.session_state.scored_df

    # Individual customer result
    result = engine.score_customer(selected_row)

    # Apply filters
    if filter_risk:
        filtered_df = scored_df[scored_df["risk_category"].isin(filter_risk)]
    else:
        filtered_df = scored_df
else:
    scored_df = None
    result = None
    filtered_df = None


# ─────────────────────────────────────────────────────────────────
# Hero Header
# ─────────────────────────────────────────────────────────────────

# ── Main UI Rendering ───────────────────────────────────────────

if df is None:
    # Landing Page / Empty State
    st.markdown("""
    <div style='text-align:center;padding:5rem 2rem;background:#0f172a;border-radius:20px;border:1px dashed #1e3a5f;margin-top:2rem;'>
        <div style='font-size:4rem;margin-bottom:1rem;'>🛡️</div>
        <h2 style='font-family:IBM Plex Mono,monospace;color:#38bdf8;'>Ready to Analyze Risk?</h2>
        <p style='color:#64748b;max-width:500px;margin:0 auto 2rem;'>
            Upload your customer data CSV or load the sample dataset from the sidebar to begin 
            the real-time risk profiling and financial health analysis.
        </p>
        <div style='display:flex;justify-content:center;gap:1rem;'>
            <div style='background:rgba(56,189,248,0.1);padding:1rem;border-radius:12px;border:1px solid #1e3a5f;width:200px;'>
                <div style='font-size:0.7rem;color:#38bdf8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;'>Step 1</div>
                <div style='font-size:0.9rem;'>Upload Customer CSV</div>
            </div>
            <div style='background:rgba(56,189,248,0.1);padding:1rem;border-radius:12px;border:1px solid #1e3a5f;width:200px;'>
                <div style='font-size:0.7rem;color:#38bdf8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;'>Step 2</div>
                <div style='font-size:0.9rem;'>Process & Score</div>
            </div>
            <div style='background:rgba(56,189,248,0.1);padding:1rem;border-radius:12px;border:1px solid #1e3a5f;width:200px;'>
                <div style='font-size:0.7rem;color:#38bdf8;text-transform:uppercase;letter-spacing:0.1em;margin-bottom:0.5rem;'>Step 3</div>
                <div style='font-size:0.9rem;'>Explore Analytics</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # ── Hero Header ─────────────────────────────────────────────
    st.markdown(f"""
    <div class="hero-header">
      <div class="hero-title">🛡️ {APP_TITLE}
        <span class="hero-badge">v{APP_VERSION}</span>
      </div>
      <div class="hero-sub">{APP_SUBTITLE} · Cyber Security + Finance + Analytics</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Risk Banner for Selected Customer ──────────────────────────
    banner_color = result.risk_color
    banner_bg    = f"rgba{tuple(int(banner_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.12,)}"

    st.markdown(f"""
    <div class="risk-banner" style="background:{banner_bg};border:1px solid {banner_color}80;color:{banner_color};">
      {result.risk_icon} RISK MONITORING ACTIVE &nbsp;|&nbsp; Customer: <strong>{result.name}</strong>
      &nbsp;|&nbsp; Score: <strong>{result.final_score}</strong> / 100
      &nbsp;|&nbsp; Status: <strong>{result.risk_category}</strong>
    </div>
    """, unsafe_allow_html=True)

    # ── Dataset Overview KPIs ──────────────────────────────────────
    st.markdown('<div class="section-header">Dataset Overview</div>', unsafe_allow_html=True)

    total = len(scored_df)
    critical = int((scored_df["risk_category"] == "Critical Risk").sum())
    high      = int((scored_df["risk_category"] == "High Risk").sum())
    medium    = int((scored_df["risk_category"] == "Medium Risk").sum())
    low       = int((scored_df["risk_category"] == "Low Risk").sum())
    avg_score = scored_df["final_score"].mean()

    ov1, ov2, ov3, ov4, ov5 = st.columns(5)
    with ov1:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Total Customers</div>
            <div class="kpi-value" style="color:#38bdf8">{total}</div>
            <div class="kpi-sub">in dataset</div>
        </div>""", unsafe_allow_html=True)
    with ov2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Avg Risk Score</div>
            <div class="kpi-value" style="color:#f59e0b">{avg_score:.1f}</div>
            <div class="kpi-sub">out of 100</div>
        </div>""", unsafe_allow_html=True)
    with ov3:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Critical Risk</div>
            <div class="kpi-value" style="color:#7c3aed">{critical}</div>
            <div class="kpi-sub">{100*critical//total}% of customers</div>
        </div>""", unsafe_allow_html=True)
    with ov4:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">High Risk</div>
            <div class="kpi-value" style="color:#ef4444">{high}</div>
            <div class="kpi-sub">{100*high//total}% of customers</div>
        </div>""", unsafe_allow_html=True)
    with ov5:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Low Risk</div>
            <div class="kpi-value" style="color:#22c55e">{low}</div>
            <div class="kpi-sub">{100*low//total}% of customers</div>
        </div>""", unsafe_allow_html=True)

    # ── Selected Customer KPI Cards ────────────────────────────────
    st.markdown('<div class="section-header">Customer Risk Profile · ' + result.name + '</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        score_color = result.risk_color
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Final Risk Score</div>
            <div class="kpi-value" style="color:{score_color}">{result.final_score}</div>
            <div class="kpi-sub">Base: {result.base_score:.1f} | Adj: {result.adjustment:+.1f}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Risk Category</div>
            <div class="kpi-value" style="color:{result.risk_color};font-size:1.2rem;margin-top:0.3rem">
              {result.risk_icon} {result.risk_category}
            </div>
            <div class="kpi-sub">{RISK_COLORS[result.risk_category]}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        grade_color = CREDIT_GRADE_COLORS.get(result.credit_grade, "#94a3b8")
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Credit Grade</div>
            <div class="kpi-value" style="color:{grade_color}">{result.credit_grade}</div>
            <div class="kpi-sub">Score: {int(selected_row['credit_score'])}</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        fraud_val = int(selected_row.get("fraud_alerts", 0))
        fraud_color = "#ef4444" if fraud_val > 0 else "#22c55e"
        fraud_label = "⚠️ FLAGGED" if fraud_val > 0 else "✅ CLEAN"
        st.markdown(f"""<div class="kpi-card">
            <div class="kpi-label">Fraud Status</div>
            <div class="kpi-value" style="color:{fraud_color};font-size:1.1rem;margin-top:0.3rem">
              {fraud_label}
            </div>
            <div class="kpi-sub">{fraud_val} alert(s) on record</div>
        </div>""", unsafe_allow_html=True)

    # ── Gauge + Factor Charts ──────────────────────────────────────
    st.markdown('<div class="section-header">Risk Analysis Charts</div>', unsafe_allow_html=True)
    gauge_col, radar_col = st.columns([1, 1])
    with gauge_col:
        st.plotly_chart(create_gauge_chart(result.final_score, result.risk_category), use_container_width=True)
    with radar_col:
        factors_raw = compute_risk_factors(selected_row)
        st.plotly_chart(radar_chart(factors_raw, name=result.name), use_container_width=True)
    st.plotly_chart(contribution_chart(result.factor_contributions), use_container_width=True)

    # ── Explainability Panel ────────────────────────────────────────
    st.markdown('<div class="section-header">Explainability Panel</div>', unsafe_allow_html=True)
    ex1, ex2, ex3 = st.columns(3)
    with ex1:
        st.markdown("**📌 Risk Drivers** *(Factors increasing risk)*")
        for d in result.risk_drivers:
            st.markdown(f'<div class="explain-item" style="border-color:#ef4444">{d}</div>', unsafe_allow_html=True)
    with ex2:
        st.markdown("**✅ Risk Reducers** *(Factors reducing risk)*")
        for r_ in result.risk_reducers:
            st.markdown(f'<div class="explain-item" style="border-color:#22c55e">{r_}</div>', unsafe_allow_html=True)
    with ex3:
        st.markdown("**⚡ Business Rules Triggered**")
        if result.rules_triggered:
            for rule in result.rules_triggered:
                st.markdown(f'<div class="rule-item">{rule}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="rule-item" style="border-color:#22c55e;color:#86efac">✅ No business rules triggered</div>', unsafe_allow_html=True)

    st.markdown("**📊 Factor Contribution Table**")
    contrib_df = engine.get_contribution_table(selected_row)
    st.dataframe(contrib_df.style.background_gradient(subset=["Contribution"], cmap="RdYlGn_r"), use_container_width=True, hide_index=True)

    # ── Decision Engine ────────────────────────────────────────────
    st.markdown('<div class="section-header">Decision Engine</div>', unsafe_allow_html=True)
    decision_color = DECISION_COLORS.get(result.decision, "#64748b")
    dec_bg = f"rgba{tuple(int(decision_color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4)) + (0.12,)}"
    d1, d2, d3 = st.columns([1.5, 1, 1])
    with d1:
        st.markdown(f'<div class="decision-card" style="border-color:{decision_color};background:{dec_bg};color:{decision_color};">{result.decision}</div>', unsafe_allow_html=True)
    with d2:
        st.metric("Monthly Income", fmt_currency(selected_row["monthly_income"]))
        st.metric("Debt Ratio", f"{selected_row['debt_ratio']:.1f}%")
    with d3:
        st.metric("Employment Years", f"{selected_row['employment_years']:.0f} yrs")
        st.metric("Account Age", f"{selected_row['account_age_months']:.0f} months")

    # ── Portfolio Analytics ────────────────────────────────────────
    st.markdown('<div class="section-header">Portfolio Analytics</div>', unsafe_allow_html=True)
    pie_col, hist_col = st.columns(2)
    with pie_col:
        st.plotly_chart(pie_chart(scored_df), use_container_width=True)
    with hist_col:
        st.plotly_chart(histogram_chart(scored_df), use_container_width=True)
    st.plotly_chart(top_risk_chart(scored_df, top_n=15), use_container_width=True)
    scatter_col, loc_col = st.columns(2)
    with scatter_col:
        st.plotly_chart(scatter_score_credit(scored_df), use_container_width=True)
    with loc_col:
        st.plotly_chart(location_risk_chart(scored_df), use_container_width=True)
    st.plotly_chart(correlation_heatmap(scored_df), use_container_width=True)

    # ── Customer Data Table ────────────────────────────────────────
    st.markdown('<div class="section-header">Customer Data Table</div>', unsafe_allow_html=True)
    search_term = st.text_input("🔍 Search by name or location", placeholder="Type to filter...", label_visibility="collapsed")
    sort_by = st.selectbox("Sort by", options=["final_score", "credit_score", "monthly_income", "debt_ratio", "name"], index=0)
    sort_asc = st.checkbox("Ascending", value=False)

    display_cols = ["customer_id", "name", "age", "credit_score", "payment_history", "monthly_income", "debt_ratio", "fraud_alerts", "security_flags", "final_score", "risk_category", "credit_grade", "decision"]
    available_cols = [c for c in display_cols if c in filtered_df.columns]
    table_df = filtered_df[available_cols].copy()
    if search_term:
        mask = (table_df["name"].str.contains(search_term, case=False, na=False) | (filtered_df["location"].str.contains(search_term, case=False, na=False) if "location" in filtered_df.columns else pd.Series([False]*len(table_df))))
        table_df = table_df[mask]
    if sort_by in table_df.columns:
        table_df = table_df.sort_values(sort_by, ascending=sort_asc)

    st.dataframe(table_df.style.apply(lambda row: [f"background-color: {RISK_COLORS.get(row.get('risk_category', ''), '')}22"] * len(row), axis=1), use_container_width=True, height=420, hide_index=True)
    st.caption(f"Showing {len(table_df)} of {len(scored_df)} customers · FinRisk Pro v{APP_VERSION}")

# ── Footer ───────────────────────────────────────────────────────
st.markdown("""
<hr style="border:none;border-top:1px solid #1e3a5f;margin:2rem 0 1rem"/>
<div style='text-align:center;font-size:0.72rem;color:#334155;font-family:IBM Plex Mono,monospace;'>
  FinRisk Pro · Data-Driven Risk Profiling · Python · Pandas · Streamlit · Plotly<br>
  Built for: Banks · Fintech · Insurance · Cybersecurity · NBFC
</div>
""", unsafe_allow_html=True)
