# import os
# from fastapi import UploadFile
# from sqlalchemy.orm import Session
# from app.services.parsing import extract_info
# from minio import Minio
# from minio.error import S3Error
# from io import BytesIO

# # --- Configuration MinIO ---
# MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "127.0.0.1:9000")
# MINIO_ACCESS_KEY = os.getenv("MINIO_ROOT_USER", "jeremi")
# MINIO_SECRET_KEY = os.getenv("MINIO_ROOT_PASSWORD", "Jeremi123")
# MINIO_BUCKET = os.getenv("MINIO_BUCKET", "cvs")

# minio_client = Minio(
#     MINIO_ENDPOINT,
#     access_key=MINIO_ACCESS_KEY,
#     secret_key=MINIO_SECRET_KEY,
#     secure=False  # HTTP
# )

# if not minio_client.bucket_exists(MINIO_BUCKET):
#     minio_client.make_bucket(MINIO_BUCKET)


# # --- Fonction principale: save_upload_file ---
# def save_upload_file(db: Session, file: UploadFile, candidature_id: int) -> dict:
#     """
#     Mandefa fichier CV any amin'ny MinIO sy mitahiry info ao amin'ny database.
#     """
#     filename = file.filename


#     file_bytes = file.file.read()
#     file.file.seek(0)  
#     file_obj = BytesIO(file_bytes)

#     try:
#         minio_client.put_object(
#             MINIO_BUCKET,
#             filename,
#             data=file_obj,
#             length=len(file_bytes),
#             content_type=file.content_type or "application/octet-stream"
#         )
#     except S3Error as e:
#         raise Exception(f"Erreur MinIO: {str(e)}")

#     text = ""
#     if filename.lower().endswith(".pdf"):
#         from app.services.parsing import parse_pdf
#         text = parse_pdf(file_obj)
#     elif filename.lower().endswith(".docx"):
#         from app.services.parsing import parse_docx
#         text = parse_docx(file_obj)

#     # Extract info
#     info = extract_info(text)
#     return info


# # --- Fonction fanampiny: process_cv_from_bytes ---
# def process_cv_from_bytes(db: Session, file_bytes: bytes, filename: str, candidature_id: int) -> dict:
#     """
#     Mandefa CV avy amin'ny bytes (ohatra avy amin'ny mail) ary miantso save_upload_file.
#     """
#     from fastapi.datastructures import UploadFile

#     fake_file = UploadFile(filename=filename, file=BytesIO(file_bytes))
#     return save_upload_file(db, fake_file, candidature_id)


# # --- Fonction fanampiny: delete file amin'ny MinIO (tsy voatery) ---
# def delete_file(filename: str):
#     """
#     Mamafa fichier amin'ny MinIO.
#     """
#     try:
#         if minio_client.bucket_exists(MINIO_BUCKET):
#             minio_client.remove_object(MINIO_BUCKET, filename)
#     except S3Error as e:
#         raise Exception(f"Erreur MinIO: {str(e)}")













# import os
# from fastapi import UploadFile
# from sqlalchemy.orm import Session
# from app.services.parsing import extract_info
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
#     secure=False  # HTTP
# )

# # Mamorona bucket raha tsy misy
# if not minio_client.bucket_exists(MINIO_BUCKET):
#     minio_client.make_bucket(MINIO_BUCKET)


# # ==========================================================
# # 🔹 Fonction principale: save_upload_file
# # ==========================================================
# def save_upload_file(db: Session, file: UploadFile, candidature_id: int) -> dict:
#     """
#     Mandefa fichier (CV, LM, Diplome, sns.) any amin'ny MinIO
#     ary mitahiry info ao amin'ny DB raha misy modely CandidatureFile.
#     """
#     filename = file.filename
#     content = file.file.read()
#     print("Uploading to MinIO:", filename, "Size:", len(content))
#     print("Uploading to MinIO:", filename, "Size:", len(content))
#     print("MinIO bucket:", MINIO_BUCKET)
#     print("Content-Type:", file.content_type)



