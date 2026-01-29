# import os
# from fastapi import UploadFile
# from sqlalchemy.orm import Session
# from app.services.parsing import extract_info
# from app.services.scoring_auto import calculer_score_auto
# from minio import Minio
# from minio.error import S3Error
# from io import BytesIO

# # ==========================================================
# # 🔹 Configuration MinIO
# # ==========================================================
# MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000")
# MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "jeremi")
# MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "Jeremi123")
# MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cvs")

# minio_client = Minio(
#     MINIO_ENDPOINT,
#     access_key=MINIO_ACCESS_KEY,
#     secret_key=MINIO_SECRET_KEY,
#     secure=False
# )

# if not minio_client.bucket_exists(MINIO_BUCKET):
#     minio_client.make_bucket(MINIO_BUCKET)
#     print(f"🔹 Bucket MinIO créé: {MINIO_BUCKET}")
# else:
#     print(f"🔹 Bucket MinIO existe déjà: {MINIO_BUCKET}")

# # ==========================================================
# # 🔹 Fonction principale: save_upload_file avec scoring + DB update
# # ==========================================================
# def save_upload_file(db: Session, file: UploadFile, candidature_id: int, offre: dict = None) -> dict:
#     """
#     Sauvegarde le fichier sur MinIO, parse le CV, extrait les infos,
#     calcule automatiquement le score si offre fournie,
#     et met à jour raw_cv_s3 dans la DB.
#     """
#     filename = file.filename
#     content = file.file.read()
#     file.file.seek(0)

#     print(f"📤 Upload fichier: {filename} ({len(content)} bytes)")

#     # ---- Upload sur MinIO ----
#     try:
#         minio_client.put_object(
#             bucket_name=MINIO_BUCKET,
#             object_name=filename,
#             data=file.file,
#             length=len(content),
#             part_size=10 * 1024 * 1024,
#             content_type=file.content_type
#         )
#         print(f"✅ Fichier envoyé sur MinIO: {MINIO_BUCKET}/{filename}")
#     except S3Error as e:
#         print(f"❌ Erreur MinIO pour {filename}: {str(e)}")
#         raise Exception(f"Erreur MinIO: {str(e)}")

#     # ---- Mettre à jour raw_cv_s3 dans la DB ----
#     s3_path = f"{MINIO_BUCKET}/{filename}"
#     try:
#         db.execute(
#             "UPDATE candidatures SET raw_cv_s3=:s3path WHERE id=:id",
#             {"s3path": s3_path, "id": candidature_id}
#         )
#         db.commit()
#         print(f"✅ DB raw_cv_s3 mise à jour pour candidature_id={candidature_id}")
#     except Exception as e:
#         print(f"❌ Erreur DB update raw_cv_s3: {e}")

#     # ---- Parse le fichier ----
#     text = ""
#     if filename.lower().endswith(".pdf"):
#         from app.services.parsing import parse_pdf
#         text = parse_pdf(BytesIO(content))
#     elif filename.lower().endswith(".docx"):
#         from app.services.parsing import parse_docx
#         text = parse_docx(BytesIO(content))
#     print(f"✏️  Texte extrait: {len(text)} caractères")

#     # ---- Extract info ----
#     info = {}
#     if text:
#         info = extract_info(text)
#         print(f"📝 Infos extraites: {info}")

#     # ---- Calcul automatique du score ----
#     score_result = {"score": 0, "passed_threshold": False}
#     if text and offre:
#         score_result = calculer_score_auto(text, offre)
#         print(f"⚡ Score calculé: {score_result}")

#     return {
#         "filename": filename,
#         "filepath": s3_path,
#         "text_preview": text[:1000],
#         "firstname": info.get("firstname"),
#         "lastname": info.get("lastname"),
#         "score": score_result["score"],
#         "passed_threshold": score_result["passed_threshold"]
#     }

# # ==========================================================
# # 🔹 Fonction fanampiny: process_cv_from_bytes
# # ==========================================================
# def process_cv_from_bytes(db: Session, file_bytes: bytes, filename: str, candidature_id: int, offre: dict = None) -> dict:
#     fake_file = UploadFile(filename=filename, file=BytesIO(file_bytes))
#     return save_upload_file(db, fake_file, candidature_id, offre)

# # ==========================================================
# # 🔹 Alias ho an'ny formulaire
# # ==========================================================
# def save_formulaire_files(db: Session, files_list: list[UploadFile], candidature_id: int, offre: dict = None) -> list[dict]:
#     results = []
#     for file in files_list:
#         if file:
#             res = save_upload_file(db, file, candidature_id, offre)
#             results.append(res)
#             print(f"📌 Upload formulaire: {res['filename']} → {res['filepath']}")
#         else:
#             results.append(None)
#     return results

# # Alias ho an'ny import externe
# upload_files_to_minio = save_formulaire_files

# # ==========================================================
# # 🔹 Suppression fichier MinIO
# # ==========================================================
# def delete_file(filename: str):
#     try:
#         if minio_client.bucket_exists(MINIO_BUCKET):
#             minio_client.remove_object(MINIO_BUCKET, filename)
#             print(f"🗑️ Fichier supprimé: {filename}")
#     except S3Error as e:
#         print(f"❌ Erreur suppression MinIO: {str(e)}")
#         raise Exception(f"Erreur MinIO: {str(e)}")




















import os
from io import BytesIO
from typing import List, Optional

from fastapi import UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text

from minio import Minio
from minio.error import S3Error

