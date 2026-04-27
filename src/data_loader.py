# src/data_loader.py
"""
Data loading, validation, and cleaning module for Risk Profiling Finance.
"""

import logging
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from src.constants import (
    REQUIRED_COLUMNS, NUMERIC_COLUMNS, PAYMENT_HISTORY_MAP, DEFAULT_WEIGHTS
)
from src.utils import setup_logger

logger = setup_logger("data_loader")


# ─────────────────────────────────────────────
# Load Customer Data
# ─────────────────────────────────────────────

def load_customer_data(filepath: str) -> pd.DataFrame:
    """
    Load customer data from a CSV file.

    Args:
        filepath: Path to the CSV file.

    Returns:
        A cleaned and validated DataFrame.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If required columns are missing.
    """
    logger.info(f"Loading customer data from: {filepath}")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        logger.error(f"File not found: {filepath}")
        raise
    except Exception as e:
        logger.error(f"Failed to read CSV: {e}")
        raise

    df = validate_dataset(df)
    df = clean_missing_values(df)
    logger.info(f"Loaded {len(df)} customer records.")
    return df


def load_customer_data_from_upload(uploaded_file) -> pd.DataFrame:
    """Load customer data from a Streamlit UploadedFile object."""
    logger.info("Loading customer data from uploaded file.")
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        logger.error(f"Failed to read uploaded file: {e}")
        raise
    df = validate_dataset(df)
    df = clean_missing_values(df)
    logger.info(f"Loaded {len(df)} customer records from upload.")
    return df


# ─────────────────────────────────────────────
# Load Weights
# ─────────────────────────────────────────────

def load_weights(filepath: str) -> dict:
    """
    Load factor weights from a CSV file.

    Returns:
        dict mapping factor -> weight (float).
    """
    logger.info(f"Loading weights from: {filepath}")
    try:
        df = pd.read_csv(filepath)
        weights = dict(zip(df["factor"], df["weight"].astype(float)))
        logger.info(f"Loaded {len(weights)} weight factors.")
        return weights
    except FileNotFoundError:
        logger.warning(f"Weights file not found. Using defaults.")
        return DEFAULT_WEIGHTS.copy()
    except Exception as e:
        logger.error(f"Failed to load weights: {e}. Using defaults.")
        return DEFAULT_WEIGHTS.copy()


# ─────────────────────────────────────────────
# Validate Dataset
# ─────────────────────────────────────────────

def validate_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Validate that required columns exist and data types are reasonable.

    Raises:
        ValueError: If critical columns are missing.
    """
    logger.info("Validating dataset schema...")
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        logger.error(f"Missing required columns: {missing}")
        raise ValueError(f"Dataset is missing required columns: {missing}")

    # Coerce numeric columns
    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Normalize payment_history to lowercase string
    if "payment_history" in df.columns:
        df["payment_history"] = df["payment_history"].astype(str).str.strip().str.lower()

    logger.info("Dataset validation passed.")
    return df


# ─────────────────────────────────────────────
# Clean Missing Values
# ─────────────────────────────────────────────

def clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill or drop missing values intelligently.
    """
    logger.info("Cleaning missing values...")
    initial_nulls = df.isnull().sum().sum()

    # Numeric columns – fill with median
    for col in NUMERIC_COLUMNS:
        if col in df.columns and df[col].isnull().any():
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            logger.debug(f"Filled '{col}' NaNs with median={median_val:.2f}")

    # payment_history – fill with mode
    if "payment_history" in df.columns and df["payment_history"].isnull().any():
        mode_val = df["payment_history"].mode()[0] if not df["payment_history"].mode().empty else "fair"
        df["payment_history"] = df["payment_history"].fillna(mode_val)

    # String columns
    for col in ["name", "location"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown")

    # Clip numeric columns to valid ranges
    df["credit_score"] = df["credit_score"].clip(300, 900)
    df["debt_ratio"] = df["debt_ratio"].clip(0, 100)
    df["fraud_alerts"] = df["fraud_alerts"].clip(0, None)
    df["security_flags"] = df["security_flags"].clip(0, None)
    df["monthly_income"] = df["monthly_income"].clip(0, None)
    df["employment_years"] = df["employment_years"].clip(0, None)
    df["account_age_months"] = df["account_age_months"].clip(0, None)

    final_nulls = df.isnull().sum().sum()
    logger.info(f"Cleaned {initial_nulls - final_nulls} null values. Remaining: {final_nulls}")
    return df


# ─────────────────────────────────────────────
# Dataset Summary
# ─────────────────────────────────────────────

def get_dataset_summary(df: pd.DataFrame) -> dict:
    """Return a quick summary of the loaded dataset."""
    return {
        "total_customers": len(df),
        "avg_credit_score": round(df["credit_score"].mean(), 1),
        "avg_income": round(df["monthly_income"].mean(), 0),
        "avg_debt_ratio": round(df["debt_ratio"].mean(), 1),
        "fraud_flagged": int((df["fraud_alerts"] > 0).sum()),
        "security_flagged": int((df["security_flags"] > 0).sum()),
        "locations": df["location"].nunique() if "location" in df.columns else 0,
    }
