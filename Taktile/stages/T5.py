"""
DEPRECATED MODULE

This project now uses:
  - T3.evaluate_credit_policy for credit policy evaluation
  - S3.get_credit_report for Experian requests

If you are importing from T5, update your imports to:
  from Taktile.stages.T3 import evaluate_credit_policy
"""

raise ImportError("Taktile.stages.T5 is deprecated. Use Taktile.stages.T3.evaluate_credit_policy instead.")
