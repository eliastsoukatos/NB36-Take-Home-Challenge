import React from "react";
import { Dialog } from "@headlessui/react";
import { motion } from "framer-motion";
import ChecksList from "./ChecksList.jsx";
import TechDetails from "./TechDetails.jsx";
import { CheckCircle2, XCircle } from "lucide-react";

function Donut({ percent = 0 }) {
  const size = 80;
  const stroke = 8;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const clamped = Math.max(0, Math.min(100, percent));
  const offset = c - (clamped / 100) * c;

  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`} aria-label={`Passed ${clamped}%`}>
      <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#E2E8F0" strokeWidth={stroke} />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="#10B981"
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={offset}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text x="50%" y="50%" dominantBaseline="middle" textAnchor="middle" fontSize="14" className="fill-slate-800">
        {clamped}%
      </text>
    </svg>
  );
}

/**
 * @param {{
 *  open: boolean,
 *  onClose: () => void,
 *  phase: 'running'|'report',
 *  checks: Array<{ id: string, label: string, status: 'pending'|'pass'|'fail', detail?: string, tStart?: number, tEnd?: number }>,
 *  report?: { requestId: string, startedAt: number, finishedAt: number, checks: any[] },
 *  logs?: any,
 *  onDownloadJson?: () => void,
 *  onCopyId?: () => void
 * }} props
 */
export default function ApplyModal({ open, onClose, phase, checks = [], report, logs, onDownloadJson, onCopyId }) {
  // Derive approval data from raw backend response (prefer logs.requests[0].response)
  const raw = logs?.requests?.[0]?.response || {};
  const amlDecision = raw?.aml_decision?.decision || "";
  const fraudDecision = (raw?.fraud_decision?.decision || "").toUpperCase();
  const creditDecision = raw?.credit_decision?.decision || "";
  const incomeDecision = raw?.income_decision?.decision || "";

  const isAmlPass = amlDecision === "PROCEED";
  const isFraudPass = fraudDecision.includes("PASS");
  const isCreditPass = creditDecision === "CREDIT_PASS";
  const isIncomePass = incomeDecision === "INCOME_PASS";
  const isApproved = isAmlPass && isFraudPass && isCreditPass && isIncomePass;

  const creditLimit =
    typeof raw?.income_decision?.credit_limit === "number" ? raw.income_decision.credit_limit : null;

  const userTier =
    typeof raw?.final_tier === "number"
      ? raw.final_tier
      : typeof raw?.credit_decision?.final_tier === "number"
      ? raw.credit_decision.final_tier
      : typeof report?.summary?.tiers?.final === "number"
      ? report.summary.tiers.final
      : null;

  const locale = typeof navigator !== "undefined" && navigator.language ? navigator.language : "en-US";
  const currency = "USD";
  const formattedLimit =
    typeof creditLimit === "number"
      ? new Intl.NumberFormat(locale, { style: "currency", currency }).format(creditLimit)
      : "—";

  const checkList = [
    { label: "AML Scan", ok: isAmlPass },
    { label: "Fraud Signals", ok: isFraudPass },
    { label: "Credit Risk Assessment", ok: isCreditPass },
    { label: "Income Verification", ok: isIncomePass },
  ];

  return (
    <Dialog open={open} onClose={onClose} className="relative z-[100]">
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" />
      <div className="fixed inset-0 overflow-y-auto">
        <div className="flex min-h-full items-end justify-center p-4 sm:items-center">
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="w-full max-w-2xl"
          >
            <div className="w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl" role="document">
              <div className="border-b border-slate-200 px-4 py-3">
                <div className="flex items-center justify-between">
<h3 className="text-base font-semibold text-slate-900">
                    {phase === "running"
                      ? "Checking…"
                      : isApproved
                      ? "🎉 Congratulations! You’re eligible for a credit card"
                      : "⚠️ Unfortunately, you are not eligible for a credit card at this time"}
                  </h3>
                  <button
                    onClick={onClose}
                    className="rounded-md px-2 py-1 text-sm text-slate-600 hover:bg-slate-100"
                    aria-label="Close modal"
                  >
                    Close
                  </button>
                </div>
              </div>

              <div className="px-4 py-4">
                {phase === "running" ? (
                  <div className="space-y-4">
                    <div className="flex items-center gap-3">
                      <div className="h-2 w-2 animate-pulse rounded-full bg-amber-500" />
                      <div className="text-sm text-slate-700">We’re running checks and verifying your details.</div>
                    </div>
                    <ChecksList items={checks} />
                  </div>
                ) : (
                  <div className="space-y-5">
                    <p className="text-sm text-slate-600">
                      {isApproved
                        ? "Your application has been approved."
                        : "We encourage you to explore our other programs that might be a better fit for your needs."}
                    </p>

                    <div className="grid gap-4 sm:grid-cols-2">
                      <div className="rounded-2xl border border-emerald-200 bg-emerald-50 p-4">
                        <div className="text-xs font-medium text-emerald-700">Credit Limit</div>
                        <div className="mt-1 text-3xl font-extrabold tracking-tight text-emerald-800">
                          {formattedLimit}
                        </div>
                      </div>
                      <div className="rounded-2xl border border-slate-200 bg-white p-4">
                        <div className="text-xs font-medium text-slate-600">Tier</div>
                        <div className="mt-1 text-3xl font-extrabold tracking-tight text-slate-900">
                          {userTier != null ? String(userTier) : "—"}
                        </div>
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold text-slate-900">Eligibility Checks</h4>
                      <ul className="mt-2 grid gap-2">
                        {checkList.map((c) => (
                          <li key={c.label} className="flex items-center gap-2 text-sm">
                            {c.ok ? (
                              <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                            ) : (
                              <XCircle className="h-5 w-5 text-red-600" />
                            )}
                            <span className="font-medium text-slate-800">{c.label}</span>
                          </li>
                        ))}
                      </ul>
                    </div>

                    <TechDetails logs={logs} onDownloadJson={onDownloadJson} />
                  </div>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </Dialog>
  );
}

function Badge({ children, tone = "neutral" }) {
  const toneClass =
    tone === "success"
      ? "bg-emerald-50 text-emerald-700 ring-emerald-100"
      : tone === "danger"
      ? "bg-red-50 text-red-700 ring-red-100"
      : tone === "warning"
      ? "bg-amber-50 text-amber-800 ring-amber-100"
      : "bg-slate-50 text-slate-700 ring-slate-200";
  return (
    <span className={"inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-[11px] font-medium ring-1 ring-inset " + toneClass}>
      {tone === "success" ? <CheckCircle2 className="h-3.5 w-3.5" /> : tone === "danger" ? <XCircle className="h-3.5 w-3.5" /> : null}
      {children}
    </span>
  );
}
