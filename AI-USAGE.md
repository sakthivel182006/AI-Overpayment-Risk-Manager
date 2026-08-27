# AI-USAGE.md

# AI Usage Disclosure

## 1. Purpose

AI assistance was used during development of the AI Overpayment Risk
Manager project.

The project remains a code-based ML/data-analysis prototype. Generated
suggestions were reviewed, executed, tested, and iterated during
development.

## 2. Areas Where AI Assistance Was Used

AI assistance was used for:

-   Project structure planning
-   Python code generation and refinement
-   Feature-engineering implementation
-   Risk-scoring implementation
-   Ranking implementation
-   Plain-language explanation generation
-   Fairness-analysis implementation
-   Investigator-feedback integration
-   Automated test generation
-   Documentation drafting
-   Debugging assistance
-   Explaining runtime errors
-   Command-line guidance

## 3. Human Verification

Generated code was not accepted blindly.

The implementation was:

1.  Added to the local project.
2.  Executed against the supplied dataset.
3.  Checked through command-line outputs.
4.  Updated when runtime errors occurred.
5.  Tested using automated unit tests.

The current automated test suite contains:

``` text
23 tests
23 passed
0 failed
```

The complete application also runs using:

``` bash
python main.py
```

## 4. AI-Generated Code Review

AI-generated code was reviewed and adapted to the actual project
structure.

Particular attention was given to:

-   input/output paths
-   feature names
-   risk-score columns
-   ranking behaviour
-   fairness dimensions
-   investigator-feedback behaviour
-   CSV output generation
-   human-review safeguards

## 5. Investigator Feedback

AI assistance was used to help incorporate the investigator feedback
concerning case `C-33248`.

The resulting implementation preserves the original risk score and adds
investigator-context information instead of treating administrative
activity as automatic evidence of improper payment.

## 6. Fairness and Governance

AI assistance was used to help structure fairness analysis and
governance documentation.

Observed disparities were not intentionally changed simply to produce
better-looking numbers.

The project reports observed disparities and identifies further
validation as necessary before real-world deployment.

## 7. Limitations of AI Assistance

AI-generated suggestions may contain errors or assumptions.

Therefore:

-   Runtime behaviour was verified locally.
-   Test results were checked.
-   Generated explanations were reviewed.
-   Model decisions were treated as design choices requiring human
    review.
-   AI output was not treated as evidence of real-world policy or legal
    correctness.

## 8. Final Responsibility

The final project structure, implementation decisions, testing,
interpretation of outputs, and submission are subject to human review
and responsibility.

AI assistance was used as a development aid, not as an autonomous
decision-maker.
