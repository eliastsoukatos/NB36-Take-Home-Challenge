import React from "react";

/**
 * Reusable form section with title/description and consistent spacing.
 * Props:
 * - title: string
 * - description?: string
 * - children: ReactNode
 * - id?: string for aria-labelledby
 */
export default function Section({ title, description, children, id }) {
  const headingId = id ? `${id}-title` : undefined;
  const descId = id ? `${id}-desc` : undefined;

  return (
    <section aria-labelledby={headingId} aria-describedby={descId} className="rounded-2xl border border-emerald-200 bg-white p-4 shadow-sm">
      <header className="mb-3">
        <h2 id={headingId} className="text-base font-semibold text-slate-900">
          {title}
        </h2>
        {description ? (
          <p id={descId} className="mt-1 text-sm text-slate-600">
            {description}
          </p>
        ) : null}
      </header>
      <div className="grid gap-3">{children}</div>
    </section>
  );
}
