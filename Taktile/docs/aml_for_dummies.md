# AML Compliance Check — KO & “Tiers” (For Dummies)

What is this step?
- This is a hard safety check. We ask: “Are we legally/compliantly allowed to do business with this person?” If the answer is no, we stop right here.

What do we check?
- We search the person’s full name + (DOB/country when available) against official and reputable lists:
  - Sanctions lists (governments/UN say “do not do business with these people/entities”)
  - PEP (Politically Exposed Persons) — higher scrutiny; your policy decides if certain PEPs are allowed or not
  - Criminal/watchlists (known high-risk individuals)
  - Adverse media (news coverage suggesting financial crime)
- We use SEON’s AML API to do these searches in one shot.

Simple rule: “Red lights stop the car”
- If we get a sanctions match → Decline (absolute KO)
- If we get a disqualifying PEP or criminal list match → Decline
- If we get adverse media only → Don’t auto-decline. It’s a yellow light (context). We can review later if needed.

Why so strict?
- Because this is about laws and serious risk (fincrime, AML). If we’re not allowed to do business with someone, no amount of “good credit” or “deposit” can fix that. This is non-negotiable.

Do we assign tiers here?
- No. AML is pass/fail:
  - Fail = Decline (stop)
  - Pass = Proceed to the next check (Fraud risk, then later Credit Bureau & Income)
- Tiers (0–7) are about how much risk we’re willing to take if the person is legally okay. That comes after AML.

What do we tell the customer?
- If Declined (Compliance): We say we’re unable to proceed at this time and provide a general reason category (per legal guidance). We do not reveal sensitive list details.
- If Passed: We tell them we’re moving to the next step.

What if the AML service fails (timeout/error)?
- We do not auto-approve. We either queue for manual review or try again.
- In this demo, we mark it as a technical decline; in real life, you’d route to Review.

Summary in one line
- AML = legal red-light check. Red light → stop. Green light → continue. No tiers here.
