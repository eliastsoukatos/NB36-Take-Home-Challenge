"""
DEPRECATED MODULE

This project now uses:
  - T4.evaluate_income for income evaluation
  - S4.get_income_bundle for Plaid requests

If you are importing from T6, update your imports to:
  from Taktile.stages.T4 import evaluate_income
"""

raise ImportError("Taktile.stages.T6 is deprecated. Use Taktile.stages.T4.evaluate_income instead.")
