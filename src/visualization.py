# src/visualization.py
"""
Visualization module for the Risk Profiling Finance dashboard.
Provides Plotly-based charts with consistent theming.
"""

from typing import Dict, List, Optional

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from src.constants import RISK_COLORS, RISK_THRESHOLDS
from src.utils import setup_logger

logger = setup_logger("visualization")

# ─────────────────────────────────────────────
# Theme Config
# ─────────────────────────────────────────────

PLOT_BG      = "rgba(0,0,0,0)"
PAPER_BG     = "rgba(0,0,0,0)"
FONT_FAMILY  = "IBM Plex Mono, monospace"
FONT_COLOR   = "#e2e8f0"
GRID_COLOR   = "rgba(255,255,255,0.08)"

BASE_LAYOUT = dict(
    plot_bgcolor=PLOT_BG,
    paper_bgcolor=PAPER_BG,
    font=dict(family=FONT_FAMILY, color=FONT_COLOR, size=12),
    margin=dict(l=20, r=20, t=40, b=20),
)


def _apply_base(fig: go.Figure, title: str = "") -> go.Figure:
    fig.update_layout(**BASE_LAYOUT, title=dict(text=title, font=dict(size=15, color="#94a3b8")))
    return fig


# ─────────────────────────────────────────────
# 1. Gauge Chart
# ─────────────────────────────────────────────

def create_gauge_chart(score: float, risk_category: str) -> go.Figure:
    """Animated gauge chart for final risk score."""
    color = RISK_COLORS.get(risk_category, "#94a3b8")

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={"x": [0, 1], "y": [0, 1]},
        number={"suffix": "", "font": {"size": 48, "color": color, "family": FONT_FAMILY}},
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#475569",
                "tickfont": {"color": "#94a3b8"},
            },
            "bar": {"color": color, "thickness": 0.3},
            "bgcolor": "rgba(30,41,59,0.8)",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 30],  "color": "rgba(34,197,94,0.15)"},
                {"range": [30, 60], "color": "rgba(245,158,11,0.15)"},
                {"range": [60, 80], "color": "rgba(239,68,68,0.15)"},
                {"range": [80, 100],"color": "rgba(124,58,237,0.15)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 4},
                "thickness": 0.75,
                "value": score,
            },
        },
        title={"text": f"<b>{risk_category}</b>", "font": {"size": 18, "color": color, "family": FONT_FAMILY}},
    ))
    fig.update_layout(**BASE_LAYOUT)
    fig.update_layout(
        height=280,
        margin=dict(l=30, r=30, t=20, b=10),
    )
    return fig


# ─────────────────────────────────────────────
# 2. Factor Contribution Bar Chart
# ─────────────────────────────────────────────

def contribution_chart(contributions: Dict[str, float]) -> go.Figure:
    """Horizontal bar chart showing each factor's risk contribution."""
    labels = list(contributions.keys())
    values = list(contributions.values())

    # Color bars by contribution magnitude
    bar_colors = [
        "#7c3aed" if v > 15 else "#ef4444" if v > 10 else "#f59e0b" if v > 5 else "#22c55e"
        for v in values
    ]

    fig = go.Figure(go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        text=[f"{v:.1f}" for v in values],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=11),
    ))

    fig.update_xaxes(
        gridcolor=GRID_COLOR, showgrid=True,
        title="Risk Contribution (pts)", title_font=dict(color="#94a3b8"),
        tickfont=dict(color="#94a3b8"),
    )
    fig.update_yaxes(tickfont=dict(color="#e2e8f0"))
    fig.update_layout(**BASE_LAYOUT, height=320, title="Factor Contribution Breakdown")
    return fig


# ─────────────────────────────────────────────
# 3. Radar Chart
# ─────────────────────────────────────────────

