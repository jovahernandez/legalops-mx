from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Task, User
from app.schemas import TaskCreate, TaskOut

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/", response_model=list[TaskOut])
def list_tasks(
    matter_id: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    q = db.query(Task).filter(Task.tenant_id == current_user.tenant_id)
    if matter_id:
        q = q.filter(Task.matter_id == matter_id)
    if status:
        q = q.filter(Task.status == status)
    return q.order_by(Task.due_at.asc().nullslast(), Task.created_at.desc()).all()


@router.post("/", response_model=TaskOut, status_code=201)
def create_task(body: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = Task(
        tenant_id=current_user.tenant_id,
        matter_id=body.matter_id,
        title=body.title,
        description=body.description,
        assigned_to_user_id=body.assigned_to_user_id,
        due_at=body.due_at,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


@router.patch("/{task_id}", response_model=TaskOut)
def update_task_status(
    task_id: str,
    new_status: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    task = db.query(Task).filter(Task.id == task_id, Task.tenant_id == current_user.tenant_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.status = new_status
    db.commit()
    db.refresh(task)
    return task
