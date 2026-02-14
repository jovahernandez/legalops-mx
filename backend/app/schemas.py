"""Pydantic schemas for request/response validation."""

import uuid
from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, EmailStr, Field


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------------------------------------------------------------------------
# Tenant
# ---------------------------------------------------------------------------
class TenantCreate(BaseModel):
    name: str
    settings_json: dict[str, Any] = {}


class TenantOut(BaseModel):
    id: uuid.UUID
    name: str
    settings_json: dict[str, Any]
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str | None = None
    role: str = "staff"


class UserOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    email: str
    full_name: str | None
    role: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Intake  (public endpoint – no auth required)
# ---------------------------------------------------------------------------
class IntakeCreate(BaseModel):
    tenant_id: uuid.UUID
    channel: str = "web"
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class IntakeOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    channel: str
    raw_payload_json: dict[str, Any]
    status: str
    pipeline_stage: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Matter
# ---------------------------------------------------------------------------
class MatterCreate(BaseModel):
    intake_id: uuid.UUID | None = None
    type: str  # immigration, tax_resolution, mx_divorce, other
    jurisdiction: str = "US"
    urgency_score: int = 0


class MatterOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    intake_id: uuid.UUID | None
    type: str
    jurisdiction: str
    urgency_score: int
    status: str
    pipeline_stage: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Person
# ---------------------------------------------------------------------------
class PersonCreate(BaseModel):
    matter_id: uuid.UUID
    role_in_matter: str = "client"
    name: str
    phone: str | None = None
    email: str | None = None
    language: str = "en"


class PersonOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    matter_id: uuid.UUID
    role_in_matter: str | None
    name: str | None
    phone: str | None
    email: str | None
    language: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------
class DocumentUpload(BaseModel):
    matter_id: uuid.UUID
    kind: str
    filename: str


class DocumentOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    matter_id: uuid.UUID
    kind: str | None
    filename: str | None
    storage_uri: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class TaskCreate(BaseModel):
    matter_id: uuid.UUID
    title: str
    description: str | None = None
    assigned_to_user_id: uuid.UUID | None = None
    due_at: datetime | None = None


class TaskOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    matter_id: uuid.UUID
    title: str
    description: str | None
    status: str
    assigned_to_user_id: uuid.UUID | None
    due_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# AgentRun
# ---------------------------------------------------------------------------
class AgentRunRequest(BaseModel):
    matter_id: uuid.UUID
    agent_name: str
    input_data: dict[str, Any] = {}


class AgentRunOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    matter_id: uuid.UUID
    agent_name: str
    input_json: dict[str, Any]
    output_json: dict[str, Any]
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Approval
# ---------------------------------------------------------------------------
class ApprovalDecision(BaseModel):
    notes: str | None = None


class ApprovalOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    matter_id: uuid.UUID | None
    object_type: str
    object_id: uuid.UUID
    status: str
    requested_by: uuid.UUID | None
    decided_by: uuid.UUID | None
    decided_at: datetime | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# MessageDraft
# ---------------------------------------------------------------------------
class MessageDraftCreate(BaseModel):
    matter_id: uuid.UUID
    channel: str = "email"
    content: str


class MessageDraftOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    matter_id: uuid.UUID
    channel: str
    content: str
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# InterpreterRequest
# ---------------------------------------------------------------------------
class InterpreterRequestCreate(BaseModel):
    matter_id: uuid.UUID
    language: str
    modality: str = "virtual"
    date_pref: datetime | None = None
    notes: str | None = None


class InterpreterRequestOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    matter_id: uuid.UUID
    language: str
    modality: str
    date_pref: datetime | None
    status: str
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ===========================================================================
# GROWTH / INSTRUMENTATION SCHEMAS
# ===========================================================================

class EventCreate(BaseModel):
    anonymous_id: str
    session_id: str | None = None
    name: str
    properties: dict[str, Any] = {}
    tenant_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None


class EventOut(BaseModel):
    id: uuid.UUID
    name: str
    anonymous_id: str
    properties_json: dict[str, Any]
    created_at: datetime
    model_config = {"from_attributes": True}


class LeadCreate(BaseModel):
    source_type: str = "b2c_prepkit"
    vertical: str | None = None
    contact: dict[str, Any] = {}
    utm: dict[str, str] = {}


