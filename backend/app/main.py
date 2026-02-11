# #app/main.py
# import os
# import shutil
# from pathlib import Path
# from typing import Optional
# from datetime import datetime
# from app.routers import candidature_rh, convocation
# from app.models.models import Candidature
# from fastapi import FastAPI, UploadFile, File, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# import sqlalchemy

# from app.db import Base, engine
# from app.routers import employees, contrats, paie, auth
# from app.routers import scoring
# from app.routers import offres
# from fastapi.staticfiles import StaticFiles

# from app.services.upload_service import save_upload_file
# from app.routers import rapports  # ✅ nouveau import
# from app.routers import notifications
# from app.routers import discipline
# from app.routers import soldes, export_paie
# from app.routers import time_entries, leaves, payroll, absences
# from app.routers.pointages import router as pointages_router 
# from app.routers import settings_smtp
# from app.routers import mail_listener
# from app.routers import candidature_selection,candidature_rh, convocation


# # ==========================================================
# # 🚀 CONFIGURATION GÉNÉRALE
# # ==========================================================
# app = FastAPI(title="SIIRH Backend - FastAPI", version="1.2")
# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
#     "http://localhost:5174",
#     "http://127.0.0.1:5174",
#     "http://localhost:3000",      
#     "http://127.0.0.1:3000",   
    
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,      # na ["*"] raha dev fotsiny
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # Database init
# Base.metadata.create_all(bind=engine)

# UPLOAD_DIR = Path("uploads")
# UPLOAD_DIR.mkdir(exist_ok=True)

# @app.get("/")
# async def root():
#     return {"message": "Bienvenue sur l’API SIIRH 🎉"}


# # ==========================================================
# # 📁 INCLUSION ROUTERS
# # ==========================================================
# app.include_router(employees.router, prefix="/api/employes", tags=["Employés"])
# app.include_router(contrats.router, prefix="/api/contrats", tags=["Contrats"])
# app.include_router(paie.router)
# app.include_router(auth.router, prefix="/auth", tags=["Authentification"])
# app.include_router(rapports.router, prefix="/api/rapports", tags=["Rapports RH"]) 
# app.include_router(convocation.router) 
# app.include_router(candidature_rh.router, prefix="/rh", tags=["Candidatures RH"])
# app.include_router(scoring.router)
# app.include_router(offres.router, prefix="/api/offres", tags=["Offres"])
# app.include_router(notifications.router, prefix="/rh", tags=["Notifications"])
# app.include_router(discipline.router)
# app.include_router(soldes.router)
# app.include_router(export_paie.router)

# # 🔹 Nouveaux modules Temps & Absences
# app.include_router(absences.router)          # /api/absences
# app.include_router(pointages_router)
# app.include_router(time_entries.router)      # /api/pointages
# app.include_router(leaves.router)          # /api/conges
# app.include_router(payroll.router)           # /api/payroll

# # 🔹 Ajout du router formulaire public candidatures (MinIO)
# from app.routers import candidatures  # ✅ router misy create_candidature
# app.include_router(candidatures.router, prefix="/api/candidatures", tags=["Candidatures Public"])

# app.mount("/exports", StaticFiles(directory="app/exports"), name="exports")
# app.include_router(settings_smtp.router, prefix="/api")
# app.include_router(mail_listener.router)
# app.include_router(candidature_selection.router, prefix="/rh/candidatures",  tags=["Candidature Selection"])

# # ✅ Candidatures RH
# app.include_router(candidature_rh.router, prefix="/rh", tags=["Candidatures RH"])
# app.include_router(convocation.router, prefix="/rh/convocations", tags=["Convocations RH"])

# # ==========================================================
# # 🧾 FORMULAIRE DE CANDIDATURE
# # ==========================================================
# @app.post("/api/candidatures")
# async def create_candidature(
#     ref_offre: str = Form(...),
#     nom: str = Form(...),
#     prenom: str = Form(...),
#     email: str = Form(...),
#     phone: Optional[str] = Form(None),
#     adresse: Optional[str] = Form(None),
#     date_naissance: Optional[str] = Form(None),
#     poste: str = Form(...),
#     disponibilite: Optional[str] = Form(None),
#     salaire: Optional[str] = Form(None),
#     type_contrat: Optional[str] = Form(None),
#     mobilite: Optional[str] = Form(None),
#     autorisation: Optional[str] = Form(None),
#     cv: UploadFile = File(...),
#     lettre: Optional[UploadFile] = File(None),
#     diplomes: Optional[UploadFile] = File(None),
# ):
#     """Enregistre une candidature avec upload de fichiers et offre_id + notification automatique"""
#     try:
#         def save_file(file: Optional[UploadFile]):
#             if file:
#                 path = UPLOAD_DIR / file.filename
#                 with path.open("wb") as f:
#                     shutil.copyfileobj(file.file, f)
#                 return str(path)
#             return None

