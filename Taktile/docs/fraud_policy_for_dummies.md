# Fraud Check — Simple Explainer (“For Dummies”)

What is this step?
- This checks if the session/device/network looks trustworthy before we proceed.
- Think of it as: “Is anything about how you’re applying (device, IP, email/phone) suspicious?”

What do we look at?
- Email/phone signals (age, risk lists, known breaches)
- IP reputation (country, datacenter vs. residential, VPN/proxy/Tor)
- Device fingerprint and behavior (emulator/bot flags, consistency)
- Geolocation consistency (IP vs. claimed address/country)
- Combined “fraud score” from the vendor (SEON mock in this demo)

How do we decide?
- Red light (Fraud Decline):
  - Very high risk score, OR
  - Multiple severe red flags together (e.g., VPN/proxy + datacenter IP + emulator/bot)
- Yellow light (Fraud Review):
  - Medium-high score, OR
  - A single severe red flag, OR
  - Missing device/session data (not enough information to trust)
- Green light (Fraud Pass):
  - Low risk score and clean signals

What about tiers?
- When we Pass fraud, we assign a provisional tier (0–7) where 7 is best.
- Lower fraud score ⇒ higher tier.
- These thresholds are placeholders for demo and will be tuned later.

What do we tell the customer?
- Decline: Neutral message that we’re unable to proceed at this time (don’t reveal sensitive vendor details).
- Review: We may say “We’re reviewing your application; you’ll receive an update soon.”
- Pass: Move on to the next checks (e.g., credit, income) and let them know we’re proceeding.

Why this matters
- We want to stop fraud early—before we consider credit history or income.
- This reduces losses and protects genuine customers.

How this demo works
- We call a mock vendor (SEON) which returns a fraud score and signals.
- We apply simple rules to return: Fraud Decline, Fraud Review, or Fraud Pass (with a provisional tier).
- You can force scenarios for testing (e.g., “ko_fraud”, “review”, “pass”).
