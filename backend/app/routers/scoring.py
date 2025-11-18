from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Candidature 
from app.models.offres import Offre
from app.services.scoring_auto import calculer_score_auto

router = APIRouter(prefix="/api/score", tags=["Score"])

@router.post("/auto/{candidature_id}")
def calcul_score_auto(candidature_id: int, db: Session = Depends(get_db)):
    candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
    if not candidature:
        raise HTTPException(status_code=404, detail="Candidature introuvable")

    offre = db.query(Offre).filter(Offre.id == candidature.offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre associée introuvable")

    # Lecture du CV
    cv_text = ""
    if candidature.parsed_json and "text" in candidature.parsed_json:
        cv_text = candidature.parsed_json["text"]
    else:
        cv_text = candidature.raw_cv_s3 or ""

    # Calcul du score automatique
    score = calculer_score_auto(cv_text, offre)

    # Mise à jour en base
    candidature.score = score
    db.commit()
    db.refresh(candidature)

    return {"candidature_id": candidature.id, "score": score}
