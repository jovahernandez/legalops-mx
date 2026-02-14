# Riskiest Assumptions (Hypotheses)

## H1: Firms will adopt AI-assisted intake over their current process

**Assumption:** Small-to-mid legal firms (5-30 people) currently do intake via
phone/email/paper and will switch to a structured digital intake + agent triage
if it saves them >2 hours/week.

**Success criteria:** 2 out of 3 pilot firms process >80% of new intakes through
the platform within 4 weeks of onboarding.

**Failure signal:** Firms revert to phone intake or stop using the platform
within 2 weeks.

**Experiment:** E1 (below).

---

## H2: The "Human Approval Gate" is fast enough to not kill the funnel

**Assumption:** Attorneys/staff will review and approve/reject agent outputs
within 24 hours, keeping the client experience acceptable.

**Success criteria:** Median time-to-approve < 24 hours across all tenants.

**Failure signal:** Median time-to-approve > 48 hours, or >30% of approvals
sit in "pending" for >72 hours.

**Experiment:** E2 (below).

---

## H3: B2C "Prep Kit" generates qualified leads for partner firms

**Assumption:** Individuals who use the free Prep Kit (document checklist +
questions for their attorney) are 3x more likely to convert into paying clients
for a partner firm compared to cold leads.

**Success criteria:** >15% of Prep Kit users click "Contact partner firm" AND
>5% of those become Matter conversions within 30 days.

**Failure signal:** <5% click "Contact partner firm" OR <1% convert.

**Experiment:** E3 (below).

---

## H4: The Policy Engine catches enough UPL to keep us compliant

**Assumption:** Regex-based UPL detection + mandatory approval gate is sufficient
for v1 compliance. Zero UPL incidents reach clients unreviewed.

**Success criteria:** 0 UPL incidents in 90 days. Policy engine catches >90%
of flagged outputs (measured via manual audit of 50 random agent runs).

**Failure signal:** Any UPL incident reaches a client, or manual audit shows
>10% false negatives.

**Measurement:** Weekly audit of 10 random agent_runs by a compliance officer.

---

## H5: Multi-vertical platform is viable (immigration + tax + MX divorce)

**Assumption:** A single platform can serve immigration, tax resolution, and
MX divorce without the UX becoming too generic or confusing.

**Success criteria:** Each vertical has >3 active matters within 6 weeks.
NPS survey per vertical >30.

**Failure signal:** One vertical has 0 matters after 4 weeks, or users report
confusion about which workflow applies to them.

**Measurement:** Track matter creation by `type` field. Survey at week 6.