def radar_chart(factors: Dict[str, float], name: str = "Customer") -> go.Figure:
    """Spider/radar chart for factor visualization."""
    categories = list(factors.keys())
    values = [v * 100 for v in factors.values()]
    values_closed = values + [values[0]]
    categories_closed = categories + [categories[0]]

    fig = go.Figure(go.Scatterpolar(
        r=values_closed,
        theta=categories_closed,
        fill="toself",
        name=name,
        line=dict(color="#38bdf8", width=2),
        fillcolor="rgba(56,189,248,0.15)",
    ))

    fig.update_layout(
        **BASE_LAYOUT,
        height=350,
        polar=dict(
            bgcolor="rgba(15,23,42,0.5)",
            radialaxis=dict(
                visible=True, range=[0, 100],
                gridcolor=GRID_COLOR, tickfont=dict(color="#64748b", size=9),
            ),
            angularaxis=dict(tickfont=dict(color="#94a3b8", size=11)),
        ),
        title="Risk Factor Radar",
        showlegend=False,
    )
    return fig


# ─────────────────────────────────────────────
# 4. Pie Chart – Risk Distribution
# ─────────────────────────────────────────────

def pie_chart(df: pd.DataFrame) -> go.Figure:
    """Pie chart showing distribution of risk categories in dataset."""
    counts = df["risk_category"].value_counts().reset_index()
    counts.columns = ["category", "count"]

    colors = [RISK_COLORS.get(c, "#64748b") for c in counts["category"]]

    fig = go.Figure(go.Pie(
        labels=counts["category"],
        values=counts["count"],
        marker=dict(colors=colors, line=dict(color="#0f172a", width=2)),
        textinfo="label+percent",
        textfont=dict(color="#e2e8f0", family=FONT_FAMILY, size=12),
        hole=0.42,
        pull=[0.04] * len(counts),
    ))
    fig.update_layout(**BASE_LAYOUT, height=340, title="Risk Category Distribution")
    return fig


# ─────────────────────────────────────────────
# 5. Histogram – Score Distribution
# ─────────────────────────────────────────────

def histogram_chart(df: pd.DataFrame) -> go.Figure:
    """Distribution of final risk scores."""
    fig = go.Figure()

    # Add background zone bands
    for cat, (lo, hi) in RISK_THRESHOLDS.items():
        fig.add_vrect(
            x0=lo, x1=hi,
            fillcolor=RISK_COLORS[cat],
            opacity=0.06,
            layer="below",
            line_width=0,
        )

    fig.add_trace(go.Histogram(
        x=df["final_score"],
        nbinsx=20,
        marker=dict(
            color="#38bdf8",
            line=dict(color="#0f172a", width=1),
        ),
        opacity=0.85,
        name="Score Distribution",
    ))

    fig.update_xaxes(title="Risk Score", gridcolor=GRID_COLOR, tickfont=dict(color="#94a3b8"))
    fig.update_yaxes(title="Customers", gridcolor=GRID_COLOR, tickfont=dict(color="#94a3b8"))
    fig.update_layout(**BASE_LAYOUT, height=300, title="Risk Score Distribution")
    return fig


# ─────────────────────────────────────────────
# 6. Correlation Heatmap
# ─────────────────────────────────────────────

def correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    """Correlation heatmap of numeric financial features."""
    numeric_cols = [
        "credit_score", "monthly_income", "debt_ratio", "existing_loans",
        "employment_years", "fraud_alerts", "security_flags",
        "transactions_per_month", "insurance_claims", "final_score"
    ]
    available = [c for c in numeric_cols if c in df.columns]
    corr = df[available].corr().round(2)

    fig = go.Figure(go.Heatmap(
        z=corr.values,
        x=corr.columns,
        y=corr.index,
        colorscale=[
            [0.0, "#7c3aed"],
            [0.5, "#0f172a"],
            [1.0, "#22c55e"],
        ],
        zmid=0,
        text=corr.values,
        texttemplate="%{text}",
        textfont={"size": 9, "color": "#e2e8f0"},
        hoverongaps=False,
        colorbar=dict(tickfont=dict(color="#94a3b8")),
    ))
    fig.update_xaxes(tickfont=dict(color="#94a3b8", size=9), tickangle=-35)
    fig.update_yaxes(tickfont=dict(color="#94a3b8", size=9))
    fig.update_layout(**BASE_LAYOUT, height=420, title="Feature Correlation Matrix")
    return fig