#         cv_path = save_file(cv)
#         lettre_path = save_file(lettre)
#         diplomes_path = save_file(diplomes)

#         # ✅ Récupérer l'ID de l'offre correspondant à la ref
#         with engine.begin() as conn:
#             result = conn.execute(
#                 sqlalchemy.text("SELECT id FROM offres WHERE job_ref = :ref_offre"),
#                 {"ref_offre": ref_offre}
#             ).fetchone()
#             if not result:
#                 raise HTTPException(status_code=400, detail="Référence d'offre invalide")
#             offre_id = result.id

#         # ✅ VERSION CORRIGÉE COMPLÈTE (avec ref_offre)
#         query = sqlalchemy.text("""
#             INSERT INTO candidatures (
#                 offre_id, ref_offre, nom, prenom, fullname, email, phone, adresse, 
#                 date_naissance, poste, disponibilite, salaire, type_contrat, 
#                 mobilite, autorisation, cv_path, lettre_path, diplomes_path, 
#                 date_candidature, statut, score
#             ) VALUES (
#                 :offre_id, :ref_offre, :nom, :prenom, :fullname, :email, :phone, :adresse, 
#                 :date_naissance, :poste, :disponibilite, :salaire, :type_contrat, 
#                 :mobilite, :autorisation, :cv_path, :lettre_path, :diplomes_path, 
#                 :date_candidature, :statut, :score
#             )
#         """)

#         with engine.begin() as conn:
#             res = conn.execute(query, {
#                 "offre_id": offre_id,
#                 "ref_offre": ref_offre,  # ⬅️ TRÈS IMPORTANT!
#                 "nom": nom,
#                 "prenom": prenom,
#                 "fullname": f"{nom} {prenom}",
#                 "email": email,
#                 "phone": phone,
#                 "adresse": adresse,
#                 "date_naissance": date_naissance,
#                 "poste": poste,
#                 "disponibilite": disponibilite,
#                 "salaire": salaire,
#                 "type_contrat": type_contrat,
#                 "mobilite": mobilite,
#                 "autorisation": autorisation,
#                 "cv_path": cv_path,
#                 "lettre_path": lettre_path,
#                 "diplomes_path": diplomes_path,
#                 "date_candidature": datetime.utcnow(),
#                 "statut": "En attente",
#                 "score": 0.0,
#             })
            
#             # ✅ Insert automatique notification pour RH
#             conn.execute(
#                 sqlalchemy.text("INSERT INTO notifications (message, read, date) VALUES (:message, false, :date)"),
#                 {"message": f"Nouveau candidat: {prenom} {nom} pour l'offre {ref_offre}", "date": datetime.utcnow()}
#             )

#         return {"message": "✅ Candidature envoyée avec succès et notification créée !"}

#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")
# #=========================================================
# # Ajouter dans main.py
# @app.post("/api/candidatures/{candidature_id}/selectionner")
# def selectionner_candidature(candidature_id: int):
#     from sqlalchemy import text
    
#     with engine.connect() as conn:
#         try:
#             # 1. Mettre à jour le statut
#             update_query = text("""
#                 UPDATE candidatures 
#                 SET statut = 'Sélectionné',
#                     date_maj = CURRENT_TIMESTAMP
#                 WHERE id = :id
#             """)
#             conn.execute(update_query, {"id": candidature_id})
#             conn.commit()
            
#             # 2. Vérifier la mise à jour
#             check_query = text("SELECT id, fullname, statut FROM candidatures WHERE id = :id")
#             result = conn.execute(check_query, {"id": candidature_id}).fetchone()
            
#             return {
#                 "success": True,
#                 "message": f"Candidature {candidature_id} sélectionnée",
#                 "data": {
#                     "id": result[0],
#                     "nom": result[1],
#                     "statut": result[2]
#                 }
#             }
            