from app.services.parsing import extract_info
from app.services.scoring_auto import calculer_score_auto

# ==========================================================
# 🔹 Configuration MinIO
# ==========================================================
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "jeremi")
MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "Jeremi123")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cvs")

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)
    print(f"🔹 Bucket MinIO créé: {MINIO_BUCKET}")
else:
    print(f"🔹 Bucket MinIO existe déjà: {MINIO_BUCKET}")

# ==========================================================
# 🔹 Fonction principale
# ==========================================================
def save_upload_file(
    db: Session,
    file: UploadFile,
    candidature_id: int,
    offre: Optional[dict] = None,
    is_cv: bool = True
) -> dict:
    """
    - Upload fichier vers MinIO
    - Enregistre le chemin dans raw_cv_s3 (UNIQUEMENT pour le CV)
    - Parse le CV
    - Extrait les infos
    - Calcule le score automatiquement
    """

    if not file:
        raise ValueError("Aucun fichier fourni")

    filename = file.filename
    content = file.file.read()
    file.file.seek(0)

    print(f"📤 Upload fichier: {filename} ({len(content)} bytes)")

    # ======================================================
    # 🔹 Chemin MinIO UNIQUE par candidature
    # ======================================================
    object_name = f"cv/{candidature_id}/{filename}"

    # ======================================================
    # 🔹 Upload MinIO (BytesIO obligatoire)
    # ======================================================
    try:
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=object_name,
            data=BytesIO(content),
            length=len(content),
            content_type=file.content_type
        )
        print(f"✅ MinIO OK: {MINIO_BUCKET}/{object_name}")
    except S3Error as e:
        print(f"❌ Erreur MinIO: {e}")
        raise Exception("Erreur upload MinIO")

    # ======================================================
    # 🔹 Update DB raw_cv_s3 (CV SEULEMENT)
    # ======================================================
    if is_cv:
        try:
            db.execute(
                text("""
                    UPDATE candidatures
                    SET raw_cv_s3 = :path
                    WHERE id = :id
                """),
                {
                    "path": object_name,
                    "id": candidature_id
                }
            )
            db.commit()
            print(f"✅ DB raw_cv_s3 mis à jour (ID={candidature_id})")
        except Exception as e:
            db.rollback()
            print(f"❌ Erreur DB raw_cv_s3: {e}")

    # ======================================================
    # 🔹 Parsing du fichier
    # ======================================================
    text_content = ""

    try:
        if filename.lower().endswith(".pdf"):
            from app.services.parsing import parse_pdf
            text_content = parse_pdf(BytesIO(content))
        elif filename.lower().endswith(".docx"):
            from app.services.parsing import parse_docx
            text_content = parse_docx(BytesIO(content))
    except Exception as e:
        print(f"❌ Erreur parsing fichier: {e}")

    print(f"✏️ Texte extrait: {len(text_content)} caractères")

    # ======================================================
    # 🔹 Extraction d'informations
    # ======================================================
    info = {}
    if text_content:
        try:
            info = extract_info(text_content)
        except Exception as e:
            print(f"❌ Erreur extract_info: {e}")

    # ======================================================
    # 🔹 Calcul automatique du score
    # ======================================================
    score_result = {"score": 0, "passed_threshold": False}

    if text_content and offre:
        try:
            score_result = calculer_score_auto(text_content, offre)
        except Exception as e:
            print(f"❌ Erreur scoring: {e}")

    return {
        "filename": filename,
        "object_name": object_name,
        "text_preview": text_content[:1000],
        "firstname": info.get("firstname"),
        "lastname": info.get("lastname"),
        "score": score_result["score"],
        "passed_threshold": score_result["passed_threshold"]
    }

# ==========================================================
# 🔹 Traitement depuis bytes (mail)
# ==========================================================
def process_cv_from_bytes(
    db: Session,
    file_bytes: bytes,
    filename: str,
    candidature_id: int,
    offre: Optional[dict] = None
) -> dict:
    fake_file = UploadFile(
        filename=filename,
        file=BytesIO(file_bytes)
    )
    return save_upload_file(
        db=db,
        file=fake_file,
        candidature_id=candidature_id,
        offre=offre,
        is_cv=True
    )

# ==========================================================
# 🔹 Formulaire (CV + autres fichiers)
# ==========================================================
def save_formulaire_files(
    db: Session,
    cv: Optional[UploadFile],
    lm: Optional[UploadFile],
    diplomes: Optional[UploadFile],
    candidature_id: int,
    offre: Optional[dict] = None
) -> dict:
    results = {}

    if cv:
        results["cv"] = save_upload_file(
            db=db,
            file=cv,
            candidature_id=candidature_id,
            offre=offre,
            is_cv=True
        )

    if lm:
        results["lm"] = save_upload_file(
            db=db,
            file=lm,
            candidature_id=candidature_id,
            offre=None,
            is_cv=False
        )

    if diplomes:
        results["diplomes"] = save_upload_file(
            db=db,
            file=diplomes,
            candidature_id=candidature_id,
            offre=None,
            is_cv=False
        )

    return results

# Alias rétro-compatibilité
upload_files_to_minio = save_formulaire_files

# ==========================================================
# 🔹 Suppression fichier MinIO
# ==========================================================
def delete_file(object_name: str):
    try:
        if minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.remove_object(MINIO_BUCKET, object_name)
            print(f"🗑️ Fichier supprimé: {object_name}")
    except S3Error as e:
        print(f"❌ Erreur suppression MinIO: {e}")
        raise Exception("Erreur suppression MinIO")
