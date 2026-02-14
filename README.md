# LegalOps Agent Platform — MX-First

Plataforma multi-tenant de operaciones legales para México. Automatiza intake, recopilación de documentos, generación de expedientes y coordinación operativa para despachos jurídicos.

**WEDGE:** Divorcio incausado express — intake + checklist + coordinación + expediente listo para abogado.

**North Star Metric:** Expedientes listos y aprobados por semana por despacho.

**This platform does NOT provide legal advice.** All client-facing outputs pass through a mandatory **Human Approval Gate** before delivery.

---

## Quick Start

```bash
docker-compose up --build
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Swagger)

### Credenciales Demo

| Rol       | Email                  | Password      |
|-----------|------------------------|---------------|
| Admin     | admin@demo.legal       | admin123      |
| Abogado   | abogado@demo.legal     | abogado123    |
| Paralegal | paralegal@demo.legal   | paralegal123  |
| Closer    | closer@demo.legal      | closer123     |

### Flujo E2E Completo

1. **B2C:** Ir a http://localhost:3000/help → completar Prep Kit (divorcio incausado)
2. **Login:** http://localhost:3000/app/login (admin@demo.legal / admin123)
3. **Pipeline:** Ver leads y casos en el Kanban de 9 etapas MX
4. **Leads:** `/app/leads` → ver leads ruteados por vertical + región
5. **Completeness:** Abrir matter → ver documentos faltantes vs. template
6. **Aprobaciones:** Aprobar/rechazar expedientes y borradores de mensajes
7. **Feedback:** Dejar feedback desde el modal en `/help`

---

## Modelos de Negocio

| Modelo | Flujo | Métrica |
|--------|-------|---------|
| **B2B SaaS** | Despacho → Dashboard → Pipeline → Completeness → Aprobación | MRR por despacho |
| **B2C Prep Kit** | Cliente → `/help` → Checklist + Preguntas → Lead capturado | Leads calificados/semana |
| **B2B2C Routing** | Lead B2C → auto-ruteo por vertical + región → Despacho partner | Leads ruteados → convertidos |

---

## Verticales MX (Primary)

### mx_divorce — Divorcio Incausado (WEDGE)
- 7 documentos (4 requeridos: acta de matrimonio, INE, CURP, comprobante domicilio)
- 8 campos de intake (7 requeridos)
- Disclaimers en español e inglés
- 6 tareas default, 7 preguntas sugeridas para el abogado

### mx_consumer — Queja de Consumidor (PROFECO/CONDUSEF)
- 5 documentos (3 requeridos)
- 8 campos (proveedor/banco, monto reclamado, fecha)

### mx_labor — Asunto Laboral
- 6 documentos (3 requeridos)
- 10 campos (empresa, salario, motivo, fechas)

### Verticales US (Secondary)
- `immigration` — Immigration (US)
- `tax_resolution` — Tax Resolution (US)

---

## Pipeline MX (9 Etapas)

```
new_lead → intake_completed → docs_pending → expediente_draft → pending_approval → approved → contract_onboarding → in_progress → closed
```

| Etapa | Label | Acción |
|-------|-------|--------|
| new_lead | Nuevo Lead | Contactar y calificar |
| intake_completed | Intake Completo | Revisar información |
| docs_pending | Docs Pendientes | Enviar recordatorio WhatsApp |
| expediente_draft | Exp. Borrador | Revisar y completar |
| pending_approval | Por Aprobar | Aprobar expediente |
| approved | Aprobado | Generar contrato |
| contract_onboarding | Contrato | Firmar y cobrar |
| in_progress | En Proceso | Dar seguimiento |
| closed | Cerrado | Archivar |

---

## Features

### E1: Pipeline Kanban MX
- 9 etapas con labels en español
- Cards con nombre del cliente, vertical, urgencia, días en etapa
- Avance/retroceso por botón (sin drag)

### E2: Completeness Engine
- Calcula cobertura de docs + campos contra template de la vertical
- `GET /matters/{id}/completeness` → porcentaje, docs faltantes, campos faltantes
- Funciona para mx_divorce, mx_consumer, mx_labor, immigration, tax_resolution

### E3: WhatsApp Draft Cadence (Simulated)
- `check_whatsapp_reminders(db, tenant_id)` — encuentra matters en docs_pending con docs faltantes
- Crea `MessageDraft` con `channel="whatsapp"`, contenido en español
- Cadencia: 1er recordatorio a las 24h, 2do a las 48h, máximo 2
- Cada borrador genera `Approval` (nunca se envía automáticamente)
- Idempotente: cooldown de 12h entre recordatorios

### E4: Approval SLA Nudges
- `check_sla_breaches(db, tenant_id, sla_hours=4)` — detecta aprobaciones vencidas
- Crea `Task` con prefijo `[SLA Nudge]` + evento `approval_sla_breached`
- Idempotente: no duplica nudges

### E5: Partner Lead Routing (B2C → B2B)
- Reglas in-memory: `add_routing_rule(vertical, tenant_id, region=None)`
- `route_lead(db, lead)` — match por vertical + entidad federativa, fallback vertical-only
- Round-robin determinístico (SHA-256 hash del lead ID)
- Actualiza `lead.tenant_id` y `lead.status = "routed"`
- Evento `lead_routed` con detalle de regla aplicada

### E6: Feedback Loop
- `POST /feedback/` público — rating 1-5, texto, página, anonymous_id
- `GET /feedback/` autenticado — lista feedback del tenant
- FeedbackModal en `/help` y pipeline

---

## Páginas

| Página | URL | Auth | Descripción |
|--------|-----|------|-------------|
| Landing | `/` | No | Dual CTA: B2B (despachos) + B2C (clientes) |
| Prep Kit | `/help` | No | Multi-step: tipo de caso → situación → datos → resultado |
| Intake | `/intake` | No | Formulario B2B embeddable (widget para despachos) |
| Login | `/app/login` | No | JWT auth |
| Pipeline | `/app/pipeline` | Sí | Kanban 9 etapas MX |
| Leads | `/app/leads` | Sí | Tabla de leads con filtros por estado |
| Analytics | `/app/analytics` | Sí | KPIs + funnel |
| Approvals | `/app/approvals` | Sí | Cola de aprobaciones |

---

## UX MX-First

- **Español MX** por default en `/help`, `/intake`, pipeline, leads
- **Mobile-first:** `max-w-lg`, pasos cortos, botones grandes (py-3.5)
- **Disclaimer arriba del fold** en todas las páginas públicas
- **WhatsApp-first:** campo "Teléfono / WhatsApp" como requerido, email opcional
- **Entidad federativa:** selector de 32 estados para MX verticals
- **Trust signals:** cédula profesional, ubicación, horarios en tenant settings

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                 │
│  /help (B2C Prep Kit)  │ /intake (embeddable)          │
│  /app/pipeline (Kanban) │ /app/leads (routing table)   │
│  /app/analytics │ /app/approvals │ /app/login           │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP (CORS)
┌───────────────────────────▼─────────────────────────────┐
│                   Backend (FastAPI)                      │
│  Routers: leads, pipeline, templates, feedback, ...     │
│  Services: whatsapp_cadence, lead_routing, sla_nudge    │
│  Agents: orchestrator + mock LLM + policy engine        │
│  Models: 15+ SQLAlchemy tables (tenant-scoped)          │
└───────────────────────────┬─────────────────────────────┘
                            │
              PostgreSQL + Redis + Local FS
```

