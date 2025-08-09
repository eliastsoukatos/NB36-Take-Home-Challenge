from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict

from Taktile.stages.T1 import run_aml_first, run_fraud
from Taktile.stages.T2 import evaluate_aml
from Taktile.stages.T4 import evaluate_fraud


app = FastAPI(title="Taktile Orchestrator (T*)", version="1.0.0")


class AmlFirstIn(BaseModel):
    case_id: str
    intake: Dict[str, Any] = Field(default_factory=dict)


@app.post("/workflows/kyc/aml-first")
def aml_first(input: AmlFirstIn):
    """
    Orchestrates AML-first flow:
      - T1: Build payload and call SEON AML (no decision)
      - T2: Apply KO logic to AML response
    Returns both the decision and raw AML JSON for transparency.
    """
    try:
        t1 = run_aml_first(case_id=input.case_id, intake=input.intake)
        aml_raw = t1.get("aml_raw")
        decision = evaluate_aml(aml_raw)
    except Exception as e:
        # Bubble up a clear error to the backend; it's expected to handle technical failure
        raise HTTPException(status_code=502, detail=f"AML orchestration error: {e}")

    return {
        "case_id": input.case_id,
        "decision": decision.get("decision"),
        "reasons": decision.get("reasons", []),
        "details": decision.get("details", {}),
        "aml_raw": aml_raw,
    }


class FullKycIn(BaseModel):
    case_id: str
    intake: Dict[str, Any] = Field(default_factory=dict)


@app.post("/workflows/kyc/full")
def kyc_full(input: FullKycIn):
    """
    Orchestrates full KYC flow:
      - AML (T1 -> S1) then T2
      - If AML DECLINE: return AML decision
      - If AML PROCEED: Fraud (S2) then T4 with provisional tier
    Returns combined summary + raw vendor payloads for transparency.
    """
    try:
        # AML stage
        aml_out = run_aml_first(case_id=input.case_id, intake=input.intake)
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

    status = fraud_decision.get("decision") or "FRAUD_REVIEW"
    provisional_tier = fraud_decision.get("provisional_tier")

    return {
        "case_id": input.case_id,
        "status": status,  # FRAUD_DECLINE | FRAUD_REVIEW | FRAUD_PASS
        "aml_decision": aml_decision,
        "fraud_decision": fraud_decision,
        "provisional_tier": provisional_tier,
        "aml_raw": aml_raw,
        "fraud_raw": fraud_raw,
    }