#         except Exception as e:
#             conn.rollback()
#             return {"success": False, "error": str(e)}




# # ==========================================================
# # 🧩 MODULE ENTRETIEN RH
# # ==========================================================
# from pydantic import BaseModel

# class Entretien(BaseModel):
#     job_ref: str
#     cand_id: str
#     round_type: str
#     date: str
#     time: str
#     evaluators: str
#     tech_score: int
#     soft_score: int
#     cult_score: int
#     lang_score: int
#     disp_score: int
#     sal_score: int
#     notes: str
#     risks: str
#     decision: str
#     proposal_type: str
#     proposal_salary: str

# @app.post("/api/entretiens")
# async def enregistrer_entretien(data: Entretien):
#     """Enregistrer une fiche d’entretien RH"""
#     try:
#         query = sqlalchemy.text("""
#             INSERT INTO entretiens (
#                 job_ref, cand_id, round_type, date, time, evaluators,
#                 tech_score, soft_score, cult_score, lang_score,
#                 disp_score, sal_score, notes, risks,
#                 decision, proposal_type, proposal_salary, created_at
#             ) VALUES (
#                 :job_ref, :cand_id, :round_type, :date, :time, :evaluators,
#                 :tech_score, :soft_score, :cult_score, :lang_score,
#                 :disp_score, :sal_score, :notes, :risks,
#                 :decision, :proposal_type, :proposal_salary, :created_at
#             )
#         """)

#         with engine.begin() as conn:
#             conn.execute(query, {
#                 **data.dict(),
#                 "created_at": datetime.utcnow()
#             })

#         return {"message": "✅ Entretien enregistré avec succès !"}

#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur lors de l’enregistrement: {e}")

# @app.get("/api/entretiens")
# async def liste_entretiens():
#     """Retourne la liste des entretiens enregistrés"""
#     try:
#         query = sqlalchemy.text("""
#             SELECT e.*, c.nom, c.prenom, c.poste
#             FROM entretiens e
#             LEFT JOIN candidatures c ON c.id = e.cand_id::int
#             ORDER BY (
#                 (tech_score + soft_score + cult_score + lang_score + disp_score + sal_score)/6
#             ) DESC
#         """)
#         with engine.begin() as conn:
#             result = conn.execute(query).mappings().all()
#         return result
#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# # ==========================================================
# # 🚀 NOUVEAU: ROUTE POST POUR CRÉER UNE OFFRE ET UPLOAD SCORING AUTOMATIQUE
# # ==========================================================
# from typing import List, Dict

# class OffreSchema(BaseModel):
#     title: str
#     job_ref: str
#     department: str
#     site: str
#     contract_type: str
#     creation_date: str
#     mission: str
#     activities_public: str
#     goals: str
#     education_level: str
#     exp_required_years: int
#     tech_skills: List[str]
#     soft_skills: List[str]
#     langs_lvl: Dict[str, str]
#     w_skills: float = 0.4
#     w_exp: float = 0.3
#     w_edu: float = 0.2
#     w_proj: float = 0.1
#     threshold: float = 60
#     deadline: Optional[str] = None
#     apply_link: Optional[str] = None

# @app.post("/api/offres")
# async def create_offre(data: OffreSchema):
#     """Créer une offre et préparer le scoring automatique"""
#     try:
#         query = sqlalchemy.text("""
#             INSERT INTO offres (
#                 title, job_ref, department, site, contract_type,
#                 creation_date, mission, activities_public, goals,
#                 education_level, exp_required_years, tech_skills,
#                 soft_skills, langs_lvl, w_skills, w_exp, w_edu, w_proj,
#                 threshold, deadline, apply_link
#             ) VALUES (
#                 :title, :job_ref, :department, :site, :contract_type,
#                 :creation_date, :mission, :activities_public, :goals,
#                 :education_level, :exp_required_years, :tech_skills,
#                 :soft_skills, :langs_lvl, :w_skills, :w_exp, :w_edu, :w_proj,
#                 :threshold, :deadline, :apply_link
#             )
#         """)

