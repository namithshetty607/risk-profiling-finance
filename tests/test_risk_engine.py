# tests/test_risk_engine.py
"""
Unit tests for the Risk Engine and supporting modules.
Run with: pytest tests/test_risk_engine.py -v
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pandas as pd
import pytest

from src.risk_engine import RiskEngine, RiskResult
from src.preprocessing import compute_risk_factors, normalize_minmax, encode_payment_history
from src.data_loader import validate_dataset, clean_missing_values
from src.utils import get_risk_category, get_credit_grade, get_decision
from src.constants import DEFAULT_WEIGHTS


# ─────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────

@pytest.fixture
def low_risk_row():
    return pd.Series({
        "customer_id": "T001",
        "name": "Test Low",
        "age": 35,
        "credit_score": 800,
        "payment_history": "excellent",
        "monthly_income": 150000,
        "debt_ratio": 15,
        "existing_loans": 1,
        "employment_years": 12,
        "fraud_alerts": 0,
        "security_flags": 0,
        "transactions_per_month": 30,
        "insurance_claims": 0,
        "location": "Mumbai",
        "account_age_months": 60,
    })


@pytest.fixture
def high_risk_row():
    return pd.Series({
        "customer_id": "T002",
        "name": "Test High",
        "age": 28,
        "credit_score": 480,
        "payment_history": "poor",
        "monthly_income": 28000,
        "debt_ratio": 82,
        "existing_loans": 6,
        "employment_years": 1,
        "fraud_alerts": 4,
        "security_flags": 2,
        "transactions_per_month": 90,
        "insurance_claims": 4,
        "location": "Delhi",
        "account_age_months": 3,
    })


@pytest.fixture
def engine():
    return RiskEngine()


@pytest.fixture
def sample_df():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_customers.csv")
    if os.path.exists(path):
        return pd.read_csv(path)
    # Minimal fallback
    return pd.DataFrame([{
        "customer_id": f"C{i:03d}", "name": f"Customer {i}", "age": 30+i,
        "credit_score": 600+i*5, "payment_history": "good",
        "monthly_income": 50000+i*1000, "debt_ratio": 40+i,
        "existing_loans": 2, "employment_years": 5, "fraud_alerts": 0,
        "security_flags": 0, "transactions_per_month": 30, "insurance_claims": 0,
        "location": "Mumbai", "account_age_months": 24+i
    } for i in range(10)])


# ─────────────────────────────────────────────
# Tests: Normalize + Encode
# ─────────────────────────────────────────────

class TestPreprocessing:
    def test_normalize_minmax_midpoint(self):
        result = normalize_minmax(50, 0, 100)
        assert abs(result - 0.5) < 1e-6

    def test_normalize_minmax_min(self):
        assert normalize_minmax(0, 0, 100) == 0.0

    def test_normalize_minmax_max(self):
        assert normalize_minmax(100, 0, 100) == 1.0

    def test_normalize_minmax_clamp(self):
        assert normalize_minmax(150, 0, 100) == 1.0
        assert normalize_minmax(-50, 0, 100) == 0.0

    def test_encode_payment_history_excellent(self):
        assert encode_payment_history("excellent") == 1

    def test_encode_payment_history_poor(self):
        assert encode_payment_history("poor") == 4

    def test_encode_payment_history_unknown(self):
        assert encode_payment_history("unknown") == 3  # default fair

    def test_compute_risk_factors_keys(self, low_risk_row):
        factors = compute_risk_factors(low_risk_row)
        expected_keys = {
            "credit_score", "payment_history", "monthly_income",
            "debt_ratio", "existing_loans", "employment_years",
            "fraud_alerts", "security_flags"
        }
        assert expected_keys == set(factors.keys())

    def test_compute_risk_factors_range(self, low_risk_row, high_risk_row):
        for row in [low_risk_row, high_risk_row]:
            factors = compute_risk_factors(row)
            for k, v in factors.items():
                assert 0.0 <= v <= 1.0, f"{k} out of [0,1]: {v}"


# ─────────────────────────────────────────────
# Tests: Risk Engine Scoring
# ─────────────────────────────────────────────

class TestRiskEngine:
    def test_low_risk_score_is_low(self, engine, low_risk_row):
        result = engine.score_customer(low_risk_row)
        assert result.final_score < 50, f"Expected low score, got {result.final_score}"

    def test_high_risk_score_is_high(self, engine, high_risk_row):
        result = engine.score_customer(high_risk_row)
        assert result.final_score > 60, f"Expected high score, got {result.final_score}"

    def test_score_in_range(self, engine, low_risk_row, high_risk_row):
        for row in [low_risk_row, high_risk_row]:
            r = engine.score_customer(row)
            assert 0 <= r.final_score <= 100

    def test_risk_result_type(self, engine, low_risk_row):
        result = engine.score_customer(low_risk_row)
        assert isinstance(result, RiskResult)

    def test_result_has_contributions(self, engine, low_risk_row):
        result = engine.score_customer(low_risk_row)
        assert len(result.factor_contributions) > 0

    def test_rules_triggered_for_high_risk(self, engine, high_risk_row):
        result = engine.score_customer(high_risk_row)
        assert len(result.rules_triggered) > 0

    def test_no_rules_for_clean_customer(self, engine, low_risk_row):
        result = engine.score_customer(low_risk_row)
        # Low-risk customer should have few or no rule triggers
        assert len(result.rules_triggered) <= 1

    def test_weight_update(self, engine):
        engine.update_weights({"fraud_alerts": 0.40})
        assert abs(sum(engine.weights.values()) - 1.0) < 1e-6

    def test_weights_sum_to_one(self):
        e = RiskEngine(DEFAULT_WEIGHTS)
        assert abs(sum(e.weights.values()) - 1.0) < 1e-6

    def test_batch_score_returns_correct_columns(self, engine, sample_df):
        from src.data_loader import validate_dataset, clean_missing_values
        df = validate_dataset(sample_df.copy())
        df = clean_missing_values(df)
        result = engine.score_all(df)
        for col in ["final_score", "risk_category", "credit_grade", "decision"]:
            assert col in result.columns, f"Missing column: {col}"

    def test_batch_score_row_count(self, engine, sample_df):
        from src.data_loader import validate_dataset, clean_missing_values
        df = validate_dataset(sample_df.copy())
        df = clean_missing_values(df)
        result = engine.score_all(df)
        assert len(result) == len(df)

    def test_contribution_table(self, engine, low_risk_row):
        table = engine.get_contribution_table(low_risk_row)
        assert "Factor" in table.columns
        assert "Contribution" in table.columns
        assert len(table) == len(DEFAULT_WEIGHTS)

    def test_credit_grade_assigned(self, engine, low_risk_row):
        result = engine.score_customer(low_risk_row)
        assert result.credit_grade in ("A+", "A", "B", "C", "D", "F")

    def test_decision_assigned(self, engine, low_risk_row, high_risk_row):
        for row in [low_risk_row, high_risk_row]:
            r = engine.score_customer(row)
            assert r.decision in (
                "✅ Approve Loan",
                "🔍 Review Manually",
                "❌ Reject Application",
                "🚨 Escalate to Fraud Team",
            )


# ─────────────────────────────────────────────
# Tests: Utils
# ─────────────────────────────────────────────

class TestUtils:
    def test_risk_category_low(self):
        assert get_risk_category(20) == "Low Risk"

    def test_risk_category_medium(self):
        assert get_risk_category(45) == "Medium Risk"

    def test_risk_category_high(self):
        assert get_risk_category(70) == "High Risk"

    def test_risk_category_critical(self):
        assert get_risk_category(90) == "Critical Risk"

    def test_credit_grade_excellent(self):
        assert get_credit_grade(800) == "A+"

    def test_credit_grade_poor(self):
        assert get_credit_grade(480) == "F"

    def test_decision_low_risk(self):
        assert get_decision("Low Risk") == "✅ Approve Loan"

    def test_decision_critical(self):
        assert get_decision("Critical Risk") == "🚨 Escalate to Fraud Team"


# ─────────────────────────────────────────────
# Tests: Data Loader
# ─────────────────────────────────────────────

class TestDataLoader:
    def test_validate_dataset_passes(self, sample_df):
        df = validate_dataset(sample_df.copy())
        assert df is not None

    def test_clean_missing_values(self, sample_df):
        df = validate_dataset(sample_df.copy())
        df.loc[0, "credit_score"] = np.nan
        df.loc[1, "payment_history"] = np.nan
        cleaned = clean_missing_values(df)
        assert cleaned["credit_score"].isnull().sum() == 0
        assert cleaned["payment_history"].isnull().sum() == 0

    def test_validate_rejects_missing_columns(self):
        bad_df = pd.DataFrame({"name": ["X"], "age": [30]})
        with pytest.raises(ValueError):
            validate_dataset(bad_df)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
