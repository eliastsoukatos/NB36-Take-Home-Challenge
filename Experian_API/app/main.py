"""
Mock Experian US Credit Profile API (v2) - FastAPI single-file service

README (developer quickstart)
- Install:
    pip install fastapi uvicorn pydantic

- Run (port 8000):
    uvicorn Experian_API.app.main:app --reload --port 8000

- Health:
    curl -s http://localhost:8000/

- Success example:
    curl -X POST http://localhost:8000/v2/credit-report \
      -H "Authorization: Bearer sandbox-token" \
      -H "clientReferenceId: SBMYSQL" \
      -H "Content-Type: application/json" \
      -H "Accept: application/json" \
      -d '{
            "consumerPii": {
              "primaryApplicant": {
                "name": { "firstName": "JON", "lastName": "CONSUMER" },
                "dob": { "dob": "1991-01-01" },
                "ssn": { "ssn": "123-45-6789" },
                "currentAddress": { "line1": "1475 MAIN ST", "city": "ANYTOWN", "state": "WA", "zipCode": "12345", "country": "US" }
              }
            }
          }'

- Error simulations (set lastName):
  FAIL_400 -> 400, FAIL_403 -> 403, FAIL_404 -> 404, FAIL_500 -> 500, TIMEOUT -> ~12s delay then 504
"""

from __future__ import annotations

import asyncio
import uuid
from typing import List, Optional

from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel


# --------- Pydantic request models (minimal fields we use) ---------


class Name(BaseModel):
    firstName: Optional[str] = None
    middleName: Optional[str] = None
    lastName: str
    generationCode: Optional[str] = None
    prefix: Optional[str] = None


class Dob(BaseModel):
    dob: Optional[str] = None  # ISO or YYYY-MM-DD


class SSN(BaseModel):
    ssn: Optional[str] = None


class Address(BaseModel):
    line1: Optional[str] = None
    line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zipCode: Optional[str] = None
    country: Optional[str] = None


class PrimaryApplicant(BaseModel):
    name: Name
    dob: Optional[Dob] = None
    ssn: Optional[SSN] = None
    currentAddress: Optional[Address] = None
    previousAddress: Optional[List[Address]] = None


class ConsumerPii(BaseModel):
    primaryApplicant: PrimaryApplicant


class CreditReportRequest(BaseModel):
    consumerPii: ConsumerPii
    requestor: Optional[dict] = None
    permissiblePurpose: Optional[dict] = None
    addOns: Optional[dict] = None


# --------- Header / Auth dependency ---------


def require_headers(
    authorization: str = Header(..., alias="Authorization"),
    client_ref_id: str = Header(..., alias="clientReferenceId"),
    content_type: str = Header(..., alias="Content-Type"),
    accept: str = Header(..., alias="Accept"),
) -> dict:
    # Basic header validation (bearer and content types)
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization scheme")
    token = authorization.split(" ", 1)[1]
    if token != "sandbox-token":
        raise HTTPException(status_code=401, detail="Invalid bearer token")

    if content_type.lower() != "application/json":
        raise HTTPException(status_code=415, detail="Unsupported Content-Type")
    if "application/json" not in accept.lower():
        raise HTTPException(status_code=406, detail="Not Acceptable")

    return {
        "clientReferenceId": client_ref_id,
    }


# --------- Error helpers (shaped like OAS examples) ---------


def error_body(status: int, code: str, message: str) -> dict:
    # Minimal shape with headerRecordError, errors, endTotalsError
    return {
        "creditProfile": [
            {
                "headerRecordError": [
                    {
                        "code": code,
                        "message": message,
                    }
                ],
                "endTotalsError": [
                    {
                        "code": code,
                        "message": message,
                    }
                ],
            }
        ],
        "errors": [
            {
                "code": code,
                "message": message,
                "status": str(status),
            }
        ],
        "arf": {"arfResponse": "N/A"},
        "tty": {"ttyResponse": "N/A"},
        "dataSource": {"dataSourceResponse": "BUREAU"},
        "referenceIds": [],
    }


def make_timeout_body() -> dict:
    return error_body(504, "TIMEOUT", "Gateway Timeout")


# --------- Success body (sample-based) ---------


