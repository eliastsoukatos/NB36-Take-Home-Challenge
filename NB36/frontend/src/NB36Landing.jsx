import React from "react";
import { motion } from "framer-motion";
import {
  Shield,
  CreditCard,
  Sparkles,
  Lock,
  CheckCircle2,
  Smartphone,
  Banknote,
  ArrowRight,
  Apple,
  Store,
  Trophy,
  Gift,
} from "lucide-react";
import ApplyPageForm from "../components/form/ApplyPageForm.jsx";
import DemoPanel from "../components/demo/DemoPanel.jsx";
import WizardModal from "../components/wizard/WizardModal.jsx";

// NB36 — Landing page with redesigned Apply flow (modal + balanced layout)
// TailwindCSS + Framer Motion + Lucide icons
// Palette: white base with emerald/green accents

const features = [
  {
    title: "Up to 5% Back",
    desc: "Earn elevated rewards on dining & travel, plus 1% everywhere.",
    icon: Trophy,
  },
  {
    title: "$0 Annual Fee",
    desc: "Transparent pricing with no hidden charges or surprises.",
    icon: Banknote,
  },
  {
    title: "Instant Virtual Card",
    desc: "Start using your card online the moment you’re approved.",
    icon: Smartphone,
  },
  {
    title: "Bank‑Grade Security",
    desc: "24/7 fraud monitoring, biometric login, and card‑freezing.",
    icon: Shield,
  },
  {
    title: "Premium Perks",
    desc: "Airport lounge discounts, partner offers, and more.",
    icon: Gift,
  },
  {
    title: "Zero Liability",
    desc: "You’re protected from unauthorized purchases.",
    icon: Lock,
  },
];

const REPO_URL = "https://github.com/eliastsoukatos/NB36-Take-Home-Challenge"; // TODO: replace with your real GitHub repo URL

const faqs = [
  {
    q: "What’s the APR?",
    a: "Variable APRs from 17.99%–24.99% based on creditworthiness. Subject to change; see terms at application.",
  },
  {
    q: "Is there an annual fee?",
    a: "$0 annual fee. Some premium upgrades may include optional fees—clearly disclosed before you enroll.",
  },
  {
    q: "How do rewards work?",
    a: "Earn 5% on dining (up to a quarterly cap), 3% on travel, and 1% on all other purchases. Redeem for statement credits, travel, or gift cards.",
  },
  {
    q: "How fast is approval?",
    a: "Most applicants receive a decision in under a minute. Approved users get an instant virtual card for online purchases.",
  },
  {
    q: "Can I freeze my card?",
    a: "Yes—freeze/unfreeze in one tap from the NB36 app. You can also set merchant, geography, and amount limits.",
  },
];

export default function NB36Landing() {
  const [wizardOpen, setWizardOpen] = React.useState(false);
  React.useEffect(() => {
    setWizardOpen(true);
  }, []);
  // Hidden-by-default demo controls; passed to ApplyPageForm
  const [demoConfig, setDemoConfig] = React.useState({
    scenario: "pass",
    incomeScenario: "income_pass",
    incomeCoverageMonths: 12,
  });

  return (
    <div className="min-h-screen bg-white text-slate-900 overflow-x-hidden">
      {/* Decorative background */}
      <div className="pointer-events-none absolute inset-0 -z-10 overflow-hidden" aria-hidden>
        <div className="absolute -top-1/3 left-1/2 h-[700px] w-[700px] -translate-x-1/2 rounded-full bg-emerald-400/20 blur-[120px]" />
        <div className="absolute bottom-[-200px] right-[-200px] h-[500px] w-[500px] rounded-full bg-emerald-200/30 blur-[100px]" />
      </div>

      <Header onLaunchWizard={() => setWizardOpen(true)} />
      <Hero />
      <Highlights />
      <Features />
      <CardShowcase />
      <Security />
      <FAQ />
      <CTA demoConfig={demoConfig} setDemoConfig={setDemoConfig} />
      <Footer />
      <StickyApplyBar />

      {/* Hidden demo controls (gated in component) */}
      <DemoPanel demoConfig={demoConfig} setDemoConfig={setDemoConfig} />
      <WizardModal open={wizardOpen} onClose={() => setWizardOpen(false)} />
    </div>
  );
}

