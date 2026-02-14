"""Tests for partner lead routing (B2C → B2B)."""

import uuid

from app.models import Lead, Event
from app.services.lead_routing import (
    add_routing_rule,
    clear_routing_rules,
    route_lead,
)


def test_route_lead_by_vertical_and_region(db, seed_tenant):
    """Lead matched by vertical + region routes to correct tenant."""
    clear_routing_rules()
    add_routing_rule("mx_divorce", seed_tenant.id, region="Ciudad de México")

    lead = Lead(
        id=uuid.uuid4(),
        source_type="b2c_prepkit",
        vertical="mx_divorce",
        status="new",
        contact_json={"name": "Laura", "entidad_federativa": "Ciudad de México"},
    )
    db.add(lead)
    db.flush()

    result = route_lead(db, lead, contact_json=lead.contact_json)

    assert result is not None
    assert result["tenant_id"] == str(seed_tenant.id)
    assert "region=Ciudad de México" in result["rule_matched"]
    assert lead.status == "routed"
    assert str(lead.tenant_id) == str(seed_tenant.id)

    # Verify event was tracked
    events = db.query(Event).filter(Event.name == "lead_routed").all()
    assert len(events) == 1

    clear_routing_rules()


def test_route_lead_fallback_to_vertical_only(db, seed_tenant):
    """Lead with no matching region falls back to vertical-only rule."""
    clear_routing_rules()
    add_routing_rule("mx_divorce", seed_tenant.id)  # no region = catch-all

    lead = Lead(
        id=uuid.uuid4(),
        source_type="b2c_prepkit",
        vertical="mx_divorce",
        status="new",
        contact_json={"name": "José", "entidad_federativa": "Jalisco"},
    )
    db.add(lead)
    db.flush()

    result = route_lead(db, lead, contact_json=lead.contact_json)

    assert result is not None
    assert result["tenant_id"] == str(seed_tenant.id)
    assert "region" not in result["rule_matched"]  # used catch-all
    assert lead.status == "routed"

    clear_routing_rules()


def test_route_lead_no_match(db, seed_tenant):
    """Lead with no matching rules returns None and stays 'new'."""
    clear_routing_rules()
    # Add rule for mx_consumer, but lead is mx_divorce
    add_routing_rule("mx_consumer", seed_tenant.id)

    lead = Lead(
        id=uuid.uuid4(),
        source_type="b2c_prepkit",
        vertical="mx_divorce",
        status="new",
        contact_json={"name": "No Match"},
    )
    db.add(lead)
    db.flush()

    result = route_lead(db, lead, contact_json=lead.contact_json)

    assert result is None
    assert lead.status == "new"  # unchanged

    clear_routing_rules()


def test_route_lead_deterministic(db, seed_tenant):
    """Same lead ID always routes to the same tenant (deterministic round-robin)."""
    clear_routing_rules()

    # Create two "tenants" in routing rules
    tenant_id_a = seed_tenant.id
    tenant_id_b = uuid.uuid4()
    add_routing_rule("mx_labor", tenant_id_a)
    add_routing_rule("mx_labor", tenant_id_b)

    # Create lead with fixed ID
    fixed_id = uuid.UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
    lead = Lead(
        id=fixed_id,
        source_type="b2c_prepkit",
        vertical="mx_labor",
        status="new",
        contact_json={"name": "Test Deterministic"},
    )
    db.add(lead)
    db.flush()

    result = route_lead(db, lead, contact_json=lead.contact_json)
    first_tenant = result["tenant_id"]

    # Reset lead and route again — should get same result
    lead.status = "new"
    lead.tenant_id = None
    db.flush()

    result2 = route_lead(db, lead, contact_json=lead.contact_json)
    assert result2["tenant_id"] == first_tenant

    clear_routing_rules()


def test_route_lead_exact_match_preferred(db, seed_tenant):
    """Region-specific rule takes priority over catch-all."""
    clear_routing_rules()

    catch_all_tenant = uuid.uuid4()
    add_routing_rule("mx_divorce", catch_all_tenant)  # catch-all
    add_routing_rule("mx_divorce", seed_tenant.id, region="Jalisco")  # specific

    lead = Lead(
        id=uuid.uuid4(),
        source_type="b2c_prepkit",
        vertical="mx_divorce",
        status="new",
        contact_json={"name": "Jalisco Lead", "entidad_federativa": "Jalisco"},
    )
    db.add(lead)
    db.flush()

    result = route_lead(db, lead, contact_json=lead.contact_json)

    assert result is not None
    assert result["tenant_id"] == str(seed_tenant.id)  # specific match, not catch-all
    assert "Jalisco" in result["rule_matched"]

    clear_routing_rules()


def test_route_lead_no_vertical(db, seed_tenant):
    """Lead without vertical returns None."""
    clear_routing_rules()
    add_routing_rule("mx_divorce", seed_tenant.id)

    lead = Lead(
        id=uuid.uuid4(),
        source_type="b2c_prepkit",
        vertical=None,
        status="new",
        contact_json={"name": "No Vertical"},
    )
    db.add(lead)
    db.flush()

    result = route_lead(db, lead, contact_json=lead.contact_json)
    assert result is None

    clear_routing_rules()
