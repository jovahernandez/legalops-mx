"""Public lead capture + B2B onboarding + B2C Prep Kit + lead management."""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user, hash_password
from app.models import Lead, Tenant, User, Intake, Matter, Approval, AgentRun
from app.schemas import (
    LeadCreate, LeadOut, PrepKitRequest, PrepKitResponse,
    OnboardTenantRequest, OnboardTenantResponse,
)
from app.agents.orchestrator import AgentOrchestrator
from app.agents.openai_llm import OpenAIProvider
from app.agents.policy_engine import PolicyEngine
from app.config import settings
from app.services.lead_routing import route_lead
from app.routers.templates import VERTICAL_TEMPLATES
from app.rate_limit import limiter

router = APIRouter(tags=["leads"])

orchestrator = AgentOrchestrator()
_prepkit_llm = OpenAIProvider()
_prepkit_policy = PolicyEngine()


def _check_honeypot(body) -> None:
    """Reject submissions that fill in the hidden honeypot field."""
    hp = getattr(body, "website", None) or getattr(body, "hp_field", None)
    if hp:
        raise HTTPException(status_code=422, detail="Invalid submission")


def _get_checklist_for_vertical(case_type: str) -> list[str]:
    """Get document checklist from template registry."""
    template = VERTICAL_TEMPLATES.get(case_type)
    if template:
        return [d.label for d in template.required_documents]
    return ["Identificación oficial", "Documentos relevantes a su caso", "Resumen escrito de su situación"]


def _get_questions_for_vertical(case_type: str) -> list[str]:
    """Get suggested questions from template registry."""
    template = VERTICAL_TEMPLATES.get(case_type)
    if template and template.suggested_questions:
        return template.suggested_questions
    return ["¿Qué tipo de profesional debo consultar?", "¿Qué documentos necesito?", "¿Cuáles son los costos?"]


def _get_disclaimer_for_vertical(case_type: str, language: str = "es") -> str:
    """Get disclaimer from template registry."""
    template = VERTICAL_TEMPLATES.get(case_type)
    if template and template.disclaimers:
        return template.disclaimers.get(language, template.disclaimers.get("es", template.disclaimers.get("en", "")))
    return (
        "Esta herramienta NO proporciona asesoría legal. Toda la información "
        "es orientativa y debe ser revisada por un profesional. "
        "No se crea relación abogado-cliente al usar esta plataforma."
    )