#         with engine.begin() as conn:
#             conn.execute(query, {
#                 "title": data.title,
#                 "job_ref": data.job_ref,
#                 "department": data.department,
#                 "site": data.site,
#                 "contract_type": data.contract_type,
#                 "creation_date": data.creation_date,
#                 "mission": data.mission,
#                 "activities_public": data.activities_public,
#                 "goals": data.goals,
#                 "education_level": data.education_level,
#                 "exp_required_years": data.exp_required_years,
#                 "tech_skills": str(data.tech_skills),
#                 "soft_skills": str(data.soft_skills),
#                 "langs_lvl": str(data.langs_lvl),
#                 "w_skills": data.w_skills,
#                 "w_exp": data.w_exp,
#                 "w_edu": data.w_edu,
#                 "w_proj": data.w_proj,
#                 "threshold": data.threshold,
#                 "deadline": data.deadline,
#                 "apply_link": data.apply_link
#             })

#         return {"message": "✅ Offre créée avec succès !"}

#     except Exception as e:
#         import traceback
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur création offre : {e}")

# @app.get("/api/test")
# async def test_connection():
#     return {"message": "✅ Backend connecté avec succès !"}





# app/main.py - VERSION COMPLÈTE TSY MISY ESORINA
import os
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
from app.routers import candidature_rh, convocation
from app.models.models import Candidature
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import sqlalchemy
from sqlalchemy import text
import logging

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
from app.routers import candidature_selection, candidature_rh, convocation



# ==========================================================
# 🚀 CONFIGURATION GÉNÉRALE
# ==========================================================
app = FastAPI(title="SIIRH Backend - FastAPI", version="1.3")

# Configuration CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:3000",      
    "http://127.0.0.1:3000",   
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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
    return {"message": "Bienvenue sur l'API SIIRH 🎉 - Système Intégré d'Information des Ressources Humaines"}

