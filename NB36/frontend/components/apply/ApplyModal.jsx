import React from "react";
import { Dialog } from "@headlessui/react";
import { motion } from "framer-motion";
import ChecksList from "./ChecksList.jsx";
import TechDetails from "./TechDetails.jsx";
import { Copy, CheckCircle2, XCircle } from "lucide-react";

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
  const passed = checks.filter((c) => c.status === "pass").length;
  const percent = checks.length > 0 ? Math.round((passed / checks.length) * 100) : 0;
  const backendStatus = (report?.summary?.status || "").toString().toUpperCase();
  const overall =
    report?.summary?.overall ||
    (checks.every((c) => c.status === "pass") ? "pass" : checks.some((c) => c.status === "fail") ? "fail" : "pending");
  let mainTone = "neutral";
  let mainLabel = "Processing";
  if (backendStatus.includes("PASS") || overall === "pass") {
    mainTone = "success";
    mainLabel = "Eligible";
  } else if (backendStatus.includes("REVIEW")) {
    mainTone = "warning";
    mainLabel = "Needs Review";
  } else if (backendStatus.includes("KO") || backendStatus.includes("DECLINE") || overall === "fail") {
    mainTone = "danger";
    mainLabel = "Not Eligible";
  }
  const tiers = report?.summary?.tiers || {};
  const finalTier = tiers?.final ?? null;

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
                    {phase === "running" ? "Checking…" : "Eligibility Report"}
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
                    <div className="grid gap-4 sm:grid-cols-[auto_1fr] sm:items-center">
                      <Donut percent={percent} />
                      <div className="space-y-2">
                            <div className="flex flex-wrap items-center gap-2">
                          <Badge tone={mainTone}>
                            {mainLabel}
                          </Badge>
                          {finalTier != null ? <Badge tone="neutral">Final Tier {String(finalTier)}</Badge> : null}
                          {checks.map((c) => (
                            <Badge key={c.id} tone={c.status === "pass" ? "success" : c.status === "fail" ? "danger" : "neutral"}>
                              {c.label}
                            </Badge>
                          ))}
                        </div>
                        <div className="text-sm text-slate-600">
                          Request ID:{" "}
                          <code className="rounded bg-slate-100 px-1.5 py-0.5">{report?.requestId || "—"}</code>
                          <button
                            onClick={onCopyId}
                            className="ml-2 inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-1 text-[11px] font-medium text-slate-700 hover:bg-slate-50"
                            aria-label="Copy Request ID"
                          >
                            <Copy className="h-3.5 w-3.5" />
                            Copy
                          </button>
                        </div>
                      </div>
                    </div>

                    <div className="flex flex-wrap gap-2">
                      <button
                        type="button"
                        onClick={onDownloadJson}
                        className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-semibold text-slate-700 hover:bg-slate-50"
                      >
                        Download JSON
                      </button>
                      <button
                        type="button"
                        onClick={onClose}
                        className="inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-700"
                      >
                        Done
                      </button>
                    </div>

                    <div>
                      <h4 className="text-sm font-semibold text-slate-900">Checks</h4>
                      <div className="mt-2">
                        <ChecksList items={checks} />
                      </div>
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