@router.post("/public/lead", response_model=LeadOut, status_code=201)
@limiter.limit("10/minute")
def create_lead(request: Request, body: LeadCreate, db: Session = Depends(get_db)):
    """Public: capture a lead from B2C or B2B channel."""
    _check_honeypot(body)
    contact = {**body.contact, **{f"utm_{k}": v for k, v in body.utm.items()}}
    lead = Lead(
        source_type=body.source_type,
        vertical=body.vertical,
        status="new",
        contact_json=contact,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    # Try to route lead to a partner tenant
    route_lead(db, lead, contact_json=contact)

    return lead


@router.post("/public/prepkit", response_model=PrepKitResponse, status_code=201)
@limiter.limit("5/minute")
def generate_prepkit(request: Request, body: PrepKitRequest, db: Session = Depends(get_db)):
    """B2C Prep Kit: generate safe document checklist + questions.
    Case packet ALWAYS goes to needs_approval.
    Lead is auto-routed to partner tenant if routing rules exist."""
    _check_honeypot(body)

    tenant = db.query(Tenant).filter(Tenant.id == body.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # 1. Create intake
    intake = Intake(
        tenant_id=body.tenant_id,
        channel="b2c_prepkit",
        raw_payload_json={
            "nombre_completo": body.full_name,
            "full_name": body.full_name,
            "email": body.email,
            "phone": body.phone,
            "case_type": body.case_type,
            "descripcion": body.description,
            "description": body.description,
            "language": body.language,
            "source": "b2c_prepkit",
            **{f"utm_{k}": v for k, v in body.utm.items()},
        },
        status="new",
        pipeline_stage="new_lead",
    )
    db.add(intake)
    db.flush()

    # 2. Create matter
    matter = Matter(
        tenant_id=body.tenant_id,
        intake_id=intake.id,
        type=body.case_type,
        jurisdiction="MX" if body.case_type.startswith("mx_") else "US",
        urgency_score=0,
        status="open",
        pipeline_stage="intake_completed" if body.case_type.startswith("mx_") else "matter_created",
    )
    db.add(matter)
    db.flush()

    # 3. Generate structured PrepKit via GPT (or fallback)
    prepkit_data = _prepkit_llm.generate_prepkit(
        case_type=body.case_type,
        description=body.description,
        language=body.language,
    )

    # 4. Pass PrepKit output through PolicyEngine (UPL guard)
    prepkit_data = _prepkit_policy.check_and_annotate(prepkit_data)

    # 5. Run agent for internal case packet (goes to approval queue)
    agent_result = orchestrator.run("intake_specialist", {
        "case_type": body.case_type,
        "description": body.description,
        "full_name": body.full_name,
        "language": body.language,
    })

    # 6. Store agent run as needs_approval (ALWAYS)
    agent_run = AgentRun(
        tenant_id=body.tenant_id,
        matter_id=matter.id,
        agent_name="intake_specialist",
        input_json={"source": "b2c_prepkit", "case_type": body.case_type},
        output_json=agent_result,
        status="needs_approval",
    )
    db.add(agent_run)
    db.flush()

    # 7. Create mandatory approval
    approval = Approval(
        tenant_id=body.tenant_id,
        matter_id=matter.id,
        object_type="agent_run",
        object_id=agent_run.id,
        status="pending",
    )
    db.add(approval)

    # 8. Create lead + route to partner
    lead = Lead(
        tenant_id=body.tenant_id,
        source_type="b2c_prepkit",
        vertical=body.case_type,
        status="new",
        contact_json={
            "name": body.full_name,
            "email": body.email,
            "phone": body.phone,
            "entidad_federativa": body.utm.get("entidad_federativa"),
            **{f"utm_{k}": v for k, v in body.utm.items()},
        },
    )
    db.add(lead)
    db.flush()

    # Try partner routing
    route_lead(db, lead, contact_json=lead.contact_json)

    db.commit()
    db.refresh(intake)

    # Use GPT-generated checklist/questions, fall back to templates if blocked
    policy_blocked = "_policy_status" in prepkit_data
    doc_checklist = (
        _get_checklist_for_vertical(body.case_type) if policy_blocked
        else prepkit_data.get("checklist_docs", _get_checklist_for_vertical(body.case_type))
    )
    questions = (
        _get_questions_for_vertical(body.case_type) if policy_blocked
        else prepkit_data.get("questions_for_lawyer", _get_questions_for_vertical(body.case_type))
    )
    disclaimer = prepkit_data.get("disclaimer", _get_disclaimer_for_vertical(body.case_type, body.language))

    return PrepKitResponse(
        intake_id=intake.id,
        document_checklist=doc_checklist,
        questions_for_attorney=questions,
        case_packet_status="needs_approval",
        disclaimer=disclaimer,
        message=(
            "Su expediente ha sido generado. Un profesional revisará su caso. "
            "Le contactaremos cuando la revisión esté completa."
            if body.language == "es" else
            "Your Prep Kit has been generated. A licensed professional will "
            "review your case summary. You will be contacted when the review "
            "is complete."
        ),
    )


@router.post("/public/onboard", response_model=OnboardTenantResponse, status_code=201)
@limiter.limit("3/minute")
def onboard_tenant(request: Request, body: OnboardTenantRequest, db: Session = Depends(get_db)):
    """B2B: create a new tenant + admin user."""
    _check_honeypot(body)
    existing = db.query(User).filter(User.email == body.admin_email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    tenant = Tenant(
        name=body.firm_name,
        settings_json={
            "practice_areas": body.practice_areas,
            "disclaimer_en": body.disclaimer_en,
            "disclaimer_es": body.disclaimer_es,
        },
    )
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        email=body.admin_email,
        hashed_password=hash_password(body.admin_password),
        full_name=f"Admin - {body.firm_name}",
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(tenant)

    base_url = settings.FRONTEND_URL.rstrip("/")
    embed_snippet = (
        f'<a href="{base_url}/intake?tenant_id={tenant.id}'
        f'&utm_source=widget&utm_medium=embed&utm_campaign={body.firm_name.lower().replace(" ", "_")}" '
        f'target="_blank" style="padding:12px 24px;background:#2563eb;color:white;'
        f'border-radius:8px;text-decoration:none;font-family:sans-serif;">'
        f'Obtener Ayuda Legal</a>'
    )

    return OnboardTenantResponse(
        tenant_id=tenant.id,
        admin_email=body.admin_email,
        embed_snippet=embed_snippet,
        login_url=f"{base_url}/app/login",
    )


# ---------------------------------------------------------------------------
# Authenticated: lead management for tenant staff
# ---------------------------------------------------------------------------
@router.get("/app/leads", response_model=list[LeadOut])
def list_leads(
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List leads routed to or owned by the current tenant."""
    query = db.query(Lead).filter(Lead.tenant_id == current_user.tenant_id)
    if status:
        query = query.filter(Lead.status == status)
    return query.order_by(Lead.created_at.desc()).all()