function Header({ onLaunchWizard }) {
  const navItems = [
    { label: "Diagram", href: "/diagram.html" },
    { label: "Documentation", href: REPO_URL },
    { label: "Credit Policy", href: "/credit-policy.html" },
    { label: "Credit Limits", href: "#creditlimit" },
  ];
  return (
    <header className="sticky top-0 z-40 backdrop-blur supports-[backdrop-filter]:bg-white/60 bg-white/50">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 md:px-6">
        <a href="#top" className="flex items-center gap-2">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-500 text-white shadow-lg">
            <span className="font-bold">N</span>
          </div>
          <span className="text-lg font-semibold tracking-tight">NB36 Bank</span>
        </a>
        <nav className="hidden items-center gap-8 md:flex">
          {navItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className="text-sm font-medium text-slate-700 transition-colors hover:text-emerald-700"
            >
              {item.label}
            </a>
          ))}
        </nav>
        <div className="hidden md:flex items-center gap-3">
          <button
            type="button"
            onClick={onLaunchWizard}
            className="rounded-2xl border border-emerald-600 px-5 py-2.5 text-sm font-semibold text-emerald-700 hover:bg-emerald-50"
          >
            Launch Wizard
          </button>
          <a
            href="#apply"
            aria-label="Apply Now"
            className="group inline-flex items-center gap-2 rounded-2xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-600/20 transition hover:bg-emerald-700"
          >
            Apply Now <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </a>
        </div>
        <div className="md:hidden flex items-center gap-2">
          <button
            type="button"
            onClick={onLaunchWizard}
            className="rounded-xl border border-emerald-600 px-3 py-2 text-sm font-semibold text-emerald-700"
          >
            Wizard
          </button>
          <a
            href="#apply"
            aria-label="Open application form section"
            className="rounded-xl border border-emerald-600 px-3 py-2 text-sm font-semibold text-emerald-700"
          >
            Open form
          </a>
        </div>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="relative mx-auto max-w-7xl px-4 pb-16 pt-10 md:px-6 md:pt-16 lg:pt-24">
      <div className="grid items-center gap-10 md:grid-cols-2">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs font-medium text-emerald-800">
            <Sparkles className="h-3.5 w-3.5" />
            New: NB36 Credit Card
          </div>
<h1 className="mt-4 text-4xl font-extrabold leading-tight tracking-tight sm:text-5xl md:text-6xl">
            A new way to <span className="text-emerald-600">credit</span>
<span className="block">powered by <span className="text-slate-900">Taktile</span></span>
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-slate-600 sm:text-lg">
            Review the detailed solution architecture diagram to understand the end-to-end process—from the moment of application to the final delivery.
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <a
              href="#apply"
              aria-label="Apply Now"
              className="group inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-600/25 transition hover:bg-emerald-700"
            >
              Apply Now <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </a>
            <a
              href="/diagram.html"
              className="inline-flex items-center justify-center gap-2 rounded-2xl border border-emerald-200 bg-white px-6 py-3 text-sm font-semibold text-emerald-700 hover:border-emerald-300"
            >
              View diagram
            </a>
          </div>
          <div className="mt-6 flex items-center gap-6 text-xs text-slate-500">
            <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> No annual fee</div>
            <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> Instant virtual card</div>
          </div>
        </div>
        <div className="relative pb-6">
<motion.img
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            style={{ filter: "drop-shadow(0 18px 28px rgba(16,24,40,0.22)) drop-shadow(0 2px 8px rgba(16,24,40,0.12))" }}
            className="relative z-10 mx-auto w-full max-w-md rounded-3xl"
src="/images/cc_front.png"
            alt="NB36 Card"
/>
          {/* Under-ellipse shadow */}
          <div
            aria-hidden
            className="pointer-events-none absolute left-1/2 -bottom-2 h-12 w-[110%] -translate-x-1/2 rounded-[999px] bg-black/30 blur-3xl"
          />
          {/* Soft glow */}
          <div className="absolute left-1/2 top-1/2 -z-10 h-56 w-56 -translate-x-1/2 -translate-y-1/2 rounded-full bg-emerald-400/20 blur-3xl" />
        </div>
      </div>
    </section>
  );
}

