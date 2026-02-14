"""Partner lead routing service (B2C → B2B).

Simple rule-based routing: match leads to tenants by vertical + region.
Supports round-robin when multiple tenants match.
"""

import hashlib
from sqlalchemy.orm import Session

from app.models import Lead, Tenant, Event


# In-memory routing rules (in production, store in DB or tenant settings)
# Each rule: {"vertical": str, "region": str|None, "tenant_id": UUID}
# Region is entidad_federativa or city. None = catch-all for that vertical.
ROUTING_RULES: list[dict] = []


def add_routing_rule(vertical: str, tenant_id, region: str | None = None):
    """Add a routing rule. Called from seed or admin setup."""
    ROUTING_RULES.append({
        "vertical": vertical,
        "region": region,
        "tenant_id": str(tenant_id),
    })


def clear_routing_rules():
    """Clear all routing rules (for testing)."""
    ROUTING_RULES.clear()


def route_lead(
    db: Session,
    lead: Lead,
    contact_json: dict | None = None,
) -> dict | None:
    """Route a lead to a partner tenant based on vertical + region rules.

    Returns {"tenant_id": str, "rule_matched": str} or None if no match.
    Uses deterministic round-robin based on lead ID hash.
    """
    vertical = lead.vertical
    if not vertical:
        return None

    contact = contact_json or lead.contact_json or {}
    region = contact.get("entidad_federativa") or contact.get("region")

    # Find matching rules: first try vertical + region, then vertical only
    exact_matches = [
        r for r in ROUTING_RULES
        if r["vertical"] == vertical and r.get("region") and r["region"] == region
    ]
    fallback_matches = [
        r for r in ROUTING_RULES
        if r["vertical"] == vertical and not r.get("region")
    ]

    candidates = exact_matches if exact_matches else fallback_matches

    if not candidates:
        return None

    # Deterministic round-robin using lead ID hash
    lead_hash = int(hashlib.sha256(str(lead.id).encode()).hexdigest(), 16)
    selected = candidates[lead_hash % len(candidates)]

    # Update lead with routed tenant
    lead.tenant_id = selected["tenant_id"]
    lead.status = "routed"

    # Track event
    rule_desc = f"vertical={vertical}"
    if selected.get("region"):
        rule_desc += f", region={selected['region']}"

    db.add(Event(
        tenant_id=selected["tenant_id"],
        anonymous_id="system",
        name="lead_routed",
        properties_json={
            "lead_id": str(lead.id),
            "vertical": vertical,
            "region": region,
            "routed_to_tenant": selected["tenant_id"],
            "rule_matched": rule_desc,
        },
    ))

    db.commit()
    db.refresh(lead)

    return {
        "tenant_id": selected["tenant_id"],
        "rule_matched": rule_desc,
    }