@app.get("/health")
async def health_check():
    """Endpoint de santé de l'application"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.3"
    }

# Dans main.py, avant app.include_router
import logging
logger = logging.getLogger(__name__)

try:
    from app.routers import candidatures
    logger.info("✅ Module candidatures importé avec succès")
    
    # Vérifier contenu
    logger.info(f"Router candidatures: {dir(candidatures.router)}")
    
    app.include_router(candidatures.router, prefix="/api/candidatures", tags=["Candidatures Public"])
    logger.info("✅ Router candidatures inclus avec succès")
    
except Exception as e:
    logger.error(f"❌ Erreur inclusion router candidatures: {e}", exc_info=True)
    raise


# ==========================================================
# 📁 INCLUSION ROUTERS (TSY NOVAIKY - MANDEHA TSARA)
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
app.include_router(leaves.router)            # /api/conges
app.include_router(payroll.router)           # /api/payroll

# 🔹 Ajout du router formulaire public candidatures (MinIO) - NOUVEAU VERSION
from app.routers import candidatures  # ✅ Import du nouveau router avec MinIO
app.include_router(candidatures.router, prefix="/api/candidatures", tags=["Candidatures Public"])


# Mount static files
app.mount("/exports", StaticFiles(directory="app/exports"), name="exports")

# 🔹 Autres modules
app.include_router(settings_smtp.router, prefix="/api")
app.include_router(mail_listener.router)
app.include_router(candidature_selection.router, prefix="/rh/candidatures",  tags=["Candidature Selection"])

# ✅ Candidatures RH (pour interface interne RH)
app.include_router(candidature_rh.router, prefix="/rh", tags=["Candidatures RH"])
app.include_router(convocation.router, prefix="/rh/convocations", tags=["Convocations RH"])

# ==========================================================
# 🧾 FORMULAIRE DE CANDIDATURE ORIGINAL (MANDEHA TSARA - TSY ESORINA)
# ==========================================================
@app.post("/api/candidatures-old")  # ✅ NOVAIKY: nanova nom ho "candidatures-old" mba tsy conflict
async def create_candidature_old(
    ref_offre: str = Form(...),
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
    """
    ✅ VERSION ORIGINALE: Formulaire candidature upload local (uploads/)
    Mandeha tsara, tsy esorina, nefa atao ho /api/candidatures-old
    """
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

        # ✅ INSERTION dans candidatures
        query = sqlalchemy.text("""
            INSERT INTO candidatures (
                offre_id, ref_offre, nom, prenom, fullname, email, phone, adresse, 
                date_naissance, poste, disponibilite, salaire, type_contrat, 
                mobilite, autorisation, cv_path, lettre_path, diplomes_path, 
                date_candidature, statut, score
            ) VALUES (
                :offre_id, :ref_offre, :nom, :prenom, :fullname, :email, :phone, :adresse, 
                :date_naissance, :poste, :disponibilite, :salaire, :type_contrat, 
                :mobilite, :autorisation, :cv_path, :lettre_path, :diplomes_path, 
                :date_candidature, :statut, :score
            )
        """)

        with engine.begin() as conn:
            res = conn.execute(query, {
                "offre_id": offre_id,
                "ref_offre": ref_offre,
                "nom": nom,
                "prenom": prenom,
                "fullname": f"{nom} {prenom}",
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

        return {
            "message": "✅ Candidature envoyée avec succès et notification créée !",
            "note": "Version originale (upload local)",
            "cv_path": cv_path
        }

    except Exception as e:
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# ==========================================================
# 🔥 NOUVEAU ENDPOINT FORMULAIRE AVEC MINIO (COMPATIBILITÉ)
# ==========================================================
@app.post("/api/candidatures-minio")
async def create_candidature_minio(
    ref_offre: str = Form(...),
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
    """
    ✅ NOUVELLE VERSION: Formulaire candidature avec upload MinIO
    Mi-compatibiliser amin'ny structure original, nefa mankany MinIO
    """
    logger = logging.getLogger(__name__)
    
    try:
        # 1️⃣ Vérifier offre existe
        with engine.connect() as conn:
            result = conn.execute(
                text("SELECT id, title, job_ref FROM offres WHERE job_ref = :ref_offre"),
                {"ref_offre": ref_offre}
            ).fetchone()
            
            if not result:
                raise HTTPException(status_code=404, detail=f"Offre avec référence '{ref_offre}' non trouvée")
            
            offre_id, offre_title, offre_job_ref = result
            logger.info(f"✅ Offre trouvée: {offre_title} (ID: {offre_id})")
        
        # 2️⃣ Créer candidature en base (sans fichiers d'abord)
        fullname = f"{nom} {prenom}"
        date_candidature = datetime.utcnow()
        
        insert_query = text("""
            INSERT INTO candidatures (
                offre_id, ref_offre, nom, prenom, fullname, email, phone, adresse, 
                date_naissance, poste, disponibilite, salaire, type_contrat, 
                mobilite, autorisation, date_candidature, statut, score,
                source
            ) VALUES (
                :offre_id, :ref_offre, :nom, :prenom, :fullname, :email, :phone, :adresse, 
                :date_naissance, :poste, :disponibilite, :salaire, :type_contrat, 
                :mobilite, :autorisation, :date_candidature, :statut, :score,
                :source
            ) RETURNING id
        """)
        
        with engine.begin() as conn:
            # Insert candidature
            result = conn.execute(insert_query, {
                "offre_id": offre_id,
                "ref_offre": ref_offre,
                "nom": nom,
                "prenom": prenom,
                "fullname": fullname,
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
                "date_candidature": date_candidature,
                "statut": "En attente",
                "score": 0.0,
                "source": "formulaire_minio"  # ✅ Fanamarihana source
            })
            
            candidature_id = result.scalar()
            logger.info(f"✅ Candidature créée ID: {candidature_id}")
            
            # Insert notification
            conn.execute(
                text("INSERT INTO notifications (message, read, date) VALUES (:message, false, :date)"),
                {"message": f"Nouveau candidat MinIO: {prenom} {nom} pour {ref_offre}", "date": datetime.utcnow()}
            )
        
        # 3️⃣ Traitement CV avec MinIO via le nouveau service
        try:
            from app.services.upload_service import process_cv_from_bytes
            
            # Lire le fichier CV
            cv_content = await cv.read()
            cv_filename = cv.filename
            
            logger.info(f"📤 Début traitement CV MinIO: {cv_filename} ({len(cv_content)} bytes)")
            
            # 4️⃣ Appeler le service de traitement MinIO
            # Il faut une session DB pour le service
            from app.db import SessionLocal
            db = SessionLocal()
            
            try:
                # Appeler process_cv_from_bytes qui gère:
                # - Upload MinIO
                # - Extraction texte
                # - Parsing NLP
                # - Calcul score
                upload_result = process_cv_from_bytes(
                    db=db,
                    content=cv_content,
                    filename=cv_filename,
                    candidature_id=candidature_id
                )
                
                if upload_result.get("success"):
                    logger.info(f"✅ CV traité MinIO: {upload_result.get('minio_path')}")
                    
                    # Mettre à jour avec le chemin MinIO
                    update_query = text("""
                        UPDATE candidatures 
                        SET raw_cv_s3 = :minio_path,
                            score = :score,
                            cv_path = :minio_path  # ✅ Compatibilité ancien champ
                        WHERE id = :id
                    """)
                    
                    with engine.begin() as conn:
                        conn.execute(update_query, {
                            "minio_path": upload_result.get("minio_path"),
                            "score": upload_result.get("score", 0),
                            "id": candidature_id
                        })
                    
                    cv_final_path = upload_result.get("minio_path")
                    final_score = upload_result.get("score", 0)
                else:
                    logger.error(f"❌ Erreur traitement MinIO: {upload_result.get('error')}")
                    # Fallback: sauvegarder local
                    cv_local_path = str(UPLOAD_DIR / cv_filename)
                    with open(cv_local_path, "wb") as f:
                        f.write(cv_content)
                    
                    cv_final_path = cv_local_path
                    final_score = 0
                    
                    # Mettre à jour avec chemin local
                    with engine.begin() as conn:
                        conn.execute(
                            text("UPDATE candidatures SET cv_path = :path WHERE id = :id"),
                            {"path": cv_local_path, "id": candidature_id}
                        )
            
            finally:
                db.close()
        
        except Exception as cv_error:
            logger.error(f"❌ Erreur traitement CV: {cv_error}")
            # Fallback simple
            cv_local_path = str(UPLOAD_DIR / cv.filename)
            with open(cv_local_path, "wb") as f:
                f.write(await cv.read())
            
            cv_final_path = cv_local_path
            final_score = 0
        
        # 5️⃣ Traitement fichiers optionnels (lettre, diplômes)
        fichiers_optionnels = []
        
        if lettre and lettre.filename:
            try:
                lettre_content = await lettre.read()
                lettre_filename = lettre.filename
                
                # Upload vers MinIO si disponible
                from app.services.upload_service import minio_service
                if minio_service.minio_available:
                    lettre_path = minio_service.upload_cv(
                        file_data=lettre_content,
                        filename=lettre_filename,
                        offre_ref=ref_offre,
                        candidate_email=email
                    )
                    if lettre_path:
                        with engine.begin() as conn:
                            conn.execute(
                                text("UPDATE candidatures SET lettre_path = :path WHERE id = :id"),
                                {"path": lettre_path, "id": candidature_id}
                            )
                        fichiers_optionnels.append(f"lettre: {lettre_path}")
                else:
                    # Fallback local
                    lettre_local = str(UPLOAD_DIR / lettre_filename)
                    with open(lettre_local, "wb") as f:
                        f.write(lettre_content)
                    fichiers_optionnels.append(f"lettre: {lettre_local}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur traitement lettre: {e}")
        
        if diplomes and diplomes.filename:
            try:
                diplomes_content = await diplomes.read()
                diplomes_filename = diplomes.filename
                
                from app.services.upload_service import minio_service
                if minio_service.minio_available:
                    diplomes_path = minio_service.upload_cv(
                        file_data=diplomes_content,
                        filename=diplomes_filename,
                        offre_ref=ref_offre,
                        candidate_email=email
                    )
                    if diplomes_path:
                        with engine.begin() as conn:
                            conn.execute(
                                text("UPDATE candidatures SET diplomes_path = :path WHERE id = :id"),
                                {"path": diplomes_path, "id": candidature_id}
                            )
                        fichiers_optionnels.append(f"diplômes: {diplomes_path}")
                else:
                    diplomes_local = str(UPLOAD_DIR / diplomes_filename)
                    with open(diplomes_local, "wb") as f:
                        f.write(diplomes_content)
                    fichiers_optionnels.append(f"diplômes: {diplomes_local}")
            except Exception as e:
                logger.warning(f"⚠️ Erreur traitement diplômes: {e}")
        
        # 6️⃣ Retour final
        return {
            "success": True,
            "message": "✅ Candidature créée avec succès via MinIO",
            "candidature_id": candidature_id,
            "nom": nom,
            "prenom": prenom,
            "email": email,
            "offre": ref_offre,
            "cv_path": cv_final_path,
            "score": final_score,
            "fichiers_optionnels": fichiers_optionnels if fichiers_optionnels else "Aucun",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur globale candidature MinIO: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Erreur création candidature: {str(e)}")

# ==========================================================
# 🧩 MODULE ENTRETIEN RH (TSY NOVAIKY)
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
    """Enregistrer une fiche d'entretien RH"""
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
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement: {e}")

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
# 🚀 ROUTE POST POUR CRÉER UNE OFFRE (TSY NOVAIKY)
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