# ─────────────────────────────────────────────
# 7. Top High-Risk Customers Bar Chart
# ─────────────────────────────────────────────

def top_risk_chart(df: pd.DataFrame, top_n: int = 15) -> go.Figure:
    """Bar chart of the top-N highest risk customers."""
    top = df.nlargest(top_n, "final_score").copy()
    top = top.sort_values("final_score")

    bar_colors = [RISK_COLORS.get(c, "#64748b") for c in top["risk_category"]]

    fig = go.Figure(go.Bar(
        x=top["final_score"],
        y=top["name"],
        orientation="h",
        marker=dict(color=bar_colors, line=dict(color="rgba(0,0,0,0)", width=0)),
        text=[f"{s:.1f}" for s in top["final_score"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=10),
    ))

    fig.update_xaxes(range=[0, 110], gridcolor=GRID_COLOR, tickfont=dict(color="#94a3b8"), title="Risk Score")
    fig.update_yaxes(tickfont=dict(color="#e2e8f0", size=10))
    fig.update_layout(**BASE_LAYOUT, height=420, title=f"Top {top_n} Highest Risk Customers")
    return fig


# ─────────────────────────────────────────────
# 8. Score by Location Box Plot
# ─────────────────────────────────────────────

def location_risk_chart(df: pd.DataFrame) -> go.Figure:
    """Average risk score by city/location."""
    loc_avg = (
        df.groupby("location")["final_score"]
        .mean()
        .sort_values(ascending=False)
        .head(20)
        .reset_index()
    )

    bar_colors = [
        RISK_COLORS.get(
            "Critical Risk" if s > 80 else "High Risk" if s > 60 else "Medium Risk" if s > 30 else "Low Risk",
            "#64748b"
        )
        for s in loc_avg["final_score"]
    ]

    fig = go.Figure(go.Bar(
        x=loc_avg["location"],
        y=loc_avg["final_score"],
        marker=dict(color=bar_colors),
        text=[f"{s:.1f}" for s in loc_avg["final_score"]],
        textposition="outside",
        textfont=dict(color="#e2e8f0", size=10),
    ))
    fig.update_xaxes(tickangle=-45, tickfont=dict(color="#94a3b8", size=9))
    fig.update_yaxes(gridcolor=GRID_COLOR, tickfont=dict(color="#94a3b8"), title="Avg Risk Score")
    fig.update_layout(**BASE_LAYOUT, height=380, title="Average Risk Score by Location (Top 20)")
    return fig


# ─────────────────────────────────────────────
# 9. Score vs Credit Score Scatter
# ─────────────────────────────────────────────

def scatter_score_credit(df: pd.DataFrame) -> go.Figure:
    """Scatter plot: Credit Score vs Final Risk Score."""
    fig = go.Figure()

    for cat, color in RISK_COLORS.items():
        mask = df["risk_category"] == cat
        subset = df[mask]
        if len(subset) == 0:
            continue
        fig.add_trace(go.Scatter(
            x=subset["credit_score"],
            y=subset["final_score"],
            mode="markers",
            name=cat,
            marker=dict(color=color, size=7, opacity=0.8,
                        line=dict(color="#0f172a", width=0.5)),
            text=subset["name"],
            hovertemplate="<b>%{text}</b><br>Credit: %{x}<br>Risk: %{y:.1f}<extra></extra>",
        ))

    fig.update_xaxes(title="Credit Score", gridcolor=GRID_COLOR, tickfont=dict(color="#94a3b8"))
    fig.update_yaxes(title="Final Risk Score", gridcolor=GRID_COLOR, tickfont=dict(color="#94a3b8"))
    fig.update_layout(**BASE_LAYOUT, height=360, title="Credit Score vs Risk Score", legend=dict(
        font=dict(color="#94a3b8"), bgcolor="rgba(15,23,42,0.7)"
    ))
    return fig
