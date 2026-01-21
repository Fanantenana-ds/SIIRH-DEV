# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# from sqlalchemy.orm import Session
# from datetime import datetime
# import shutil
# import os
# import difflib

# from app.db import get_db
# from app.models.models import Candidature, Offre
# from app.schemas.candidatures import CandidatureResponse

# router = APIRouter(prefix="/api/candidatures", tags=["Candidatures"])

# UPLOAD_DIR = "uploads"
# os.makedirs(UPLOAD_DIR, exist_ok=True)


# @router.post("/", response_model=CandidatureResponse)
# def create_candidature(
#     nom: str = Form(...),
#     prenom: str = Form(...),
#     email: str = Form(...),
#     phone: str = Form(None),
#     adresse: str = Form(None),
#     date_naissance: str = Form(None),
#     poste: str = Form(...),
#     disponibilite: str = Form(None),
#     salaire: str = Form(None),
#     type_contrat: str = Form(None),
#     mobilite: str = Form(None),
#     autorisation: str = Form(None),
#     offre_reference: str = Form(...),  # référence de l'offre 
#     competences_techniques: str = Form(None),
#     competences_comportementales: str = Form(None),
#     langues: str = Form(None),
#     cv: UploadFile = File(...),
#     lettre: UploadFile = File(None),
#     diplomes: UploadFile = File(None),
#     db: Session = Depends(get_db)
# ):
#     """
#     Enregistrement complet d'une candidature venant du frontend public
#     + Liaison automatique avec l'offre
#     + Calcul automatique du score
#     """

#     # --- Fonction de sauvegarde des fichiers ---
#     def save_file(upload: UploadFile | None):
#         if upload:
#             file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().timestamp()}_{upload.filename}")
#             with open(file_path, "wb") as buffer:
#                 shutil.copyfileobj(upload.file, buffer)
#             return file_path
#         return None

#     cv_path = save_file(cv)
#     lettre_path = save_file(lettre)
#     diplomes_path = save_file(diplomes)

#     # --- Vérification existence offre ---
#     offre = db.query(Offre).filter(Offre.titre == offre_reference).first()
#     if not offre:
#         raise HTTPException(status_code=404, detail="Offre non trouvée")

#     # --- Fonction de calcul du score ---
#     def calculer_score(offre_competences: str, candidat_competences: str):
#         if not offre_competences or not candidat_competences:
#             return 0.0
#         liste_offre = [c.strip().lower() for c in offre_competences.split(",")]
#         liste_candidat = [c.strip().lower() for c in candidat_competences.split(",")]
#         similitudes = []
#         for comp in liste_offre:
#             best_match = difflib.get_close_matches(comp, liste_candidat, n=1, cutoff=0.5)
#             if best_match:
#                 similitudes.append(comp)
#         score = (len(similitudes) / len(liste_offre)) * 100 if liste_offre else 0
#         return round(score, 2)

#     # --- Calcul du score global ---
#     score_tech = calculer_score(offre.competences, competences_techniques)
#     score_comport = calculer_score(offre.competences, competences_comportementales)
#     score_langue = calculer_score(offre.competences, langues)

#     score_global = round((score_tech * 0.6) + (score_comport * 0.3) + (score_langue * 0.1), 2)

#     # --- Création objet Candidature ---
#     new_candidature = Candidature(
#         fullname=f"{prenom} {nom}",
#         email=email,
#         phone=phone,
#         source="formulaire",
#         raw_cv_s3=cv_path,
#         score=score_global,
#         statut="En attente",
#         offre_id=offre.id,
#     )

#     db.add(new_candidature)
#     db.commit()
#     db.refresh(new_candidature)
#     return new_candidature


# @router.get("/", response_model=list[CandidatureResponse])
# def list_candidatures(db: Session = Depends(get_db)):
#     candidatures = db.query(Candidature).order_by(Candidature.id.desc()).all()
#     return candidatures













# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# from sqlalchemy.orm import Session
# import difflib

# from app.db import get_db
# from app.models.models import Candidature, Offre
# from app.schemas.candidatures import CandidatureResponse

# # 🔧 MinIO upload service (mitovy amin’ny mail)
# from app.services.upload_service import upload_files_to_minio

# router = APIRouter(prefix="/api/candidatures", tags=["Candidatures"])


# @router.post("/", response_model=CandidatureResponse)
# def create_candidature(
#     nom: str = Form(...),
#     prenom: str = Form(...),
#     email: str = Form(...),
#     phone: str = Form(None),
#     adresse: str = Form(None),
#     date_naissance: str = Form(None),
#     poste: str = Form(...),
#     disponibilite: str = Form(None),
#     salaire: str = Form(None),
#     type_contrat: str = Form(None),
#     mobilite: str = Form(None),
#     autorisation: str = Form(None),
#     offre_reference: str = Form(...),
#     competences_techniques: str = Form(None),
#     competences_comportementales: str = Form(None),
#     langues: str = Form(None),
#     cv: UploadFile = File(...),
#     lettre: UploadFile = File(None),
#     diplomes: UploadFile = File(None),
#     db: Session = Depends(get_db)
# ):
#     """
#     Enregistrement candidature depuis formulaire public
#     - Liaison offre
#     - Calcul score
#     - Upload fichiers vers MinIO (même logique que mail)
#     """

#     # ==================================================
#     # Vérification existence offre (INCHANGÉ)
#     # ==================================================
#     offre = db.query(Offre).filter(Offre.titre == offre_reference).first()
#     if not offre:
#         raise HTTPException(status_code=404, detail="Offre non trouvée")

