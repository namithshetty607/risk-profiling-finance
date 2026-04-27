# src/utils.py
"""
Utility functions for the Risk Profiling Finance application.
"""

import logging
import os
from datetime import datetime
from typing import Dict, Optional

import pandas as pd

from src.constants import (
    CREDIT_GRADE_THRESHOLDS, CREDIT_GRADE_COLORS,
    RISK_THRESHOLDS, RISK_COLORS, RISK_ICONS, DECISION_MAP, REPORTS_DIR
)


# ─────────────────────────────────────────────
# Logger Setup
# ─────────────────────────────────────────────

def setup_logger(name: str = "risk_profiler", level: int = logging.INFO) -> logging.Logger:
    """Configure and return a logger instance."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        fmt = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(fmt)
        logger.addHandler(handler)
    logger.setLevel(level)
    return logger


logger = setup_logger()


# ─────────────────────────────────────────────
# Credit Grade
# ─────────────────────────────────────────────

def get_credit_grade(credit_score: float) -> str:
    """Return letter grade for a given credit score."""
    for grade, (low, high) in CREDIT_GRADE_THRESHOLDS.items():
        if low <= credit_score <= high:
            return grade
    return "F"


def get_credit_grade_color(grade: str) -> str:
    return CREDIT_GRADE_COLORS.get(grade, "#94a3b8")


# ─────────────────────────────────────────────
# Risk Category
# ─────────────────────────────────────────────

def get_risk_category(score: float) -> str:
    """Classify a numeric risk score into a risk label."""
    for category, (low, high) in RISK_THRESHOLDS.items():
        if low <= score <= high:
            return category
    return "Critical Risk"


def get_risk_color(category: str) -> str:
    return RISK_COLORS.get(category, "#94a3b8")


def get_risk_icon(category: str) -> str:
    return RISK_ICONS.get(category, "❓")


def get_decision(category: str) -> str:
    return DECISION_MAP.get(category, "🔍 Review Manually")


# ─────────────────────────────────────────────
# Score Badge HTML
# ─────────────────────────────────────────────

def score_badge_html(score: float, category: str) -> str:
    color = get_risk_color(category)
    icon = get_risk_icon(category)
    return (
        f"<span style='background:{color};color:#fff;padding:4px 12px;"
        f"border-radius:20px;font-weight:bold;font-size:0.9rem;'>"
        f"{icon} {category} ({score:.1f})</span>"
    )


# ─────────────────────────────────────────────
# Export Helpers
# ─────────────────────────────────────────────

def ensure_reports_dir() -> str:
    os.makedirs(REPORTS_DIR, exist_ok=True)
    return REPORTS_DIR


def export_to_csv(df: pd.DataFrame, filename: Optional[str] = None) -> str:
    dir_ = ensure_reports_dir()
    if filename is None:
        filename = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = os.path.join(dir_, filename)
    df.to_csv(path, index=False)
    logger.info(f"Exported CSV: {path}")
    return path


def export_to_excel(df: pd.DataFrame, filename: Optional[str] = None) -> str:
    dir_ = ensure_reports_dir()
    if filename is None:
        filename = f"risk_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    path = os.path.join(dir_, filename)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Risk Report", index=False)
    logger.info(f"Exported Excel: {path}")
    return path


def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")


def df_to_excel_bytes(df: pd.DataFrame) -> bytes:
    from io import BytesIO
    buf = BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Risk Report", index=False)
    return buf.getvalue()


# ─────────────────────────────────────────────
# Formatting
# ─────────────────────────────────────────────

def fmt_currency(value: float) -> str:
    """Format a number as Indian Rupees."""
    return f"₹{value:,.0f}"


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def fmt_score(value: float) -> str:
    return f"{value:.1f}"


def color_risk_row(row: pd.Series) -> list:
    """Return styling for a dataframe row based on risk category."""
    color_map = {
        "Low Risk":      "background-color: #d1fae5",
        "Medium Risk":   "background-color: #fef3c7",
        "High Risk":     "background-color: #fee2e2",
        "Critical Risk": "background-color: #ede9fe",
    }
    cat = row.get("risk_category", "")
    style = color_map.get(cat, "")
    return [style] * len(row)