function Highlights() {
  const apis = [
    {
      name: "SEON",
      desc: "Fraud signals & device risk mock for demo flows.",
      href: REPO_URL + "?ref=seon",
      icon: Shield,
      accent: "from-emerald-50 to-white",
    },
    {
      name: "Experian",
      desc: "Credit bureau mock with tiers & scorecard hints.",
      href: REPO_URL + "?ref=experian",
      icon: Trophy,
      accent: "from-emerald-50 to-white",
    },
    {
      name: "Plain",
      desc: "Income verification mock with payroll/bank modes.",
      href: REPO_URL + "?ref=plain",
      icon: Banknote,
      accent: "from-emerald-50 to-white",
    },
    {
      name: "Taktile",
      desc: "Decision orchestration mock powering final outcome.",
      href: REPO_URL + "?ref=taktile",
      icon: Sparkles,
      accent: "from-emerald-50 to-white",
    },
  ];

  return (
    <section id="rewards" className="bg-gradient-to-b from-emerald-50/60 to-white">
      <div className="mx-auto max-w-7xl px-4 py-12 md:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">4 Mock APIs for this Demo</h2>
          <p className="mt-3 text-slate-600">
            SEON, Experian, Plain, and Taktile power this demo end-to-end.
          </p>
          <a
            href={REPO_URL}
            className="mt-4 inline-flex items-center gap-2 rounded-xl border border-emerald-200 bg-white px-4 py-2 text-sm font-semibold text-emerald-700 hover:border-emerald-300"
          >
            View GitHub repository
          </a>
        </div>

        <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          {apis.map(({ name, desc, href, icon: Icon, accent }) => (
            <a
              key={name}
              href={href}
              className="group block rounded-2xl border border-emerald-100 bg-white p-5 shadow-sm ring-emerald-100 transition hover:-translate-y-0.5 hover:shadow-md hover:ring-2"
            >
              <div className={`mb-4 inline-flex rounded-xl bg-gradient-to-br ${accent} p-3 text-emerald-700 ring-1 ring-inset ring-emerald-100 group-hover:shadow`}>
                <Icon className="h-5 w-5" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900">{name}</h3>
              <p className="mt-1 text-sm leading-relaxed text-slate-600">{desc}</p>
              <div className="mt-3 text-sm font-medium text-emerald-700 group-hover:underline">
                View on GitHub →
              </div>
            </a>
          ))}
        </div>
      </div>
    </section>
  );
}

function Highlight({ label, value, note }) {
  return (
    <div className="rounded-2xl border border-emerald-100 bg-white p-5 shadow-sm transition hover:shadow-md">
      <div className="text-xs font-medium uppercase tracking-wide text-emerald-700">{label}</div>
      <div className="mt-2 text-3xl font-extrabold tracking-tight text-slate-900">{value}</div>
      <div className="text-xs text-slate-500">{note}</div>
    </div>
  );
}

function Features() {
  return null;
}

