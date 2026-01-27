# app/routers/offres.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.schemas.offre import OffreCreate, OffreResponse
from app.models.offres import Offre
from app.utils.offre_ref import generate_job_reference
from typing import List

router = APIRouter(tags=["Offres"])

# --- POST: Créer une offre ---
@router.post("", response_model=OffreResponse)
def create_offre(offre_data: OffreCreate, db: Session = Depends(get_db)):

    # Générer la référence
    job_ref = generate_job_reference(db)

    # Créer l'objet Offre
    new_offre = Offre(
        job_ref=job_ref,
        title=offre_data.title,
        department=offre_data.department,
        site=offre_data.site,
        contract_type=offre_data.contract_type,
        creation_date=offre_data.creation_date,
        mission=offre_data.mission,
        activities_public=offre_data.activities_public,
        goals=offre_data.goals,
        education_level=offre_data.education_level,
        exp_required_years=offre_data.exp_required_years,
        w_skills=offre_data.w_skills,
        w_exp=offre_data.w_exp,
        w_edu=offre_data.w_edu,
        w_proj=offre_data.w_proj,
        threshold=offre_data.threshold,
        scoring_config_path=offre_data.scoring_config_path,
        deadline=offre_data.deadline,
        apply_link=offre_data.apply_link
    )

    # Sauvegarder les champs JSON
    new_offre.set_tech_skills(offre_data.tech_skills)
    new_offre.set_soft_skills(offre_data.soft_skills)
    new_offre.set_langs_lvl(offre_data.langs_lvl)

    # 🔹 Définir scoring_criteres par défaut si non fourni
    if not offre_data.scoring_criteres:
        new_offre.scoring_criteres = {
            "competences": ["Python", "SQL", "FastAPI"],
            "experience_min": 3,
            "diplome_requis": "Master Informatique",
            "poids": {"competences": 0.4, "experience": 0.3, "formation": 0.2, "projets": 0.1}
    }
    else:
        new_offre.scoring_criteres = offre_data.scoring_criteres


    # Ajouter à la session et commit
    db.add(new_offre)
    db.commit()
    db.refresh(new_offre)

    return new_offre

# --- GET: Récupérer toutes les offres ---
@router.get("", response_model=List[OffreResponse])
def get_offres(db: Session = Depends(get_db)):
    offres = db.query(Offre).all()
    return offres
