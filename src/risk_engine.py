# src/risk_engine.py
"""
Core Risk Calculation Engine for the Risk Profiling Finance system.

Implements:
  - Weighted factor scoring (0-100 normalized)
  - Business rule adjustments
  - Explainability breakdown
  - Batch scoring for all customers
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd

from src.constants import (
    DEFAULT_WEIGHTS, RULE_ADJUSTMENTS,
    RISK_THRESHOLDS, DECISION_MAP
)
from src.preprocessing import compute_risk_factors, preprocess_dataframe
from src.utils import (
    setup_logger, get_risk_category, get_credit_grade, get_decision, get_risk_color, get_risk_icon
)

logger = setup_logger("risk_engine")


# ─────────────────────────────────────────────────────────────────
# Result Dataclass
# ─────────────────────────────────────────────────────────────────

@dataclass
class RiskResult:
    customer_id: str
    name: str
    base_score: float
    adjustment: float
    final_score: float
    risk_category: str
    credit_grade: str
    decision: str
    factor_contributions: Dict[str, float] = field(default_factory=dict)
    rules_triggered: List[str] = field(default_factory=list)
    risk_drivers: List[str] = field(default_factory=list)
    risk_reducers: List[str] = field(default_factory=list)

    @property
    def risk_color(self) -> str:
        return get_risk_color(self.risk_category)

    @property
    def risk_icon(self) -> str:
        return get_risk_icon(self.risk_category)


# ─────────────────────────────────────────────────────────────────
# Risk Engine Class
# ─────────────────────────────────────────────────────────────────

class RiskEngine:
    """
    Calculates financial risk scores for customers using weighted factors
    and business rules.
    """

    FACTOR_LABELS = {
        "credit_score":     "Credit Score",
        "payment_history":  "Payment History",
        "monthly_income":   "Monthly Income",
        "debt_ratio":       "Debt Ratio",
        "existing_loans":   "Existing Loans",
        "employment_years": "Employment Stability",
        "fraud_alerts":     "Fraud Alerts",
        "security_flags":   "Security Flags",
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or DEFAULT_WEIGHTS.copy()
        self._normalize_weights()
        logger.info(f"RiskEngine initialized with weights: {self.weights}")

    def _normalize_weights(self):
        """Ensure weights sum to 1.0."""
        total = sum(self.weights.values())
        if total > 0:
            self.weights = {k: v / total for k, v in self.weights.items()}

    def update_weights(self, new_weights: Dict[str, float]):
        """Dynamically update weights and re-normalize."""
        self.weights.update(new_weights)
        self._normalize_weights()
        logger.info("Weights updated and normalized.")

    # ─────────────────────────────────────────────
    # Core Scoring
    # ─────────────────────────────────────────────

    def _weighted_base_score(self, factors: Dict[str, float]) -> Tuple[float, Dict[str, float]]:
        """
        Calculate weighted base score and per-factor contributions.

        Each factor is a value in [0, 1] where higher = higher risk.
        Contributions are scaled to 0-100.
        """
        contributions = {}
        total = 0.0
        for factor, weight in self.weights.items():
            value = factors.get(factor, 0.5)
            contribution = weight * value * 100
            contributions[factor] = round(contribution, 2)
            total += weight * value

        base_score = total * 100
        return round(base_score, 2), contributions

    def _apply_business_rules(self, row: pd.Series) -> Tuple[float, List[str]]:
        """
        Apply hard-coded business rule adjustments.

        Returns:
            (total_adjustment, list_of_triggered_rules)
        """
        adjustment = 0.0
        rules_triggered = []

        # Rule 1: Fraud alerts > 2
        if row.get("fraud_alerts", 0) > 2:
            adjustment += RULE_ADJUSTMENTS["fraud_alerts_high"]
            rules_triggered.append(
                f"🚨 Fraud Alerts > 2 (alerts={int(row['fraud_alerts'])}) → +{RULE_ADJUSTMENTS['fraud_alerts_high']}"
            )

        # Rule 2: Debt ratio > 70
        if row.get("debt_ratio", 0) > 70:
            adjustment += RULE_ADJUSTMENTS["debt_ratio_high"]
            rules_triggered.append(
                f"📈 Debt Ratio > 70% (ratio={row['debt_ratio']:.1f}%) → +{RULE_ADJUSTMENTS['debt_ratio_high']}"
            )

        # Rule 3: Income > 100,000
        if row.get("monthly_income", 0) > 100000:
            adjustment += RULE_ADJUSTMENTS["income_high"]
            rules_triggered.append(
                f"💰 High Income > ₹1,00,000 → {RULE_ADJUSTMENTS['income_high']}"
            )

        # Rule 4: Payment history poor
        ph = str(row.get("payment_history", "")).strip().lower()
        if ph == "poor":
            adjustment += RULE_ADJUSTMENTS["payment_poor"]
            rules_triggered.append(
                f"❌ Poor Payment History → +{RULE_ADJUSTMENTS['payment_poor']}"
            )

        # Rule 5: Security flags > 0
        if row.get("security_flags", 0) > 0:
            adjustment += RULE_ADJUSTMENTS["security_flags"]
            rules_triggered.append(
                f"🔒 Security Flags Triggered (flags={int(row['security_flags'])}) → +{RULE_ADJUSTMENTS['security_flags']}"
            )

        # Rule 6: Transaction spike (>80 transactions/month)
        if row.get("transactions_per_month", 0) > 80:
            adjustment += RULE_ADJUSTMENTS["transaction_spike"]
            rules_triggered.append(
                f"📊 Suspicious Transaction Spike ({int(row['transactions_per_month'])}/month) → +{RULE_ADJUSTMENTS['transaction_spike']}"
            )

        # Rule 7: New account (< 6 months)
        if row.get("account_age_months", 100) < 6:
            adjustment += RULE_ADJUSTMENTS["new_account"]
            rules_triggered.append(
                f"🆕 New Account (age={int(row['account_age_months'])} months) → +{RULE_ADJUSTMENTS['new_account']}"
            )

        # Rule 8: High insurance claims
        if row.get("insurance_claims", 0) >= 3:
            adjustment += RULE_ADJUSTMENTS["insurance_claims_high"]
            rules_triggered.append(
                f"🏥 High Insurance Claims ({int(row['insurance_claims'])} claims) → +{RULE_ADJUSTMENTS['insurance_claims_high']}"
            )

        return round(adjustment, 2), rules_triggered

    def _build_explainability(
        self, contributions: Dict[str, float]
    ) -> Tuple[List[str], List[str]]:
        """
        Identify the top risk drivers and reducers.
        """
        sorted_contributions = sorted(contributions.items(), key=lambda x: x[1], reverse=True)

        drivers = []
        reducers = []

        # Top 3 highest contributors = risk drivers
        for factor, value in sorted_contributions[:3]:
            label = self.FACTOR_LABELS.get(factor, factor)
            drivers.append(f"📌 **{label}**: contributes {value:.1f} pts to risk")

        # Bottom 3 = risk reducers (low contribution = doing well)
        for factor, value in sorted_contributions[-3:]:
            label = self.FACTOR_LABELS.get(factor, factor)
            reducers.append(f"✅ **{label}**: low risk contribution ({value:.1f} pts)")

        return drivers, reducers

    # ─────────────────────────────────────────────
    # Score a Single Row
    # ─────────────────────────────────────────────

    def score_customer(self, row: pd.Series) -> RiskResult:
        """
        Calculate complete risk profile for a single customer row.
        """
        factors = compute_risk_factors(row)
        base_score, contributions = self._weighted_base_score(factors)
        adjustment, rules_triggered = self._apply_business_rules(row)

        final_score = float(np.clip(base_score + adjustment, 0, 100))
        risk_category = get_risk_category(final_score)
        credit_grade = get_credit_grade(row.get("credit_score", 650))
        decision = get_decision(risk_category)
        drivers, reducers = self._build_explainability(contributions)

        return RiskResult(
            customer_id=str(row.get("customer_id", "N/A")),
            name=str(row.get("name", "Unknown")),
            base_score=base_score,
            adjustment=adjustment,
            final_score=round(final_score, 1),
            risk_category=risk_category,
            credit_grade=credit_grade,
            decision=decision,
            factor_contributions=contributions,
            rules_triggered=rules_triggered,
            risk_drivers=drivers,
            risk_reducers=reducers,
        )

    # ─────────────────────────────────────────────
    # Batch Score All Customers
    # ─────────────────────────────────────────────

    def score_all(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Score all customers in a DataFrame and return enriched DataFrame.
        """
        logger.info(f"Batch scoring {len(df)} customers...")
        results = []
        for _, row in df.iterrows():
            r = self.score_customer(row)
            results.append({
                "customer_id":      r.customer_id,
                "name":             r.name,
                "base_score":       r.base_score,
                "adjustment":       r.adjustment,
                "final_score":      r.final_score,
                "risk_category":    r.risk_category,
                "credit_grade":     r.credit_grade,
                "decision":         r.decision,
                "rules_count":      len(r.rules_triggered),
            })

        scored_df = pd.DataFrame(results)
        # Merge back with original
        merged = df.merge(scored_df, on="customer_id", how="left", suffixes=("", "_scored"))
        # Prefer scored name column if it exists
        if "name_scored" in merged.columns:
            merged.drop(columns=["name_scored"], inplace=True)

        logger.info("Batch scoring complete.")
        return merged

    # ─────────────────────────────────────────────
    # Contribution Table
    # ─────────────────────────────────────────────

    def get_contribution_table(self, row: pd.Series) -> pd.DataFrame:
        """Return a DataFrame showing factor, weight, raw value, and contribution."""
        factors = compute_risk_factors(row)
        _, contributions = self._weighted_base_score(factors)

        rows = []
        for factor, contrib in contributions.items():
            rows.append({
                "Factor":       self.FACTOR_LABELS.get(factor, factor),
                "Weight":       f"{self.weights.get(factor, 0)*100:.1f}%",
                "Risk Score":   round(factors.get(factor, 0) * 100, 1),
                "Contribution": round(contrib, 2),
            })
        return pd.DataFrame(rows).sort_values("Contribution", ascending=False)
