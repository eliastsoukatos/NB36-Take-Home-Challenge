"""
Taktile stages package

S-series (Sources): Perform external API calls and build payloads.
  - S1: SEON AML request
  - S2: SEON Fraud request
  - S3: Experian Credit report
  - S4: Plaid Income bundle

T-series (Transforms): Pure evaluation/policy.
  - T1: AML evaluation
  - T2: Fraud evaluation
  - T3: Credit policy
  - T4: Income policy
"""

# Sources
from .S1 import build_aml_payload, run_aml  # noqa: F401
from .S2 import build_fraud_payload, run_fraud  # noqa: F401
from .S3 import build_experian_payload, get_credit_report  # noqa: F401
from .S4 import build_income_options_from_intake, get_income_bundle  # noqa: F401

# Transforms
from .T1 import evaluate_aml  # noqa: F401
from .T2 import evaluate_fraud  # noqa: F401
from .T3 import evaluate_credit_policy, CONFIG as CREDIT_CONFIG  # noqa: F401
from .T4 import evaluate_income  # noqa: F401
