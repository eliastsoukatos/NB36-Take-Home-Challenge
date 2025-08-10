import React from "react";

/**
 * Compact sticky card summarizing "Applying Minutes" with a tiny donut.
 * Props:
 * - status: 'idle' | 'running' | 'done'
 * - passed: number
 * - total: number
 */
export default function ApplyingMinutesCard({ status = "idle", passed = 0, total = 4 }) {
  const percent = total > 0 ? Math.round((passed / total) * 100) : 0;
  const pending = status === "running";
  const label =
    status === "done" ? "Completed" : status === "running" ? "Submitting…" : "Ready to apply";

  return (
    <div className="rounded-2xl border border-emerald-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-slate-900">Applying Minutes</h2>
        <span
          className={
            "inline-flex items-center rounded-full px-2.5 py-0.5 text-[11px] font-medium " +
            (status === "done"
              ? "bg-emerald-50 text-emerald-700 ring-1 ring-inset ring-emerald-100"
              : status === "running"
              ? "bg-amber-50 text-amber-700 ring-1 ring-inset ring-amber-100"
              : "bg-slate-50 text-slate-700 ring-1 ring-inset ring-slate-200")
          }
        >
          {label}
        </span>
      </div>

      <div className="mt-4 flex items-center gap-4">
        <TinyDonut percent={percent} pending={pending} />
        <div>
          <div className="text-sm font-medium text-slate-800">{percent}% complete</div>
          <div className="text-xs text-slate-500">
            {passed}/{total} checks {status === "running" ? "in progress" : "ready"}
          </div>
        </div>
      </div>

      <div className="mt-4 grid gap-2 text-xs text-slate-600">
        <div className="flex items-center justify-between">
          <span>Identity</span>
          <span className="font-medium">{status === "idle" ? "Pending" : passed >= 1 ? "Checked" : "Pending"}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Income Verification</span>
          <span className="font-medium">{status === "done" || passed >= 2 ? "Checked" : "Pending"}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Overage Month</span>
          <span className="font-medium">{status === "done" || passed >= 3 ? "Checked" : "Pending"}</span>
        </div>
        <div className="flex items-center justify-between">
          <span>Fraud Signals</span>
          <span className="font-medium">{status === "done" || passed >= 4 ? "Checked" : "Pending"}</span>
        </div>
      </div>
    </div>
  );
}

function TinyDonut({ percent = 0, pending = false }) {
  const size = 54;
  const stroke = 6;
  const r = (size - stroke) / 2;
  const c = 2 * Math.PI * r;
  const clamped = Math.max(0, Math.min(100, percent));
  const offset = c - (clamped / 100) * c;

  return (
    <svg
      width={size}
      height={size}
      viewBox={`0 0 ${size} ${size}`}
      className={pending ? "animate-pulse" : ""}
      aria-label={`Progress ${percent}%`}
    >
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="#E2F7EC" /* emerald-100 */
        strokeWidth={stroke}
      />
      <circle
        cx={size / 2}
        cy={size / 2}
        r={r}
        fill="none"
        stroke="#10B981" /* emerald-500 */
        strokeWidth={stroke}
        strokeLinecap="round"
        strokeDasharray={c}
        strokeDashoffset={offset}
        transform={`rotate(-90 ${size / 2} ${size / 2})`}
      />
      <text
        x="50%"
        y="50%"
        dominantBaseline="middle"
        textAnchor="middle"
        fontSize="11"
        className="fill-slate-700"
      >
        {clamped}%
      </text>
    </svg>
  );
}
