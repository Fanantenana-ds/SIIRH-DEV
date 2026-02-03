

# backend/app/routers/candidatures.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.models import Candidature
from app.models.offres import Offre
from app.schemas.candidatures import CandidatureResponse
from app.services.upload_service import save_upload_file

router = APIRouter(prefix="/api/candidatures", tags=["Candidatures Public"])


@router.post("/", response_model=CandidatureResponse)
def create_candidature(
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form("") ,
    poste: str = Form(...),
    offre_reference: str = Form(...),
    cv: UploadFile = File(...),
    lettre: UploadFile = File(None),
    diplomes: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    # ==========================================================
    # 1️⃣ Vérification offre
    # ==========================================================
    offre = db.query(Offre).filter(Offre.titre == offre_reference).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")

    # ==========================================================
    # 2️⃣ Création candidature DB
    # ==========================================================
    candidature = Candidature(
        nom=nom.upper(),
        prenom=prenom,
        email=email,
        telephone=telephone or "",
        source="formulaire",
        raw_cv_s3=None,
        score=0,
        statut="En attente",
        poste=poste,
        offre_id=offre.id
    )

    db.add(candidature)
    db.commit()
    db.refresh(candidature)

    # ==========================================================
    # 3️⃣ Upload CV vers MinIO + parsing + score
    # ==========================================================
    upload_result = save_upload_file(
        db=db,
        file=cv,
        candidature_id=candidature.id,
        offre=offre.__dict__
    )

    # ==========================================================
    # 4️⃣ Mise à jour raw_cv_s3 + score
    # ==========================================================
    candidature.raw_cv_s3 = upload_result.get("filepath")
    candidature.score = upload_result.get("score", 0)

    db.commit()
    db.refresh(candidature)

    # ==========================================================
    # 5️⃣ Retour
    # ==========================================================
    return candidature
