# # backend/app/routers/candidatures.py - VERSION FENO MANDRAKA NY NOTIFICATION
# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
# from sqlalchemy.orm import Session
# from typing import Optional
# from datetime import datetime
# import logging
# import traceback

# from app.db import get_db
# from app.models.models import Candidature
# from app.models.offres import Offre
# from app.services.upload_service import process_cv_from_bytes

# # ✅ Notification
# from app.routers.notifications import add_mail_notification

# logger = logging.getLogger(__name__)

# router = APIRouter(tags=["Candidatures Public"])

# @router.post("/")
# async def create_candidature(
#     ref_offre: str = Form(...),
#     nom: str = Form(...),
#     prenom: str = Form(...),
#     email: str = Form(...),
#     telephone: str = Form(""),
#     poste: Optional[str] = Form(None),
#     cv: UploadFile = File(...),
#     lm: Optional[UploadFile] = File(None),
#     diplomes: Optional[UploadFile] = File(None),
#     db: Session = Depends(get_db)
# ):
#     """
#     Création candidature depuis formulaire
#     + Notification automatique
#     """
#     try:
#         # ==========================================================
#         # 1️⃣ Vérification de l'offre
#         # ==========================================================
#         offre = db.query(Offre).filter(Offre.job_ref == ref_offre).first()
#         if not offre:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Offre avec référence '{ref_offre}' non trouvée"
#             )
#         logger.info(f"✅ Offre trouvée: {offre.title} (ID: {offre.id}, Ref: {offre.job_ref})")

#         # ==========================================================
#         # 2️⃣ Création candidature (originale, sans toucher)
#         # ==========================================================
#         candidature = Candidature(
#             nom=nom.upper(),
#             prenom=prenom,
#             fullname=f"{nom} {prenom}",
#             email=email,
#             telephone=telephone or "",
#             source="formulaire_web",
#             raw_cv_s3=None,
#             score=0,
#             statut="En attente",
#             poste=poste,
#             offre_id=offre.id,
#             ref_offre=offre.job_ref
#         )
#         db.add(candidature)
#         db.commit()
#         db.refresh(candidature)
#         logger.info(f"✅ Candidature créée ID: {candidature.id} pour {email}")

#         # ==========================================================
#         # 3️⃣ Traitement CV
#         # ==========================================================
#         cv_content = await cv.read()
#         upload_result = process_cv_from_bytes(
#             db=db,
#             content=cv_content,
#             filename=cv.filename,
#             candidature_id=candidature.id
#         )

#         if upload_result.get("success"):
#             candidature.raw_cv_s3 = upload_result.get("minio_path")
#             candidature.score = upload_result.get("score", 0)
#             if upload_result.get("nlp_info"):
#                 candidature.parsed_json = upload_result.get("nlp_info")
#             db.commit()
#             logger.info(f"✅ CV traité: {candidature.raw_cv_s3}, Score: {candidature.score}%")
#         else:
#             logger.error(f"❌ Erreur traitement CV: {upload_result.get('error')}")
#             candidature.statut = "CV erreur"
#             db.commit()

#         # ==========================================================
#         # 4️⃣ Fichiers optionnels (lettre + diplômes)
#         # ==========================================================
#         fichiers_traites = []

#         if lm and lm.filename:
#             try:
#                 from app.services.upload_service import minio_service
#                 lettre_content = await lm.read()
#                 lettre_path = minio_service.upload_cv(
#                     file_data=lettre_content,
#                     filename=lm.filename,
#                     offre_ref=offre.job_ref,
#                     candidate_email=email
#                 )
#                 if lettre_path:
#                     candidature.lettre_path = lettre_path
#                     fichiers_traites.append("lettre")
#                     db.commit()
#             except Exception as e:
#                 logger.warning(f"⚠️ Erreur lettre: {e}")