#     # Mandefa any MinIO
#     try:
#         data_stream = BytesIO(content)
#         minio_client.put_object(
#             MINIO_BUCKET,
#             filename,
#             data=data_stream,
#             length=len(content),
#             content_type=file.content_type
#         )
#     except S3Error as e:
#         raise Exception(f"Erreur MinIO: {str(e)}")

#     # Maka text avy amin'ny fichier (raha CV)
#     text = ""
#     if filename.lower().endswith(".pdf"):
#         from app.services.parsing import parse_pdf
#         text = parse_pdf(BytesIO(content))
#     elif filename.lower().endswith(".docx"):
#         from app.services.parsing import parse_docx
#         text = parse_docx(BytesIO(content))

#     # Extraire info raha CV
#     info = {}
#     if text:
#         info = extract_info(text)

#     # Mitahiry info ao amin'ny DB raha misy modely CandidatureFile
#     try:
#         from app.models import CandidatureFile  # alaina eto ihany raha misy modely
#         db_file = CandidatureFile(
#             candidature_id=candidature_id,
#             filename=filename,
#             filepath=f"{MINIO_BUCKET}/{filename}",
#             firstname=info.get("firstname"),
#             lastname=info.get("lastname"),
#             email=info.get("email"),
#             phone=info.get("phone"),
#             skills=",".join(info.get("skills", [])),
#             diplomes=",".join(info.get("diplomes", [])),
#             langues=",".join(info.get("langues", [])),
#             exp_years=info.get("exp_years", 0),
#             projects=",".join(info.get("projects", [])),
#             text_preview=text[:1000] if text else ""
#         )
#         db.add(db_file)
#         db.commit()
#         db.refresh(db_file)
#     except Exception:
#         pass  # raha tsy misy modely CandidatureFile dia tsy manao zavatra

#     return {"filename": filename, "text_preview": text[:1000]}


# # ==========================================================
# # 🔹 Fonction fanampiny: process_cv_from_bytes
# # ==========================================================
# def process_cv_from_bytes(db: Session, file_bytes: bytes, filename: str, candidature_id: int) -> dict:
#     """
#     Mandefa CV avy amin'ny bytes (mail) ary miantso save_upload_file.
#     """
#     fake_file = UploadFile(filename=filename, file=BytesIO(file_bytes))
#     return save_upload_file(db, fake_file, candidature_id)


# # ==========================================================
# # 🔹 Fonction fanampiny: save_formulaire_files
# # ==========================================================
# def save_formulaire_files(db: Session, files_list: list[UploadFile], candidature_id: int) -> list[dict]:
#     """
#     Mandefa ireo fichiers avy amin'ny formulaire (CV, LM, Diplome, sns.) ho any amin'ny MinIO.
#     """
#     results = []
#     for file in files_list:
#         if file is not None:
#             result = save_upload_file(db, file, candidature_id)
#             results.append(result)
#     return results

# # Alias ho an'ny candidature_rh.py
# upload_files_to_minio = save_formulaire_files


# # ==========================================================
# # 🔹 Fonction fanampiny: delete file amin'ny MinIO
# # ==========================================================
# def delete_file(filename: str):
#     """
#     Mamafa fichier amin'ny MinIO.
#     """
#     try:
#         if minio_client.bucket_exists(MINIO_BUCKET):
#             minio_client.remove_object(MINIO_BUCKET, filename)
#     except S3Error as e:
#         raise Exception(f"Erreur MinIO: {str(e)}")
















import os
from fastapi import UploadFile
from sqlalchemy.orm import Session
from app.services.parsing import extract_info
from minio import Minio
from minio.error import S3Error
from io import BytesIO

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
    secure=False  # HTTP
)
print("✅ MinIO config:", MINIO_ENDPOINT, MINIO_ACCESS_KEY, MINIO_SECRET_KEY)
print("✅ Bucket exists?", minio_client.bucket_exists(MINIO_BUCKET))

