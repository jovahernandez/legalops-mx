from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from app.config import settings
from app.rate_limit import limiter
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

# Explicit origins: FRONTEND_URL + localhost dev servers
_explicit_origins = [
    settings.FRONTEND_URL.rstrip("/"),
    "http://localhost:3000",
    "http://web:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o for o in _explicit_origins if o],
    allow_origin_regex=r"^https://.*\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Rate limiter ---
app.state.limiter = limiter

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."},
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
