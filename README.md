# AI Overpayment Risk Manager

An explainable ML/data-analysis prototype that helps investigators
prioritize potentially unusual payment cases for human review.

The system analyzes payment behaviour against recorded monthly awards,
ranks the 20 cases most worth reviewing, generates plain-language
reasons, and reports how the ranking behaves across population groups.

> **Important:** A high risk score is a review signal, not a finding of
> improper payment.

## Problem

Investigators can only review a limited number of cases each week.

The goal is to produce:

-   a ranked worklist of the 20 cases most worth reviewing
-   a plain-language reason for each case
-   honest population-level fairness analysis
-   investigator context for administrative activity

The project is a decision-support prototype rather than an automatic
fraud or recovery system.

## Key Features

### 1. Payment Pattern Analysis

The system identifies:

-   payments substantially above the recorded award
-   repeated high payments
-   payments above award across multiple months
-   unusually large individual payments
-   payment variability
-   monthly increases and decreases

### 2. Explainable Risk Score

Each case receives a risk score from 0 to 100.

The score uses interpretable payment-behaviour features rather than a
black-box prediction.

### 3. TOP 20 Investigator Worklist

All 4,200 cases are ranked and the 20 highest-priority cases are
selected.

### 4. Plain-Language Explanations

Each TOP 20 case receives a reason explaining the main payment signals
behind its priority.

### 5. Investigator Feedback

The system incorporates the lesson from reviewed case `C-33248`.

Administrative activity such as payment adjustments and contact attempts
is treated as **context**, not automatic evidence of improper payment.

### 6. Fairness Analysis

The worklist is evaluated across:

-   age band
-   language preference
-   district
-   tenure

The project reports observed disparities rather than hiding them.

### 7. Automated Tests

The project includes automated tests covering:

-   data loading
-   feature engineering
-   risk scoring
-   ranking

Current result:

``` text
23 tests passed
0 failed
```

# Project Structure

``` text
AI-Overpayment-Risk-Manager/
│
├── data/
│   ├── cases.csv
│   └── payments.csv
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_pattern_discovery.ipynb
│   ├── 03_risk_model.ipynb
│   └── 04_fairness_analysis.ipynb
│
├── outputs/
│   ├── all_ranked_cases.csv
│   ├── top20_cases.csv
│   ├── fairness_report.csv
│   ├── case_explanations.csv
│   └── investigator_feedback_analysis.csv
│
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── feature_engineering.py
│   ├── pattern_analysis.py
│   ├── risk_scoring.py
│   ├── ranking.py
│   ├── explanations.py
│   ├── fairness.py
│   └── investigator_feedback.py
│
├── tests/
│   ├── test_data_loader.py
│   ├── test_features.py
│   ├── test_ranking.py
│   └── test_risk_scoring.py
│
├── main.py
├── requirements.txt
├── DECISIONS.md
├── AI-USAGE.md
└── README.md
```

# Project Architecture

``` text
                    cases.csv
                        │
                    payments.csv
                        │
                        ▼
                ┌─────────────────┐
                │  Data Loading    │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │    Feature      │
                │   Engineering   │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │  Risk Scoring   │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │  Investigator   │
                │    Feedback     │
                └────────┬────────┘
                         ▼
                ┌─────────────────┐
                │    Ranking      │
                └────────┬────────┘
                         ▼
                 TOP 20 Worklist
                         │
              ┌──────────┴──────────┐
              ▼                     ▼
       Explanations            Fairness
                                Analysis
              │                     │
              └──────────┬──────────┘
                         ▼
                      Outputs
```

# Technologies

-   Python
-   Pandas
-   NumPy
-   Scikit-learn
-   Jupyter Notebook
-   Unittest
-   CSV-based data processing

# Dataset

The supplied dataset contains:

``` text
Cases    : 4,200
Payments : 24,756
```

The system processes the supplied data locally.

# Installation

## 1. Clone the repository

