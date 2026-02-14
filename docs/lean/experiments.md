# Experiments v1 (Week 1)

## E1: "Digital Intake vs. Status Quo" (validates H1)

**Goal:** Prove that a firm will process real intakes through the platform.

**Setup:**
- Onboard 2 pilot firms (immigration + tax).
- Each firm processes their next 10 new client inquiries through the platform.
- Control: their existing process (phone/email) for the previous 10 clients.

**Metrics & Events:**
| Event | Tracked as |
|---|---|
| Firm signs up | `tenant_created` |
| Intake submitted | `intake_submitted` |
| Intake converted to matter | `intake_converted_to_matter` |
| Agent run completed | `agent_run_created` |
| Case packet approved | `approval_approved` |
| Time from intake to approved packet | computed: `approval.decided_at - intake.created_at` |

**Success criteria:**
- >8/10 intakes processed through platform per firm.
- Time from intake to approved case packet < 48 hours (vs. baseline).

**Duration:** 7 days from onboarding.

---

## E2: "Approval SLA Nudge" (validates H2)

**Goal:** Test whether notification nudges reduce time-to-approve.

**Setup:**
- Experiment key: `approval_sla_nudge`
- Variant A (control): No nudge. Approval sits in queue.
- Variant B (treatment): After 4 hours pending, show a banner "3 approvals
  waiting >4h" on dashboard + highlight in sidebar.

**Metrics & Events:**
| Event | Tracked as |
|---|---|
| Approval created | `approval_requested` |
| Nudge shown (variant B) | `nudge_shown` (with experiment context) |
| Approval decided | `approval_approved` or `approval_rejected` |
| Time to decide | computed: `decided_at - created_at` |

**Success criteria:**
- Variant B median time-to-approve is >30% lower than Variant A.

**Duration:** 7 days, minimum 20 approvals per variant.

---

## E3: "B2C Prep Kit → Lead Conversion" (validates H3)

**Goal:** Test whether the free Prep Kit generates qualified leads.

**Setup:**
- Experiment key: `prepkit_cta_variant`
- Variant A: CTA says "Get your free Prep Kit"
- Variant B: CTA says "Prepare for your legal consultation"

**Metrics & Events:**
| Event | Tracked as |
|---|---|
| Landing page view | `page_view` (path=/help) |
| Prep Kit form started | `prepkit_started` |
| Prep Kit generated | `prepkit_generated` |
| "Contact firm" clicked | `lead_created` |
| Lead becomes matter | `lead_converted` (tracked when matter created from lead) |

**Success criteria:**
- >15% of Prep Kit completions → "Contact firm" click.
- >5% of leads → Matter conversion within 30 days.
- Identify which CTA variant drives higher lead quality.

**Duration:** 7 days, minimum 50 Prep Kit completions total.

---

## Event Taxonomy (full list for v1)

### Public (B2C + anonymous)
- `page_view` — path, referrer, utm_*
- `cta_click` — variant: b2b | b2c
- `intake_started` — case_type
- `intake_submitted` — intake_id, case_type
- `prepkit_started` — case_type
- `prepkit_generated` — intake_id
- `lead_created` — vertical, source_type

### Authenticated (B2B staff)
- `intake_converted_to_matter` — matter_id, type
- `agent_run_created` — matter_id, agent_name
- `approval_requested` — approval_id, object_type
- `approval_approved` — approval_id
- `approval_rejected` — approval_id
- `message_draft_created` — matter_id, channel
- `message_sent` — matter_id, channel

### System
- `tenant_created` — tenant_id
- `experiment_exposed` — experiment_key, variant
