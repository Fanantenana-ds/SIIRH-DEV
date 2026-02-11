from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Candidature
from pathlib import Path
import shutil
import json

router = APIRouter()
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@router.post("/candidatures")
async def create_candidature(
    job_ref: str = Form(...),
    lastname: str = Form(...),
    firstname: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    cv_file: UploadFile = File(...),
    job_requirements: str = Form(...),
    db: Session = Depends(get_db)
):
    file_location = UPLOAD_DIR / cv_file.filename
    with file_location.open("wb") as f:
        shutil.copyfileobj(cv_file.file, f)

    try:
        job_req_dict = json.loads(job_requirements)
    except:
        job_req_dict = {}

    score_total = 50  # TODO: refine scoring rules

    cand = Candidature(
        lastname=lastname,
        firstname=firstname,
        email=email,
        phone=phone,
        job_ref=job_ref,
        cv_filename=cv_file.filename,
        job_requirements=job_req_dict,
        score=score_total
    )
    db.add(cand)
    db.commit()
    db.refresh(cand)

    return {"message": "Candidature envoyée ✅", "id": cand.id}
