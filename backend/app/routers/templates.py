"""Vertical templates + matter completeness endpoint.

MX-first template registry. Each vertical defines:
- required_documents, required_fields
- disclaimers (es/en), default_tasks, suggested_questions
- pipeline_stages
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Matter, Document, Intake, Person, User
from app.schemas import VerticalTemplate, TemplateDoc, TemplateField, CompletenessResult

router = APIRouter(tags=["templates"])

# MX pipeline stages (shared across MX verticals)
MX_PIPELINE_STAGES = [
    "new_lead",
    "intake_completed",
    "docs_pending",
    "expediente_draft",
    "pending_approval",
    "approved",
    "contract_onboarding",
    "in_progress",
    "closed",
]

# ---------------------------------------------------------------------------
# MX WEDGE: Divorcio incausado express
# ---------------------------------------------------------------------------
VERTICAL_TEMPLATES: dict[str, VerticalTemplate] = {
    "mx_divorce": VerticalTemplate(
        vertical="mx_divorce",
        display_name="Divorcio Incausado (MX)",
        country="MX",
        required_documents=[
            TemplateDoc(key="acta_matrimonio", label="Acta de matrimonio (copia certificada)"),
            TemplateDoc(key="ine_pasaporte", label="Identificación oficial (INE o pasaporte)"),
            TemplateDoc(key="curp", label="CURP"),
            TemplateDoc(key="comprobante_domicilio", label="Comprobante de domicilio reciente (< 3 meses)"),
            TemplateDoc(key="actas_hijos", label="Actas de nacimiento de hijos menores", required=False),
            TemplateDoc(key="convenio_propuesta", label="Convenio propuesto (custodia, alimentos, bienes)", required=False),
            TemplateDoc(key="regimen_patrimonial", label="Documento de régimen patrimonial (separación/sociedad conyugal)", required=False),
        ],
        required_fields=[
            TemplateField(key="nombre_completo", label="Nombre completo"),
            TemplateField(key="phone", label="Teléfono / WhatsApp"),
            TemplateField(key="case_type", label="Tipo de caso"),
            TemplateField(key="descripcion", label="Descripción de la situación"),
            TemplateField(key="entidad_federativa", label="Entidad federativa"),
            TemplateField(key="regimen_patrimonial", label="Régimen patrimonial (separación/sociedad conyugal)"),
            TemplateField(key="hijos_menores", label="¿Tiene hijos menores de edad?"),
            TemplateField(key="email", label="Correo electrónico", required=False),
        ],
        pipeline_stages=MX_PIPELINE_STAGES,
        disclaimers={
            "es": (
                "Esta herramienta NO proporciona asesoría legal. Toda la información "
                "es orientativa y debe ser revisada por un abogado con cédula profesional. "
                "No se crea relación abogado-cliente al usar esta plataforma."
            ),
            "en": (
                "This tool does NOT provide legal advice. All information is for guidance "
                "only and must be reviewed by a licensed attorney. No attorney-client "
                "relationship is created by using this platform."
            ),
        },
        default_tasks=[
            "Verificar documentos de identidad",
            "Revisar régimen patrimonial",
            "Confirmar datos de hijos menores (si aplica)",
            "Preparar convenio de custodia y alimentos (si aplica)",
            "Generar borrador de demanda incausada",
            "Solicitar aprobación del abogado",
        ],
        suggested_questions=[
            "¿Cuáles son los requisitos para divorcio incausado en mi estado?",
            "¿Cuánto tiempo toma el proceso de divorcio?",
            "¿Cómo se resuelve la custodia y pensión alimenticia?",
            "¿Necesito el consentimiento de mi cónyuge para el divorcio incausado?",
            "¿Qué pasa con los bienes del matrimonio?",
            "¿Cuáles son los costos aproximados del proceso?",
            "¿Puedo tramitarlo si mi cónyuge vive en otro estado?",
        ],
    ),

    "mx_consumer": VerticalTemplate(
        vertical="mx_consumer",
        display_name="Queja de Consumidor (PROFECO/CONDUSEF)",
        country="MX",
        required_documents=[
            TemplateDoc(key="ine_pasaporte", label="Identificación oficial (INE o pasaporte)"),
            TemplateDoc(key="comprobante_compra", label="Comprobante de compra o contrato"),
            TemplateDoc(key="evidencia_problema", label="Evidencia del problema (fotos, capturas, recibos)"),
            TemplateDoc(key="comunicaciones", label="Comunicaciones con el proveedor/banco", required=False),
            TemplateDoc(key="folio_queja", label="Folio de queja ante PROFECO/CONDUSEF (si existe)", required=False),
        ],
        required_fields=[
            TemplateField(key="nombre_completo", label="Nombre completo"),
            TemplateField(key="phone", label="Teléfono / WhatsApp"),
            TemplateField(key="case_type", label="Tipo de caso"),
            TemplateField(key="proveedor_banco", label="Nombre del proveedor o banco"),
            TemplateField(key="monto_reclamado", label="Monto reclamado (MXN)"),
            TemplateField(key="fecha_problema", label="Fecha del problema"),
            TemplateField(key="descripcion", label="Narrativa del problema"),
            TemplateField(key="email", label="Correo electrónico", required=False),
        ],
        pipeline_stages=MX_PIPELINE_STAGES,
        disclaimers={
            "es": (
                "Esta herramienta NO proporciona asesoría legal. La información es "
                "orientativa para preparar su expediente ante PROFECO o CONDUSEF. "
                "Consulte a un profesional antes de tomar decisiones."
            ),
            "en": (
                "This tool does NOT provide legal advice. Information is for guidance "
                "to prepare your file for PROFECO or CONDUSEF."
            ),
        },
        default_tasks=[
            "Verificar datos del proveedor/banco",
            "Revisar evidencias adjuntas",
            "Preparar cronología de hechos",
            "Generar borrador de queja formal",
            "Solicitar aprobación del profesional",
        ],
        suggested_questions=[
            "¿Mi caso es competencia de PROFECO o CONDUSEF?",
            "¿Cuáles son los plazos para presentar mi queja?",
            "¿Qué pruebas necesito reunir?",
            "¿Puedo reclamar daños y perjuicios adicionales?",
            "¿Qué pasa si el proveedor no responde a la conciliación?",
        ],
    ),

    "mx_labor": VerticalTemplate(
        vertical="mx_labor",
        display_name="Asunto Laboral (MX)",
        country="MX",
        required_documents=[
            TemplateDoc(key="ine_pasaporte", label="Identificación oficial (INE o pasaporte)"),
            TemplateDoc(key="contrato_laboral", label="Contrato laboral (si existe)"),
            TemplateDoc(key="recibos_nomina", label="Recibos de nómina (últimos 3 meses)"),
            TemplateDoc(key="carta_despido", label="Carta de despido o renuncia (si aplica)", required=False),
            TemplateDoc(key="alta_imss", label="Alta o baja del IMSS", required=False),
            TemplateDoc(key="evidencia_laboral", label="Evidencia adicional (correos, fotos, testigos)", required=False),
        ],
        required_fields=[
            TemplateField(key="nombre_completo", label="Nombre completo"),
            TemplateField(key="phone", label="Teléfono / WhatsApp"),
            TemplateField(key="case_type", label="Tipo de caso"),
            TemplateField(key="nombre_empresa", label="Nombre del empleador/empresa"),
            TemplateField(key="fecha_ingreso", label="Fecha de ingreso"),
            TemplateField(key="fecha_separacion", label="Fecha de separación (si aplica)"),
            TemplateField(key="salario_mensual", label="Salario mensual (MXN)"),
            TemplateField(key="motivo", label="Motivo de la consulta (despido, falta de pago, etc.)"),
            TemplateField(key="descripcion", label="Descripción de la situación"),
            TemplateField(key="email", label="Correo electrónico", required=False),
        ],
        pipeline_stages=MX_PIPELINE_STAGES,
        disclaimers={
            "es": (
                "Esta herramienta NO proporciona asesoría legal laboral. La información "
                "es orientativa para preparar su expediente. No sustituye la consulta con "
                "un abogado laboralista."
            ),
            "en": (
                "This tool does NOT provide labor legal advice. Information is for guidance "
                "to prepare your file."
            ),
        },
        default_tasks=[
            "Verificar datos de la relación laboral",
            "Calcular antigüedad y prestaciones pendientes",
            "Revisar evidencias de despido/incumplimiento",
            "Preparar cronología laboral",
            "Generar borrador de expediente laboral",
            "Solicitar aprobación del profesional",
        ],
        suggested_questions=[
            "¿Mi despido fue justificado o injustificado?",
            "¿A cuánto asciende mi liquidación o finiquito?",
            "¿Cuánto tiempo tengo para demandar?",
            "¿Me corresponden utilidades (PTU)?",
            "¿Puedo demandar si no tenía contrato formal?",
            "¿Qué prestaciones me deben por ley (aguinaldo, vacaciones, prima)?",
        ],
    ),

    # --- US verticals (kept but secondary) ---
    "immigration": VerticalTemplate(
        vertical="immigration",
        display_name="Immigration (US)",
        country="US",
        required_documents=[
            TemplateDoc(key="government_id", label="Government-issued photo ID (passport, national ID)"),
            TemplateDoc(key="immigration_notice", label="Immigration notices (NTA, RFE, denial letters)"),
            TemplateDoc(key="prior_filings", label="Prior immigration filings or receipts", required=False),
            TemplateDoc(key="proof_of_address", label="Proof of address (utility bill, lease)"),
            TemplateDoc(key="employment_auth", label="Employment authorization document (EAD)", required=False),
        ],
        required_fields=[
            TemplateField(key="full_name", label="Full legal name"),
            TemplateField(key="phone", label="Phone number"),
            TemplateField(key="case_type", label="Case type"),
            TemplateField(key="description", label="Case description"),
            TemplateField(key="language", label="Preferred language"),
            TemplateField(key="email", label="Email address", required=False),
        ],
        pipeline_stages=["new_intake", "qualified", "matter_created", "docs_pending", "case_packet_pending", "approved", "closed"],
        disclaimers={"en": "This tool does NOT provide legal advice.", "es": "Esta herramienta NO proporciona asesoría legal."},
        default_tasks=["Review intake", "Collect documents", "Run agent", "Approve case packet"],
        suggested_questions=["What is my current immigration status?", "What are my deadlines?", "What documents do I need?"],
    ),
    "tax_resolution": VerticalTemplate(
        vertical="tax_resolution",
        display_name="Tax Resolution (US)",
        country="US",
        required_documents=[
            TemplateDoc(key="irs_notice", label="IRS notices (CP2000, CP504, etc.)"),
            TemplateDoc(key="w2_1099", label="W-2s and/or 1099s for relevant years"),
            TemplateDoc(key="prior_returns", label="Prior tax returns (if filed)", required=False),
            TemplateDoc(key="income_proof", label="Proof of income (pay stubs, bank statements)"),
            TemplateDoc(key="tin_docs", label="TIN/SSN/ITIN documentation"),
        ],
        required_fields=[
            TemplateField(key="full_name", label="Full legal name"),
            TemplateField(key="phone", label="Phone number"),
            TemplateField(key="case_type", label="Case type"),
            TemplateField(key="description", label="Description of tax situation"),
            TemplateField(key="language", label="Preferred language"),
        ],
        pipeline_stages=["new_intake", "qualified", "matter_created", "docs_pending", "case_packet_pending", "approved", "closed"],
        disclaimers={"en": "This tool does NOT provide tax or legal advice."},
        default_tasks=["Review IRS notices", "Collect tax documents", "Analyze resolution options"],
        suggested_questions=["What resolution options are available?", "Am I eligible for an Offer in Compromise?"],
    ),
}


@router.get("/templates/{vertical}", response_model=VerticalTemplate)
def get_template(vertical: str):
    """Get template definition for a vertical. Public endpoint."""
    template = VERTICAL_TEMPLATES.get(vertical)
    if not template:
        raise HTTPException(status_code=404, detail=f"No template for vertical: {vertical}")
    return template


@router.get("/templates/", response_model=list[VerticalTemplate])
def list_templates():
    """List all available vertical templates."""
    return list(VERTICAL_TEMPLATES.values())


@router.get("/matters/{matter_id}/completeness", response_model=CompletenessResult)
def get_completeness(
    matter_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Calculate document and field completeness for a matter against its vertical template."""
    matter = (
        db.query(Matter)
        .filter(Matter.id == matter_id, Matter.tenant_id == current_user.tenant_id)
        .first()
    )
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    template = VERTICAL_TEMPLATES.get(matter.type)
    if not template:
        return CompletenessResult(
            matter_id=matter.id, vertical=matter.type,
            docs_required=0, docs_uploaded=0, docs_missing=[],
            fields_required=0, fields_present=0, fields_missing=[],
            completeness_pct=100.0, is_complete=True,
        )

    # --- Document completeness ---
    docs = db.query(Document).filter(
        Document.matter_id == matter.id,
        Document.status.in_(["uploaded", "verified"]),
    ).all()
    uploaded_kinds = {d.kind for d in docs}
    required_docs = [d for d in template.required_documents if d.required]
    docs_missing = [d.label for d in required_docs if d.key not in uploaded_kinds]

    # --- Field completeness (from intake payload) ---
    field_data: dict = {}
    if matter.intake_id:
        intake = db.query(Intake).filter(Intake.id == matter.intake_id).first()
        if intake and intake.raw_payload_json:
            field_data = intake.raw_payload_json

    required_fields = [f for f in template.required_fields if f.required]
    fields_missing = [f.label for f in required_fields if not field_data.get(f.key)]

    total_required = len(required_docs) + len(required_fields)
    total_present = (len(required_docs) - len(docs_missing)) + (len(required_fields) - len(fields_missing))
    pct = round(total_present / total_required * 100, 1) if total_required > 0 else 100.0

    return CompletenessResult(
        matter_id=matter.id, vertical=matter.type,
        docs_required=len(required_docs),
        docs_uploaded=len(required_docs) - len(docs_missing),
        docs_missing=docs_missing,
        fields_required=len(required_fields),
        fields_present=len(required_fields) - len(fields_missing),
        fields_missing=fields_missing,
        completeness_pct=pct,
        is_complete=(len(docs_missing) == 0 and len(fields_missing) == 0),
    )
