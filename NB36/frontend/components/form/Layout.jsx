import React from "react";

/**
 * Responsive two-column layout:
 * - Left: sticky sidebar (Applying Minutes)
 * - Right: bounded width form/content area
 */
export default function Layout({ sidebar, children }) {
  const hasSidebar = !!sidebar;
  return (
    <div className="mx-auto max-w-7xl px-4 lg:px-6">
      {hasSidebar ? (
        <div className="grid gap-6 lg:grid-cols-[280px_minmax(0,1fr)]">
          <aside className="lg:block">
            <div className="lg:sticky lg:top-4">{sidebar}</div>
          </aside>
          <main className="min-w-0">
            <div className="mx-auto w-full max-w-[800px]">{children}</div>
          </main>
        </div>
      ) : (
        <main className="min-w-0">
          <div className="mx-auto w-full max-w-[800px]">{children}</div>
        </main>
      )}
    </div>
  );
}
