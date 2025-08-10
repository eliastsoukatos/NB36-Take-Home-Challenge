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

// NB36 — Single-file, preview-ready landing page
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
  return (
    <div className="min-h-screen bg-white text-slate-900 overflow-x-hidden">
      {/* Decorative background */}
      <div
        className="pointer-events-none absolute inset-0 -z-10"
        aria-hidden
      >
        <div className="absolute -top-1/3 left-1/2 h-[700px] w-[700px] -translate-x-1/2 rounded-full bg-emerald-400/20 blur-[120px]" />
        <div className="absolute bottom-[-200px] right-[-200px] h-[500px] w-[500px] rounded-full bg-emerald-200/30 blur-[100px]" />
      </div>

      <Header />
      <Hero />
      <Highlights />
      <Features />
      <CardShowcase />
      <Security />
      <Testimonials />
      <FAQ />
      <CTA />
      <Footer />
      <StickyApplyBar />
    </div>
  );
}

function Header() {
  const navItems = [
    { label: "Features", href: "#features" },
    { label: "Rewards", href: "#rewards" },
    { label: "Security", href: "#security" },
    { label: "FAQ", href: "#faq" },
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
        <div className="hidden md:flex">
          <a
            href="#apply"
            className="group inline-flex items-center gap-2 rounded-2xl bg-emerald-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-emerald-600/20 transition hover:bg-emerald-700"
          >
            Apply now <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
          </a>
        </div>
        <div className="md:hidden">
          <a
            href="#apply"
            className="rounded-xl border border-emerald-600 px-3 py-2 text-sm font-semibold text-emerald-700"
          >
            Apply
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
            A cleaner, greener way to <span className="text-emerald-600">credit</span>
          </h1>
          <p className="mt-4 max-w-xl text-base leading-relaxed text-slate-600 sm:text-lg">
            Meet the NB36 Card—modern design, powerful rewards, and security you can trust. Apply in minutes and start using your virtual card instantly.
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <a
              href="#apply"
              className="group inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-6 py-3 text-sm font-semibold text-white shadow-lg shadow-emerald-600/25 transition hover:bg-emerald-700"
            >
              Get started <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-0.5" />
            </a>
            <a
              href="#features"
              className="inline-flex items-center justify-center gap-2 rounded-2xl border border-emerald-200 bg-white px-6 py-3 text-sm font-semibold text-emerald-700 hover:border-emerald-300"
            >
              See features
            </a>
          </div>
          <div className="mt-6 flex items-center gap-6 text-xs text-slate-500">
            <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> No annual fee</div>
            <div className="flex items-center gap-2"><CheckCircle2 className="h-4 w-4 text-emerald-600" /> Instant virtual card</div>
          </div>
        </div>
        <div className="relative">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="relative mx-auto w-full max-w-md"
          >
            <CardMockup />
          </motion.div>
          {/* Soft glow */}
          <div className="absolute left-1/2 top-1/2 -z-10 h-56 w-56 -translate-x-1/2 -translate-y-1/2 rounded-full bg-emerald-400/20 blur-3xl" />
        </div>
      </div>
    </section>
  );
}

