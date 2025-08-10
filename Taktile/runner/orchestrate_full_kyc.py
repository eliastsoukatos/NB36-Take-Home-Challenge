"""
DEPRECATED: Use the consolidated runner instead.

Run:
  python -m Taktile.runner.orchestrate full --scenario pass
or:
  python Taktile/runner/orchestrate.py full --scenario pass
"""

import sys
from Taktile.runner.orchestrate import run_full, DEFAULT_BASE


def main() -> None:
    scenario = sys.argv[1] if len(sys.argv) > 1 else "pass"
    case_id = "demo-full-001"
    # Pretty-print for readability
    run_full(DEFAULT_BASE, case_id, scenario, income_opts={}, pretty=True)


if __name__ == "__main__":
    main()
