import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
from app.routers import candidature_rh, convocation
from app.models.models import Candidature
from app.models.offres import Offre
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy

from app.db import Base, engine
from app.routers import employees, contrats, paie, auth
from app.routers import scoring
from app.routers import offres
from fastapi.staticfiles import StaticFiles

from app.services.upload_service import save_upload_file
from app.routers import rapports  # ✅ nouveau import
from app.routers import notifications
from app.routers import discipline
from app.routers import soldes, export_paie
from app.routers import time_entries, leaves, payroll, absences
from app.routers.pointages import router as pointages_router 
from app.routers import settings_smtp
from app.routers import mail_listener

# ==========================================================
# 🚀 CONFIGURATION GÉNÉRALE
# ==========================================================
app = FastAPI(title="SIIRH Backend - FastAPI", version="1.2")
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # na ["*"] raha dev fotsiny
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database init
Base.metadata.create_all(bind=engine)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Bienvenue sur l’API SIIRH 🎉"}

# ==========================================================
# 📁 INCLUSION ROUTERS
# ==========================================================
app.include_router(employees.router, prefix="/api/employes", tags=["Employés"])
app.include_router(contrats.router, prefix="/api/contrats", tags=["Contrats"])
app.include_router(paie.router)
app.include_router(auth.router, prefix="/auth", tags=["Authentification"])
app.include_router(rapports.router, prefix="/api/rapports", tags=["Rapports RH"]) 
app.include_router(convocation.router) 
app.include_router(candidature_rh.router, prefix="/rh", tags=["Candidatures RH"])
app.include_router(scoring.router)
app.include_router(offres.router, prefix="/api/offres", tags=["Offres"])
app.include_router(notifications.router, prefix="/rh", tags=["Notifications"])
app.include_router(discipline.router)
app.include_router(soldes.router)
app.include_router(export_paie.router)

# 🔹 Nouveaux modules Temps & Absences
app.include_router(absences.router)          # /api/absences
app.include_router(pointages_router)
app.include_router(time_entries.router)      # /api/pointages
app.include_router(leaves.router)          # /api/conges
app.include_router(payroll.router)           # /api/payroll

# 🔹 Ajout du router formulaire public candidatures (MinIO)
from app.routers import candidatures  # ✅ router misy create_candidature
app.include_router(candidatures.router, prefix="/api/candidatures", tags=["Candidatures Public"])

app.mount("/exports", StaticFiles(directory="app/exports"), name="exports")
app.include_router(settings_smtp.router, prefix="/api")
app.include_router(mail_listener.router)

# ==========================================================
# 🧾 FORMULAIRE DE CANDIDATURE
# ==========================================================
@app.post("/api/candidatures")
async def create_candidature(
    ref_offre: str = Form(...),  # ✅ recup ref_offre
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    adresse: Optional[str] = Form(None),
    date_naissance: Optional[str] = Form(None),
    poste: str = Form(...),
    disponibilite: Optional[str] = Form(None),
    salaire: Optional[str] = Form(None),
    type_contrat: Optional[str] = Form(None),
    mobilite: Optional[str] = Form(None),
    autorisation: Optional[str] = Form(None),
    cv: UploadFile = File(...),
    lettre: Optional[UploadFile] = File(None),
    diplomes: Optional[UploadFile] = File(None),
):
    """Enregistre une candidature avec upload de fichiers et offre_id + notification automatique"""
    try:
        def save_file(file: Optional[UploadFile]):
            if file:
                path = UPLOAD_DIR / file.filename
                with path.open("wb") as f:
                    shutil.copyfileobj(file.file, f)
                return str(path)
            return None

        cv_path = save_file(cv)
        lettre_path = save_file(lettre)
        diplomes_path = save_file(diplomes)

        # ✅ Récupérer l'ID de l'offre correspondant à la ref
        with engine.begin() as conn:
            result = conn.execute(
                sqlalchemy.text("SELECT id FROM offres WHERE job_ref = :ref_offre"),
                {"ref_offre": ref_offre}
            ).fetchone()
            if not result:
                raise HTTPException(status_code=400, detail="Référence d'offre invalide")
            offre_id = result.id

        # ✅ Insert candidature avec offre_id
        query = sqlalchemy.text("""
            INSERT INTO candidatures (
                offre_id, nom, prenom, email, phone, adresse, date_naissance, poste,
                disponibilite, salaire, type_contrat, mobilite, autorisation,
                cv_path, lettre_path, diplomes_path, date_candidature, statut, score
            ) VALUES (
                :offre_id, :nom, :prenom, :email, :phone, :adresse, :date_naissance, :poste,
                :disponibilite, :salaire, :type_contrat, :mobilite, :autorisation,
                :cv_path, :lettre_path, :diplomes_path, :date_candidature, :statut, :score
            )
        """)

        with engine.begin() as conn:
            res = conn.execute(query, {
                "offre_id": offre_id,
                "nom": nom,
                "prenom": prenom,
                "email": email,
                "phone": phone,
                "adresse": adresse,
                "date_naissance": date_naissance,
                "poste": poste,
                "disponibilite": disponibilite,
                "salaire": salaire,
                "type_contrat": type_contrat,
                "mobilite": mobilite,
                "autorisation": autorisation,
                "cv_path": cv_path,
                "lettre_path": lettre_path,
                "diplomes_path": diplomes_path,
                "date_candidature": datetime.utcnow(),
                "statut": "En attente",
                "score": 0.0,
            })
            # ✅ Insert automatique notification pour RH
            conn.execute(
                sqlalchemy.text("INSERT INTO notifications (message, read, date) VALUES (:message, false, :date)"),
                {"message": f"Nouveau candidat: {prenom} {nom} pour l'offre {ref_offre}", "date": datetime.utcnow()}
            )

        return {"message": "✅ Candidature envoyée avec succès et notification créée !"}

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# ==========================================================
# 🧩 MODULE ENTRETIEN RH
# ==========================================================
from pydantic import BaseModel