def make_success_body(req: CreditReportRequest) -> dict:
    # Could mirror request fields into response if desired; here we return a static but realistic sample.
    return {
        "creditProfile": [
            {
                "headerRecord": [
                    {
                        "reportDate": "063015",
                        "reportTime": "120000",
                        "preamble": "TCA1",
                        "versionNo": "07",
                        "mKeywordLength": "20",
                        "mKeywordText": "SEQM0CK000000000000",
                        "y2kReportedDate": "06302015",
                        "inquiringSubcode": "",
                        "reportCode": "",
                        "applicationCode": "",
                    }
                ],
                "consumerIdentity": {
                    "dob": {"day": "01", "month": "01", "year": "1991"},
                    "name": [
                        {"firstName": "JON", "middleName": "", "surname": "CONSUMER", "type": "A"},
                        {"firstName": "JONATHAN", "middleName": "", "surname": "CONSUMER", "type": "V"},
                        {"firstName": "J", "middleName": "", "surname": "CONSUMER", "type": "V"},
                    ],
                },
                "addressInformation": [
                    {
                        "streetPrefix": "1475",
                        "streetName": "MAIN ST",
                        "city": "ANYTOWN",
                        "state": "USA",
                        "zipCode": "12345-1475",
                        "dwellingType": "Single family",
                        "censusGeoCode": "0-70010-17-2520",
                        "firstReportedDate": "01012013",
                        "lastUpdatedDate": "01012015",
                        "timesReported": "1",
                    },
                    {
                        "streetPrefix": "1036",
                        "streetName": "MAIN ST APT143",
                        "city": "ANYTOWN",
                        "state": "USA",
                        "zipCode": "12345-3043",
                        "dwellingType": "Apartment complex",
                        "censusGeoCode": "0-1020410-17-2520",
                        "firstReportedDate": "01012014",
                        "lastUpdatedDate": "01012015",
                        "timesReported": "1",
                    },
                ],
                "statement": [
                    {
                        "dateReported": "06302015",
                        "statementText": "FILE FROZEN DUE TO STATE LEGISLATION.",
                        "type": "General",
                    }
                ],
                "publicRecord": [],
                "inquiry": [
                    {
                        "date": "08062013",
                        "subscriberName": "EXPERIAN",
                        "type": "SOFT",
                        "terms": "",
                        "amount": "",
                    }
                ],
                "riskModel": [
                    {
                        "modelIndicator": "V4",
                        "score": "690",
                        "grade": "",
                        "evaluation": "OK",
                        "scorePercentile": "55",
                        "scoreFactors": [
                            {"importance": "H", "code": "HIGH_UTILIZATION"},
                            {"importance": "M", "code": "PAST_DUE_HISTORY"},
                        ],
                    }
                ],
                "fraudShield": [
                    {
                        "fraudShieldIndicators": {"indicator": ["5"]},
                        "addressCount": "2",
                        "socialCount": "2",
                        "text": "No fraud alerts on file.",
                    }
                ],
                "ofac": {"messageNumber": "", "messageText": ""},
                "tradeline": [
                    {
                        "subscriberName": "123 CREDIT CARDS",
                        "subscriberCode": "0122868651",
                        "accountNumber": "4003XXXXXXXX",
                        "accountType": "Credit card",
                        "revolvingOrInstallment": "R",
                        "openOrClosed": "O",
                        "terms": "REV",
                        "status": "Open",
                        "statusDate": "062015",
                        "openDate": "112013",
                        "balanceAmount": "273",
                        "balanceDate": "06032015",
                        "amountPastDue": "20",
                        "enhancedPaymentData": {
                            "creditLimitAmount": "",
                            "highBalanceAmount": "14219",
                            "enhancedPaymentHistory84": "",
                            "enhancedPaymentStatus": "30",
                        },
                        "paymentHistory": "OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK,OK",
                    },
                    {
                        "subscriberName": "HOMETOWN AUTO",
                        "subscriberCode": "0122868651",
                        "accountNumber": "1032911005",
                        "accountType": "Auto",
                        "revolvingOrInstallment": "I",
                        "openOrClosed": "O",
                        "terms": "60 MONTHS",
                        "status": "Current",
                        "statusDate": "052015",
                        "openDate": "032013",
                        "balanceAmount": "11616",
                        "amount1": "19118",
                        "amount1Qualifier": "ORIGINAL_LOAN_AMOUNT",
                        "monthlyPaymentAmount": "350",
                        "enhancedPaymentData": {
                            "highBalanceAmount": "19118",
                            "enhancedPaymentStatus": "OK",
                        },
                        "paymentHistory": "OK x 24 months",
                    },
                    {
                        "subscriberName": "AMERICAN APARTMENTS",
                        "subscriberCode": "0122868651",
                        "accountNumber": "48886031311",
                        "accountType": "Rental",
                        "revolvingOrInstallment": "I",
                        "openOrClosed": "C",
                        "terms": "12 MONTHS",
                        "status": "Inactive/Never late",
                        "statusDate": "052015",
                        "openDate": "102014",
                        "balanceAmount": "4000",
                        "amount1": "12000",
                        "amount1Qualifier": "ORIGINAL_AMOUNT",
                        "monthlyPaymentAmount": "1000",
                        "enhancedPaymentData": {
                            "highBalanceAmount": "12000",
                            "enhancedPaymentStatus": "OK",
                        },
                        "paymentHistory": "OK x 12 months",
                    },
                ],
                "endTotals": [{"totalSegments": "20", "totalLength": "5000"}],
            }
        ],
        "arf": {"arfResponse": "N/A"},
        "tty": {"ttyResponse": "N/A"},
        "dataSource": {"dataSourceResponse": "BUREAU"},
        "referenceIds": [],
    }


