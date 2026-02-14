import uuid

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.dependencies import get_current_user
from app.models import Document, Matter, User

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", status_code=201)
def upload_document(
    matter_id: str = Form(...),
    kind: str = Form("other"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stub upload: saves metadata + file to local disk (no S3)."""
    matter = db.query(Matter).filter(Matter.id == matter_id, Matter.tenant_id == current_user.tenant_id).first()
    if not matter:
        raise HTTPException(status_code=404, detail="Matter not found")

    file_id = uuid.uuid4()
    storage_uri = f"local://uploads/{file_id}_{file.filename}"

    # Write to local filesystem (stub)
    import os
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    dest_path = os.path.join(settings.UPLOAD_DIR, f"{file_id}_{file.filename}")
    with open(dest_path, "wb") as f:
        f.write(file.file.read())

    doc = Document(
        tenant_id=current_user.tenant_id,
        matter_id=matter.id,
        kind=kind,
        filename=file.filename,
        storage_uri=storage_uri,
        status="uploaded",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return {
        "id": str(doc.id),
        "filename": doc.filename,
        "kind": doc.kind,
        "storage_uri": doc.storage_uri,
        "status": doc.status,
    }


@router.get("/", response_model=list[dict])
def list_documents(matter_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    docs = db.query(Document).filter(Document.matter_id == matter_id, Document.tenant_id == current_user.tenant_id).all()
    return [
        {
            "id": str(d.id),
            "kind": d.kind,
            "filename": d.filename,
            "status": d.status,
            "created_at": d.created_at.isoformat() if d.created_at else None,
        }
        for d in docs
    ]
