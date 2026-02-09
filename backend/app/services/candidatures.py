from sqlalchemy.orm import Session
from app.models import Candidature  
from app.schemas import CandidatureResponse

def create_candidature(db: Session, data: dict) -> CandidatureResponse:
    """
    Crée une nouvelle candidature en base de données.
    """
    db_cand = Candidature(
        fullname=data["fullname"],
        email=data["email"],
        telephone=data.get("phone"),
        source=data.get("source", "web_form"),
        raw_cv_path=data["raw_cv_path"],
        parsed_json=data["parsed_json"],
        score=data["score"]
    )
    db.add(db_cand)
    db.commit()
    db.refresh(db_cand)
    return db_cand
