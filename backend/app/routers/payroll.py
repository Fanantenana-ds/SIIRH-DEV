from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db

router = APIRouter(prefix="/paie", tags=["Paie"])

@router.post("/export")
def export_paie(period: dict, db: Session = Depends(get_db)):
    return {
        "heures_normales": 160,
        "hs": 12,
        "absences": 3,
        "conges_non_payes": 1,
        "pdf_url": "/static/paie_report.pdf"
    }
