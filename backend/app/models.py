import uuid
from datetime import datetime

from sqlalchemy import (
    Column, String, DateTime, ForeignKey, JSON, Integer, Text, func
)
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base


# ---------------------------------------------------------------------------
# Tenant
# ---------------------------------------------------------------------------
class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    settings_json = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    email = Column(String(255), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), nullable=False)  # admin, attorney, paralegal, closer, staff
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Intake
# ---------------------------------------------------------------------------
class Intake(Base):
    __tablename__ = "intakes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    channel = Column(String(50), default="web")  # web, chat, phone
    raw_payload_json = Column(JSON, default=dict)
    status = Column(String(50), default="new")  # new, processing, converted, archived
    pipeline_stage = Column(String(50), default="new_intake")  # new_intake, qualified, converted
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Matter
# ---------------------------------------------------------------------------
class Matter(Base):
    __tablename__ = "matters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    intake_id = Column(UUID(as_uuid=True), ForeignKey("intakes.id"), nullable=True)
    type = Column(String(100), nullable=False)  # immigration, tax_resolution, mx_divorce, other
    jurisdiction = Column(String(10), default="US")  # US, MX
    urgency_score = Column(Integer, default=0)  # 0-100
    status = Column(String(50), default="open")  # open, in_progress, pending_review, closed
    pipeline_stage = Column(String(50), default="matter_created")  # matter_created, docs_pending, case_packet_pending, approved, closed
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Person  (client / spouse / dependent linked to a matter)
# ---------------------------------------------------------------------------
class Person(Base):
    __tablename__ = "persons"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    role_in_matter = Column(String(50))  # client, spouse, dependent, petitioner, beneficiary
    name = Column(String(255))
    phone = Column(String(50))
    email = Column(String(255))
    language = Column(String(50), default="en")
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Document
# ---------------------------------------------------------------------------
class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    kind = Column(String(100))  # id_document, tax_notice, court_notice, marriage_cert, etc.
    filename = Column(String(500))
    storage_uri = Column(String(1000))
    status = Column(String(50), default="uploaded")  # uploaded, verified, rejected
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Task
# ---------------------------------------------------------------------------
class Task(Base):
    __tablename__ = "tasks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    status = Column(String(50), default="pending")  # pending, in_progress, completed, cancelled
    assigned_to_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    due_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# AgentRun
# ---------------------------------------------------------------------------
class AgentRun(Base):
    __tablename__ = "agent_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    input_json = Column(JSON, default=dict)
    output_json = Column(JSON, default=dict)
    status = Column(String(50), default="pending")  # pending, running, completed, blocked, failed
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# Approval  (Human Approval Gate)
# ---------------------------------------------------------------------------
class Approval(Base):
    __tablename__ = "approvals"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=True)
    object_type = Column(String(100), nullable=False)  # agent_run, message_draft
    object_id = Column(UUID(as_uuid=True), nullable=False)
    status = Column(String(50), default="pending")  # pending, approved, rejected
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decided_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decided_at = Column(DateTime, nullable=True)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# MessageDraft
# ---------------------------------------------------------------------------
class MessageDraft(Base):
    __tablename__ = "message_drafts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    channel = Column(String(50), default="email")  # email, sms, whatsapp, call_script
    content = Column(Text, nullable=False)
    status = Column(String(50), default="draft")  # draft, needs_approval, approved, sent
    created_at = Column(DateTime, server_default=func.now())


# ---------------------------------------------------------------------------
# InterpreterRequest
# ---------------------------------------------------------------------------
class InterpreterRequest(Base):
    __tablename__ = "interpreter_requests"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    matter_id = Column(UUID(as_uuid=True), ForeignKey("matters.id"), nullable=False)
    language = Column(String(50), nullable=False)  # es, mam, fr, zh, etc.
    modality = Column(String(50), default="virtual")  # in_person, virtual
    date_pref = Column(DateTime, nullable=True)
    status = Column(String(50), default="requested")  # requested, confirmed, completed, cancelled
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


# ===========================================================================
# GROWTH / INSTRUMENTATION MODELS
# ===========================================================================

class Event(Base):
    """Analytics event – public or authenticated."""
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    anonymous_id = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_id = Column(String(100))
    name = Column(String(100), nullable=False, index=True)
    properties_json = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now(), index=True)


class Lead(Base):
    """B2C lead or B2B prospect captured before becoming a tenant/matter."""
    __tablename__ = "leads"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    source_type = Column(String(50), nullable=False)  # b2c_prepkit, b2b_onboarding, referral, organic
    vertical = Column(String(100))  # immigration, tax_resolution, mx_divorce, interpreter
    status = Column(String(50), default="new")  # new, contacted, qualified, converted, lost
    contact_json = Column(JSON, default=dict)  # {name, email, phone, notes, utm_*}
    created_at = Column(DateTime, server_default=func.now())


class Experiment(Base):
    """A/B experiment definition."""
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    key = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default="active")  # draft, active, paused, completed
    variants_json = Column(JSON, default=list)  # ["control", "variant_a"]
    created_at = Column(DateTime, server_default=func.now())


class ExperimentExposure(Base):
    """Records which variant a user was assigned to."""
    __tablename__ = "experiment_exposures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id"), nullable=False)
    variant = Column(String(50), nullable=False)
    anonymous_id = Column(String(100), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())


# ===========================================================================
# PILOT READINESS MODELS
# ===========================================================================

class Feedback(Base):
    """User/visitor feedback captured from any page."""
    __tablename__ = "feedback"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    anonymous_id = Column(String(100))
    page = Column(String(255), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    text = Column(Text)
    context_json = Column(JSON, default=dict)
    created_at = Column(DateTime, server_default=func.now())