class Entretien(BaseModel):
    job_ref: str
    cand_id: str
    round_type: str
    date: str
    time: str
    evaluators: str
    tech_score: int
    soft_score: int
    cult_score: int
    lang_score: int
    disp_score: int
    sal_score: int
    notes: str
    risks: str
    decision: str
    proposal_type: str
    proposal_salary: str

@app.post("/api/entretiens")
async def enregistrer_entretien(data: Entretien):
    """Enregistrer une fiche d’entretien RH"""
    try:
        query = sqlalchemy.text("""
            INSERT INTO entretiens (
                job_ref, cand_id, round_type, date, time, evaluators,
                tech_score, soft_score, cult_score, lang_score,
                disp_score, sal_score, notes, risks,
                decision, proposal_type, proposal_salary, created_at
            ) VALUES (
                :job_ref, :cand_id, :round_type, :date, :time, :evaluators,
                :tech_score, :soft_score, :cult_score, :lang_score,
                :disp_score, :sal_score, :notes, :risks,
                :decision, :proposal_type, :proposal_salary, :created_at
            )
        """)

        with engine.begin() as conn:
            conn.execute(query, {
                **data.dict(),
                "created_at": datetime.utcnow()
            })

        return {"message": "✅ Entretien enregistré avec succès !"}

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de l’enregistrement: {e}")

@app.get("/api/entretiens")
async def liste_entretiens():
    """Retourne la liste des entretiens enregistrés"""
    try:
        query = sqlalchemy.text("""
            SELECT e.*, c.nom, c.prenom, c.poste
            FROM entretiens e
            LEFT JOIN candidatures c ON c.id = e.cand_id::int
            ORDER BY (
                (tech_score + soft_score + cult_score + lang_score + disp_score + sal_score)/6
            ) DESC
        """)
        with engine.begin() as conn:
            result = conn.execute(query).mappings().all()
        return result
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# ==========================================================
# 🚀 NOUVEAU: ROUTE POST POUR CRÉER UNE OFFRE ET UPLOAD SCORING AUTOMATIQUE
# ==========================================================
from typing import List, Dict

class OffreSchema(BaseModel):
    title: str
    job_ref: str
    department: str
    site: str
    contract_type: str
    creation_date: str
    mission: str
    activities_public: str
    goals: str
    education_level: str
    exp_required_years: int
    tech_skills: List[str]
    soft_skills: List[str]
    langs_lvl: Dict[str, str]
    w_skills: float = 0.4
    w_exp: float = 0.3
    w_edu: float = 0.2
    w_proj: float = 0.1
    threshold: float = 60
    deadline: Optional[str] = None
    apply_link: Optional[str] = None

@app.post("/api/offres")
async def create_offre(data: OffreSchema):
    """Créer une offre et préparer le scoring automatique"""
    try:
        query = sqlalchemy.text("""
            INSERT INTO offres (
                title, job_ref, department, site, contract_type,
                creation_date, mission, activities_public, goals,
                education_level, exp_required_years, tech_skills,
                soft_skills, langs_lvl, w_skills, w_exp, w_edu, w_proj,
                threshold, deadline, apply_link
            ) VALUES (
                :title, :job_ref, :department, :site, :contract_type,
                :creation_date, :mission, :activities_public, :goals,
                :education_level, :exp_required_years, :tech_skills,
                :soft_skills, :langs_lvl, :w_skills, :w_exp, :w_edu, :w_proj,
                :threshold, :deadline, :apply_link
            )
        """)

        with engine.begin() as conn:
            conn.execute(query, {
                "title": data.title,
                "job_ref": data.job_ref,
                "department": data.department,
                "site": data.site,
                "contract_type": data.contract_type,
                "creation_date": data.creation_date,
                "mission": data.mission,
                "activities_public": data.activities_public,
                "goals": data.goals,
                "education_level": data.education_level,
                "exp_required_years": data.exp_required_years,
                "tech_skills": str(data.tech_skills),
                "soft_skills": str(data.soft_skills),
                "langs_lvl": str(data.langs_lvl),
                "w_skills": data.w_skills,
                "w_exp": data.w_exp,
                "w_edu": data.w_edu,
                "w_proj": data.w_proj,
                "threshold": data.threshold,
                "deadline": data.deadline,
                "apply_link": data.apply_link
            })

        return {"message": "✅ Offre créée avec succès !"}

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur création offre : {e}")

@app.get("/api/test")
async def test_connection():
    return {"message": "✅ Backend connecté avec succès !"}
