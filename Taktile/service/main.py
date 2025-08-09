from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict

from Taktile.stages.T1 import run_aml_first, run_fraud
from Taktile.stages.T2 import evaluate_aml
from Taktile.stages.T4 import evaluate_fraud
from Taktile.clients.experian import ExperianClient
from Taktile.stages.T5_credit import evaluate_credit_policy


app = FastAPI(title="Taktile Orchestrator (T*)", version="1.0.0")

experian = ExperianClient()


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

    # Credit stage (S3 -> T5), only when Fraud PASS
    try:
        # Build minimal Experian payload from intake
        full_name = str(input.intake.get("user_fullname") or "").strip()
        parts = full_name.split()
        first = parts[0] if parts else ""
        last = parts[-1] if len(parts) > 1 else (parts[0] if parts else "CONSUMER")
        scenario_val = ((input.intake.get("custom_fields") or {}).get("scenario"))

        exp_payload = {
            "consumerPii": {
                "primaryApplicant": {
                    "name": {"firstName": first, "lastName": last},
                    "dob": {"dob": input.intake.get("user_dob")},
                    "ssn": {"ssn": input.intake.get("ssn")},
                    "currentAddress": {
                        "line1": input.intake.get("address_line1"),
                        "city": input.intake.get("address_city"),
                        "state": input.intake.get("address_state"),
                        "zipCode": input.intake.get("address_zip"),
                        "country": input.intake.get("user_country") or "US",
                    },
                }
            },
            "permissiblePurpose": {"type": "CREDIT_GRANTING"},
            "addOns": {
                "riskModels": {"modelIndicator": ["V4", "FICO8"], "scorePercentile": "Y"},
                "summaries": {"summaryType": ["PROFILE"]},
                "ofac": "Y",
                "mla": "N",
                "scenario": scenario_val,
            },
        }

        exp_resp = experian.post_credit_report(exp_payload)
        credit_raw = exp_resp.get("data") or {}
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

    return {
        "case_id": input.case_id,
        "status": credit_status,  # CREDIT_DECLINE | CREDIT_REVIEW | CREDIT_PASS
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
