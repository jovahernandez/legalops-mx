from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import (
    auth, tenants, intakes, matters, documents, agents,
    approvals, tasks, messages, interpreters,
    events, leads, analytics, experiments,
    pipeline, templates, feedback,
)

app = FastAPI(
    title="LegalOps Agent Platform",
    description=(
        "Multi-tenant platform for legal operations automation. "
        "This system does NOT provide legal advice. All client-facing "
        "outputs require Human Approval Gate before delivery."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://web:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Routers ----------------------------------------------------------------
app.include_router(auth.router)
app.include_router(tenants.router)
app.include_router(intakes.router)
app.include_router(matters.router)
app.include_router(documents.router)
app.include_router(agents.router)
app.include_router(approvals.router)
app.include_router(tasks.router)
app.include_router(messages.router)
app.include_router(interpreters.router)

# Growth / instrumentation
app.include_router(events.router)
app.include_router(leads.router)
app.include_router(analytics.router)
app.include_router(experiments.router)

# Pilot readiness
app.include_router(pipeline.router)
app.include_router(templates.router)
app.include_router(feedback.router)


@app.get("/health")
def health():
    return {"status": "ok", "service": "legalops-api"}
