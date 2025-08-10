// Orchestrates the Apply flow: calls backend, emits progressive check updates,
// and returns a final ApplyReport plus request/response logs.

/**
 * @typedef {'identity'|'incomeVerification'|'overageMonth'|'fraudSignals'} CheckId
 * @typedef {'pending'|'pass'|'fail'} CheckStatus
 *
 * @typedef {Object} CheckResult
 * @property {CheckId} id
 * @property {string} label
 * @property {CheckStatus} status
 * @property {string=} detail
 * @property {any=} raw
 * @property {number=} tStart
 * @property {number=} tEnd
 *
 * @typedef {Object} ApplyReport
 * @property {string} requestId
 * @property {number} startedAt
 * @property {number} finishedAt
 * @property {CheckResult[]} checks
 */

//const ENDPOINT = "http://localhost:9000/apply/kyc";
const ENDPOINT = "https://nb-backend-fv6v.onrender.com/apply/kyc";

/**
 * Simple UUID-like generator for demo purposes.
 */
function uuid() {
  return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, (c) => {
    const r = (Math.random() * 16) | 0;
    const v = c === "x" ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * Maps backend decision strings to boolean pass/fail.
 * @param {string|undefined|null} decision
 * @returns {'pass'|'fail'|'pending'}
 */
function decisionToStatus(decision) {
  const d = (decision || "").toString().toUpperCase();
  if (!d) return "pending";
  // Treat common "pass" synonyms as pass
  if (
    d.includes("PASS") ||
    d === "OK" ||
    d === "ACCEPT" ||
    d === "ACCEPTED" ||
    d === "APPROVE" ||
    d === "APPROVED" ||
    d === "PROCEED" // AML often returns PROCEED
  ) {
    return "pass";
  }
  // Treat review/decline/ko as fail for surfacing attention
  if (d.includes("KO") || d.includes("DECLINE") || d.includes("REJECT") || d.includes("REVIEW")) return "fail";
  return "pending";
}

/**
 * Returns a shallow, safe clone for JSON previewing.
 * @param {any} obj
 */
function safeClone(obj) {
  try {
    return JSON.parse(JSON.stringify(obj));
  } catch {
    return obj;
  }
}

/**
 * @param {any} payload
 * @param {(partial: CheckResult) => void} onCheckUpdate
 * @returns {Promise<{ report: ApplyReport, logs: { requests: Array<{ endpoint:string, method:string, status:number, duration:number, request:any, response:any }> } }>}
 */
export async function runApply(payload, onCheckUpdate) {
  const startedAt = Date.now();
  const requestId = uuid();

  const checksBase = [
    { id: "identity", label: "Identity", status: "pending" },
    { id: "incomeVerification", label: "Income Verification", status: "pending" },
    { id: "overageMonth", label: "Overage Month", status: "pending" },
    { id: "fraudSignals", label: "Fraud Signals", status: "pending" },
  ];

  // Emit initial pending states
  for (const c of checksBase) {
    onCheckUpdate({ ...c, tStart: Date.now() });
  }

  // Perform backend request
  const reqInfo = { endpoint: ENDPOINT, method: "POST", status: 0, duration: 0, request: safeClone(payload), response: null };
  const t0 = performance.now();
  let data = null;
  let resp;
  try {
    resp = await fetch(ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    reqInfo.status = resp.status;
    data = await resp.json();
  } catch (e) {
    reqInfo.status = 0;
    data = { error: e?.message || "Network error" };
  } finally {
    reqInfo.duration = Math.round(performance.now() - t0);
    reqInfo.response = safeClone(data);
  }

  // Derive check statuses from backend data
  const amlDecision = data?.aml_decision?.decision;
  const incomeDecision = data?.income_decision?.decision;
  const incomeCoverageMonths =
    data?.income_decision?.metrics?.coverage_months ?? data?.income_decision?.metrics?.coverage ?? null;
  const fraudDecision = data?.fraud_decision?.decision;

  // Identity from AML decision
  const identity = {
    id: "identity",
    label: "Identity",
    status: decisionToStatus(amlDecision),
    detail: amlDecision || undefined,
    raw: safeClone(data?.aml_decision),
  };

  // Income verification
  const incomeVerification = {
    id: "incomeVerification",
    label: "Income Verification",
    status: decisionToStatus(incomeDecision),
    detail: incomeDecision || undefined,
    raw: safeClone(data?.income_decision),
  };

  // Overage Month (coverage threshold: >= 3 months passes)
  let overageDetail = "";
  if (typeof incomeCoverageMonths === "number") {
    overageDetail = `${incomeCoverageMonths} month${incomeCoverageMonths === 1 ? "" : "s"} coverage`;
  }
  const overageMonth = {
    id: "overageMonth",
    label: "Overage Month",
    status: typeof incomeCoverageMonths === "number" ? (incomeCoverageMonths >= 3 ? "pass" : "fail") : "pending",
    detail: overageDetail || undefined,
    raw: { coverage_months: incomeCoverageMonths },
  };

  // Fraud signals (treat REVIEW as fail to surface attention)
  const fraudSignals = {
    id: "fraudSignals",
    label: "Fraud Signals",
    status: decisionToStatus(fraudDecision),
    detail: fraudDecision || undefined,
    raw: safeClone(data?.fraud_decision),
  };

  const computed = [identity, incomeVerification, overageMonth, fraudSignals];

  // Stagger updates to animate progression
  const stagger = [350, 800, 1200, 1600];
  await new Promise((resolve) => {
    let done = 0;
    computed.forEach((c, i) => {
      setTimeout(() => {
        onCheckUpdate({ ...c, tEnd: Date.now() });
        done += 1;
        if (done === computed.length) resolve();
      }, stagger[i] || 300);
    });
  });

  const finishedAt = Date.now();

  // Build a summary so the UI can show a consistent headline and tier
  const passedCount = computed.filter((c) => c.status === "pass").length;
  const overall =
    computed.every((c) => c.status === "pass")
      ? "pass"
      : computed.some((c) => c.status === "fail")
      ? "fail"
      : "pending";
  const percent = Math.round((passedCount / computed.length) * 100);

  const tiers = {
    bureau: typeof data?.credit_decision?.bureau_tier === "number" ? data.credit_decision.bureau_tier : data?.bureau_tier ?? null,
    income: typeof data?.income_decision?.income_tier === "number" ? data.income_decision.income_tier : null,
    provisional: typeof data?.fraud_decision?.provisional_tier === "number" ? data.fraud_decision.provisional_tier : data?.provisional_tier ?? null,
    final: typeof data?.credit_decision?.final_tier === "number" ? data.credit_decision.final_tier : data?.final_tier ?? null,
  };

  const report = {
    requestId: String(data?.case_id || data?.id || requestId),
    startedAt,
    finishedAt,
    checks: computed,
    summary: {
      overall, // 'pass' | 'fail' | 'pending'
      percent,
      passed: passedCount,
      total: computed.length,
      status: data?.status ?? null,
      tiers,
    },
  };

  return {
    report,
    logs: { requests: [reqInfo] },
  };
}
