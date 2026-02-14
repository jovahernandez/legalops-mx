"""Run an agent workflow (mock LLM) and enforce policy engine."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import AgentRun, Approval, Matter, User
from app.schemas import AgentRunRequest, AgentRunOut
from app.agents.orchestrator import AgentOrchestrator

router = APIRouter(prefix="/agents", tags=["agents"])

orchestrator = AgentOrchestrator()


@router.post("/run", response_model=AgentRunOut, status_code=201)
def run_agent(
    body: AgentRunRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    matter = db.query(Matter).filter(Matter.id == body.matter_id, Matter.tenant_id == current_user.tenant_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    if body.agent_name not in orchestrator.available_agents():
        raise HTTPException(status_code=400, detail=f"Unknown agent: {body.agent_name}. Available: {orchestrator.available_agents()}")

    # Execute agent (mock LLM)
    result = orchestrator.run(body.agent_name, body.input_data)

    # Determine status based on policy check
    status = "completed"
    if result.get("compliance_flags"):
        status = "blocked"

    agent_run = AgentRun(
        tenant_id=current_user.tenant_id,
        matter_id=body.matter_id,
        agent_name=body.agent_name,
        input_json=body.input_data,
        output_json=result,
        status=status,
    )
    db.add(agent_run)
    db.flush()

    # If blocked or has output for client, create approval
    if status == "blocked" or result.get("requires_approval", True):
        approval = Approval(
            tenant_id=current_user.tenant_id,
            matter_id=body.matter_id,
            object_type="agent_run",
            object_id=agent_run.id,
            status="pending",
            requested_by=current_user.id,
        )
        db.add(approval)
        if status != "blocked":
            agent_run.status = "needs_approval"

    db.commit()
    db.refresh(agent_run)
    return agent_run


@router.get("/definitions")
def list_agent_definitions():
    """Return all registered agent definitions."""
    return orchestrator.list_definitions()
