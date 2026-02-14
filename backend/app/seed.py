"""
Seed data for development — MX-first.

Run: python -m app.seed
Idempotent: checks if seed tenant already exists before inserting.
"""

import uuid
import sys

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app.models import Tenant, User, Intake, Matter, Person, Event, Lead, Experiment, Approval, AgentRun, Document, Feedback
from app.dependencies import hash_password
from app.services.lead_routing import add_routing_rule


SEED_TENANT_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
SEED_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")


def seed():
    db: Session = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Tenant).filter(Tenant.id == SEED_TENANT_ID).first():
            print("Seed data already exists, skipping.")
            return

        # --- Tenant (MX despacho demo) ---
        tenant = Tenant(
            id=SEED_TENANT_ID,
            name="Despacho Legal Demo",
            settings_json={
                "disclaimer_es": "Esta plataforma no proporciona asesoría legal. Toda la información es orientativa.",
                "disclaimer_en": "This platform does not provide legal advice. All information is for guidance only.",
                "supported_case_types": ["mx_divorce", "mx_consumer", "mx_labor"],
                "country": "MX",
                "cedula_profesional": "12345678",
                "ubicacion": "CDMX, Col. Roma Norte",
                "horarios": "Lun-Vie 9:00-18:00",
                "whatsapp_number": "+52-55-1234-5678",
            },
        )
        db.add(tenant)

        # --- Users ---
        users = [
            User(
                id=SEED_USER_ID,
                tenant_id=SEED_TENANT_ID,
                email="admin@demo.legal",
                hashed_password=hash_password("admin123"),
                full_name="Admin Usuario",
                role="admin",
            ),
            User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000011"),
                tenant_id=SEED_TENANT_ID,
                email="abogado@demo.legal",
                hashed_password=hash_password("abogado123"),
                full_name="Lic. María García López",
                role="attorney",
            ),
            User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000012"),
                tenant_id=SEED_TENANT_ID,
                email="paralegal@demo.legal",
                hashed_password=hash_password("paralegal123"),
                full_name="Carlos López Martínez",
                role="paralegal",
            ),
            User(
                id=uuid.UUID("00000000-0000-0000-0000-000000000013"),
                tenant_id=SEED_TENANT_ID,
                email="closer@demo.legal",
                hashed_password=hash_password("closer123"),
                full_name="Ana Martínez Ruiz",
                role="closer",
            ),
        ]
        db.add_all(users)

        # --- Sample Intakes (MX-focused) ---
        intake_divorce = Intake(
            id=uuid.UUID("00000000-0000-0000-0000-000000000100"),
            tenant_id=SEED_TENANT_ID,
            channel="web",
            raw_payload_json={
                "nombre_completo": "Laura Hernández Ruiz",
                "phone": "+52-55-1234-5678",
                "email": "laura.hr@email.com",
                "case_type": "mx_divorce",
                "descripcion": "Quiero divorcio incausado. Casada por bienes separados, sin hijos menores.",
                "entidad_federativa": "CDMX",
                "regimen_patrimonial": "separacion_bienes",
                "hijos_menores": "no",
                "language": "es",
            },
            status="converted",
            pipeline_stage="intake_completed",
        )

        intake_consumer = Intake(
            id=uuid.UUID("00000000-0000-0000-0000-000000000101"),
            tenant_id=SEED_TENANT_ID,
            channel="web",
            raw_payload_json={
                "nombre_completo": "Roberto Sánchez Pérez",
                "phone": "+52-55-9876-5432",
                "email": "r.sanchez@email.com",
                "case_type": "mx_consumer",
                "proveedor_banco": "Banco Nacional",
                "monto_reclamado": "45000",
                "fecha_problema": "2025-12-15",
                "descripcion": "Me cobraron comisiones no autorizadas en mi tarjeta de crédito por $45,000 MXN.",
                "language": "es",
            },
            status="new",
            pipeline_stage="new_lead",
        )

        intake_labor = Intake(
            id=uuid.UUID("00000000-0000-0000-0000-000000000102"),
            tenant_id=SEED_TENANT_ID,
            channel="whatsapp",
            raw_payload_json={
                "nombre_completo": "María Xol Chávez",
                "phone": "+52-55-5555-0103",
                "case_type": "mx_labor",
                "nombre_empresa": "Constructora del Norte SA",
                "fecha_ingreso": "2023-03-01",
                "fecha_separacion": "2025-11-30",
                "salario_mensual": "15000",
                "motivo": "Despido injustificado",
                "descripcion": "Me despidieron sin liquidación después de 2 años 8 meses. No me dieron carta de despido.",
                "language": "es",
            },
            status="new",
            pipeline_stage="new_lead",
        )

        intake_divorce2 = Intake(
            id=uuid.UUID("00000000-0000-0000-0000-000000000103"),
            tenant_id=SEED_TENANT_ID,
            channel="web",
            raw_payload_json={
                "nombre_completo": "José Ramírez Torres",
                "phone": "+52-33-1111-2222",
                "email": "jose.rt@email.com",
                "case_type": "mx_divorce",
                "descripcion": "Divorcio con hijos menores. Mi esposa y yo estamos de acuerdo en todo.",
                "entidad_federativa": "Jalisco",
                "regimen_patrimonial": "sociedad_conyugal",
                "hijos_menores": "si",
                "language": "es",
            },
            status="new",
            pipeline_stage="new_lead",
        )

        db.add_all([intake_divorce, intake_consumer, intake_labor, intake_divorce2])

        # --- Sample Matter (from divorce intake) ---
        matter = Matter(
            id=uuid.UUID("00000000-0000-0000-0000-000000001000"),
            tenant_id=SEED_TENANT_ID,
            intake_id=intake_divorce.id,
            type="mx_divorce",
            jurisdiction="MX",
            urgency_score=60,
            status="open",
            pipeline_stage="docs_pending",
        )
        db.add(matter)

        # --- Documents (partial – to demo completeness) ---
        db.add(Document(
            tenant_id=SEED_TENANT_ID, matter_id=matter.id,
            kind="ine_pasaporte", filename="ine_laura.pdf", status="uploaded",
        ))
        db.add(Document(
            tenant_id=SEED_TENANT_ID, matter_id=matter.id,
            kind="curp", filename="curp_laura.pdf", status="verified",
        ))

        # --- Person linked to matter ---
        person = Person(
            tenant_id=SEED_TENANT_ID,
            matter_id=matter.id,
            role_in_matter="client",
            name="Laura Hernández Ruiz",
            phone="+52-55-1234-5678",
            email="laura.hr@email.com",
            language="es",
        )
        db.add(person)

        # --- Agent Run + Approval ---
        agent_run = AgentRun(
            id=uuid.UUID("00000000-0000-0000-0000-000000002000"),
            tenant_id=SEED_TENANT_ID,
            matter_id=matter.id,
            agent_name="intake_specialist",
            input_json={"case_type": "mx_divorce", "description": "Divorcio incausado CDMX"},
            output_json={"case_packet": "[MOCK] Análisis de caso de divorcio incausado...", "requires_approval": True},
            status="needs_approval",
        )
        db.add(agent_run)

        approval = Approval(
            id=uuid.UUID("00000000-0000-0000-0000-000000003000"),
            tenant_id=SEED_TENANT_ID,
            matter_id=matter.id,
            object_type="agent_run",
            object_id=agent_run.id,
            status="pending",
            requested_by=SEED_USER_ID,
        )
        db.add(approval)

        # --- Analytics seed: events for funnel demo ---
        demo_anon_ids = ["anon_001", "anon_002", "anon_003", "anon_004", "anon_005"]
        funnel_events = []
        for i, anon_id in enumerate(demo_anon_ids):
            funnel_events.append(Event(tenant_id=SEED_TENANT_ID, anonymous_id=anon_id, name="page_view",
                                       properties_json={"path": "/", "utm_source": "google"}))
            funnel_events.append(Event(tenant_id=SEED_TENANT_ID, anonymous_id=anon_id, name="cta_click",
                                       properties_json={"variant": "b2c" if i % 2 == 0 else "b2b"}))
            funnel_events.append(Event(tenant_id=SEED_TENANT_ID, anonymous_id=anon_id, name="intake_started",
                                       properties_json={"case_type": "mx_divorce"}))
            if i < 4:
                funnel_events.append(Event(tenant_id=SEED_TENANT_ID, anonymous_id=anon_id, name="intake_submitted",
                                           properties_json={"case_type": "mx_divorce"}))
            if i < 3:
                funnel_events.append(Event(tenant_id=SEED_TENANT_ID, anonymous_id=anon_id,
                                           name="intake_converted_to_matter", properties_json={"type": "mx_divorce"}))
            if i < 2:
                funnel_events.append(Event(tenant_id=SEED_TENANT_ID, anonymous_id=anon_id, name="agent_run_created",
                                           properties_json={"agent_name": "intake_specialist"}))
            if i < 1:
                funnel_events.append(Event(tenant_id=SEED_TENANT_ID, anonymous_id=anon_id, name="approval_approved",
                                           properties_json={}))
        db.add_all(funnel_events)

        # --- Leads ---
        demo_leads = [
            Lead(tenant_id=SEED_TENANT_ID, source_type="b2c_prepkit", vertical="mx_divorce", status="new",
                 contact_json={"name": "Ana B.", "email": "ana@test.com", "phone": "+52-55-1111-2222", "entidad_federativa": "CDMX"}),
            Lead(tenant_id=SEED_TENANT_ID, source_type="b2c_prepkit", vertical="mx_consumer", status="new",
                 contact_json={"name": "Bob C.", "email": "bob@test.com", "phone": "+52-33-3333-4444"}),
            Lead(source_type="b2b_onboarding", vertical="mx_divorce", status="new",
                 contact_json={"firm_name": "García & Asociados", "email": "info@garcia.law"}),
        ]
        db.add_all(demo_leads)

        # --- Experiments ---
        exp1 = Experiment(key="approval_sla_nudge", status="active", variants_json=["control", "nudge_4h"])
        exp2 = Experiment(key="prepkit_cta_variant", status="active", variants_json=["control", "variant_a"])
        db.add_all([exp1, exp2])

        # --- Sample Feedback ---
        db.add(Feedback(
            tenant_id=SEED_TENANT_ID,
            anonymous_id="anon_001",
            page="/help",
            rating=4,
            text="El checklist de documentos me ayudó mucho a prepararme.",
            context_json={"case_type": "mx_divorce"},
        ))

        # --- Lead Routing Rules (demo) ---
        add_routing_rule("mx_divorce", SEED_TENANT_ID, region="CDMX")
        add_routing_rule("mx_divorce", SEED_TENANT_ID)  # catch-all
        add_routing_rule("mx_consumer", SEED_TENANT_ID)
        add_routing_rule("mx_labor", SEED_TENANT_ID)

        db.commit()
        print("Seed data created successfully! (MX-first)")
        print(f"  Tenant: {tenant.name} ({tenant.id})")
        print(f"  Users: admin@demo.legal / admin123")
        print(f"         abogado@demo.legal / abogado123")
        print(f"         paralegal@demo.legal / paralegal123")
        print(f"  Intakes: 4 (mx_divorce x2, mx_consumer, mx_labor)")
        print(f"  Matter: 1 (mx_divorce, urgency=60, stage=docs_pending)")
        print(f"  Agent Run: 1 (needs_approval)")
        print(f"  Approval: 1 (pending)")
        print(f"  Events: {len(funnel_events)} (funnel demo)")
        print(f"  Leads: {len(demo_leads)}")
        print(f"  Experiments: 2")
        print(f"  Routing Rules: 4 (mx_divorce CDMX + catch-all, mx_consumer, mx_labor)")

    except Exception as e:
        db.rollback()
        print(f"Seed error: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
