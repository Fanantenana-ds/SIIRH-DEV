from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db import get_db
from app.models.offres import Offre
from app.services.pdf_service import generate_offre_pdf

router = APIRouter()

# 🔹 Create / update offre
@router.post("/")
def create_offre(data: dict, db: Session = Depends(get_db)):
    try:
        new_offre = Offre(**data)
        db.add(new_offre)
        db.commit()
        db.refresh(new_offre)
        return {"message": "Offre créée avec succès", "id": new_offre.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# 🔹 Active / scoring automatique
@router.post("/activate/{offre_id}")
def activate_offre(offre_id: int, db: Session = Depends(get_db)):
    offre = db.query(Offre).filter(Offre.id==offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    
    offre.active = True
    db.commit()
    db.refresh(offre)

    # Ici, déclenche le scoring automatique sur les candidatures
    # Exemple: score_candidates_for_offre(offre, db)
    return {"message": "Offre activée et scoring automatique déclenché"}

# 🔹 Génération PDF / texte publique
@router.get("/export/{offre_id}")
def export_offre_pdf(offre_id: int, db: Session = Depends(get_db)):
    offre = db.query(Offre).filter(Offre.id==offre_id).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")

    if not offre.active:
        raise HTTPException(status_code=400, detail="Offre non activée")

    data = {c.name: getattr(offre, c.name) for c in offre.__table__.columns}
    pdf_path = generate_offre_pdf(data)
    return {"message": "PDF généré avec succès", "path": pdf_path}
