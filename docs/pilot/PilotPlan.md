# Pilot Plan — 14-Day Sprint

## Overview

| Field | Value |
|-------|-------|
| **Duration** | 14 calendar days |
| **Target firms** | 2-3 immigration firms (1-5 attorneys each) |
| **Vertical** | Immigration (US removal defense / asylum / family petitions) |
| **Success metric** | At least 1 firm says "I'd pay for this" unprompted |
| **Kill criteria** | Zero firms complete onboarding by Day 5, or <50% feature adoption by Day 10 |

---

## Success / Kill Criteria

### Success (continue to paid pilot)
- [ ] >= 2 firms fully onboarded and using pipeline daily
- [ ] time_to_first_response < 2 hours (vs baseline ~24h)
- [ ] doc_completeness_72h > 60% (vs baseline ~20%)
- [ ] At least 1 firm asks about pricing unprompted
- [ ] NPS/feedback rating >= 4.0 average

### Kill (pivot or rethink)
- [ ] 0 firms complete onboarding by Day 5
- [ ] Firms stop logging in after Day 3
- [ ] Feedback ratings < 3.0 average
- [ ] "This doesn't save me time" heard from 2+ firms

---

## Daily Agenda

### Phase 1: Setup (Days 1-3)

**Day 1 — Recruit + Onboard Firm #1**
- [ ] Send intro email/call to target firm
- [ ] Walk through onboarding wizard (create tenant, add users)
- [ ] Import 3-5 existing cases as seed intakes
- [ ] Train on pipeline Kanban view
- **Check:** Can they log in and see their cases?

**Day 2 — Observe + Fix**
- [ ] Watch firm use the system (screen share or in-person)
- [ ] Log every friction point (see InterviewScript.md question 8)
- [ ] Fix top 2 blocking issues same-day
- [ ] Onboard Firm #2
- **Check:** Are they moving cards on the pipeline?

**Day 3 — B2C Channel Live**
- [ ] Deploy Prep Kit page with firm's branding
- [ ] Share link with firm for their website/social media
- [ ] Monitor first B2C submissions
- [ ] Onboard Firm #3 if available
- **Check:** Did any B2C leads come through?

### Phase 2: Activation (Days 4-7)

**Day 4 — Document Workflow**
- [ ] Walk firms through document completeness view
- [ ] Upload sample documents for test matter
- [ ] Verify doc chase reminders trigger (48h threshold)
- **Metric:** doc_completeness tracking active?

**Day 5 — Approval + SLA**
- [ ] Run agent on a test matter → creates approval
- [ ] Verify SLA nudge fires after 4h
- [ ] Attorney approves/rejects with notes
- **Metric:** time_to_approval < target?

**Day 6 — Review Funnel Data**
- [ ] Check analytics dashboard: funnel, events, KPIs
- [ ] Share early metrics with firms
- [ ] Conduct 15-min check-in call with each firm
- **Metric:** How many pipeline stages used?

**Day 7 — Mid-Pilot Retrospective**
- [ ] Review all feedback submissions
- [ ] Triage: what's blocking vs. nice-to-have?
- [ ] Prioritize fixes for Phase 3
- **Decision point:** Any kill criteria triggered?

### Phase 3: Retention (Days 8-12)

**Day 8-9 — Ship Fixes**
- [ ] Address top 3 friction points from Phase 2
- [ ] Add any missing document types to immigration template
- [ ] Improve Prep Kit based on B2C feedback

**Day 10 — Deep Dive Interview**
- [ ] Conduct full interview with each firm (see InterviewScript.md)
- [ ] Record (with permission) for team review
- **Metric:** Feature adoption rate (which features used daily?)

**Day 11-12 — Measure Everything**
- [ ] Pull final KPIs: time_to_first_response, time_to_approval, doc_completeness_72h
- [ ] Calculate ROI per firm (see ROIModel.md)
- [ ] Compare before/after for each firm

### Phase 4: Decision (Days 13-14)

**Day 13 — Pricing Conversation**
- [ ] Present ROI to each firm
- [ ] Ask: "If we charged $X/mo, would you continue?"
- [ ] Document willingness to pay

**Day 14 — Retrospective + Decision**
- [ ] Score against success/kill criteria
- [ ] Write pilot report
- [ ] **GO / NO-GO / PIVOT** decision
- [ ] If GO: plan paid pilot terms

---

## Metrics to Review Daily

| Metric | Source | Target |
|--------|--------|--------|
| Active users (logged in today) | Events table | >= 1 per firm |
| Pipeline cards moved | pipeline_stage_changed events | >= 3/day/firm |
| time_to_first_response | Pilot KPIs endpoint | < 2 hours |
| time_to_approval_median | Pilot KPIs endpoint | < 8 hours |
| doc_completeness_72h | Pilot KPIs endpoint | > 60% |
| B2C Prep Kits generated | prepkit_generated events | >= 2/day |
| Feedback rating avg | Feedback table | >= 4.0 |
| SLA breaches | Pilot KPIs endpoint | < 2/day |

---

## Infrastructure Checklist

- [ ] Backend deployed (Railway/Render/fly.io)
- [ ] Frontend deployed (Vercel) with NEXT_PUBLIC_API_URL pointing to backend
- [ ] Database migrated (alembic upgrade head)
- [ ] Seed data loaded for demo tenant
- [ ] CORS configured for Vercel domain
- [ ] Each pilot firm has their own tenant + admin user
