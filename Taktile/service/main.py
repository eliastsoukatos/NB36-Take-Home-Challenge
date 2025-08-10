from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict

from Taktile.stages.S1 import run_aml
from Taktile.stages.S2 import run_fraud
from Taktile.stages.S3 import get_credit_report
from Taktile.stages.S4 import build_income_options_from_intake, get_income_bundle
from Taktile.stages.T1 import evaluate_aml
from Taktile.stages.T2 import evaluate_fraud
from Taktile.stages.T3 import evaluate_credit_policy
from Taktile.stages.T4 import evaluate_income


app = FastAPI(title="Taktile Orchestrator (S*/T*)", version="1.0.0")


class FullKycIn(BaseModel):
    case_id: str
    intake: Dict[str, Any] = Field(default_factory=dict)


@app.post("/workflows/kyc/full")
def kyc_full(input: FullKycIn):
    """
    Orchestrates full KYC flow:
      - AML: S1 (request) -> T1 (evaluate)
      - If AML DECLINE: return AML decision
      - If AML PROCEED: Fraud: S2 (request) -> T2 (evaluate)
      - Credit: S3 (request) -> T3 (evaluate)
      - Income: S4 (request) -> T4 (evaluate)
    Returns combined summary + raw vendor payloads for transparency.
    """
    try:
        # AML stage
        aml_out = run_aml(case_id=input.case_id, intake=input.intake)
        aml_raw = aml_out.get("aml_raw")
        aml_decision = evaluate_aml(aml_raw)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AML orchestration error: {e}")

    if aml_decision.get("decision") == "DECLINE":
        return {
            "case_id": input.case_id,
            "status": "AML_DECLINE",
            "aml_decision": aml_decision,
            "fraud_decision": None,
            "provisional_tier": None,
            "aml_raw": aml_raw,
            "fraud_raw": None,
        }

    # Fraud stage (only when AML passed)
    try:
        fraud_out = run_fraud(case_id=input.case_id, intake=input.intake)
        fraud_raw = fraud_out.get("fraud_raw")
        fraud_decision = evaluate_fraud(fraud_raw)
    except Exception as e:
        # If fraud stage fails technically, surface as Taktile error (backend may map to review/decline)
        raise HTTPException(status_code=502, detail=f"Fraud orchestration error: {e}")

    fraud_status = fraud_decision.get("decision") or "FRAUD_REVIEW"
    provisional_tier = fraud_decision.get("provisional_tier")

    # If Fraud did not PASS, return here
    if fraud_status != "FRAUD_PASS":
        return {
            "case_id": input.case_id,
            "status": fraud_status,  # FRAUD_DECLINE | FRAUD_REVIEW
            "aml_decision": aml_decision,
            "fraud_decision": fraud_decision,
            "provisional_tier": provisional_tier,
            "aml_raw": aml_raw,
            "fraud_raw": fraud_raw,
        }

    # Credit stage (S3 -> T3), only when Fraud PASS
    try:
        envelope = get_credit_report(input.intake)
        credit_raw = envelope.get("data") or {}
        credit_eval = evaluate_credit_policy(credit_raw, provisional_tier, None)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Credit orchestration error: {e}")

    credit_status_map = {
        "CREDIT_DECLINE": "CREDIT_DECLINE",
        "CREDIT_REVIEW": "CREDIT_REVIEW",
        "CREDIT_PASS": "CREDIT_PASS",
    }
    credit_status = credit_status_map.get(credit_eval.get("decision") or "", "CREDIT_REVIEW")

    credit_decision = {
        "decision": credit_status,
        "bureau_tier": credit_eval.get("bureau_tier"),
        "final_tier": credit_eval.get("final_tier"),
        "ko_reasons": credit_eval.get("ko_reasons", []),
        "review_reasons": credit_eval.get("review_reasons", []),
        "scorecard": credit_eval.get("scorecard", {}),
    }

    # If credit did not PASS, return here
    if credit_status != "CREDIT_PASS":
        return {
            "case_id": input.case_id,
            "status": credit_status,  # CREDIT_DECLINE | CREDIT_REVIEW
            "aml_decision": aml_decision,
            "fraud_decision": fraud_decision,
            "credit_decision": credit_decision,
            "provisional_tier": provisional_tier,  # from fraud
            "bureau_tier": credit_eval.get("bureau_tier"),
            "final_tier": credit_eval.get("final_tier"),
            "aml_raw": aml_raw,
            "fraud_raw": fraud_raw,
            "credit_raw": credit_raw,
        }

    # Income stage (Plaid mock) — run only after CREDIT_PASS
    try:
        options = build_income_options_from_intake(input.intake)

        # Use client_user_id if present; else derive a stable key from case_id
        client_user_id = str(input.intake.get("client_user_id") or input.case_id)

        bundle = get_income_bundle(client_user_id, options=options)

        income_eval = evaluate_income(
            payroll_resp=bundle.get("payroll_resp"),
            bank_resp=bundle.get("bank_resp"),
            risk_resp=bundle.get("risk_resp"),
            coverage_months=int(options.get("coverage_months") or 12),
            credit_final_tier=credit_decision.get("final_tier"),
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Income orchestration error: {e}")

    income_status = income_eval.get("decision") or "INCOME_REVIEW"

    return {
        "case_id": input.case_id,
        "status": income_status,  # INCOME_DECLINE | INCOME_REVIEW | INCOME_PASS
        "aml_decision": aml_decision,
        "fraud_decision": fraud_decision,
        "credit_decision": credit_decision,
        "income_decision": income_eval,
        "provisional_tier": provisional_tier,  # from fraud
        "bureau_tier": credit_eval.get("bureau_tier"),
        "final_tier": income_eval.get("final_tier"),
        "aml_raw": aml_raw,
        "fraud_raw": fraud_raw,
        "credit_raw": credit_raw,
    }