#         if diplomes and diplomes.filename:
#             try:
#                 from app.services.upload_service import minio_service
#                 diplomes_content = await diplomes.read()
#                 diplomes_path = minio_service.upload_cv(
#                     file_data=diplomes_content,
#                     filename=diplomes.filename,
#                     offre_ref=offre.job_ref,
#                     candidate_email=email
#                 )
#                 if diplomes_path:
#                     candidature.diplomes_path = diplomes_path
#                     fichiers_traites.append("diplômes")
#                     db.commit()
#             except Exception as e:
#                 logger.warning(f"⚠️ Erreur diplômes: {e}")

#         # ==========================================================
#         # 5️⃣ Notification automatique
#         # ==========================================================
#         try:
#             add_mail_notification(db_conn=db.connection(), 
#                                   message=f"Nouvelle candidature reçue: {nom} {prenom} pour l'offre {offre.title}")
#             logger.info(f"🔔 Notification ajoutée pour candidature ID {candidature.id}")
#         except Exception:
#             logger.error("❌ Impossible d'ajouter notification", exc_info=True)

#         # ==========================================================
#         # 6️⃣ Retour
#         # ==========================================================
#         return {
#             "success": True,
#             "candidature_id": candidature.id,
#             "nom": candidature.nom,
#             "prenom": candidature.prenom,
#             "email": candidature.email,
#             "offre": ref_offre,
#             "score": candidature.score,
#             "statut": candidature.statut,
#             "cv_path": candidature.raw_cv_s3 or "local",
#             "fichiers_traites": fichiers_traites,
#             "message": "Candidature créée avec succès"
#         }

#     except Exception as e:
#         logger.error(f"❌ Erreur globale: {e}", exc_info=True)
#         if 'candidature' in locals():
#             db.rollback()
#         raise HTTPException(
#             status_code=500,
#             detail=f"Erreur création candidature: {str(e)}"
#         )


# @router.get("/test-minio")
# async def test_minio_connection():
#     from app.services.upload_service import test_minio_connection
#     return test_minio_connection()


# @router.get("/test")
# async def test_endpoint():
#     return {"message": "✅ Router candidatures fonctionne!", "status": "ok"}


# @router.get("/offres-disponibles")
# async def get_offres_disponibles(db: Session = Depends(get_db)):
#     offres = db.query(Offre).filter(Offre.deadline >= datetime.now().date()).all()
#     result = []
#     for offre in offres:
#         result.append({
#             "job_ref": offre.job_ref,
#             "title": offre.title,
#             "department": offre.department,
#             "deadline": offre.deadline.isoformat() if offre.deadline else None
#         })
#     return result














# backend/app/routers/candidatures.py - VERSION FENO (NOTIFICATION AVANT MINIO)
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
import traceback

from app.db import get_db
from app.models.models import Candidature
from app.models.offres import Offre
from app.services.upload_service import process_cv_from_bytes

# ✅ Notification
from app.routers.notifications import add_mail_notification

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Candidatures Public"])


