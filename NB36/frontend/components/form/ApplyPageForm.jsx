import React from "react";
import Layout from "./Layout.jsx";
import Section from "./Section.jsx";
import ApplyModal from "../apply/ApplyModal.jsx";
import { runApply } from "../../lib/api/apply.js";
import { telemetry } from "../../lib/telemetry.js";
import { ArrowRight } from "lucide-react";

/**
 * Demo config is provided by parent (e.g., NB36Landing) when demo panel is enabled.
 * @typedef {{
 *   scenario?: string,
 *   incomeScenario?: string,
 *   incomeCoverageMonths?: number
 * }} DemoConfig
 */

/**
 * @param {{ demoConfig?: DemoConfig }} props
 */
export default function ApplyPageForm({ demoConfig }) {
  const [needsPriorAddress, setNeedsPriorAddress] = React.useState(false);

  // Form state
  const [fullName, setFullName] = React.useState("");
  const [dob, setDob] = React.useState("");
  const [ssn, setSsn] = React.useState("");
  const [govIdType, setGovIdType] = React.useState("");
  const [govIdNumber, setGovIdNumber] = React.useState("");
  const [email, setEmail] = React.useState("");
  const [phone, setPhone] = React.useState("");
  const [street, setStreet] = React.useState("");
  const [apt, setApt] = React.useState("");
  const [city, setCity] = React.useState("");
  const [state, setState] = React.useState("");
  const [zip, setZip] = React.useState("");

  // UX state
  const [submitting, setSubmitting] = React.useState(false);
  const [clientError, setClientError] = React.useState("");

  // Modal + checks/report state
  const [modalOpen, setModalOpen] = React.useState(false);
  const [phase, setPhase] = React.useState("running"); // 'running' | 'report'
  const [checks, setChecks] = React.useState([
    { id: "identity", label: "AML Scan", status: "pending" },
    { id: "incomeVerification", label: "Income Verification", status: "pending" },
    { id: "overageMonth", label: "Credit Risk Assessment", status: "pending" },
    { id: "fraudSignals", label: "Fraud Signals", status: "pending" },
  ]);
  const [report, setReport] = React.useState(null);
  const [logs, setLogs] = React.useState({ requests: [] });


  function buildPayload() {
    const address_line1 = apt ? `${street}, ${apt}` : street;

    // Prepare custom fields for all mocks (SEON/Experian already use "scenario"; Plaid uses income_* keys)
    const cf = {};
    if (demoConfig?.scenario) cf.scenario = demoConfig.scenario;

    // Map income scenario presets to Plaid options understood by Taktile
    // - income_force_mode: payroll | bank | document | empty
    // - income_risk_profile: clean | suspicious
    // - income_inject_error: e.g., RATE_LIMIT_EXCEEDED
    // - income_coverage_months: integer
    const incomeScenario = demoConfig?.incomeScenario || "income_pass";
    const incomeCoverageMonths = typeof demoConfig?.incomeCoverageMonths === "number" ? demoConfig.incomeCoverageMonths : 12;

    if (incomeScenario === "income_pass") {
      cf.income_force_mode = "payroll";
      cf.income_risk_profile = "clean";
      cf.income_coverage_months = incomeCoverageMonths;
    } else if (incomeScenario === "income_bank") {
      cf.income_force_mode = "bank";
      cf.income_risk_profile = "clean";
      cf.income_coverage_months = incomeCoverageMonths;
    } else if (incomeScenario === "income_empty") {
      cf.income_force_mode = "empty";
      cf.income_risk_profile = "clean";
      cf.income_coverage_months = incomeCoverageMonths;
    } else if (incomeScenario === "income_review") {
      cf.income_force_mode = "payroll";
      cf.income_risk_profile = "suspicious";
      cf.income_coverage_months = incomeCoverageMonths;
    } else if (incomeScenario === "income_ko") {
      cf.income_force_mode = "bank";
      cf.income_risk_profile = "clean";
      cf.income_coverage_months = 2;
    } else if (incomeScenario === "income_error") {
      cf.income_force_mode = "bank";
      cf.income_risk_profile = "clean";
      cf.income_inject_error = "RATE_LIMIT_EXCEEDED";
      cf.income_coverage_months = incomeCoverageMonths;
    }

    return {
      user_fullname: fullName,
      user_dob: dob,
      user_country: "US",
      ssn,
      gov_id_type: govIdType,
      gov_id_number: govIdNumber,
      address_line1,
      address_city: city,
      address_state: state,
      address_zip: zip,
      email,
      phone_number: phone,
      custom_fields: cf,
    };
  }

  async function onApply(e) {
    e.preventDefault();
    setClientError("");

    // Simple client-side validation example (expand as needed)
    if (!fullName || !dob || !ssn || !govIdType || !govIdNumber || !email || !phone || !street || !city || !state || !zip) {
      setClientError("Please complete all required fields.");
      return;
    }

    setSubmitting(true);
    setPhase("running");
    setReport(null);
    setLogs({ requests: [] });
    setChecks((prev) =>
      prev.map((c) => ({
        ...c,
        status: "pending",
        tStart: Date.now(),
        tEnd: undefined,
        detail: undefined,
      }))
    );

    setModalOpen(true);
    telemetry.apply_opened();
    telemetry.checks_started();

    const payload = buildPayload();

    try {
      const { report: rep, logs: lgs } = await runApply(payload, (update) => {
        setChecks((prev) => prev.map((c) => (c.id === update.id ? { ...c, ...update } : c)));
        telemetry.check_update({ id: update.id, status: update.status });
      });
      setReport(rep);
      setLogs(lgs);
      setPhase("report");
      telemetry.checks_completed({ requestId: rep.requestId });
      telemetry.report_viewed({ requestId: rep.requestId });
    } catch (err) {
      // Even on errors, the modal will be open and TechDetails will show (if any)
      setPhase("report");
    } finally {
      setSubmitting(false);
    }
  }

  function downloadJson() {
    const blob = new Blob([JSON.stringify({ report, logs }, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `nb36-eligibility-${report?.requestId || "unknown"}.json`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
    telemetry.json_downloaded({ requestId: report?.requestId });
  }

  function copyId() {
    try {
      navigator.clipboard.writeText(String(report?.requestId || ""));
      telemetry.id_copied({ requestId: report?.requestId });
    } catch {}
  }

  return (
    <Layout>
      <h1 className="mb-3 text-2xl font-bold tracking-tight text-slate-900">Apply in minutes</h1>
      <p className="mb-4 text-sm text-slate-600">
        No annual fee. No hidden charges. Instant virtual card on approval.
      </p>

      {clientError ? (
        <div className="mb-4 rounded-xl border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700" role="alert">
          {clientError}
        </div>
      ) : null}

      <form onSubmit={onApply} className="grid gap-4">
        <Section id="personal" title="Personal details">
          <div>
            <label className="mb-1 block text-xs font-medium text-slate-700">Full name</label>
            <input
              required
              type="text"
              placeholder="Alex Johnson"
              className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Date of Birth</label>
              <input
                required
                type="date"
                className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={dob}
                onChange={(e) => setDob(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">SSN</label>
              <input
                required
                type="password"
                inputMode="numeric"
                placeholder="123-45-6789"
                className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm tracking-widest outline-none ring-emerald-500/20 placeholder:tracking-normal focus:ring"
                aria-describedby="ssn-help"
                value={ssn}
                onChange={(e) => setSsn(e.target.value)}
              />
              <p id="ssn-help" className="mt-1 text-[11px] text-slate-500">For demo only — don’t use real SSNs.</p>
            </div>
          </div>
        </Section>

        <Section id="id" title="Government ID">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Government ID Type</label>
              <select
                required
                className="w-full appearance-none rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={govIdType}
                onChange={(e) => setGovIdType(e.target.value)}
              >
                <option value="">Select one</option>
                <option value="DL">Driver’s License</option>
                <option value="STATE_ID">State ID</option>
                <option value="PASSPORT">Passport</option>
              </select>
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">ID Number</label>
              <input
                required
                type="text"
                placeholder="ID / Passport #"
                className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={govIdNumber}
                onChange={(e) => setGovIdNumber(e.target.value)}
              />
            </div>
          </div>
        </Section>

        <Section id="contact" title="Contact">
          <div className="grid gap-3 sm:grid-cols-2">
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Email</label>
              <input
                required
                type="email"
                placeholder="alex@email.com"
                className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
            <div>
              <label className="mb-1 block text-xs font-medium text-slate-700">Mobile Phone</label>
              <input
                required
                type="tel"
                inputMode="tel"
                placeholder="(555) 555‑1234"
                className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
              />
            </div>
          </div>
        </Section>

        <Section id="address" title="Current address">
          <input
            required
            type="text"
            placeholder="Street address"
            className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
            value={street}
            onChange={(e) => setStreet(e.target.value)}
          />
          <div className="grid gap-3 sm:grid-cols-4">
            <input
              type="text"
              placeholder="Apt / Unit (optional)"
              className="sm:col-span-1 w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              value={apt}
              onChange={(e) => setApt(e.target.value)}
            />
            <input
              required
              type="text"
              placeholder="City"
              className="sm:col-span-2 w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              value={city}
              onChange={(e) => setCity(e.target.value)}
            />
            <input
              required
              type="text"
              placeholder="State"
              className="sm:col-span-1 w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              value={state}
              onChange={(e) => setState(e.target.value)}
            />
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <input
              required
              type="text"
              inputMode="numeric"
              placeholder="ZIP"
              className="sm:col-span-1 w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              value={zip}
              onChange={(e) => setZip(e.target.value)}
            />
            <div className="sm:col-span-2 flex items-center gap-2 rounded-xl border border-emerald-200 px-3 py-2.5">
              <input
                id="priorAddress"
                type="checkbox"
                className="h-4 w-4 rounded border-emerald-300 text-emerald-600 focus:ring-emerald-500"
                onChange={(e) => setNeedsPriorAddress(e.target.checked)}
              />
              <label htmlFor="priorAddress" className="text-xs text-slate-700">
                I’ve lived at this address for less than 2 years
              </label>
            </div>
          </div>
        </Section>

        {needsPriorAddress && (
          <Section id="prior" title="Prior address">
            <input
              type="text"
              placeholder="Street address"
              className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
            />
            <div className="grid gap-3 sm:grid-cols-4">
              <input
                type="text"
                placeholder="Apt / Unit (optional)"
                className="sm:col-span-1 w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              />
              <input
                type="text"
                placeholder="City"
                className="sm:col-span-2 w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              />
              <input
                type="text"
                placeholder="State"
                className="sm:col-span-1 w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
              />
            </div>
            <input
              type="text"
              inputMode="numeric"
              placeholder="ZIP"
              className="w-full rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
            />
          </Section>
        )}

        {/* The "Apply Now" submit action is unified via onApply */}
        <div className="flex items-center justify-end">
          <button
            type="submit"
            disabled={submitting}
            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-md shadow-emerald-600/25 transition hover:bg-emerald-700 disabled:opacity-60"
            aria-label="Submit Application"
          >
            {submitting ? "Submitting…" : "Submit Application"} <ArrowRight className="h-4 w-4" />
          </button>
        </div>

        <p className="text-xs text-slate-500">
          By submitting, you agree to be contacted about your application. This demo does not collect real data.
        </p>
      </form>

      <ApplyModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        phase={phase}
        checks={checks}
        report={report}
        logs={logs}
        onDownloadJson={downloadJson}
        onCopyId={copyId}
      />
    </Layout>
  );
}