---

## Project Structure

```
├── docker-compose.yml
├── README.md
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── seed.py              # MX-focused demo data
│   │   ├── routers/
│   │   │   ├── leads.py         # /public/lead, /prepkit, /onboard, /app/leads
│   │   │   ├── pipeline.py      # /app/pipeline (9 MX stages)
│   │   │   ├── templates.py     # /templates/{vertical}, /completeness
│   │   │   ├── feedback.py      # /feedback/
│   │   │   ├── analytics.py     # /app/analytics/overview
│   │   │   └── ...
│   │   ├── services/
│   │   │   ├── whatsapp_cadence.py  # WhatsApp draft reminders
│   │   │   ├── lead_routing.py      # B2C→B2B partner routing
│   │   │   ├── sla_nudge.py         # Approval SLA breach detection
│   │   │   └── doc_chase.py         # Document reminder drafts
│   │   └── agents/
│   │       ├── orchestrator.py
│   │       ├── mock_llm.py
│   │       ├── policy_engine.py
│   │       └── definitions/         # YAML agent definitions
│   └── tests/
│       ├── conftest.py
│       ├── test_mx_completeness.py  # mx_divorce, mx_consumer, mx_labor
│       ├── test_lead_routing.py     # Partner routing + deterministic round-robin
│       ├── test_whatsapp_cadence.py # WhatsApp draft reminders + idempotency
│       ├── test_sla_nudge.py        # SLA breach detection
│       ├── test_completeness.py     # Immigration completeness
│       ├── test_feedback.py         # Feedback collection
│       ├── test_pipeline.py         # Pipeline stage changes
│       └── ...
├── docs/
│   ├── mx/                          # MX Pilot Playbook
│   │   ├── ICP.md                   # Ideal Customer Profile (MX)
│   │   ├── PilotPlan.md             # 14-day MX pilot sprint
│   │   ├── InterviewScript.md       # Despacho interview questions
│   │   └── GTM_MX.md               # Go-to-market strategy + ROI model
│   ├── pilot/                       # US Pilot (Immigration)
│   │   ├── ICP.md
│   │   ├── PilotPlan.md
│   │   ├── InterviewScript.md
│   │   └── ROIModel.md
│   └── lean/                        # Lean Startup measurement
│       ├── north_star.md
│       ├── hypotheses.md
│       └── experiments.md
└── frontend/
    ├── vercel.json                  # Vercel deployment config
    └── src/
        ├── lib/
        │   ├── api.ts               # API client (includes getLeads)
        │   └── tracker.ts           # Event tracker
        └── app/
            ├── help/page.tsx        # B2C Prep Kit (Spanish MX, 4 steps)
            ├── intake/page.tsx      # Intake form (Spanish MX)
            └── app/
                ├── pipeline/page.tsx  # Kanban 9 etapas MX
                ├── leads/page.tsx     # Leads table with routing status
                └── ...
```

