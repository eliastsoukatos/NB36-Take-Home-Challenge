import React from "react";
import { Dialog } from "@headlessui/react";
import { AnimatePresence, motion } from "framer-motion";
import { ArrowLeft, ArrowRight, X } from "lucide-react";

// Define 6 steps with image + text content
const steps = [
  {
    title: "Welcome",
    image: { src: "/images/elias.png", alt: "NB36 card front" },
    body: (
      <>
        <p className="text-slate-600">
          Hi! My name is Elias Tsouaktos, and I’m truly excited about the opportunity to work at Taktile.
        </p>
        <p className="mt-3 text-slate-600">
          I have to admit — I had a lot of fun building this take-home challenge. If this is the kind of work I’d be doing at Taktile, I think I could do really well and contribute meaningfully. This project has only reinforced my belief that this would be a fantastic opportunity for me.
        </p>
      </>
    ),
  },
  {
    title: "APIs & Mock Setup",
    image: { src: "/images/github.png", alt: "NB36 card back" },
    body: (
      <>
        <p className="text-slate-600">
          To complete this challenge, I needed to connect to several APIs mentioned in the documentation. Since those APIs were not publicly accessible, I created four mock APIs to simulate the interactions. These mocks are based on the official documentation I found online and are designed to behave very similarly to the real ones.
        </p>
        <p className="mt-3 text-slate-600">
          The APIs I mocked were SEON, Experian, and Plaid. I also built a Taktile agent that calls them all, simulating Taktile’s role. The application, built with Next.js + Tailwind on the frontend and Python on the backend, connects to the mock Taktile API, which in turn interacts with the other mock APIs. The entire project is open-source on GitHub, so you can explore the full code anytime.
        </p>
      </>
    ),
  },
  {
    title: "Architecture Diagram",
    image: { src: "/images/diagram.png", alt: "NB36 card front" },
    body: (
      <>
        <p className="text-slate-600">
          To make the process clearer, I created a diagram showing the full architecture. It looks simple, but it works smoothly.
        </p>
        <ul className="mt-3 list-disc pl-5 text-sm text-slate-600 space-y-1">
          <li>Read the detailed README files on GitHub</li>
          <li>Explore the code directly</li>
          <li>Run the project yourself</li>
          <li>Or, of course, you can just ask me — I’m happy to walk you through it.</li>
        </ul>
      </>
    ),
  },
  {
    title: "KO Criteria & Credit Policy",
    image: { src: "/images/credit_policy.png", alt: "NB36 card back" },
    body: (
      <p className="text-slate-600">
        For this challenge, I designed the Knock-Out (KO) criteria and the credit policy. I studied the API documentation from each provider in the test and developed a tier system for credit approvals. Your assigned tier determines the maximum credit you can access — regardless of your income.
      </p>
    ),
  },
  {
    title: "Credit Limits & Criteria",
    image: { src: "/images/credit_limits.png", alt: "NB36 card front" },
    body: (
      <p className="text-slate-600">
        You can review the credit limits and the criteria I implemented to assign them. This is explained briefly on the landing page, and in more detail on the Credit Policy page of the application.
      </p>
    ),
  },
  {
    title: "Testing the Application",
    image: { src: "/images/kyi_check.png", alt: "NB36 card back" },
    body: (
      <>
        <p className="text-slate-600">
          To test the application, simply submit a credit application and wait for the automated analysis. You’ll be able to:
        </p>
        <ul className="mt-3 list-disc pl-5 text-sm text-slate-600 space-y-1">
          <li>Read the JSON report returned by the backend to verify that the logic matches the architecture diagram</li>
          <li>Use the demo tool (bottom-right corner) to experiment with different credit scenarios</li>
        </ul>
        <p className="mt-3 text-slate-600">
          The tool will evaluate your application, assign you a Tier level, and set a credit limit based on the criteria.
        </p>
      </>
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
  const leftBias = new Set([1, 3, 4, 5]); // steps 2, 4, 5, 6

  const next = () => setStep((s) => Math.min(s + 1, steps.length - 1));
  const prev = () => setStep((s) => Math.max(s - 1, 0));
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
                        <div className="relative mx-auto w-full aspect-square overflow-hidden rounded-xl border border-slate-200 bg-white">
                          <img
                            src={steps[step].image.src}
                            alt={steps[step].image.alt}
                            className={"w-full h-full object-cover " + (leftBias.has(step) ? "object-left" : "object-center")}
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
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </Dialog>
  );
}
