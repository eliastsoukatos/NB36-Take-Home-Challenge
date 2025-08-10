import React from "react";
import { Settings2 } from "lucide-react";
import { telemetry } from "../../lib/telemetry.js";

/**
 * Hidden-by-default Demo Panel for controlling mock scenarios.
 * Gated by !import.meta.env.PROD
 *
 * @param {{
 *   demoConfig: { scenario?: string, incomeScenario?: string, incomeCoverageMonths?: number },
 *   setDemoConfig: (cfg: any) => void
 * }} props
 */
export default function DemoPanel({ demoConfig, setDemoConfig }) {
  const enabled = true; // Always show demo controls in this demo app
  const [open, setOpen] = React.useState(false);

  React.useEffect(() => {
    if (!enabled) return;
    function onKey(e) {
      const isMac = navigator.platform.toUpperCase().includes("MAC");
      if ((isMac && e.metaKey && e.key.toLowerCase() === "d") || (!isMac && e.ctrlKey && e.key.toLowerCase() === "d")) {
        e.preventDefault();
        setOpen((v) => {
          const next = !v;
          telemetry.demo_toggled({ open: next });
          return next;
        });
      }
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [enabled]);

  if (!enabled) return null;

  function update(partial) {
    setDemoConfig({ ...demoConfig, ...partial });
  }

  return (
    <>
      {/* Tiny FAB */}
      <button
        type="button"
        onClick={() => {
          const next = !open;
          setOpen(next);
          telemetry.demo_toggled({ open: next });
        }}
        className="fixed bottom-4 right-4 z-[60] inline-flex h-9 w-9 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-700 shadow-lg hover:bg-slate-50"
        aria-label="Toggle demo controls (Cmd/Ctrl + D)"
        title="Demo controls (Cmd/Ctrl + D)"
      >
        <Settings2 className="h-5 w-5" />
      </button>

      {/* Panel */}
      {open ? (
        <div className="fixed bottom-16 right-4 z-[60] w-80 rounded-xl border border-slate-200 bg-white p-3 shadow-xl">
          <div className="mb-2 flex items-center justify-between">
            <div className="text-sm font-semibold text-slate-900">Demo controls</div>
            <button
              type="button"
              onClick={() => {
                setOpen(false);
                telemetry.demo_toggled({ open: false });
              }}
              className="rounded-md px-2 py-1 text-xs text-slate-600 hover:bg-slate-100"
            >
              Close
            </button>
          </div>

          <div className="grid gap-3">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Test scenario</label>
              <select
                className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={demoConfig?.scenario || "pass"}
                onChange={(e) => update({ scenario: e.target.value })}
              >
                <option value="pass">pass (End-to-end PASS)</option>
                <option value="review">review (Fraud REVIEW)</option>
                <option value="ko_compliance">ko_compliance (AML DECLINE)</option>
                <option value="ko_fraud">ko_fraud (Fraud DECLINE/REVIEW)</option>
                <option value="review_credit">review_credit (CREDIT REVIEW)</option>
                <option value="ko_credit">ko_credit (CREDIT DECLINE)</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Income scenario</label>
              <select
                className="w-full appearance-none rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={demoConfig?.incomeScenario || "income_pass"}
                onChange={(e) => update({ incomeScenario: e.target.value })}
              >
                <option value="income_pass">income_pass (Payroll PASS)</option>
                <option value="income_bank">income_bank (Bank PASS)</option>
                <option value="income_empty">income_empty (no income)</option>
                <option value="income_review">income_review (suspicious → REVIEW)</option>
                <option value="income_ko">income_ko (thin coverage KO)</option>
                <option value="income_error">income_error (injected error)</option>
              </select>
            </div>

            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Income coverage months</label>
              <input
                type="number"
                min="1"
                max="60"
                className="w-full rounded-lg border border-slate-200 bg-white px-3 py-2 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={Number.isFinite(demoConfig?.incomeCoverageMonths) ? demoConfig.incomeCoverageMonths : 12}
                onChange={(e) => update({ incomeCoverageMonths: parseInt(e.target.value || "12", 10) })}
              />
            </div>

            <p className="text-[11px] text-slate-500">
              These controls affect custom_fields in the request body and drive mocked outcomes. Hidden in production builds.
            </p>
          </div>
        </div>
      ) : null}
    </>
  );
}
