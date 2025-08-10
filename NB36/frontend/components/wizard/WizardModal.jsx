import React from "react";
import { Dialog } from "@headlessui/react";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight, X } from "lucide-react";

// Define 6 steps with image + text content
const steps = [
  {
    title: "Welcome to the NB36 Demo",
    image: { src: "/images/cc_front.png", alt: "NB36 card front" },
    body: (
      <>
        <p className="text-slate-600">
          This short tour walks through the key parts of the NB36 credit card demo experience.
        </p>
        <ul className="mt-3 list-disc pl-5 text-sm text-slate-600 space-y-1">
          <li>What’s on this page</li>
          <li>How to apply</li>
          <li>How decisions are made</li>
          <li>How to relaunch this tour</li>
        </ul>
      </>
    ),
  },
  {
    title: "Explore the Landing Page",
    image: { src: "/images/cc_back.png", alt: "NB36 card back" },
    body: (
      <p className="text-slate-600">
        The hero and highlights introduce the card benefits. Scroll to see features, design details, and security.
      </p>
    ),
  },
  {
    title: "Credit Policy and Limits",
    image: { src: "/images/cc_front.png", alt: "NB36 card front" },
    body: (
      <p className="text-slate-600">
        The Credit Limits section outlines tiers and indicative limits. These are demo-only and not real underwriting.
      </p>
    ),
  },
  {
    title: "Apply Flow Overview",
    image: { src: "/images/cc_back.png", alt: "NB36 card back" },
    body: (
      <p className="text-slate-600">
        Use the Apply section to submit a demo application. A modal runs checks and shows an eligibility report.
      </p>
    ),
  },
  {
    title: "Mock APIs Powering the Demo",
    image: { src: "/images/cc_front.png", alt: "NB36 card front" },
    body: (
      <p className="text-slate-600">
        SEON, Experian, Plain, and Taktile mocks simulate AML, Fraud, Credit, and Income checks end-to-end.
      </p>
    ),
  },
  {
    title: "Tips & Relaunch",
    image: { src: "/images/cc_back.png", alt: "NB36 card back" },
    body: (
      <p className="text-slate-600">
        You can close or skip anytime. Use the "Launch Wizard" button in the header to view this tour again.
      </p>
    ),
  },
];

export default function WizardModal({ open, onClose }) {
  const [step, setStep] = React.useState(0);

  React.useEffect(() => {
    if (open) setStep(0);
  }, [open]);

  const isFirst = step === 0;
  const isLast = step === steps.length - 1;
  const isOdd = step % 2 === 1;

  const next = () => setStep((s) => Math.min(s + 1, steps.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));
  const skip = () => onClose?.();
  const done = () => onClose?.();

  const progressPct = ((step + 1) / steps.length) * 100;

  return (
    <Dialog open={open} onClose={onClose} className="relative z-[200]">
      <div className="fixed inset-0 bg-black/30 backdrop-blur-sm" aria-hidden="true" />
      <div className="fixed inset-0 overflow-y-auto">
        <div className="flex min-h-full items-end justify-center p-4 sm:items-center">
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.15, ease: "easeOut" }}
            className="w-full max-w-3xl md:max-w-4xl"
          >
            <div className="overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-xl">
              {/* Header */}
              <div className="border-b border-slate-200 px-6 py-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-xs font-medium text-slate-500">
                      Step {step + 1} of {steps.length}
                    </div>
                    <h3 className="text-base font-semibold text-slate-900">
                      {steps[step].title}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={skip}
                      className="rounded-md px-2 py-1 text-sm text-slate-600 hover:bg-slate-100"
                    >
                      Skip
                    </button>
                    <button
                      type="button"
                      onClick={onClose}
                      className="rounded-md p-1 text-slate-500 hover:bg-slate-100"
                      aria-label="Close tour"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                {/* Progress bar */}
                <div className="mt-3 h-2 w-full rounded-full bg-slate-100">
                  <div
                    className="h-2 rounded-full bg-emerald-600 transition-all"
                    style={{ width: `${progressPct}%` }}
                  />
                </div>
              </div>

              {/* Content */}
              <div className="px-6 py-6">
                <div className="mb-5 flex items-center justify-center gap-1.5">
                  {steps.map((_, i) => (
                    <span
                      key={i}
                      className={
                        "h-2 w-2 rounded-full " +
                        (i === step ? "bg-emerald-600" : "bg-slate-200")
                      }
                    />
                  ))}
                </div>
                <AnimatePresence mode="wait">
                  <motion.div
                    key={step}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    transition={{ duration: 0.15 }}
                  >
                    <div className="grid items-center gap-6 md:grid-cols-2">
                      {/* Image column */}
                      <div className={(isOdd ? "md:order-2" : "md:order-1") + " order-1"}>
                        <div className="relative mx-auto w-full overflow-hidden rounded-xl border border-slate-200 bg-white">
                          <img
                            src={steps[step].image.src}
                            alt={steps[step].image.alt}
                            className="w-full h-56 md:h-80 object-contain p-4"
                          />
                        </div>
                      </div>

                      {/* Text column */}
                      <div className={(isOdd ? "md:order-1" : "md:order-2") + " order-2"}>
                        <div className="text-slate-700 text-sm sm:text-base leading-relaxed space-y-3">
                          {steps[step].body}
                        </div>
                      </div>
                    </div>
                  </motion.div>
                </AnimatePresence>
              </div>

              {/* Footer actions */}
              <div className="flex items-center justify-between gap-3 border-t border-slate-200 px-6 py-4">
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={prev}
                    disabled={isFirst}
                    className={
                      "inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-sm font-medium " +
                      (isFirst
                        ? "cursor-not-allowed border-slate-200 text-slate-300"
                        : "border-slate-200 text-slate-700 hover:bg-slate-50")
                    }
                  >
                    <ArrowLeft className="h-4 w-4" /> Back
                  </button>
                </div>
                <div className="flex items-center gap-2">
                  {!isLast ? (
                    <button
                      type="button"
                      onClick={next}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700"
                    >
                      Next <ArrowRight className="h-4 w-4" />
                    </button>
                  ) : (
                    <button
                      type="button"
                      onClick={done}
                      className="inline-flex items-center gap-1.5 rounded-lg bg-emerald-600 px-3 py-1.5 text-sm font-semibold text-white hover:bg-emerald-700"
                    >
                      Done
                    </button>
                  )}
                  <button
                    type="button"
                    onClick={onClose}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-white px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </Dialog>
  );
}