# ==========================================================
# 📊 ROUTES UTILITAIRES ET DIAGNOSTIC
# ==========================================================
@app.get("/api/test")
async def test_connection():
    """Test de connexion générale"""
    return {
        "message": "✅ Backend connecté avec succès !",
        "timestamp": datetime.now().isoformat(),
        "endpoints": {
            "formulaire_original": "/api/candidatures-old (upload local)",
            "formulaire_minio": "/api/candidatures-minio (upload MinIO)",
            "formulaire_router": "/api/candidatures/ (router nouveau)",
            "entretiens": "/api/entretiens",
            "offres": "/api/offres",
            "santé": "/health"
        }
    }

@app.get("/api/debug/minio")
async def debug_minio():
    """Debug MinIO connection"""
    from app.services.upload_service import test_minio_connection
    result = test_minio_connection()
    
    # Vérifier aussi la table candidatures
    with engine.connect() as conn:
        candidatures_count = conn.execute(
            text("SELECT COUNT(*) FROM candidatures")
        ).scalar()
        
        candidatures_minio = conn.execute(
            text("SELECT COUNT(*) FROM candidatures WHERE raw_cv_s3 IS NOT NULL")
        ).scalar()
    
    return {
        "minio_status": result,
        "database_stats": {
            "total_candidatures": candidatures_count,
            "candidatures_minio": candidatures_minio,
            "candidatures_local": candidatures_count - candidatures_minio
        },
        "env_variables": {
            "MINIO_ENDPOINT": os.getenv("MINIO_ENDPOINT"),
            "MINIO_BUCKET": os.getenv("MINIO_BUCKET")
        }
    }

