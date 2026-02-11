from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models import Employe, Contrat, Candidature

router = APIRouter(prefix="/api/recrutement/rh", tags=["Dashboard RH"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Endpoint pour retourner les statistiques globales RH :
    - Total employés
    - Total contrats
    - Total candidatures
    - Score moyen des candidats
    """
    total_employes = db.query(Employe).count()
    total_contrats = db.query(Contrat).count()
    total_candidatures = db.query(Candidature).count()

    moyenne_score = 0
    scores = [c.score for c in db.query(Candidature).all() if c.score is not None]
    if len(scores) > 0:
        moyenne_score = sum(scores) / len(scores)

    return {
        "totalEmployes": total_employes,
        "totalContrats": total_contrats,
        "totalCandidatures": total_candidatures,
        "moyenneScore": moyenne_score
    }