class LeadOut(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID | None
    source_type: str
    vertical: str | None
    status: str
    contact_json: dict[str, Any]
    created_at: datetime
    model_config = {"from_attributes": True}


class ExperimentAssignRequest(BaseModel):
    experiment_key: str
    anonymous_id: str


class ExperimentAssignResponse(BaseModel):
    experiment_key: str
    variant: str
    anonymous_id: str


class PrepKitRequest(BaseModel):
    tenant_id: uuid.UUID
    case_type: str
    description: str
    full_name: str
    email: str | None = None
    phone: str | None = None
    language: str = "en"
    utm: dict[str, str] = {}


class PrepKitResponse(BaseModel):
    intake_id: uuid.UUID
    document_checklist: list[str]
    questions_for_attorney: list[str]
    case_packet_status: str
    disclaimer: str
    message: str


class OnboardTenantRequest(BaseModel):
    firm_name: str
    admin_email: str
    admin_password: str
    practice_areas: list[str]
    disclaimer_en: str = "This platform does not provide legal advice."
    disclaimer_es: str = "Esta plataforma no proporciona asesoría legal."


class OnboardTenantResponse(BaseModel):
    tenant_id: uuid.UUID
    admin_email: str
    embed_snippet: str
    login_url: str


class AnalyticsOverview(BaseModel):
    period: str
    intakes_total: int
    matters_total: int
    approvals_pending: int
    approvals_approved: int
    approvals_rejected: int
    time_to_approve_median_hours: float | None
    leads_total: int
    events_total: int


class FunnelStep(BaseModel):
    name: str
    count: int
    conversion_from_previous: float | None = None


class FunnelResponse(BaseModel):
    vertical: str
    period: str
    steps: list[FunnelStep]


# ===========================================================================
# PILOT READINESS SCHEMAS
# ===========================================================================

# --- Pipeline ---
class PipelineStageChange(BaseModel):
    stage: str  # new_intake, qualified, matter_created, docs_pending, case_packet_pending, approved, closed


class PipelineItem(BaseModel):
    """Unified pipeline item combining intake + matter data."""
    id: uuid.UUID
    entity_type: str  # "intake" or "matter"
    pipeline_stage: str
    type: str | None = None  # case type (immigration, etc.)
    client_name: str | None = None
    urgency_score: int = 0
    created_at: datetime
    intake_id: uuid.UUID | None = None
    matter_id: uuid.UUID | None = None
    days_in_stage: int = 0
    next_action: str | None = None

    model_config = {"from_attributes": True}


class PipelineView(BaseModel):
    stages: dict[str, list[PipelineItem]]
    stage_counts: dict[str, int]


# --- Feedback ---
class FeedbackCreate(BaseModel):
    page: str
    rating: int = Field(ge=1, le=5)
    text: str | None = None
    anonymous_id: str | None = None
    context: dict[str, Any] = {}


class FeedbackOut(BaseModel):
    id: uuid.UUID
    page: str
    rating: int
    text: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- Vertical Templates ---
class TemplateField(BaseModel):
    key: str
    label: str
    required: bool = True


class TemplateDoc(BaseModel):
    key: str
    label: str
    required: bool = True


class VerticalTemplate(BaseModel):
    vertical: str
    display_name: str
    country: str = "MX"
    required_documents: list[TemplateDoc]
    required_fields: list[TemplateField]
    pipeline_stages: list[str]
    disclaimers: dict[str, str] = {}  # {"es": "...", "en": "..."}
    default_tasks: list[str] = []
    suggested_questions: list[str] = []


class CompletenessResult(BaseModel):
    matter_id: uuid.UUID
    vertical: str
    docs_required: int
    docs_uploaded: int
    docs_missing: list[str]
    fields_required: int
    fields_present: int
    fields_missing: list[str]
    completeness_pct: float
    is_complete: bool


# --- Pilot KPIs (extends AnalyticsOverview) ---
class PilotKPIs(BaseModel):
    period: str
    time_to_first_response_median_hours: float | None
    time_to_approval_median_hours: float | None
    doc_completeness_72h_pct: float | None
    consult_scheduled_count: int
    pipeline_stage_distribution: dict[str, int]
    sla_breaches: int


# --- Lead Routing ---
class LeadRoutingRule(BaseModel):
    vertical: str
    region: str | None = None  # entidad_federativa or city
    tenant_id: uuid.UUID


class LeadRouteResult(BaseModel):
    lead_id: uuid.UUID
    routed_to_tenant_id: uuid.UUID | None
    rule_matched: str | None  # description of which rule matched


# --- Tenant Credentials (MX trust signals) ---
class TenantCredentials(BaseModel):
    cedula_profesional: str | None = None
    ubicacion: str | None = None  # e.g. "CDMX, Col. Roma Norte"
    horarios: str | None = None  # e.g. "Lun-Vie 9:00-18:00"
    whatsapp_number: str | None = None
    google_business_url: str | None = None
