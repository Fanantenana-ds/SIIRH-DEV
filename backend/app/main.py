#app/main.py
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.db import Base, engine, get_db
from app.models.offres import Offre
from app.models.discipline  import Discipline
from app.models.cv_files import CVFile
from app.models.models import Employee, Paie, Contrat, Utilisateur, Convocation,Absence,Candidature # raha mbola ilaina
from app.routers import employees, contrats, paie, auth, reporting, candidature_rh
from app.routers import convocation, scoring, offres
from app.services.upload_service import save_upload_file

# ==========================================================
# 🚀 CONFIGURATION GÉNÉRALE
# ==========================================================
app = FastAPI(title="SIIRH Backend - FastAPI", version="1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================================
# Database init
# ==========================================================
Base.metadata.create_all(bind=engine)

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# ==========================================================
# ROOT
# ==========================================================
@app.get("/")
async def root():
    return {"message": "Bienvenue sur l’API SIIRH 🎉"}

# ==========================================================
# ROUTERS
# ==========================================================
app.include_router(employees.router, prefix="/api/employes", tags=["Employés"])
app.include_router(contrats.router, prefix="/api/contrats", tags=["Contrats"])
app.include_router(paie.router, prefix="/api/paie", tags=["Paie"])
app.include_router(auth.router, prefix="/auth", tags=["Authentification"])
app.include_router(reporting.router, prefix="/api/rapports", tags=["Rapports RH"])
app.include_router(convocation.router)
app.include_router(candidature_rh.router, prefix="/rh", tags=["Candidatures RH"])
app.include_router(scoring.router)
app.include_router(offres.router, prefix="/api/offres", tags=["Offres"])

# ==========================================================
# 🧾 FORMULAIRE DE CANDIDATURE (ORM)
# ==========================================================
@app.post("/api/candidatures")
async def create_candidature(
    fullname: str = Form(...),
    email: str = Form(...),
    phone: Optional[str] = Form(None),
    raw_cv: UploadFile = File(...),
    offre_id: int = Form(...),
    db: Session = Depends(get_db),
):
    """Créer une candidature via ORM et uploader CV"""
    try:
        # Sauvegarde fichier CV
        cv_path = None
        if raw_cv:
            cv_path = UPLOAD_DIR / raw_cv.filename
            with cv_path.open("wb") as f:
                shutil.copyfileobj(raw_cv.file, f)
            cv_path = str(cv_path)

        candidature = Candidature(
            fullname=fullname,
            email=email,
            phone=phone,
            raw_cv_s3=cv_path,
            date_candidature=datetime.utcnow(),
            statut="nouveau",
            score=0.0,
            offre_id=offre_id
        )
        db.add(candidature)
        db.commit()
        db.refresh(candidature)
        return {"message": "✅ Candidature créée avec succès !", "id": candidature.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================
# 🚀 ROUTE POST POUR CRÉER UNE OFFRE (ORM)
# ==========================================================
from pydantic import BaseModel

class OffreSchema(BaseModel):
    title: str
    job_ref: str
    department: str
    site: str
    contract_type: str
    creation_date: Optional[str] = None
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
async def create_offre(data: OffreSchema, db: Session = Depends(get_db)):
    """Créer une offre via ORM"""
    try:
        creation_date_obj = datetime.utcnow()
        if data.creation_date:
            try:
                creation_date_obj = datetime.strptime(data.creation_date, "%Y-%m-%d")
            except:
                pass

        offre = Offre(
            title=data.title,
            job_ref=data.job_ref,
            department=data.department,
            site=data.site,
            contract_type=data.contract_type,
            creation_date=creation_date_obj,
            mission=data.mission,
            activities_public=data.activities_public,
            goals=data.goals,
            education_level=data.education_level,
            exp_required_years=data.exp_required_years,
            tech_skills=data.tech_skills,
            soft_skills=data.soft_skills,
            langs_lvl=data.langs_lvl,
            w_skills=data.w_skills,
            w_exp=data.w_exp,
            w_edu=data.w_edu,
            w_proj=data.w_proj,
            threshold=data.threshold,
            deadline=data.deadline,
            apply_link=data.apply_link
        )
        db.add(offre)
        db.commit()
        db.refresh(offre)
        return {"message": "✅ Offre créée avec succès !", "id": offre.id}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================
# 🧩 ENTretien RH (ORM)
# ==========================================================
class EntretienSchema(BaseModel):
    candidature_id: int
    job_ref: str
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
async def create_entretien(data: EntretienSchema, db: Session = Depends(get_db)):
    """Enregistrer un entretien (ajout futur dans table Entretien si exist)"""
    try:
        # TODO: Créer model Entretien raha ilaina
        return {"message": "✅ Entretien enregistré (simulation)"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================================
# TEST
# ==========================================================
@app.get("/api/test")
async def test_connection():
    return {"message": "✅ Backend connecté avec succès !"}





from app.routers import discipline
