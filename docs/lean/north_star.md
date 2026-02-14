# North Star Metric

## Primary (B2B): Approved Case Packets per Week per Tenant

**Definition:** The number of `AgentRun` outputs that reach `status=completed`
(after human approval) per calendar week, segmented by tenant.

**Why this metric:**
- It captures the full value chain: intake → matter → agent run → human review → approved output.
- It's a proxy for "cases the platform actually helped move forward."
- It's per-tenant, so it works for multi-tenant benchmarking.
- It excludes vanity (raw intakes) and focuses on delivered value.

**Formula:**
```
approved_case_packets_per_week =
  COUNT(approvals WHERE status='approved' AND object_type='agent_run')
  / COUNT(DISTINCT calendar_week)
  GROUP BY tenant_id
```

**Target (v1, week 4):** 5 approved case packets / week / tenant (with 2 pilot tenants).

---

## Secondary (B2C Channel): Human-Reviewed Next Steps

**Definition:** The number of B2C "Prep Kit" submissions where a human professional
has reviewed and approved the case packet, enabling the client to receive
actionable (but non-legal-advice) next steps.

**Formula:**
```
b2c_reviewed =
  COUNT(approvals WHERE status='approved' AND object_type='agent_run'
        AND related_matter.source='b2c_prepkit')
```

**Why secondary:** B2C is a lead generation channel for B2B tenants, not the
core business. But it validates whether self-service intake works.

---

## Leading Indicators (to watch weekly)

| Indicator | Target | Signal |
|---|---|---|
| Intakes submitted / week | 20+ | Top of funnel is alive |
| Intake → Matter conversion rate | >50% | Intake quality is good |
| Agent runs / matter | >1 | Users are engaging with agents |
| Time to approve (median hours) | <24h | Human bottleneck is manageable |
| Leads from B2C / week | 10+ | B2C channel is generating demand |
