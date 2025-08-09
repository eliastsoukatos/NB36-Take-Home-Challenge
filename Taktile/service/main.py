from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Any, Dict

from Taktile.stages.T1 import run_aml_first
from Taktile.stages.T2 import evaluate_aml


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