function Highlights() {
  return (
    <section id="rewards" className="bg-gradient-to-b from-emerald-50/60 to-white">
      <div className="mx-auto max-w-7xl px-4 py-12 md:px-6">
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
          <Highlight label="Dining" value="5%" note="up to quarterly cap" />
          <Highlight label="Travel" value="3%" note="air, hotels, rides" />
          <Highlight label="Everything else" value="1%" note="unlimited" />
          <Highlight label="Annual fee" value="$0" note="no surprises" />
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
  return (
    <section id="features" className="mx-auto max-w-7xl px-4 py-16 md:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Thoughtful features, real benefits</h2>
        <p className="mt-3 text-slate-600">Everything you expect from a modern card—and a few delightful surprises.</p>
      </div>
      <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {features.map(({ title, desc, icon: Icon }) => (
          <motion.div
            key={title}
            initial={{ opacity: 0, y: 16 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            viewport={{ once: true }}
            className="group rounded-2xl border border-emerald-100 bg-white/80 p-6 shadow-sm backdrop-blur-sm transition hover:-translate-y-0.5 hover:shadow-md"
          >
            <div className="mb-4 inline-flex rounded-xl bg-emerald-50 p-3 text-emerald-700 ring-1 ring-inset ring-emerald-100">
              <Icon className="h-5 w-5" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">{title}</h3>
            <p className="mt-1 text-sm leading-relaxed text-slate-600">{desc}</p>
          </motion.div>
        ))}
      </div>
    </section>
  );
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
        <div className="relative grid grid-cols-1 gap-6 sm:grid-cols-2">
          <motion.div
            initial={{ rotate: -6, y: 10, opacity: 0 }}
            whileInView={{ rotate: -6, y: 0, opacity: 1 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="relative"
          >
            <CardMockup variant="emerald" className="shadow-2xl" />
          </motion.div>
          <motion.div
            initial={{ rotate: 6, y: 10, opacity: 0 }}
            whileInView={{ rotate: 6, y: 0, opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.05 }}
            viewport={{ once: true }}
            className="relative"
          >
            <CardMockup variant="white" className="shadow-2xl" />
          </motion.div>
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
            <Shield className="h-3.5 w-3.5" /> Security
          </div>
          <h2 className="mt-4 text-3xl font-bold tracking-tight sm:text-4xl">Security first. Always.</h2>
          <p className="mt-3 text-slate-600">
            From numberless cards and dynamic CVVs to biometric login and one‑tap freeze, NB36 protects your purchases—without slowing you down.
          </p>
          <ul className="mt-6 grid gap-3 sm:grid-cols-2">
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Zero liability on unauthorized transactions</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Encrypted by default, end‑to‑end</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> One‑tap card freeze in app</li>
            <li className="flex items-start gap-3"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Purchase alerts in real time</li>
          </ul>
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
    <section id="faq" className="mx-auto max-w-5xl px-4 py-16 md:px-6">
      <div className="mx-auto max-w-2xl text-center">
        <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">Questions, answered</h2>
      </div>
      <div className="mt-8 divide-y divide-emerald-100 overflow-hidden rounded-2xl border border-emerald-100 bg-white">
        {faqs.map(({ q, a }) => (
          <details key={q} className="group">
            <summary className="flex cursor-pointer list-none items-center justify-between gap-6 px-6 py-5 text-left text-sm font-medium text-slate-900 transition hover:bg-emerald-50/70">
              <span>{q}</span>
              <svg
                className="h-5 w-5 text-emerald-600 transition group-open:rotate-45"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path d="M12 5v14M5 12h14" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
              </svg>
            </summary>
            <div className="px-6 pb-6 text-sm text-slate-600">{a}</div>
          </details>
        ))}
      </div>
      <p className="mt-4 text-center text-xs text-slate-500">
        Rates and rewards subject to change. Terms apply; see your cardmember agreement for details.
      </p>
    </section>
  );
}

function CTA() {
  return (
    <section id="apply" className="relative overflow-hidden py-16">
      <div className="absolute inset-0 -z-10 bg-[radial-gradient(50%_50%_at_50%_50%,_rgba(16,185,129,0.18)_0%,_rgba(16,185,129,0)_60%)]" />
      <div className="mx-auto max-w-5xl rounded-3xl border border-emerald-200 bg-white/80 p-8 shadow-xl backdrop-blur">
        <div className="grid items-center gap-8 md:grid-cols-2">
          <div>
            <h3 className="text-2xl font-bold tracking-tight">Apply in minutes</h3>
            <p className="mt-2 text-sm text-slate-600">No annual fee. No hidden charges. Instant virtual card on approval.</p>
            <ul className="mt-4 space-y-2 text-sm text-slate-600">
              <li className="flex items-start gap-2"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Soft credit check to see your options</li>
              <li className="flex items-start gap-2"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Real‑time status updates</li>
              <li className="flex items-start gap-2"><CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" /> Add to mobile wallet instantly</li>
            </ul>
            <p className="mt-4 text-xs text-slate-500">This is a demo environment—please don’t enter real SSNs or government ID numbers here.</p>
          </div>
          <div>
            <ApplyForm />
          </div>
        </div>
      </div>
    </section>
  );
}

function ApplyForm() {
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
  const [scenario, setScenario] = React.useState("pass"); // for testing: pass | review | ko_compliance

  // UX state
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState("");
  const [result, setResult] = React.useState(null);

  function buildPayload() {
    const address_line1 = apt ? `${street}, ${apt}` : street;
    return {
      user_fullname: fullName,
      user_dob: dob,
      user_country: "US", // default; adjust if you collect it separately
      ssn,
      gov_id_type: govIdType,
      gov_id_number: govIdNumber,
      address_line1,
      address_city: city,
      address_state: state,
      address_zip: zip,
      email,
      phone_number: phone,
      custom_fields: scenario ? { scenario } : {},
    };
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const payload = buildPayload();
      const resp = await fetch("http://localhost:9000/apply/aml-first", {
      //const resp = await fetch("https://nb-backend-fv6v.onrender.com/apply/aml-first", {  
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await resp.json();
      if (!resp.ok) {
        throw new Error(data?.detail || `HTTP ${resp.status}`);
      }
      setResult(data);
    } catch (err) {
      setError(err?.message || "Submission failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-3">
      {/* Name */}
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

      {/* DOB + SSN */}
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

      {/* Government ID */}
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

      {/* Contact */}
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

      {/* Current Address */}
      <fieldset className="mt-1 rounded-xl border border-emerald-200 p-3">
        <legend className="px-1 text-xs font-semibold text-emerald-700">Current Address</legend>
        <div className="grid gap-3">
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
        </div>
      </fieldset>

      {/* Prior Address (conditional) */}
      {needsPriorAddress && (
        <fieldset className="rounded-xl border border-emerald-200 p-3">
          <legend className="px-1 text-xs font-semibold text-emerald-700">Prior Address</legend>
          <div className="grid gap-3">
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
          </div>
        </fieldset>
      )}

      {/* Income Range (kept) */}
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-700">Income range</label>
        <select className="w-full appearance-none rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring">
          <option>Under $30,000</option>
          <option>$30,000–$60,000</option>
          <option>$60,000–$100,000</option>
          <option>$100,000–$150,000</option>
          <option>$150,000+</option>
        </select>
      </div>

      {/* Testing helper: scenario */}
      <div>
        <label className="mb-1 block text-xs font-medium text-slate-700">Test scenario (demo only)</label>
        <select
          className="w-full appearance-none rounded-xl border border-emerald-200 bg-white px-4 py-2.5 text-sm outline-none ring-emerald-500/20 focus:ring"
          value={scenario}
          onChange={(e) => setScenario(e.target.value)}
        >
          <option value="pass">pass (PROCEED)</option>
          <option value="review">review (context)</option>
          <option value="ko_compliance">ko_compliance (DECLINE)</option>
        </select>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading}
        className="mt-1 inline-flex items-center justify-center gap-2 rounded-2xl bg-emerald-600 px-5 py-3 text-sm font-semibold text-white shadow-md shadow-emerald-600/25 transition hover:bg-emerald-700 disabled:opacity-60"
      >
        {loading ? "Submitting..." : "Apply now"} <ArrowRight className="h-4 w-4" />
      </button>
      <p className="text-xs text-slate-500">By submitting, you agree to be contacted about your application. This demo does not collect real data.</p>

      {/* Error */}
      {error && (
        <div className="mt-3 rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Result */}
      {result && (
        <div className="mt-3 rounded-xl border border-emerald-200 bg-emerald-50 p-4">
          <div className="text-sm font-semibold text-emerald-800">AML result</div>
          <div className="mt-1 text-sm text-slate-700">
            Status: <span className="font-mono">{result.status}</span>
          </div>
          <div className="mt-1 text-sm text-slate-700">
            Decision: <span className="font-mono">{result.aml_decision?.decision}</span>
          </div>
          {Array.isArray(result.aml_decision?.reasons) && result.aml_decision.reasons.length > 0 && (
            <div className="mt-1 text-sm text-slate-700">
              Reasons:
              <ul className="mt-1 list-disc pl-5">
                {result.aml_decision.reasons.map((r) => (
                  <li key={r} className="font-mono">{r}</li>
                ))}
              </ul>
            </div>
          )}
          <div className="mt-2 text-xs text-slate-500">
            Case ID: <span className="font-mono">{result.case_id}</span>
          </div>
        </div>
      )}
    </form>
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
          className="rounded-xl bg-emerald-600 px-4 py-2 text-xs font-semibold text-white shadow-md shadow-emerald-600/25"
        >
          Apply now
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
