"""Tests for MX vertical completeness (mx_divorce, mx_consumer, mx_labor)."""

from app.models import Intake, Matter, Document


def test_mx_divorce_completeness_partial(client, db, seed_tenant, seed_user, auth_headers):
    """mx_divorce with partial docs shows correct missing docs."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Laura García",
            "phone": "+52 55 1234 5678",
            "case_type": "mx_divorce",
            "descripcion": "Divorcio incausado sin hijos",
            "entidad_federativa": "Ciudad de México",
            "regimen_patrimonial": "separacion_bienes",
            "hijos_menores": "no",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
        pipeline_stage="docs_pending",
    )
    db.add(matter)
    db.flush()

    # Upload only 2 of 4 required docs
    db.add(Document(
        tenant_id=seed_tenant.id, matter_id=matter.id,
        kind="ine_pasaporte", filename="ine.pdf", status="uploaded",
    ))
    db.add(Document(
        tenant_id=seed_tenant.id, matter_id=matter.id,
        kind="curp", filename="curp.pdf", status="uploaded",
    ))
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["vertical"] == "mx_divorce"
    assert data["docs_required"] == 4  # acta_matrimonio, ine, curp, comprobante
    assert data["docs_uploaded"] == 2
    assert len(data["docs_missing"]) == 2
    assert "Acta de matrimonio (copia certificada)" in data["docs_missing"]
    assert "Comprobante de domicilio reciente (< 3 meses)" in data["docs_missing"]
    assert data["completeness_pct"] < 100.0
    assert data["is_complete"] is False


def test_mx_divorce_completeness_100(client, db, seed_tenant, seed_user, auth_headers):
    """mx_divorce with all required docs and fields is 100% complete."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Laura García",
            "phone": "+52 55 1234 5678",
            "case_type": "mx_divorce",
            "descripcion": "Divorcio incausado express",
            "entidad_federativa": "Ciudad de México",
            "regimen_patrimonial": "separacion_bienes",
            "hijos_menores": "no",
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
    )
    db.add(matter)
    db.flush()

    # Upload all 4 required docs
    for kind in ["acta_matrimonio", "ine_pasaporte", "curp", "comprobante_domicilio"]:
        db.add(Document(
            tenant_id=seed_tenant.id, matter_id=matter.id,
            kind=kind, filename=f"{kind}.pdf", status="uploaded",
        ))
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["completeness_pct"] == 100.0
    assert data["is_complete"] is True
    assert len(data["docs_missing"]) == 0
    assert len(data["fields_missing"]) == 0


def test_mx_divorce_missing_fields(client, db, seed_tenant, seed_user, auth_headers):
    """Missing required fields reduce completeness."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Laura García",
            # missing: phone, case_type, descripcion, entidad, regimen, hijos_menores
        },
        status="converted",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_divorce", jurisdiction="MX",
        urgency_score=50, status="open",
    )
    db.add(matter)
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert len(data["fields_missing"]) >= 4
    assert data["is_complete"] is False


def test_mx_consumer_completeness(client, db, seed_tenant, seed_user, auth_headers):
    """mx_consumer template returns correct required docs."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "Roberto López",
            "phone": "+52 33 9876 5432",
            "case_type": "mx_consumer",
            "proveedor_banco": "Banco X",
            "monto_reclamado": "15000",
            "fecha_problema": "2025-12-01",
            "descripcion": "Cobro indebido en tarjeta de crédito",
        },
        status="new",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_consumer", jurisdiction="MX",
        urgency_score=30, status="open",
    )
    db.add(matter)
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["vertical"] == "mx_consumer"
    assert data["docs_required"] == 3  # ine, comprobante_compra, evidencia_problema
    assert data["docs_uploaded"] == 0
    assert len(data["docs_missing"]) == 3
    assert data["is_complete"] is False


def test_mx_labor_completeness(client, db, seed_tenant, seed_user, auth_headers):
    """mx_labor template returns correct required docs."""
    intake = Intake(
        tenant_id=seed_tenant.id, channel="web",
        raw_payload_json={
            "nombre_completo": "María Hernández",
            "phone": "+52 81 5555 0000",
            "case_type": "mx_labor",
            "nombre_empresa": "Empresa S.A.",
            "fecha_ingreso": "2020-01-15",
            "fecha_separacion": "2025-11-30",
            "salario_mensual": "18000",
            "motivo": "Despido injustificado",
            "descripcion": "Me despidieron sin liquidación",
        },
        status="new",
    )
    db.add(intake)
    db.flush()

    matter = Matter(
        tenant_id=seed_tenant.id, intake_id=intake.id,
        type="mx_labor", jurisdiction="MX",
        urgency_score=70, status="open",
    )
    db.add(matter)
    db.commit()

    resp = client.get(f"/matters/{matter.id}/completeness", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()

    assert data["vertical"] == "mx_labor"
    assert data["docs_required"] == 3  # ine, contrato_laboral, recibos_nomina
    assert data["docs_uploaded"] == 0
    assert data["is_complete"] is False


def test_mx_divorce_template_endpoint(client):
    """mx_divorce template returns full MX template with disclaimers."""
    resp = client.get("/templates/mx_divorce")
    assert resp.status_code == 200
    data = resp.json()

    assert data["vertical"] == "mx_divorce"
    assert data["country"] == "MX"
    assert len(data["required_documents"]) >= 4
    assert len(data["disclaimers"]) >= 2  # es + en
    assert len(data["default_tasks"]) >= 5
    assert len(data["suggested_questions"]) >= 5
    assert "pipeline_stages" in data
    assert "new_lead" in data["pipeline_stages"]
    assert "expediente_draft" in data["pipeline_stages"]
