"""
DEPRECATED: Use the consolidated runner instead.

Run:
  python -m Taktile.runner.orchestrate aml-first --scenario pass
or:
  python Taktile/runner/orchestrate.py aml-first --scenario pass
"""

import sys
from Taktile.runner.orchestrate import run_aml_first, DEFAULT_BASE


def main() -> None:
    scenario = sys.argv[1] if len(sys.argv) > 1 else "pass"
    case_id = "demo-aml-001"
    # Pretty-print for readability
    run_aml_first(DEFAULT_BASE, case_id, scenario, pretty=True)


if __name__ == "__main__":
    main()
