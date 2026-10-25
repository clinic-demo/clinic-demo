from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile
from sqlalchemy.orm import Session

from src.conf.config import DOCUMENTS_DIR
from src.database.db import get_db
from src.entity.models import User
from src.repository.clinic import create_document, get_document
from src.routes.deps import get_current_user
from src.schemas.clinic import DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("", response_model=DocumentOut)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can upload documents")

    safe_name = Path(file.filename or "upload.txt").name
    docs_dir = DOCUMENTS_DIR
    docs_dir.mkdir(parents=True, exist_ok=True)
    file_path = docs_dir / safe_name
    content = file.file.read()
    file_path.write_bytes(content)

    summary = "Uploaded clinical document" if file.content_type else None
    document = create_document(
        db,
        current_user.id,
        safe_name,
        file.content_type or "application/octet-stream",
        str(file_path),
        len(content),
        summary,
    )
    return document


@router.get("/{document_id}", response_model=DocumentOut)
def get_document_endpoint(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can access documents")
    return get_document(db, document_id, current_user.id)


@router.get("/{document_id}/download")
def download_document(document_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can download documents")
    document = get_document(db, document_id, current_user.id)
    content = Path(document.file_path).read_bytes()
    return Response(
        content=content,
        media_type=document.content_type,
        headers={"Content-Disposition": f'attachment; filename="{document.filename}"'},
    )