``` bash
git clone <your-github-repository-url>
cd AI-Overpayment-Risk-Manager
```

## 2. Create a virtual environment (recommended)

Windows:

``` bash
python -m venv venv
venv\Scripts\activate
```

Linux/macOS:

``` bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install dependencies

``` bash
pip install -r requirements.txt
```

# How to Run the Complete Project

The recommended command is:

``` bash
python main.py
```

This runs the complete pipeline:

``` text
Feature Engineering
        ↓
Risk Scoring
        ↓
Investigator Feedback
        ↓
Ranking
        ↓
TOP 20 Explanations
        ↓
Fairness Analysis
```

# Individual Development Commands

Individual modules can also be executed during development:

## Data Loader

``` bash
python src/data_loader.py
```

## Pattern Analysis

``` bash
python src/pattern_analysis.py
```

## Feature Engineering

``` bash
python src/feature_engineering.py
```

## Risk Scoring

``` bash
python src/risk_scoring.py
```

## Ranking

``` bash
python src/ranking.py
```

## Investigator Feedback

``` bash
python src/investigator_feedback.py
```

## Explanations

``` bash
python src/explanations.py
```

## Fairness Analysis

``` bash
python src/fairness.py
```

For the final demonstration, use:

``` bash
python main.py
```

# Running Tests

Run the complete automated test suite:

``` bash
python -m unittest discover -s tests -v
```

Expected result:

``` text
Ran 23 tests

OK
```

# Output Files

After running the project, important outputs are stored in:

``` text
outputs/
```

### `all_ranked_cases.csv`

Contains the complete ranked case population.

### `top20_cases.csv`

Contains the 20 highest-priority cases for investigator review.

### `fairness_report.csv`

Contains group-level fairness and selection-rate analysis.

### `investigator_feedback_analysis.csv`

Contains administrative-context analysis associated with investigator
feedback.

# Example Result

The current pipeline produces a TOP 20 worklist.

The highest-ranked case in the current supplied data is:

``` text
C-31298
Risk Score: 88.66
```

Its payment pattern includes:

``` text
Average payment / award : 2.68x
Maximum payment / award : 2.96x
High-payment months     : 6
Months above award     : 6
```

These are review signals, not proof of fraud or definitively improper
payment.

# Fairness

The system evaluates selection behaviour across:

``` text
Age band
Language preference
District
Tenure
```

The current analysis identifies differences in selection rates between
groups.

These results are intentionally reported rather than hidden.

A production deployment would require further investigation into the
causes of these disparities and validation with appropriate domain
experts and historical outcomes.

# Investigator Feedback and Governance

The project incorporates investigator feedback from case `C-33248`.

The feedback demonstrated that administrative activity can have
legitimate explanations.

Therefore:

``` text
Payment anomaly
      +
Administrative activity
      ↓
Investigator context
```

rather than:

``` text
Administrative activity
      ↓
Automatically higher risk
```

The system remains human-in-the-loop.

A high score means:

> Review this case earlier.

It does not mean:

> This person committed fraud.

# Limitations

This is a hackathon prototype.

It should not be treated as a production decision system because:

-   the data is the supplied challenge dataset
-   risk-score weights are not operationally validated
-   fairness disparities remain
-   real investigation outcomes are not available for full validation
-   production monitoring is not implemented
-   privacy/security controls are not production-complete
-   human governance procedures would need to be established

# Before Real-World Deployment

The system would require:

-   domain-expert validation
-   historical outcome validation
-   precision/recall measurement
-   threshold calibration
-   fairness investigation
-   privacy and security review
-   audit logging
-   monitoring and drift detection
-   human-review procedures
-   clear accountability and escalation rules

# Documentation

Additional project decisions are documented in:

``` text
DECISIONS.md
```

AI assistance and verification are documented in:

``` text
AI-USAGE.md
```

# Final Principle

> **Prioritize investigation. Explain the evidence. Keep humans
> accountable for the decision.**
