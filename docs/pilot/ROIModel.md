# ROI Model — Pilot Firms

## Formula

```
Monthly ROI = (Value of Time Saved + Value of Leads Captured) - Platform Cost
```

---

## Time Saved

### Per-Intake Time Savings

| Task | Before (manual) | After (platform) | Saved |
|------|-----------------|-------------------|-------|
| Initial intake data entry | 20 min | 5 min (auto from web form) | 15 min |
| Document checklist creation | 15 min | 0 min (auto-generated) | 15 min |
| Client follow-up for docs | 30 min/week | 10 min/week (doc chase drafts) | 20 min |
| Case stage tracking | 10 min/day | 2 min/day (Kanban view) | 8 min |
| Attorney approval routing | 15 min | 3 min (in-app + SLA nudge) | 12 min |
| **Total per intake** | **~90 min** | **~20 min** | **~70 min** |

### Monthly Calculation

```
time_saved_monthly = intakes_per_month * 70 min
                   = 20 intakes * 70 min
                   = 1,400 min = ~23 hours/month

value_of_time = 23 hours * hourly_rate
```

| Role | Hourly Rate | Monthly Value |
|------|-------------|---------------|
| Attorney ($150/hr) | $150 | $3,450 |
| Paralegal ($40/hr) | $40 | $920 |
| **Blended (70% paralegal, 30% attorney)** | **$73** | **$1,679** |

---

## Leads Captured (B2C Channel)

### Prep Kit → Lead Conversion

```
leads_value = prep_kits_generated * conversion_to_client * avg_case_value

Example:
  50 prep kits/month * 10% conversion * $3,000 avg case
  = $15,000 potential revenue
  = $1,500 attributable value (10% platform attribution)
```

| Metric | Conservative | Moderate | Optimistic |
|--------|-------------|----------|------------|
| Prep Kits / month | 20 | 50 | 100 |
| Conversion rate | 5% | 10% | 15% |
| Avg case value | $2,000 | $3,000 | $5,000 |
| Revenue captured | $2,000 | $15,000 | $75,000 |
| Platform attribution (10%) | $200 | $1,500 | $7,500 |

---

## Platform Cost (Projected)

| Tier | Price/mo | Includes |
|------|----------|----------|
| Starter (1 user) | $99/mo | Pipeline, docs, 50 Prep Kits |
| Pro (up to 5 users) | $299/mo | Everything + SLA nudges, analytics, unlimited Prep Kits |
| Custom | Contact us | Multi-vertical, API access, custom branding |

---

## ROI Summary

### Conservative (Solo attorney, 20 intakes/mo)

```
Time saved value:     $920/mo  (paralegal rate)
Lead value:           $200/mo
Platform cost:       -$99/mo
─────────────────────────────
Net ROI:              $1,021/mo
ROI multiple:         ~10x
```

### Moderate (Small firm, 40 intakes/mo, B2C active)

```
Time saved value:     $3,358/mo  (blended rate, 2x volume)
Lead value:           $1,500/mo
Platform cost:       -$299/mo
─────────────────────────────
Net ROI:              $4,559/mo
ROI multiple:         ~15x
```

---

## How to Present to Pilot Firms

1. **Ask them** to estimate their current time per intake (validate our assumptions)
2. **Show them** the actual metrics from the pilot (time_to_first_response before/after)
3. **Calculate together** using THEIR numbers, not ours
4. **Anchor on ROI multiple**, not absolute cost ("Would you spend $1 to get $10 back?")

### Key Talking Points

- "Our pilot data shows your intake time went from X hours to Y minutes"
- "You collected documents Z% faster with automated reminders"
- "The Prep Kit brought in N pre-qualified leads this month"
- "At $299/month, that's less than 2 hours of attorney time — and we save you 23+"

---

## Metrics to Track During Pilot

| Metric | How to Measure | Maps to ROI |
|--------|---------------|-------------|
| `time_to_first_response` | KPIs endpoint | Time saved |
| `time_to_approval_median` | KPIs endpoint | Time saved |
| `doc_completeness_72h` | KPIs endpoint | Fewer follow-ups |
| `prepkit_generated` count | Events table | Lead generation |
| `lead_created` count | Leads table | Lead generation |
| Pipeline cards moved/day | Events table | Workflow adoption |