function CardShowcase() {
  return (
    <section className="bg-emerald-900/95 py-16 text-white">
      <div className="mx-auto grid max-w-7xl items-center gap-12 px-4 md:grid-cols-2 md:px-6">
        <div>
          <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-1 text-xs font-medium">
            <CreditCard className="h-3.5 w-3.5" /> Design
          </div>
          <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">Minimal on the outside, mighty on the inside</h2>
          <p className="mt-3 max-w-xl text-white/80">
            The NB36 Card blends clean lines with a soft emerald gradient and subtle micro‑texture. Tap to pay, numberless face, and dynamic CVV in-app.
          </p>
          <ul className="mt-6 space-y-3 text-sm text-white/80">
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-300" /> Contactless + EMV chip</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-300" /> Numberless card surface</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-300" /> Eco‑conscious materials</li>
          </ul>
          <div className="mt-8 flex flex-wrap gap-3">
            <Store className="h-5 w-5" /> <Apple className="h-5 w-5" />
            <span className="text-sm text-white/70">Add to Apple Pay® & Google Pay™</span>
          </div>
        </div>
        <div className="relative">
          <motion.img
            initial={{ opacity: 0, y: 10 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="mx-auto w-full max-w-lg rounded-2xl"
            src="/images/cc_back.png"
            alt="NB36 card"
          />
        </div>
      </div>
    </section>
  );
}

function Security() {
  return (
    <section id="security" className="mx-auto max-w-7xl px-4 py-16 md:px-6">
      <div className="grid items-center gap-10 md:grid-cols-2">
        <div className="order-2 md:order-1">
          <div className="relative mx-auto max-w-md">
            <div className="absolute -inset-2 -z-10 rounded-3xl bg-emerald-200/40 blur-xl" />
            <div className="rounded-3xl border border-emerald-100 bg-gradient-to-br from-white to-emerald-50/50 p-6 shadow">
              <div className="flex items-center gap-3">
                <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-emerald-600 text-white">
                  <Lock className="h-5 w-5" />
                </div>
                <div>
                  <div className="text-sm font-semibold">Real‑time Protection</div>
                  <div className="text-xs text-slate-500">24/7 monitoring + instant alerts</div>
                </div>
              </div>
              <div className="mt-5 rounded-2xl border border-emerald-100 bg-white p-4">
                <div className="flex items-center justify-between text-sm">
                  <span className="font-medium text-slate-700">Freeze Card</span>
                  <span className="text-emerald-700">Enabled</span>
                </div>
                <div className="mt-3 h-2 w-full rounded-full bg-emerald-100">
                  <div className="h-2 w-2/3 rounded-full bg-emerald-500" />
                </div>
                <div className="mt-3 text-xs text-slate-500">Spending controls, merchant limits, and location rules keep you in control.</div>
              </div>
            </div>
          </div>
        </div>
        <div className="order-1 md:order-2">
          <div className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-white px-3 py-1 text-xs font-medium text-emerald-800">
            <Shield className="h-3.5 w-3.5" /> Credit Policy
          </div>
          <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">Credit Policy</h2>
          <p className="mt-3 text-slate-600">
            We evaluate each application using a transparent policy across key risk and affordability dimensions.
          </p>
          <ul className="mt-6 grid gap-3 sm:grid-cols-2">
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> AML — anti‑money laundering screening</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Fraud — device, behavioral, and identity risk</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Credit — bureau data and scorecard insights</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Income — verification coverage and stability</li>
          </ul>
          <div className="mt-6">
            <a
              href="/credit-policy.html"
              className="inline-flex items-center gap-2 rounded-2xl bg-emerald-600 px-4 py-2 text-sm font-semibold text-white shadow hover:bg-emerald-700"
            >
              View Credit Policy
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

function Testimonials() {
  return (
    <section className="bg-gradient-to-b from-white to-emerald-50/60 py-16">
      <div className="mx-auto max-w-7xl px-4 md:px-6">
        <div className="mx-auto max-w-2xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Loved by early members</h2>
          <p className="mt-3 text-slate-600">Real people. Real upgrades to daily spending.</p>
        </div>
        <div className="mt-10 grid gap-6 md:grid-cols-3">
          <TestimonialCard
            quote="The virtual card was live before my physical card arrived—super clutch for booking travel."
            name="Amara N."
            role="Product Manager"
          />
          <TestimonialCard
            quote="Clean design, great app, and the 5% dining category basically pays for my coffee addiction."
            name="Leo R."
            role="Barista & DJ"
          />
          <TestimonialCard
            quote="I froze my card in seconds and set a limit for online stores. Peace of mind is priceless."
            name="Priya K."
            role="Engineer"
          />
        </div>
      </div>
    </section>
  );
}

function TestimonialCard({ quote, name, role }) {
  return (
    <motion.blockquote
      initial={{ opacity: 0, y: 16 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true }}
      transition={{ duration: 0.4 }}
      className="h-full rounded-2xl border border-emerald-100 bg-white p-6 shadow-sm"
    >
      <p className="text-slate-700">“{quote}”</p>
      <footer className="mt-4 flex items-center gap-3">
        <div className="h-9 w-9 rounded-full bg-emerald-100" />
        <div>
          <div className="text-sm font-semibold">{name}</div>
          <div className="text-xs text-slate-500">{role}</div>
        </div>
      </footer>
    </motion.blockquote>
  );
}

function FAQ() {
  return (
    <section id="creditlimit" className="mx-auto max-w-5xl px-4 py-16 md:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Credit Limits</h2>
        <p className="mt-3 text-slate-600">
          Tiers 0–7 with indicative limits and demo‑only criteria. Final tier reflects the minimum across AML, Fraud, Credit, and Income checks.
        </p>
      </div>
      <div className="mt-8 divide-y divide-emerald-100 overflow-hidden rounded-2xl border border-emerald-100 bg-white">
        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 0 — under $6,400 limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Decline if sanctions, PEP, or criminal match found.</li>
              <li>Fraud: Decline if fraud score ≥ 90 or severe red flags.</li>
              <li>Credit: Decline if score below 660 or major derogatory events.</li>
              <li>Income: Under $800/month or insufficient proof.</li>
            </ul>
          </div>
        </details>

        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 1 — $6,400 – $7,992 limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Pass.</li>
              <li>Fraud: Fraud score ≤ 90.</li>
              <li>Credit: Bureau tier = 1 (low tier, close to decline).</li>
              <li>Income: $800–$999 monthly.</li>
            </ul>
          </div>
        </details>

        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 2 — $8,000 – $11,192 limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Pass.</li>
              <li>Fraud: Fraud score ≤ 80.</li>
              <li>Credit: Bureau tier = 2 (borderline, moderate negatives).</li>
              <li>Income: $1,000–$1,399 monthly.</li>
            </ul>
          </div>
        </details>

        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 3 — $11,200 – $14,392 limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Pass.</li>
              <li>Fraud: Fraud score ≤ 70.</li>
              <li>Credit: Bureau tier = 3 (fair credit, some issues).</li>
              <li>Income: $1,400–$1,799 monthly.</li>
            </ul>
          </div>
        </details>

        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 4 — $14,400 – $19,992 limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Pass.</li>
              <li>Fraud: Fraud score ≤ 60.</li>
              <li>Credit: Bureau tier = 4 (good credit, manageable concerns).</li>
              <li>Income: $1,800–$2,499 monthly.</li>
            </ul>
          </div>
        </details>

        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 5 — $20,000 – $27,992 limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Pass.</li>
              <li>Fraud: Fraud score ≤ 50.</li>
              <li>Credit: Bureau tier = 5 (very good credit, few minor issues).</li>
              <li>Income: $2,500–$3,499 monthly.</li>
            </ul>
          </div>
        </details>

        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 6 — $28,000 – $39,992 limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Pass.</li>
              <li>Fraud: Fraud score ≤ 40, minimal risk signs.</li>
              <li>Credit: Bureau tier = 6 (excellent credit, small negatives).</li>
              <li>Income: $3,500–$4,999 monthly.</li>
            </ul>
          </div>
        </details>

        <details className="group">
          <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
            <span>Tier 7 — $40,000 + limit</span>
            <svg className="h-5 w-5 text-emerald-600 transition group-open:rotate-45" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" /></svg>
          </summary>
          <div className="px-6 pb-6 text-sm text-slate-600">
            <ul className="list-disc pl-5 space-y-1">
              <li>AML: Must pass with no sanctions, PEP, or criminal matches.</li>
              <li>Fraud: Fraud score ≤ 30, no severe device/IP red flags.</li>
              <li>Credit: Bureau tier = 7 (excellent score, very low debt use, long history).</li>
              <li>Income: $5,000+ monthly (verified, ≥ 3 months coverage or payroll).</li>
            </ul>
          </div>
        </details>
      </div>
      <p className="mt-4 text-center text-xs text-slate-500">
        Limits and criteria are for demo only and not indicative of real underwriting.
      </p>
    </section>
  );
}

function CTA({ demoConfig, setDemoConfig }) {
  return (
    <section id="apply" className="relative overflow-hidden py-16">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(50%_50%_at_50%_50%,_rgba(16,185,129,0.18)_0%,_rgba(16,185,129,0)_60%)]" />
      <div className="mx-auto max-w-5xl rounded-3xl border border-emerald-200 bg-white/80 p-6 shadow-xl backdrop-blur">
        <ApplyPageForm demoConfig={demoConfig} />
        <p className="mt-4 text-xs text-slate-500">
          This is a demo environment—please don’t enter real SSNs or government ID numbers here.
        </p>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-emerald-100/70 bg-white">
      <div className="mx-auto max-w-7xl px-4 py-10 md:px-6">
        <div className="flex flex-col items-start justify-between gap-6 md:flex-row md:items-center">
          <a href="#top" className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-emerald-600 text-white">
              <span className="font-bold">N</span>
            </div>
            <span className="text-lg font-semibold">NB36 Bank</span>
          </a>
          <div className="text-xs text-slate-500">
            © {new Date().getFullYear()} NB36 Bank. All rights reserved. | Member FDIC | Equal Housing Lender
          </div>
        </div>
        <div className="mt-6 text-xs text-slate-500">
          <p>
            All credit products are subject to credit approval. Terms, conditions, and exclusions apply. Rewards categories, caps, and rates may change.
          </p>
        </div>
      </div>
    </footer>
  );
}

function StickyApplyBar() {
  return (
    <div className="fixed inset-x-0 bottom-0 z-40 border-t border-emerald-200 bg-white/95 p-3 backdrop-blur supports-[backdrop-filter]:bg-white/70 md:hidden">
      <div className="mx-auto flex max-w-7xl items-center justify-between">
        <div className="flex items-center gap-2 text-sm">
          <CreditCard className="h-4 w-4 text-emerald-700" />
          <span className="font-medium text-slate-800">NB36 Credit Card</span>
        </div>
        <a
          href="#apply"
          aria-label="Open application form section"
          className="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-emerald-600/25"
        >
          Open form
        </a>
      </div>
    </div>
  );
}

function CardMockup({ variant = "emerald", className = "" }) {
  const isEmerald = variant === "emerald";
  return (
    <div
      className={
        "relative mx-auto h-56 w-96 max-w-full rounded-3xl border p-5 shadow-xl " +
        (isEmerald
          ? "border-emerald-200 bg-gradient-to-br from-emerald-500 to-emerald-700 text-white"
          : "border-emerald-100 bg-white text-slate-900") +
        " " +
        className
      }
      style={{
        backgroundImage: isEmerald
          ? undefined
          : "radial-gradient(120% 120% at 0% 0%, rgba(16,185,129,0.12) 0%, rgba(16,185,129,0) 40%), radial-gradient(120% 120% at 100% 100%, rgba(16,185,129,0.1) 0%, rgba(16,185,129,0) 40%)",
      }}
    >
      {/* Top Row */}
      <div className="flex items-center justify-between">
        <div className={"flex h-9 w-9 items-center justify-center rounded-xl " + (isEmerald ? "bg-white/20" : "bg-emerald-50") }>
          <span className={"font-bold " + (isEmerald ? "text-white" : "text-emerald-700")}>N</span>
        </div>
        <div className={"rounded-full px-3 py-1 text-[10px] uppercase tracking-wider " + (isEmerald ? "bg-white/20 text-white" : "bg-emerald-50 text-emerald-700")}>NB36</div>
      </div>

      {/* Chip + Waves */}
      <div className="mt-6 flex items-center gap-3">
        <div className={"h-8 w-10 rounded bg-gradient-to-br " + (isEmerald ? "from-white/85 to-white/60" : "from-emerald-100 to-emerald-50")}></div>
        <div className={"h-6 w-10 rounded " + (isEmerald ? "bg-white/25" : "bg-emerald-100")} />
      </div>

      {/* Numberless face */}
      <div className="mt-8 grid grid-cols-2 items-end">
        <div>
          <div className={"text-xs " + (isEmerald ? "text-white/80" : "text-slate-500")}>Cardholder</div>
          <div className="text-lg font-semibold tracking-wide">ALEX JOHNSON</div>
        </div>
        <div className="justify-self-end text-right">
          <div className={"text-xs " + (isEmerald ? "text-white/80" : "text-slate-500")}>Valid thru</div>
          <div className="text-lg font-semibold tracking-wide">12/28</div>
        </div>
      </div>

      {/* Bottom stripe */}
      <div className={"absolute inset-x-5 bottom-4 h-1 rounded-full " + (isEmerald ? "bg-white/30" : "bg-emerald-200")} />
    </div>
  );
}
