# app/routers/candidatures.py
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
import shutil
import os
import difflib

from app.db import get_db
from app.models.models import Candidature, Offre
from app.schemas.candidatures import CandidatureResponse

router = APIRouter(prefix="/api/candidatures", tags=["Candidatures"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/", response_model=CandidatureResponse)
def create_candidature(
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    phone: str = Form(None),
    adresse: str = Form(None),
    date_naissance: str = Form(None),
    poste: str = Form(...),
    disponibilite: str = Form(None),
    salaire: str = Form(None),
    type_contrat: str = Form(None),
    mobilite: str = Form(None),
    autorisation: str = Form(None),
    competences_techniques: str = Form(None),
    competences_comportementales: str = Form(None),
    langues: str = Form(None),
    cv: UploadFile = File(...),
    lettre: UploadFile = File(None),
    diplomes: UploadFile = File(None),
    ref_offre: str = Form(...),  # ✔ VERSION CORRECTE
    db: Session = Depends(get_db)
):
    """
    Enregistrement complet d'une candidature venant du frontend public
    + Liaison automatique avec l'offre
    + Calcul automatique du score
    """

    # --- Fonction de sauvegarde des fichiers ---
    def save_file(upload: UploadFile | None):
        if upload:
            file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{upload.filename}")
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(upload.file, buffer)
            return file_path
        return None

    cv_path = save_file(cv)
    lettre_path = save_file(lettre)
    diplomes_path = save_file(diplomes)

    # --- Vérification existence offre ---
    offre = db.query(Offre).filter(Offre.titre == ref_offre).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")

    # --- Fonction de calcul du score ---
    def calculer_score(offre_competences: str, candidat_competences: str):
        if not offre_competences or not candidat_competences:
            return 0.0
        liste_offre = [c.strip().lower() for c in offre_competences.split(",")]
        liste_candidat = [c.strip().lower() for c in candidat_competences.split(",")]
        similitudes = []
        for comp in liste_offre:
            best_match = difflib.get_close_matches(comp, liste_candidat, n=1, cutoff=0.5)
            if best_match:
                similitudes.append(comp)
        score = (len(similitudes) / len(liste_offre)) * 100 if liste_offre else 0
        return round(score, 2)

    # --- Calcul du score global ---
    score_tech = calculer_score(offre.competences, competences_techniques)
    score_comport = calculer_score(offre.competences, competences_comportementales)
    score_langue = calculer_score(offre.competences, langues)

    score_global = round((score_tech * 0.6) + (score_comport * 0.3) + (score_langue * 0.1), 2)

    # --- Création objet Candidature ---
    new_candidature = Candidature(
        fullname=f"{prenom} {nom}",
        email=email,
        phone=phone,
        source="formulaire",
        raw_cv_s3=cv_path,
        score=score_global,
        statut="En attente",
        ref_offre=ref_offre,          # ✔ NOT NULL: inserted correctly
    )

    db.add(new_candidature)
    db.commit()
    db.refresh(new_candidature)
    return new_candidature


@router.get("/", response_model=list[CandidatureResponse])
def list_candidatures(db: Session = Depends(get_db)):
    candidatures = db.query(Candidature).order_by(Candidature.id.desc()).all()
    return candidatures


# ==========================================================
# 🔹 NOUVEAU : Envoyer convocation
# ==========================================================
@router.post("/{id}/send-invitation", response_model=CandidatureResponse)
def send_invitation(id: int, db: Session = Depends(get_db)):
    """
    Met à jour le statut à 'Convoqué'
    et enregistre la date et heure de convocation
    """
    candidature = db.query(Candidature).filter(Candidature.id == id).first()
    if not candidature:
        raise HTTPException(status_code=404, detail="Candidature non trouvée")

    now = datetime.now()
    candidature.statut = "Convoqué"
    candidature.date_convocation = now.date()
    candidature.heure_convocation = now.time().strftime("%H:%M:%S")

    db.commit()
    db.refresh(candidature)

    return candidature
