import React from "react";
import { Disclosure } from "@headlessui/react";
import { ChevronDown, Copy, Download } from "lucide-react";

/**
 * @param {{
 *   logs: {
 *     requests: Array<{
 *       endpoint: string,
 *       method: string,
 *       status: number,
 *       duration: number,
 *       request: any,
 *       response: any
 *     }>
 *   },
 *   onDownloadJson?: () => void
 * }} props
 */
export default function TechDetails({ logs, onDownloadJson }) {
  const requests = logs?.requests || [];

  return (
    <div className="mt-4">
      <Disclosure>
        {({ open }) => (
          <div className="rounded-xl border border-slate-200 bg-white">
            <Disclosure.Button className="flex w-full items-center justify-between gap-2 px-4 py-3 text-left text-sm font-medium text-slate-900">
              <span>Technical details</span>
              <ChevronDown className={"h-5 w-5 transition " + (open ? "rotate-180" : "")} />
            </Disclosure.Button>
            <Disclosure.Panel className="px-4 pb-4">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  onClick={onDownloadJson}
                  className="inline-flex items-center gap-2 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-700 hover:bg-slate-50"
                  aria-label="Download JSON"
                >
                  <Download className="h-4 w-4" />
                  Download JSON
                </button>
              </div>

              <div className="mt-4">
                <h4 className="text-sm font-semibold text-slate-900">Network</h4>
                <div className="mt-2 divide-y divide-slate-200 overflow-hidden rounded-lg border border-slate-200">
                  {requests.length === 0 ? (
                    <div className="px-3 py-2 text-sm text-slate-500">No requests logged.</div>
                  ) : (
                    requests.map((r, idx) => (
                      <div key={idx} className="grid grid-cols-1 gap-2 px-3 py-2 text-sm sm:grid-cols-4">
                        <div className="font-mono text-xs text-slate-600">{r.method} {r.endpoint}</div>
                        <div className={"text-xs " + (r.status >= 200 && r.status < 300 ? "text-emerald-700" : "text-red-700")}>
                          Status: {r.status || "—"}
                        </div>
                        <div className="text-xs text-slate-600">Duration: {r.duration}ms</div>
                        <div className="text-xs text-slate-600">Size: {JSON.stringify(r.response || {}).length}B</div>
                      </div>
                    ))
                  )}
                </div>
              </div>

              {requests.map((r, idx) => (
                <div key={"json-" + idx} className="mt-4 grid gap-3 sm:grid-cols-2">
                  <JsonBlock title="Request JSON" json={r.request} />
                  <JsonBlock title="Response JSON" json={r.response} />
                </div>
              ))}
            </Disclosure.Panel>
          </div>
        )}
      </Disclosure>
    </div>
  );
}

function JsonBlock({ title, json }) {
  const text = safeStringify(json, 2);

  function copy() {
    try {
      navigator.clipboard.writeText(text);
    } catch {}
  }

  return (
    <div>
      <div className="mb-1 flex items-center justify-between">
        <div className="text-sm font-semibold text-slate-900">{title}</div>
        <button
          type="button"
          onClick={copy}
          className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-1 text-[11px] font-medium text-slate-700 hover:bg-slate-50"
          aria-label={"Copy " + title}
        >
          <Copy className="h-3.5 w-3.5" />
          Copy
        </button>
      </div>
      <pre className="max-h-56 overflow-auto rounded-lg border border-slate-200 bg-slate-50 p-2 text-xs text-slate-800">
        {text}
      </pre>
    </div>
  );
}

function safeStringify(obj, space) {
  try {
    return JSON.stringify(obj ?? {}, null, space);
  } catch {
    return String(obj);
  }
}
