# app/services/upload_service.py

import os
from datetime import datetime
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.models.cv_files import CVFile
from app.models.models import Candidature
from app.models.offres import Offre
from app.services.parsing import parse_docx, parse_pdf, extract_info
from app.services.scoring_auto import calculer_score_auto

UPLOAD_DIR = "uploads"

def save_upload_file(db: Session, file: UploadFile, candidature_id: int) -> CVFile:
    """
    Enregistre le fichier uploadé, parse le contenu et calcule le score automatique.
    """
    # --- 1️⃣ Dossier upload ---
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # --- 2️⃣ Enregistrement du fichier ---
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # --- 3️⃣ Création objet CVFile ---
    db_file = CVFile(
        filename=file.filename,
        path=file_path,
        mimetype=file.content_type,
        size=os.path.getsize(file_path),
        uploaded_at=datetime.utcnow()
    )
    db.add(db_file)
    db.commit()
    db.refresh(db_file)

    # --- 4️⃣ Parsing automatique du CV ---
    if file.filename.lower().endswith(".pdf"):
        text = parse_pdf(file_path)
    elif file.filename.lower().endswith(".docx"):
        text = parse_docx(file_path)
    else:
        text = ""

    # --- 5️⃣ Récupération candidature et offre associée ---
    candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
    if not candidature:
        raise Exception("Candidature introuvable.")

    offre = db.query(Offre).filter(Offre.id == candidature.offre_id).first()
    if not offre:
        raise Exception("Offre associée introuvable.")

    # --- 6️⃣ Définir mots-clés projets pour extraire du CV ---
    project_keywords = []
    if offre.mission:
        project_keywords += [w.strip() for w in offre.mission.split() if len(w) > 2]
    if offre.goals:
        project_keywords += [w.strip() for w in offre.goals.split() if len(w) > 2]
    if offre.activities_public:
        project_keywords += [w.strip() for w in offre.activities_public.split() if len(w) > 2]

    # --- 7️⃣ Extraction des infos du CV ---
    parsed = extract_info(text, project_keywords=project_keywords)

    # --- 8️⃣ Préparer l'offre sous forme de dict pour scoring_auto.py ---
    offre_dict = {
        "tech_skills": offre.tech_skills or [],
        "soft_skills": offre.soft_skills or [],
        "langs_lvl": offre.langs_lvl or {},
        "education_level": offre.education_level or "",
        "exp_required_years": offre.exp_required_years or 0,
        "mission": offre.mission or "",
        "activities_public": offre.activities_public or "",
        "goals": offre.goals or "",
        "w_skills": offre.w_skills or 0.4,
        "w_exp": offre.w_exp or 0.3,
        "w_edu": offre.w_edu or 0.2,
        "w_proj": offre.w_proj or 0.1,
        "threshold": offre.threshold or 60
    }

    # --- 9️⃣ Calcul du score automatique ---
    result = calculer_score_auto(cv_text=text, offre=offre_dict, projets_keywords=parsed.get("projects", []))
    score = result["score"]

    # --- 🔟 Mise à jour de la candidature ---
    candidature.raw_cv_s3 = text[:3000]
    candidature.parsed_json = parsed
    candidature.score = score
    candidature.statut = "Analysé"
    db.commit()
    db.refresh(candidature)

    print(f"✅ Candidature {candidature.fullname} analysée automatiquement : {score}/100")

    return db_file
