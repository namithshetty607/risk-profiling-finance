# 🛡️ FinRisk Pro — Data-Driven Risk Profiling for Finance

> **An industry-grade financial risk assessment platform** combining Cyber Security, Data Analytics, and Finance into a single powerful Streamlit dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32+-FF4B4B?style=for-the-badge&logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-2.1+-150458?style=for-the-badge&logo=pandas)
![Plotly](https://img.shields.io/badge/Plotly-5.18+-3F4F75?style=for-the-badge&logo=plotly)
![License](https://img.shields.io/badge/License-MIT-22c55e?style=for-the-badge)

---

## 📌 Project Overview

**FinRisk Pro** simulates how banks, insurance companies, fintech platforms, and cybersecurity systems evaluate customer risk. It computes a final **Risk Score (0–100)** using weighted financial and behavioral factors, applies smart business rules, and delivers explainable AI-style breakdowns with actionable decisions.

**Domain:** Cyber Security + Ethical Finance Analytics + Data Science

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🧮 **Weighted Risk Scoring** | 8-factor weighted formula normalized to 0-100 |
| ⚡ **Business Rules Engine** | 8 smart rules (fraud, debt, income, account age, etc.) |
| 🎯 **Explainability Panel** | Risk drivers, reducers, and triggered rules per customer |
| 🏦 **Decision Engine** | Approve / Review / Reject / Escalate based on risk level |
| 📊 **9 Interactive Charts** | Gauge, Radar, Heatmap, Scatter, Bar, Pie, Histogram & more |
| 👤 **Customer Profiler** | Deep-dive into any individual customer |
| 🔍 **Searchable Data Table** | Filter, sort, and search 120+ customers |
| ⚖️ **Adjustable Weights** | Real-time slider-based weight recalculation |
| 📥 **Export Reports** | Download CSV or Excel reports |
| 🧪 **Unit Tests** | 30+ pytest tests covering core logic |

---

## 🚀 Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/yourname/risk-profiling-finance.git
cd risk-profiling-finance
pip install -r requirements.txt
```

### 2. Run the App

```bash
streamlit run app.py
```

The dashboard opens at `http://localhost:8501`

### 3. Run Tests

```bash
pytest tests/test_risk_engine.py -v
```

---

## 📁 Project Structure

```
risk-profiling-finance/
│── app.py                    ← Main Streamlit dashboard
│── requirements.txt
│── README.md
│── .gitignore
│
│── data/
│   ├── sample_customers.csv  ← 120 realistic customer records
│   └── weights_config.csv    ← Default factor weights
│
│── src/
│   ├── __init__.py
│   ├── constants.py          ← All project constants & thresholds
│   ├── data_loader.py        ← CSV loading, validation, cleaning
│   ├── preprocessing.py      ← Feature normalization & encoding
│   ├── risk_engine.py        ← Core scoring engine & rules
│   ├── visualization.py      ← All Plotly chart functions
│   └── utils.py              ← Logging, exports, formatters
│
│── reports/
│   └── exported_reports/     ← Auto-generated reports land here
│
│── tests/
│   └── test_risk_engine.py   ← 30+ unit tests
│
│── notebooks/
│   └── analysis.ipynb        ← EDA notebook
```

---

## 🧮 Risk Score Formula

```
Risk Score =
  (credit_weight   × credit_factor)    +
  (history_weight  × history_factor)   +
  (income_weight   × income_factor)    +
  (debt_weight     × debt_factor)      +
  (loan_weight     × loan_factor)      +
  (employment_weight × employment_factor) +
  (fraud_weight    × fraud_factor)     +
  (security_weight × security_factor)

Final Score = clip(base_score + business_rule_adjustments, 0, 100)
```

### Default Weights

| Factor | Weight | Direction |
|--------|--------|-----------|
| Credit Score | 25% | Lower score → Higher risk |
| Payment History | 20% | Poor history → Higher risk |
| Debt Ratio | 15% | Higher ratio → Higher risk |
| Monthly Income | 10% | Lower income → Higher risk |
| Existing Loans | 10% | More loans → Higher risk |
| Fraud Alerts | 10% | More alerts → Higher risk |
| Employment Years | 5% | Less experience → Higher risk |
| Security Flags | 5% | More flags → Higher risk |

---

## ⚡ Business Rules

| Rule | Condition | Adjustment |
|------|-----------|-----------|
| Fraud Spike | Fraud alerts > 2 | **+15** |
| Heavy Debt | Debt ratio > 70% | **+10** |
| High Income | Monthly income > ₹1,00,000 | **-5** |
| Poor Payments | Payment history = "poor" | **+20** |
| Security Breach | Security flags > 0 | **+25** |
| Transaction Spike | Transactions > 80/month | **+10** |
| New Account | Account age < 6 months | **+8** |
| Insurance Claims | Claims ≥ 3 | **+12** |

---

## 🎯 Risk Categories & Decisions

| Score Range | Category | Decision |
|-------------|----------|----------|
| 0 – 30 | ✅ Low Risk | Approve Loan |
| 31 – 60 | ⚠️ Medium Risk | Review Manually |
| 61 – 80 | 🔴 High Risk | Reject Application |
| 81 – 100 | 💀 Critical Risk | Escalate to Fraud Team |

---

## 📊 Dashboard Screenshots

> *(Add screenshots here after running the app)*

| Section | Description |
|---------|-------------|
| Hero Header | App banner with live risk status |
| KPI Cards | Score, Category, Grade, Fraud status |
| Gauge Chart | Animated risk meter |
| Radar Chart | Multi-factor spider visualization |
| Contribution Bar | Per-factor risk breakdown |
| Explainability | Drivers, reducers, triggered rules |
| Decision Engine | Final loan decision with context |
| Portfolio Analytics | Dataset-wide charts and heatmaps |
| Data Table | Searchable, filterable customer grid |

---

## 🛠️ Tech Stack

- **Python 3.10+** – Core language
- **Pandas & NumPy** – Data manipulation
- **Streamlit** – Interactive web dashboard
- **Plotly** – Interactive charts
- **Matplotlib / Seaborn** – Static visualizations
- **Scikit-learn** – (Ready for ML enhancement)
- **OpenPyXL** – Excel export
- **Pytest** – Unit testing
- **OOP + Logging** – Production patterns

---

## 🔮 Future Enhancements

- [ ] Machine Learning risk model (Random Forest / XGBoost)
- [ ] PDF report generation
- [ ] Role-based access control (Analyst / Manager / Admin)
- [ ] Real-time API data integration (credit bureaus)
- [ ] Multi-language support
- [ ] Dark/Light theme toggle
- [ ] Customer timeline view
- [ ] Anomaly detection module

---

## 💼 Resume Value

This project demonstrates:
- **Data Engineering** – Loading, validating, and cleaning financial data
- **Quantitative Finance** – Weighted scoring, risk modeling
- **Cybersecurity Analytics** – Fraud detection, security flag analysis
- **Full-Stack Python** – From data layer to interactive UI
- **Software Engineering** – OOP, logging, modular architecture, unit tests
- **Data Visualization** – 9+ chart types with professional theming

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

*Built with Python · Streamlit · Plotly · FinRisk Pro v2.0.0*
