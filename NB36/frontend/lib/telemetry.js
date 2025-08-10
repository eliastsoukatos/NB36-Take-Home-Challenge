// Minimal telemetry stub to keep API flexible without breaking anything.
// Replace console.log with your analytics/event pipeline when ready.

/**
 * @typedef {Object} TelemetryEvent
 * @property {string} name
 * @property {Record<string, any>=} props
 */

const enabled = true;

/**
 * @param {TelemetryEvent} evt
 */
export function track(evt) {
  if (!enabled) return;
  try {
    // eslint-disable-next-line no-console
    console.log("[telemetry]", evt.name, evt.props ?? {});
  } catch {}
}

export const telemetry = {
  apply_opened: (context) => track({ name: "apply_opened", props: context }),
  checks_started: (context) => track({ name: "checks_started", props: context }),
  check_update: (context) => track({ name: "check_update", props: context }),
  checks_completed: (context) => track({ name: "checks_completed", props: context }),
  report_viewed: (context) => track({ name: "report_viewed", props: context }),
  json_downloaded: (context) => track({ name: "json_downloaded", props: context }),
  id_copied: (context) => track({ name: "id_copied", props: context }),
  demo_toggled: (context) => track({ name: "demo_toggled", props: context }),
};
