# src/constants.py
"""
Project-wide constants for the Risk Profiling Finance application.
"""

# ─────────────────────────────────────────────
# Risk Category Thresholds
# ─────────────────────────────────────────────
RISK_THRESHOLDS = {
    "Low Risk":      (0, 30),
    "Medium Risk":   (31, 60),
    "High Risk":     (61, 80),
    "Critical Risk": (81, 100),
}

RISK_COLORS = {
    "Low Risk":      "#22c55e",   # green
    "Medium Risk":   "#f59e0b",   # amber
    "High Risk":     "#ef4444",   # red
    "Critical Risk": "#7c3aed",   # purple
}

RISK_ICONS = {
    "Low Risk":      "✅",
    "Medium Risk":   "⚠️",
    "High Risk":     "🔴",
    "Critical Risk": "💀",
}

# ─────────────────────────────────────────────
# Decision Engine Mapping
# ─────────────────────────────────────────────
DECISION_MAP = {
    "Low Risk":      "✅ Approve Loan",
    "Medium Risk":   "🔍 Review Manually",
    "High Risk":     "❌ Reject Application",
    "Critical Risk": "🚨 Escalate to Fraud Team",
}

DECISION_COLORS = {
    "✅ Approve Loan":           "#22c55e",
    "🔍 Review Manually":        "#f59e0b",
    "❌ Reject Application":     "#ef4444",
    "🚨 Escalate to Fraud Team": "#7c3aed",
}

# ─────────────────────────────────────────────
# Credit Score Grading
# ─────────────────────────────────────────────
CREDIT_GRADE_THRESHOLDS = {
    "A+": (780, 900),
    "A":  (740, 779),
    "B":  (680, 739),
    "C":  (620, 679),
    "D":  (550, 619),
    "F":  (300, 549),
}

CREDIT_GRADE_COLORS = {
    "A+": "#22c55e",
    "A":  "#84cc16",
    "B":  "#f59e0b",
    "C":  "#f97316",
    "D":  "#ef4444",
    "F":  "#7c3aed",
}

# ─────────────────────────────────────────────
# Column Definitions
# ─────────────────────────────────────────────
REQUIRED_COLUMNS = [
    "customer_id", "name", "age", "credit_score", "payment_history",
    "monthly_income", "debt_ratio", "existing_loans", "employment_years",
    "fraud_alerts", "security_flags", "transactions_per_month",
    "insurance_claims", "location", "account_age_months",
]

NUMERIC_COLUMNS = [
    "age", "credit_score", "monthly_income", "debt_ratio",
    "existing_loans", "employment_years", "fraud_alerts",
    "security_flags", "transactions_per_month", "insurance_claims",
    "account_age_months",
]

PAYMENT_HISTORY_MAP = {
    "excellent": 1,
    "good":      2,
    "fair":      3,
    "poor":      4,
}

# ─────────────────────────────────────────────
# Default Weights
# ─────────────────────────────────────────────
DEFAULT_WEIGHTS = {
    "credit_score":    0.25,
    "payment_history": 0.20,
    "monthly_income":  0.10,
    "debt_ratio":      0.15,
    "existing_loans":  0.10,
    "employment_years":0.05,
    "fraud_alerts":    0.10,
    "security_flags":  0.05,
}

# ─────────────────────────────────────────────
# Business Rule Adjustments
# ─────────────────────────────────────────────
RULE_ADJUSTMENTS = {
    "fraud_alerts_high":      +15,
    "debt_ratio_high":        +10,
    "income_high":            -5,
    "payment_poor":           +20,
    "security_flags":         +25,
    "transaction_spike":      +10,
    "new_account":            +8,
    "insurance_claims_high":  +12,
}

# ─────────────────────────────────────────────
# Normalization Ranges
# ─────────────────────────────────────────────
NORM_RANGES = {
    "credit_score":     (300, 900),
    "monthly_income":   (10000, 200000),
    "debt_ratio":       (0, 100),
    "existing_loans":   (0, 10),
    "employment_years": (0, 40),
    "fraud_alerts":     (0, 10),
    "security_flags":   (0, 10),
    "transactions_per_month": (0, 100),
    "account_age_months": (0, 120),
    "insurance_claims": (0, 10),
}

# ─────────────────────────────────────────────
# App Settings
# ─────────────────────────────────────────────
APP_TITLE = "FinRisk Pro"
APP_SUBTITLE = "Data-Driven Risk Profiling for Finance"
APP_VERSION = "2.0.0"
REPORTS_DIR = "reports/exported_reports"
