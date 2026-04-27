# src/preprocessing.py
"""
Feature engineering and normalization for the Risk Profiling engine.
"""

import numpy as np
import pandas as pd

from src.constants import NORM_RANGES, PAYMENT_HISTORY_MAP
from src.utils import setup_logger

logger = setup_logger("preprocessing")


def normalize_minmax(value: float, min_val: float, max_val: float) -> float:
    """Min-Max normalization to [0, 1]."""
    if max_val == min_val:
        return 0.5
    return float(np.clip((value - min_val) / (max_val - min_val), 0.0, 1.0))


def encode_payment_history(value: str) -> int:
    """Convert payment_history string to numeric ordinal (1=excellent, 4=poor)."""
    return PAYMENT_HISTORY_MAP.get(str(value).strip().lower(), 3)


def compute_risk_factors(row: pd.Series) -> dict:
    """
    Compute normalized risk factor scores (0–1) for each dimension.

    For positive-risk factors (e.g. debt_ratio), higher value → higher risk.
    For negative-risk factors (e.g. credit_score), higher value → lower risk.

    Returns:
        dict of factor_name -> risk_contribution (0.0 – 1.0)
    """
    factors = {}

    # ── Credit Score (higher = lower risk) ──────────────────────────────
    cs_norm = normalize_minmax(
        row["credit_score"],
        NORM_RANGES["credit_score"][0],
        NORM_RANGES["credit_score"][1],
    )
    factors["credit_score"] = 1.0 - cs_norm  # invert

    # ── Payment History (1=excellent=low risk, 4=poor=high risk) ────────
    ph_enc = encode_payment_history(row["payment_history"])
    factors["payment_history"] = normalize_minmax(ph_enc, 1, 4)

    # ── Monthly Income (higher = lower risk) ─────────────────────────────
    inc_norm = normalize_minmax(
        row["monthly_income"],
        NORM_RANGES["monthly_income"][0],
        NORM_RANGES["monthly_income"][1],
    )
    factors["monthly_income"] = 1.0 - inc_norm  # invert

    # ── Debt Ratio (higher = higher risk) ───────────────────────────────
    factors["debt_ratio"] = normalize_minmax(
        row["debt_ratio"],
        NORM_RANGES["debt_ratio"][0],
        NORM_RANGES["debt_ratio"][1],
    )

    # ── Existing Loans (higher = higher risk) ───────────────────────────
    factors["existing_loans"] = normalize_minmax(
        row["existing_loans"],
        NORM_RANGES["existing_loans"][0],
        NORM_RANGES["existing_loans"][1],
    )

    # ── Employment Years (higher = lower risk) ───────────────────────────
    emp_norm = normalize_minmax(
        row["employment_years"],
        NORM_RANGES["employment_years"][0],
        NORM_RANGES["employment_years"][1],
    )
    factors["employment_years"] = 1.0 - emp_norm  # invert

    # ── Fraud Alerts (higher = higher risk) ─────────────────────────────
    factors["fraud_alerts"] = normalize_minmax(
        row["fraud_alerts"],
        NORM_RANGES["fraud_alerts"][0],
        NORM_RANGES["fraud_alerts"][1],
    )

    # ── Security Flags (higher = higher risk) ────────────────────────────
    factors["security_flags"] = normalize_minmax(
        row["security_flags"],
        NORM_RANGES["security_flags"][0],
        NORM_RANGES["security_flags"][1],
    )

    return factors


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add preprocessed factor columns to the DataFrame.
    """
    logger.info("Preprocessing DataFrame – computing risk factors...")
    factor_rows = df.apply(compute_risk_factors, axis=1)
    factor_df = pd.DataFrame(list(factor_rows))
    factor_df.columns = [f"factor_{c}" for c in factor_df.columns]
    df = pd.concat([df.reset_index(drop=True), factor_df.reset_index(drop=True)], axis=1)
    logger.info("Preprocessing complete.")
    return df