---

## Running Tests

```bash
# Inside backend container:
docker-compose exec api pytest tests/ -v

# Or locally:
cd backend
pip install -r requirements.txt
pytest tests/ -v

# Run specific test suites:
pytest tests/test_mx_completeness.py -v    # MX vertical completeness
pytest tests/test_lead_routing.py -v       # Partner lead routing
pytest tests/test_whatsapp_cadence.py -v   # WhatsApp draft cadence
pytest tests/test_sla_nudge.py -v          # SLA nudge service
```

---

## Deploy

### Frontend → Vercel

```bash
cd frontend
npm i -g vercel
vercel

# Set env var:
vercel env add NEXT_PUBLIC_API_URL
# Enter your backend URL, e.g.: https://your-api.fly.dev

vercel --prod
```

`frontend/vercel.json` includes security headers and env var reference.

### Backend → Render / Fly.io

**Render:**
1. Connect GitHub repo
2. Set build command: `pip install -r requirements.txt`
3. Set start command: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add env vars: `DATABASE_URL`, `SECRET_KEY`, `CORS_ORIGINS`

**Fly.io:**
```bash
cd backend
fly launch
fly secrets set DATABASE_URL=postgresql://... SECRET_KEY=... CORS_ORIGINS=https://your-frontend.vercel.app
fly deploy
```

---

## Deploy Readiness Checklist

### Done
- [x] MX vertical templates (mx_divorce, mx_consumer, mx_labor) with completeness
- [x] 9-stage MX pipeline with Spanish labels
- [x] WhatsApp draft cadence (simulated, behind approval gate)
- [x] Partner lead routing (vertical + region, deterministic round-robin)
- [x] SLA nudge service (approval breach detection)
- [x] B2C Prep Kit (Spanish MX, 4-step mobile-first)
- [x] B2B tenant onboarding (with embed widget snippet)
- [x] Pipeline Kanban, Leads table, Analytics dashboard
- [x] Feedback loop (public + authenticated endpoints)
- [x] Event tracking + A/B experiments
- [x] CI/CD (GitHub Actions)
- [x] Vercel deploy config + security headers
- [x] Pilot playbook: ICP, PilotPlan, InterviewScript, GTM_MX
- [x] Comprehensive test suite (MX completeness, lead routing, WhatsApp, SLA, feedback)

### Pending (Post-Pilot)
- [ ] Real LLM integration (replace MockLLMProvider with Claude/OpenAI)
- [ ] WhatsApp Business API (replace simulated drafts)
- [ ] S3/Cloud storage for document uploads
- [ ] Field-level encryption (PII at rest)
- [ ] Real payment integration (Stripe / OpenPay MX)
- [ ] Firma electrónica (DocuSign / mifiel.com)
- [ ] Facturación CFDI integration
- [ ] Redis job queues (async agent execution)
- [ ] E2E tests (Playwright)
- [ ] Production deployment (managed Postgres + Redis)

---

## Compliance Notes

- The system **never presents itself as an attorney or legal advisor**
- All client-facing outputs require **Human Approval Gate**
- **Policy Engine** scans for unauthorized practice of law (EN + ES)
- `tenant_id` enforced on every query for **multi-tenant isolation**
- Disclaimers displayed above the fold on all public pages
- MX trust signals: cédula profesional, ubicación, horarios in tenant settings
- PII encryption is stubbed — implement before production