# ==========================================================
# 🔄 SELECTION CANDIDATURE (TSY NOVAIKY)
# ==========================================================
@app.post("/api/candidatures/{candidature_id}/selectionner")
def selectionner_candidature(candidature_id: int):
    """Sélectionner une candidature"""
    from sqlalchemy import text
    
    with engine.connect() as conn:
        try:
            # 1. Mettre à jour le statut
            update_query = text("""
                UPDATE candidatures 
                SET statut = 'Sélectionné',
                    date_maj = CURRENT_TIMESTAMP
                WHERE id = :id
            """)
            conn.execute(update_query, {"id": candidature_id})
            conn.commit()
            
            # 2. Vérifier la mise à jour
            check_query = text("SELECT id, fullname, statut FROM candidatures WHERE id = :id")
            result = conn.execute(check_query, {"id": candidature_id}).fetchone()
            
            return {
                "success": True,
                "message": f"Candidature {candidature_id} sélectionnée",
                "data": {
                    "id": result[0],
                    "nom": result[1],
                    "statut": result[2]
                }
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}

# ==========================================================
# 📁 STATIC FILES (TSY NOVAIKY)
# ==========================================================
@app.get("/api/uploads/{filename}")
async def get_uploaded_file(filename: str):
    """Accéder aux fichiers uploadés"""
    file_path = UPLOAD_DIR / filename
    if file_path.exists():
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Fichier non trouvé")

# ==========================================================
# 🎯 ROUTE DE TEST UPLOAD SIMPLE
# ==========================================================
@app.post("/api/test-upload")
async def test_upload_simple(
    file: UploadFile = File(...),
    email: str = Form(...),
    offre_ref: str = Form("TEST")
):
    """Test simple d'upload MinIO"""
    try:
        from app.services.upload_service import minio_service
        
        content = await file.read()
        filename = file.filename
        
        result = minio_service.upload_cv(
            file_data=content,
            filename=filename,
            offre_ref=offre_ref,
            candidate_email=email
        )
        
        return {
            "success": result is not None,
            "minio_path": result,
            "filename": filename,
            "size_bytes": len(content),
            "message": "Test upload MinIO" + (" réussi" if result else " échoué")
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==========================================================
# 🏁 FIN DE FICHIER
# ==========================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")