@router.post("/")
async def create_candidature(
    ref_offre: str = Form(...),
    nom: str = Form(...),
    prenom: str = Form(...),
    email: str = Form(...),
    telephone: str = Form(""),
    poste: Optional[str] = Form(None),
    cv: UploadFile = File(...),
    lm: Optional[UploadFile] = File(None),
    diplomes: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Création candidature depuis formulaire
    + Notification automatique
    """
    try:
        # ==========================================================
        # 1️⃣ Vérification de l'offre
        # ==========================================================
        offre = db.query(Offre).filter(Offre.job_ref == ref_offre).first()
        if not offre:
            raise HTTPException(
                status_code=404,
                detail=f"Offre avec référence '{ref_offre}' non trouvée"
            )
        logger.info(f"✅ Offre trouvée: {offre.title} (ID: {offre.id}, Ref: {offre.job_ref})")

        # ==========================================================
        # 2️⃣ Création candidature (originale, sans toucher)
        # ==========================================================
        candidature = Candidature(
            nom=nom.upper(),
            prenom=prenom,
            fullname=f"{nom} {prenom}",
            email=email,
            telephone=telephone or "",
            source="formulaire_web",
            raw_cv_s3=None,
            score=0,
            statut="En attente",
            poste=poste,
            offre_id=offre.id,
            ref_offre=offre.job_ref
        )
        db.add(candidature)
        db.commit()
        db.refresh(candidature)
        logger.info(f"✅ Candidature créée ID: {candidature.id} pour {email}")

        # ==========================================================
        # 3️⃣ Notification automatique (AVANT traitement MinIO)
        # ==========================================================
        try:
            add_mail_notification(
                db=db,
                message=f"Nouvelle candidature reçue: {nom} {prenom} pour l'offre {offre.title}"
            )

            logger.info(f"🔔 Notification ajoutée pour candidature ID {candidature.id}")
        except Exception:
            logger.error("❌ Impossible d'ajouter notification", exc_info=True)

        # ==========================================================
        # 4️⃣ Traitement CV
        # ==========================================================
        cv_content = await cv.read()
        upload_result = process_cv_from_bytes(
            db=db,
            content=cv_content,
            filename=cv.filename,
            candidature_id=candidature.id
        )

        if upload_result.get("success"):
            candidature.raw_cv_s3 = upload_result.get("minio_path")
            candidature.score = upload_result.get("score", 0)
            if upload_result.get("nlp_info"):
                candidature.parsed_json = upload_result.get("nlp_info")
            db.commit()
            logger.info(f"✅ CV traité: {candidature.raw_cv_s3}, Score: {candidature.score}%")
        else:
            logger.error(f"❌ Erreur traitement CV: {upload_result.get('error')}")
            candidature.statut = "CV erreur"
            db.commit()

        # ==========================================================
        # 5️⃣ Fichiers optionnels (lettre + diplômes)
        # ==========================================================
        fichiers_traites = []

        if lm and lm.filename:
            try:
                from app.services.upload_service import minio_service
                lettre_content = await lm.read()
                lettre_path = minio_service.upload_cv(
                    file_data=lettre_content,
                    filename=lm.filename,
                    offre_ref=offre.job_ref,
                    candidate_email=email
                )
                if lettre_path:
                    candidature.lettre_path = lettre_path
                    fichiers_traites.append("lettre")
                    db.commit()
            except Exception as e:
                logger.warning(f"⚠️ Erreur lettre: {e}")

        if diplomes and diplomes.filename:
            try:
                from app.services.upload_service import minio_service
                diplomes_content = await diplomes.read()
                diplomes_path = minio_service.upload_cv(
                    file_data=diplomes_content,
                    filename=diplomes.filename,
                    offre_ref=offre.job_ref,
                    candidate_email=email
                )
                if diplomes_path:
                    candidature.diplomes_path = diplomes_path
                    fichiers_traites.append("diplômes")
                    db.commit()
            except Exception as e:
                logger.warning(f"⚠️ Erreur diplômes: {e}")

        # ==========================================================
        # 6️⃣ Retour
        # ==========================================================
        return {
            "success": True,
            "candidature_id": candidature.id,
            "nom": candidature.nom,
            "prenom": candidature.prenom,
            "email": candidature.email,
            "offre": ref_offre,
            "score": candidature.score,
            "statut": candidature.statut,
            "cv_path": candidature.raw_cv_s3 or "local",
            "fichiers_traites": fichiers_traites,
            "message": "Candidature créée avec succès"
        }

    except Exception as e:
        logger.error(f"❌ Erreur globale: {e}", exc_info=True)
        if 'candidature' in locals():
            db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erreur création candidature: {str(e)}"
        )


@router.get("/test-minio")
async def test_minio_connection():
    from app.services.upload_service import test_minio_connection
    return test_minio_connection()


@router.get("/test")
async def test_endpoint():
    return {"message": "✅ Router candidatures fonctionne!", "status": "ok"}


@router.get("/offres-disponibles")
async def get_offres_disponibles(db: Session = Depends(get_db)):
    offres = db.query(Offre).filter(Offre.deadline >= datetime.now().date()).all()
    result = []
    for offre in offres:
        result.append({
            "job_ref": offre.job_ref,
            "title": offre.title,
            "department": offre.department,
            "deadline": offre.deadline.isoformat() if offre.deadline else None
        })
    return result
