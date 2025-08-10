import json
import sys
import urllib.request
import urllib.error

TAKTILE_BASE_URL = "https://nb-taktile.onrender.com"
#TAKTILE_BASE_URL = "http://localhost:9100"


def example_intake(scenario: str | None = None) -> dict:
    """
    Build an example intake payload for AML + Fraud.
    You can pass scenario: pass | review | ko_fraud | ko_compliance (for the SEON mock).
    """
    intake = {
        "user_fullname": "Alice Smith",
        "user_dob": "1995-01-01",
        "user_country": "US",
        "ssn": "123-45-6789",
        "gov_id_type": "DL",
        "gov_id_number": "A1234567",
        "address_line1": "123 Main St",
        "address_city": "Austin",
        "address_state": "TX",
        "address_zip": "78701",
        "email": "alice@good.com",
        "phone_number": "+14155550123",
        "ip": "1.2.3.4",
        "session": "mock-session",
        "custom_fields": {},
    }
    if scenario:
        intake["custom_fields"]["scenario"] = scenario
    return intake


def post_json(url: str, payload: dict) -> tuple[int, dict | str]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except Exception:
                return resp.status, body
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode("utf-8", errors="replace")
            return e.code, json.loads(body)
        except Exception:
            return e.code, body
    except Exception as e:
        return 0, f"Request error: {e}"


def main():
    # Optional CLI arg: scenario (pass | review | ko_fraud | ko_compliance)
    scenario = sys.argv[1] if len(sys.argv) > 1 else "pass"
    case_id = "demo-case-full-kyc-001"

    intake = example_intake(scenario=scenario)

    status, resp = post_json(
        f"{TAKTILE_BASE_URL}/workflows/kyc/full",
        {"case_id": case_id, "intake": intake},
    )

    print(json.dumps({"http_status": status, "response": resp}, indent=2))


if __name__ == "__main__":
    main()
