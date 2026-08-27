# DECISIONS.md

# AI Overpayment Risk Manager --- Decision Log

## 1. Project Objective

The objective is to help investigators review a limited number of cases
by producing a ranked worklist of the 20 cases most worth reviewing.

The system is a **decision-support tool**. It identifies payment
patterns that deserve human investigation. It does not determine that a
payment is improper and it does not make an automatic enforcement
decision.

## 2. Problem Approach

We chose an explainable, evidence-based risk scoring approach rather
than a black-box model.

Pipeline:

``` text
cases.csv + payments.csv
        ↓
Data Loading
        ↓
Feature Engineering
        ↓
Risk Scoring
        ↓
Investigator Feedback
        ↓
Ranking
        ↓
TOP 20 Worklist
        ↓
Plain-Language Explanations
        ↓
Fairness Analysis
```

The approach was selected because investigators need to understand why a
case appears near the top of the worklist.

## 3. Data Used

The project uses:

``` text
data/
├── cases.csv
└── payments.csv
```

Current dataset:

-   4,200 cases
-   24,756 payment records

## 4. Feature Engineering Decisions

The feature engineering stage creates payment-behaviour features
including:

-   payment count
-   total paid
-   average payment
-   maximum payment
-   payment standard deviation
-   average payment-to-award ratio
-   maximum payment-to-award ratio
-   payment variability
-   adjustment rate
-   award-to-needs ratio
-   unusual payment count
-   first-month payment
-   last-month payment
-   first-to-last payment change
-   first-to-last percentage change
-   high-payment months
-   months above award
-   largest monthly increase
-   largest monthly decrease

The final feature dataset contains 35 columns.

Payment-to-award ratios are important because a payment amount alone is
difficult to interpret. Comparing payment amounts with the recorded
monthly award creates a more meaningful review signal.

## 5. Risk Scoring Decision

The risk score is designed to prioritize cases using payment anomalies.

Important signals include:

1.  Average payment relative to the recorded award
2.  Maximum payment relative to the recorded award
3.  Number of months with high payments
4.  Number of months above the recorded award
5.  Payment variability

The score is normalized to a 0--100 range.

A higher score means:

> The payment pattern deserves higher investigation priority.

It does **not** mean:

> The case has been proven to contain an improper payment.

## 6. Monthly Pattern Decision

Monthly-pattern features were added because a single unusual payment can
have a legitimate explanation.

Persistent behaviour across several months provides a stronger review
signal.

The system therefore considers repeated payment behaviour across the
available monthly history.

## 7. Investigator Feedback --- C-33248

The investigator feedback provided an important governance lesson.

Case `C-33248` had:

-   5 payment adjustments
-   7 contact attempts
-   Risk score: 12.77

The investigator feedback indicated that the adjustments were
departmental corrections and the contact attempts had a
communication-related explanation.

Therefore:

> Administrative activity should not automatically be treated as
> evidence of improper payment.

The implementation adds an `administrative_activity_flag` and
explanatory context while preserving the original payment-risk score.

This prevents administrative activity from automatically increasing
suspicion.

## 8. Explanation Decision

Every TOP 20 case receives a plain-language explanation.

Explanations can include:

-   average payment-to-award ratio
-   maximum payment-to-award ratio
-   persistence of high payments
-   months above award
-   payment variability
-   administrative-context warning where applicable

The explanation also states:

> This is a review signal, not a finding of improper payment.

## 9. Ranking Decision

The ranking module sorts all 4,200 cases by final risk score and assigns
an investigator rank.

The TOP 20 is the investigator worklist.

The complete ranking is also saved so the TOP 20 can be understood in
the wider population.

## 10. Fairness Decision

Fairness is evaluated across:

-   age band
-   language preference
-   district
-   tenure

The current analysis identified disparities, including:

``` text
Age 60–74        1.68
Age 75+          0.40
Spanish          1.65
Other language   0.00
Ash Hill         1.90
Northgate        0.56
Private tenancy  1.77
Social tenancy   0.48
```

These results are not hidden or artificially corrected.

### Decision

The current system reports these disparities honestly rather than
changing the ranking only to make the fairness statistics look better.

Before real-world use, these disparities require further investigation
and validation.

## 11. Sensitive/Protected Attributes

Demographic attributes are used for **fairness evaluation**, not as
direct evidence that a payment is improper.

The risk score is based primarily on payment behaviour and award
relationships.

## 12. Human Oversight

The system must remain human-in-the-loop.

It should:

``` text
Prioritize cases
        ↓
Explain the signals
        ↓
Support investigator review
```

It should not:

``` text
Automatically declare fraud
Automatically stop a payment
Automatically recover money
Automatically penalize a resident
Automatically make an eligibility decision
```

## 13. Current Limitations

This is a hackathon prototype using the supplied dataset.

Important limitations:

-   The ranking is not validated on real operational data.
-   A high score is not proof of an improper payment.
-   Fairness disparities are present and require further investigation.
-   The administrative-context rule is based on limited investigator
    feedback.
-   Thresholds and scoring weights have not been validated with domain
    experts.
-   Production monitoring and model-drift detection are not implemented.
-   There is no automated investigator feedback-learning loop.

## 14. What Would Be Needed Before Real-World Use

Before deployment on real residents, we would need:

1.  Domain-expert validation of features and thresholds.
2.  Historical investigation outcomes for validation.
3.  Out-of-sample testing.
4.  Precision/recall evaluation against reliable labels.
5.  Calibration and threshold analysis.
6.  Detailed fairness evaluation.
7.  Investigation of the causes of observed group disparities.
8.  Human-review procedures and escalation rules.
9.  Privacy and security review.
10. Model monitoring and drift detection.
11. Audit logging.
12. Clear governance and accountability ownership.

## 15. Final Design Principle

> **Use ML to prioritize investigation, not to replace investigation.**
