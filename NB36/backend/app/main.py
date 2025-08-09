from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

from .stages import B1
from .clients.taktile_client import TaktileClient

app = FastAPI(title="NB36 Backend (B*) — orchestrates via Taktile (T*)")

# CORS for local development (frontend -> backend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost",
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

taktile = TaktileClient()


class ApplicationIntake(BaseModel):
    user_fullname: str
    user_dob: str
    user_country: str
    ssn: str
    gov_id_type: str
    gov_id_number: str
    address_line1: str
    address_city: str
    address_state: str
    address_zip: str
    email: str
    phone_number: str
    ip: Optional[str] = None
    session: Optional[str] = None
    custom_fields: Optional[Dict[str, Any]] = Field(default_factory=dict)


@app.post("/apply/aml-first")
def apply_aml_first(intake: ApplicationIntake):
    # B1: Create case
    case = B1.create_case(intake.dict())
    # Delegate workflow to Taktile (T*)
    try:
        result = taktile.aml_first(case_id=case["case_id"], intake=case["intake"])
    except Exception as e:
        # Technical failure contacting Taktile — mark case accordingly
        B1.update_case(case["case_id"], status="AML_DECLINE")
        B1.append_timeline(
            case["case_id"],
            "taktile.error",
            {"error": str(e)},
        )
        return {
            "case_id": case["case_id"],
            "status": "AML_DECLINE",
            "aml_decision": {
                "decision": "DECLINE",
                "reasons": ["taktile_unavailable_or_error"],
                "details": {"exception": str(e)},
            },
            "message": "AML stage failed due to technical error contacting Taktile.",
        }

    # Persist AML outcome on case
    aml_decision = {
        "decision": result.get("decision"),
        "reasons": result.get("reasons", []),
        "details": result.get("details", {}),
    }
    B1.update_case(
        case["case_id"],
        status=f"AML_{aml_decision['decision']}",
        aml_raw=result.get("aml_raw"),
        aml_decision=aml_decision,
    )
    B1.append_timeline(case["case_id"], "aml.completed", {"decision": aml_decision})

    return {
        "case_id": case["case_id"],
        "status": f"AML_{aml_decision['decision']}",
        "aml_decision": aml_decision,
        "message": "AML stage completed via Taktile.",
    }


@app.post("/apply/kyc")
def apply_kyc(intake: ApplicationIntake):
    # B1: Create case
    case = B1.create_case(intake.dict())
    # Delegate full KYC (AML + Fraud) to Taktile (T*)
    try:
        result = taktile.kyc_full(case_id=case["case_id"], intake=case["intake"])
    except Exception as e:
        # Technical failure contacting Taktile — treat as review for this stage
        B1.update_case(case["case_id"], status="FRAUD_REVIEW")
        B1.append_timeline(case["case_id"], "taktile.error", {"error": str(e)})
        return {
            "case_id": case["case_id"],
            "status": "FRAUD_REVIEW",
            "aml_decision": None,
            "fraud_decision": {
                "decision": "FRAUD_REVIEW",
                "reasons": ["taktile_unavailable_or_error"],
                "details": {"exception": str(e)},
            },
            "provisional_tier": None,
            "message": "KYC stage failed due to technical error contacting Taktile.",
        }

    # Persist outcome on case
    aml_decision = result.get("aml_decision")
    fraud_decision = result.get("fraud_decision")
    provisional_tier = result.get("provisional_tier")

    # New credit stage outputs (present only if fraud passed)
    credit_decision = result.get("credit_decision")
    bureau_tier = result.get("bureau_tier")
    final_tier = result.get("final_tier")

    # New income stage outputs (present only if credit passed)
    income_decision = result.get("income_decision")

    status = result.get("status") or ("AML_DECLINE" if (aml_decision and aml_decision.get("decision") == "DECLINE") else None)

    B1.update_case(
        case["case_id"],
        status=status,
        aml_raw=result.get("aml_raw"),
        aml_decision=aml_decision,
        fraud_raw=result.get("fraud_raw"),
        fraud_decision=fraud_decision,
        provisional_tier=provisional_tier,
        credit_raw=result.get("credit_raw"),
        credit_decision=credit_decision,
        bureau_tier=bureau_tier,
        # Persist income if provided
        income_decision=income_decision,
        final_tier=final_tier,
    )
    if fraud_decision is not None:
        B1.append_timeline(case["case_id"], "fraud.screened", {"decision": fraud_decision})
    if credit_decision is not None:
        B1.append_timeline(case["case_id"], "credit.screened", {"decision": credit_decision})
    if income_decision is not None:
        B1.append_timeline(case["case_id"], "income.screened", {"decision": income_decision})
    B1.append_timeline(case["case_id"], "kyc.completed", {"status": status})

    return {
        "case_id": case["case_id"],
        "status": status,
        "aml_decision": aml_decision,
        "fraud_decision": fraud_decision,
        "provisional_tier": provisional_tier,
        "credit_decision": credit_decision,
        "income_decision": income_decision,
        "bureau_tier": bureau_tier,
        "final_tier": final_tier,
        "message": "End-to-end KYC (AML + Fraud + Credit + Income) completed for demo",
    }


@app.get("/cases/{case_id}")
def get_case(case_id: str):
    c = B1.get_case(case_id)
    if not c:
        raise HTTPException(status_code=404, detail="Case not found")
    return c