# Mamorona bucket raha tsy misy
if not minio_client.bucket_exists(MINIO_BUCKET):
    minio_client.make_bucket(MINIO_BUCKET)


# ==========================================================
# 🔹 Fonction principale: save_upload_file
# ==========================================================
def save_upload_file(db: Session, file: UploadFile, candidature_id: int) -> dict:
    """
    Mandefa fichier (CV, LM, Diplome, sns.) any amin'ny MinIO
    ary mitahiry info ao amin'ny DB raha misy modely CandidatureFile.
    """
    filename = file.filename

    # --- lecture pour parsing (logique existante)
    content = file.file.read()

    print("Uploading to MinIO:", filename, "Size:", len(content))
    print("MinIO bucket:", MINIO_BUCKET)
    print("Content-Type:", file.content_type)

    # 🔴 CRITIQUE : averina amin'ny début ny stream
    file.file.seek(0)

    # Mandefa any MinIO
    try:
        minio_client.put_object(
            bucket_name=MINIO_BUCKET,
            object_name=filename,
            data=file.file,      # stream DIRECT
            length=len(content),
            part_size=10 * 1024 * 1024,
            content_type=file.content_type
        )
    except S3Error as e:
        raise Exception(f"Erreur MinIO: {str(e)}")

    # Maka text avy amin'ny fichier (raha CV)
    text = ""
    if filename.lower().endswith(".pdf"):
        from app.services.parsing import parse_pdf
        text = parse_pdf(BytesIO(content))
    elif filename.lower().endswith(".docx"):
        from app.services.parsing import parse_docx
        text = parse_docx(BytesIO(content))

    # Extraire info raha CV
    info = {}
    if text:
        info = extract_info(text)

    # Mitahiry info ao amin'ny DB raha misy modely CandidatureFile
    try:
        from app.models import CandidatureFile
        db_file = CandidatureFile(
            candidature_id=candidature_id,
            filename=filename,
            filepath=f"{MINIO_BUCKET}/{filename}",
            firstname=info.get("firstname"),
            lastname=info.get("lastname"),
            email=info.get("email"),
            phone=info.get("phone"),
            skills=",".join(info.get("skills", [])),
            diplomes=",".join(info.get("diplomes", [])),
            langues=",".join(info.get("langues", [])),
            exp_years=info.get("exp_years", 0),
            projects=",".join(info.get("projects", [])),
            text_preview=text[:1000] if text else ""
        )
        db.add(db_file)
        db.commit()
        db.refresh(db_file)
    except Exception:
        pass

    return {"filename": filename, "text_preview": text[:1000]}


# ==========================================================
# 🔹 Fonction fanampiny: process_cv_from_bytes
# ==========================================================
def process_cv_from_bytes(db: Session, file_bytes: bytes, filename: str, candidature_id: int) -> dict:
    """
    Mandefa CV avy amin'ny bytes (mail) ary miantso save_upload_file.
    """
    fake_file = UploadFile(filename=filename, file=BytesIO(file_bytes))
    return save_upload_file(db, fake_file, candidature_id)


# ==========================================================
# 🔹 Fonction fanampiny: save_formulaire_files
# ==========================================================
def save_formulaire_files(db: Session, files_list: list[UploadFile], candidature_id: int) -> list[dict]:
    """
    Mandefa ireo fichiers avy amin'ny formulaire (CV, LM, Diplome, sns.) ho any amin'ny MinIO.
    """
    results = []
    for file in files_list:
        if file is not None:
            result = save_upload_file(db, file, candidature_id)
            results.append(result)
    return results

# Alias ho an'ny candidature_rh.py
upload_files_to_minio = save_formulaire_files


# ==========================================================
# 🔹 Fonction fanampiny: delete file amin'ny MinIO
# ==========================================================
def delete_file(filename: str):
    """
    Mamafa fichier amin'ny MinIO.
    """
    try:
        if minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.remove_object(MINIO_BUCKET, filename)
    except S3Error as e:
        raise Exception(f"Erreur MinIO: {str(e)}")
