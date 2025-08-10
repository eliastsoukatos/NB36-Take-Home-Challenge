import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, Clock } from "lucide-react";

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
 */

/**
 * Animated list of checks with status icons and subtle transitions.
 * @param {{ items: CheckResult[] }} props
 */
export default function ChecksList({ items = [] }) {
  return (
    <div role="status" aria-live="polite" className="space-y-2">
      <AnimatePresence initial={false}>
        {items.map((item) => (
          <motion.div
            key={item.id}
            layout
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="flex items-center justify-between rounded-xl border border-slate-200 bg-white/70 px-3 py-2"
          >
            <div className="flex items-center gap-2">
              <StatusIcon status={item.status} />
              <div className="text-sm font-medium text-slate-800">{item.label}</div>
              {item.detail ? (
                <div className="text-xs text-slate-500">({item.detail})</div>
              ) : null}
            </div>
            <div className="text-xs tabular-nums text-slate-500">
              {typeof item.tStart === "number" && typeof item.tEnd === "number"
                ? `${Math.max(0, item.tEnd - item.tStart)}ms`
                : "--"}
            </div>
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
}

function StatusIcon({ status }) {
  if (status === "pass") {
    return <CheckCircle2 className="h-5 w-5 text-emerald-600" />;
  }
  if (status === "fail") {
    return <XCircle className="h-5 w-5 text-red-600" />;
  }
  return <Clock className="h-5 w-5 text-amber-600 animate-pulse" />;
}
