from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Candidature, Paie, Absence, Contrat
from app.models.discipline import Discipline
router = APIRouter()

@router.get("/stats")
def reporting(db: Session = Depends(get_db)):
    nb_candidatures = db.query(Candidature).count()
    nb_contrats = db.query(Contrat).count()
    total_paie = sum([p.net_a_payer for p in db.query(Paie).all()])
    absences = db.query(Absence).count()
    sanctions = db.query(Discipline).count()

    return {
        "candidatures": nb_candidatures,
        "contrats": nb_contrats,
        "total_paie": total_paie,
        "absences": absences,
        "sanctions": sanctions
    }