# --------- FastAPI app ---------


app = FastAPI(title="Mock Experian Credit Profile", version="0.1.0")


@app.get("/")
async def root():
    return {"status": "ok", "service": "mock-experian-credit-profile"}


@app.post("/v2/credit-report")
async def credit_report(
    req: CreditReportRequest,
    resp: Response,
    hdrs: dict = Depends(require_headers),
):
    # Error forcing based on last name
    last = req.consumerPii.primaryApplicant.name.lastName.upper().strip()

    if last == "TIMEOUT":
        # Simulate timeout then return 504
        await asyncio.sleep(12)
        body = make_timeout_body()
        # Set headers even on error for parity (optional)
        resp.headers["experianTransactionId"] = str(uuid.uuid4())
        resp.headers["clientReferenceId"] = hdrs.get("clientReferenceId", "SBMYSQL")
        return JSONResponse(status_code=504, content=body)

    error_map = {
        "FAIL_400": (400, "BAD_REQUEST", "Malformed request"),
        "FAIL_403": (403, "FORBIDDEN", "Forbidden"),
        "FAIL_404": (404, "NOT_FOUND", "Resource not found"),
        "FAIL_500": (500, "SERVER_ERROR", "Internal server error"),
    }
    if last in error_map:
        status, code, msg = error_map[last]
        body = error_body(status, code, msg)
        resp.headers["experianTransactionId"] = str(uuid.uuid4())
        resp.headers["clientReferenceId"] = hdrs.get("clientReferenceId", "SBMYSQL")
        return JSONResponse(status_code=status, content=body)

    # Success body
    body = make_success_body(req)

    # Scenario shaping to support demo outcomes
    scenario = (req.addOns or {}).get("scenario") if isinstance(req.addOns, dict) else None
    try:
        cp_list = body.get("creditProfile") or []
        cp = cp_list[0] if cp_list else {}
        if scenario == "pass":
            # Clear severe fraud/OFAC flags and ensure a high score
            if "fraudShield" in cp and cp["fraudShield"]:
                fs0 = cp["fraudShield"][0] or {}
                if "fraudShieldIndicators" in fs0 and isinstance(fs0["fraudShieldIndicators"], dict):
                    fs0["fraudShieldIndicators"]["indicator"] = []
                fs0.pop("dateOfDeath", None)
            cp["statement"] = []
            if "ofac" in cp and isinstance(cp["ofac"], dict):
                cp["ofac"]["messageText"] = ""
            if "riskModel" in cp and cp["riskModel"]:
                cp["riskModel"][0]["score"] = "790"
        elif scenario == "review_credit":
            # Remove risk model and mark a tradeline as disputed to trigger REVIEW
            cp["riskModel"] = []
            if "tradeline" in cp and cp["tradeline"]:
                tl0 = cp["tradeline"][0] or {}
                tl0["consumerDisputeFlag"] = "Y"
        elif scenario == "ko_credit":
            # Force OFAC match to trigger DECLINE
            if "ofac" not in cp or not isinstance(cp["ofac"], dict):
                cp["ofac"] = {}
            cp["ofac"]["messageText"] = "MATCH FOUND"
    except Exception:
        # If shaping fails, return the default success body
        pass

    # Set response headers
    resp.headers["experianTransactionId"] = str(uuid.uuid4())
    resp.headers["clientReferenceId"] = hdrs.get("clientReferenceId", "SBMYSQL")

    return body


if __name__ == "__main__":
    # Run on port 8000 (distinct from any other local services)
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