#     # ==================================================
#     # Fonction calcul score (INCHANGÉ)
#     # ==================================================
#     def calculer_score(offre_competences: str, candidat_competences: str):
#         if not offre_competences or not candidat_competences:
#             return 0.0

#         liste_offre = [c.strip().lower() for c in offre_competences.split(",")]
#         liste_candidat = [c.strip().lower() for c in candidat_competences.split(",")]

#         similitudes = []
#         for comp in liste_offre:
#             best_match = difflib.get_close_matches(
#                 comp, liste_candidat, n=1, cutoff=0.5
#             )
#             if best_match:
#                 similitudes.append(comp)

#         score = (len(similitudes) / len(liste_offre)) * 100 if liste_offre else 0
#         return round(score, 2)

#     # ==================================================
#     # Calcul score global (INCHANGÉ)
#     # ==================================================
#     score_tech = calculer_score(offre.competences, competences_techniques)
#     score_comport = calculer_score(offre.competences, competences_comportementales)
#     score_langue = calculer_score(offre.competences, langues)

#     score_global = round(
#         (score_tech * 0.6)
#         + (score_comport * 0.3)
#         + (score_langue * 0.1),
#         2
#     )

#     # ==================================================
#     # Création candidature (INCHANGÉ logique)
#     # ==================================================
#     new_candidature = Candidature(
#         fullname=f"{prenom} {nom}",
#         email=email,
#         phone=phone,
#         source="formulaire",
#         raw_cv_s3=None,   # rempli par upload_service
#         score=score_global,
#         statut="En attente",
#         offre_id=offre.id,
#     )

#     db.add(new_candidature)
#     db.commit()
#     db.refresh(new_candidature)

#     # ==================================================
#     # Upload fichiers vers MinIO (UNIFIÉ – PAS DE DOUBLON)
#     # ==================================================
#     files_to_upload = [cv, lettre, diplomes]

#     # Antsoina ny service MinIO
#     upload_results = upload_files_to_minio(
#         db=db,
#         candidature_id=new_candidature.id,
#         files=files_to_upload
#     )

#     # Raha tianao dia afaka manavao raw_cv_s3 amin'ny CV voalohany
#     if upload_results and "cv" in upload_results:
#         new_candidature.raw_cv_s3 = upload_results["cv"]
#         db.commit()
#         db.refresh(new_candidature)

#     return new_candidature


# @router.get("/", response_model=list[CandidatureResponse])
# def list_candidatures(db: Session = Depends(get_db)):
#     return db.query(Candidature).order_by(Candidature.id.desc()).all()











from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import difflib

from app.db import get_db
from app.models.models import Candidature
from app.models.offres import Offre
from app.schemas.candidatures import CandidatureResponse

# 🔧 MinIO upload service
from app.services.upload_service import upload_files_to_minio

router = APIRouter(prefix="/api/candidatures", tags=["Candidatures"])


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
    offre_reference: str = Form(...),
    competences_techniques: str = Form(None),
    competences_comportementales: str = Form(None),
    langues: str = Form(None),
    cv: UploadFile = File(...),
    lettre: UploadFile = File(None),
    diplomes: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """
    Endpoint formulaire public + upload fichiers MinIO (debug-safe)
    """

    print("===== CREATE CANDIDATURE DEBUG =====")
    print(f"Nom: {nom}, Prénom: {prenom}, Email: {email}")
    print(f"Fichiers reçus: CV={cv.filename if cv else None}, Lettre={lettre.filename if lettre else None}, Diplomes={diplomes.filename if diplomes else None}")

    # ==================================================
    # Vérification existence offre
    # ==================================================
    offre = db.query(Offre).filter(Offre.titre == offre_reference).first()
    if not offre:
        raise HTTPException(status_code=404, detail="Offre non trouvée")
    print(f"Offre trouvée: {offre.titre}")

    # ==================================================
    # Calcul score (inchangé)
    # ==================================================
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

    score_tech = calculer_score(offre.competences, competences_techniques)
    score_comport = calculer_score(offre.competences, competences_comportementales)
    score_langue = calculer_score(offre.competences, langues)
    score_global = round((score_tech*0.6 + score_comport*0.3 + score_langue*0.1), 2)
    print(f"Scores calculés: Tech={score_tech}, Comport={score_comport}, Langue={score_langue}, Global={score_global}")

    # ==================================================
    # Création candidature
    # ==================================================
    new_candidature = Candidature(
        fullname=f"{prenom} {nom}",
        email=email,
        phone=phone,
        source="formulaire",
        raw_cv_s3=None,
        score=score_global,
        statut="En attente",
        offre_id=offre.id,
    )

    db.add(new_candidature)
    db.commit()
    db.refresh(new_candidature)
    print(f"Candidature créée avec ID: {new_candidature.id}")

    # ==================================================
    # Upload fichiers vers MinIO (debug-safe)
    # ==================================================
    files_to_upload = [cv, lettre, diplomes]
    print("Début upload fichiers vers MinIO...")
    print("📤 UPLOAD APPELE")
    upload_results = upload_files_to_minio(db, new_candidature.id, files_to_upload)
    print("Upload terminé, résultats:", upload_results)

    # Si CV uploadé, mettre à jour raw_cv_s3
    if upload_results and "cv" in upload_results:
        new_candidature.raw_cv_s3 = upload_results["cv"]
        db.commit()
        db.refresh(new_candidature)
        print("raw_cv_s3 mis à jour avec URL CV MinIO.")

    print("===== FIN CREATE CANDIDATURE DEBUG =====")
    return new_candidature


