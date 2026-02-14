"""A/B experiment assignment – deterministic by anonymous_id."""

import hashlib

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Experiment, ExperimentExposure
from app.schemas import ExperimentAssignRequest, ExperimentAssignResponse

router = APIRouter(prefix="/experiments", tags=["experiments"])


def _deterministic_variant(experiment_key: str, anonymous_id: str, variants: list[str]) -> str:
    """Deterministic hash-based assignment. Same input → same variant always."""
    if not variants:
        return "control"
    hash_input = f"{experiment_key}:{anonymous_id}"
    hash_value = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
    return variants[hash_value % len(variants)]


@router.post("/assign", response_model=ExperimentAssignResponse)
def assign_variant(
    body: ExperimentAssignRequest,
    db: Session = Depends(get_db),
):
    """Public: assign a variant for an experiment. Deterministic + idempotent."""
    experiment = (
        db.query(Experiment)
        .filter(Experiment.key == body.experiment_key, Experiment.status == "active")
        .first()
    )
    if not experiment:
        raise HTTPException(status_code=404, detail=f"Experiment '{body.experiment_key}' not found or not active")

    variants = experiment.variants_json or ["control"]

    # Check existing exposure
    existing = (
        db.query(ExperimentExposure)
        .filter(
            ExperimentExposure.experiment_id == experiment.id,
            ExperimentExposure.anonymous_id == body.anonymous_id,
        )
        .first()
    )
    if existing:
        return ExperimentAssignResponse(
            experiment_key=body.experiment_key,
            variant=existing.variant,
            anonymous_id=body.anonymous_id,
        )

    # Assign new variant
    variant = _deterministic_variant(body.experiment_key, body.anonymous_id, variants)

    exposure = ExperimentExposure(
        experiment_id=experiment.id,
        variant=variant,
        anonymous_id=body.anonymous_id,
    )
    db.add(exposure)
    db.commit()

    return ExperimentAssignResponse(
        experiment_key=body.experiment_key,
        variant=variant,
        anonymous_id=body.anonymous_id,
    )
