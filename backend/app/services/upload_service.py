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
#     secure=False
# )
# if not minio_client.bucket_exists(MINIO_BUCKET):
#     minio_client.make_bucket(MINIO_BUCKET)

# # ==========================================================
# # 🔹 Fonction principale: save_upload_file
# # ==========================================================
# def save_upload_file(db: Session, file: UploadFile, candidature_id: int) -> dict:
#     filename = file.filename
#     content = file.file.read()
#     file.file.seek(0)

#     try:
#         minio_client.put_object(
#             bucket_name=MINIO_BUCKET,
#             object_name=filename,
#             data=file.file,
#             length=len(content),
#             part_size=10 * 1024 * 1024,
#             content_type=file.content_type
#         )
#     except S3Error as e:
#         raise Exception(f"Erreur MinIO: {str(e)}")

#     text = ""
#     if filename.lower().endswith(".pdf"):
#         from app.services.parsing import parse_pdf
#         text = parse_pdf(BytesIO(content))
#     elif filename.lower().endswith(".docx"):
#         from app.services.parsing import parse_docx
#         text = parse_docx(BytesIO(content))

#     info = {}
#     if text:
#         info = extract_info(text)

#     try:
#         from app.models import CandidatureFile
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
#         pass

#     # 🔹 Mamerina ihany koa firstname & lastname ho an'ny fanavaozana amin'ny Candidature
#     return {
#         "filename": filename,
#         "text_preview": text[:1000],
#         "firstname": info.get("firstname"),
#         "lastname": info.get("lastname"),
#     }

# # ==========================================================
# # 🔹 Fonction fanampiny: process_cv_from_bytes
# # ==========================================================
# def process_cv_from_bytes(db: Session, file_bytes: bytes, filename: str, candidature_id: int) -> dict:
#     fake_file = UploadFile(filename=filename, file=BytesIO(file_bytes))
#     return save_upload_file(db, fake_file, candidature_id)

# # ==========================================================
# # 🔹 Alias ho an'ny formulaire
# # ==========================================================
# def save_formulaire_files(db: Session, files_list: list[UploadFile], candidature_id: int) -> list[dict]:
#     results = []
#     for file in files_list:
#         if file:
#             results.append(save_upload_file(db, file, candidature_id))
#     return results

# upload_files_to_minio = save_formulaire_files

# def delete_file(filename: str):
#     try:
#         if minio_client.bucket_exists(MINIO_BUCKET):
#             minio_client.remove_object(MINIO_BUCKET, filename)
#     except S3Error as e:
#         raise Exception(f"Erreur MinIO: {str(e)}")

















# app/services/upload_service.py 
import os, io, logging, shutil, tempfile, re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
import uuid
from pathlib import Path
from fastapi import UploadFile, HTTPException

logger = logging.getLogger(__name__)

# ==================== FONCTIONS DE BASE ====================

def save_upload_file(upload_file: UploadFile, destination: Path) -> str:
    """Sauvegarde un fichier uploadé localement"""
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with open(destination, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        logger.info(f"📁 Fichier sauvegardé: {destination}")
        return str(destination)
    except Exception as e:
        logger.error(f"❌ Erreur sauvegarde: {e}")
        raise

def get_file_extension(filename: str) -> str:
    """Retourne l'extension"""
    return Path(filename).suffix.lower()

# ==================== SERVICE MINIO CORRIGÉ ====================

class MinioService:
    def __init__(self):
        try:
            from minio import Minio
            from minio.error import S3Error
            
            # Configuration MinIO
            self.endpoint = os.getenv("MINIO_ENDPOINT", "localhost:9000")
            self.access_key = os.getenv("MINIO_ACCESS_KEY", "jeremi")
            self.secret_key = os.getenv("MINIO_SECRET_KEY", "Jeremi123")
            self.bucket_name = os.getenv("MINIO_BUCKET", "siirh-candidatures")
            
            logger.info(f"🔗 Tentative connexion MinIO: {self.endpoint}")
            
            self.minio_client = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=False
            )
            
            self._ensure_bucket()
            self.minio_available = True
            logger.info("✅ Service MinIO initialisé")
            
        except Exception as e:
            logger.error(f"❌ MinIO non disponible: {e}")
            self.minio_available = False
            self.minio_client = None
    
    def _ensure_bucket(self):
        """Créer le bucket si nécessaire"""
        try:
            if not self.minio_client.bucket_exists(self.bucket_name):
                self.minio_client.make_bucket(self.bucket_name)
                logger.info(f"✅ Bucket '{self.bucket_name}' créé")
            else:
                logger.info(f"✅ Bucket '{self.bucket_name}' existe")
        except Exception as e:
            logger.error(f"❌ Erreur bucket: {e}")
            raise
    
    def upload_cv(self, file_data: bytes, filename: str, offre_ref: str, candidate_email: str) -> Optional[str]:
        """Upload d'un CV vers MinIO"""
        if not self.minio_available or not self.minio_client:
            logger.error("❌ Service MinIO non disponible")
            return None
        
        try:
            # Nettoyer les noms
            safe_ref = re.sub(r'[^\w\-]', '_', offre_ref)
            email_local = candidate_email.split('@')[0]
            safe_email = re.sub(r'[^\w\-]', '_', email_local)
            
            # Nom de fichier unique
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            file_ext = Path(filename).suffix.lower()
            if not file_ext:
                file_ext = '.pdf'
            
            new_filename = f"cv_{timestamp}_{unique_id}{file_ext}"
            
            # Chemin MinIO
            object_path = f"offres/{safe_ref}/candidats/{safe_email}/{new_filename}"
            
            # Content-type
            content_type = self._get_content_type(file_ext)
            
            # Taille du fichier
            file_size = len(file_data)
            
            # Upload vers MinIO
            self.minio_client.put_object(
                bucket_name=self.bucket_name,
                object_name=object_path,
                data=io.BytesIO(file_data),
                length=file_size,
                content_type=content_type
            )
            
            logger.info(f"✅ CV uploadé vers MinIO: {object_path} ({file_size} bytes)")
            return object_path
            
        except Exception as e:
            logger.error(f"❌ Erreur upload MinIO: {e}")
            return None
    
    def _get_content_type(self, extension: str) -> str:
        """Déterminer le content-type"""
        types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.txt': 'text/plain',
            '.rtf': 'application/rtf',
        }
        return types.get(extension.lower(), 'application/octet-stream')

# Instance globale
minio_service = MinioService()

# ==================== FONCTIONS PRINCIPALES ====================

def process_cv_from_bytes(db, content: bytes, filename: str, candidature_id: int) -> Dict[str, Any]:
    """Fonction principale pour traiter un CV depuis mail_listener"""
    try:
        from app.models.models import Candidature
        from app.models.offres import Offre
        from app.services.parsing import extract_info
        from app.services.scoring_auto import calculate_cv_score
        
        logger.info(f"📤 Début traitement CV: {filename} ({len(content)} bytes)")
        
        # Récupérer la candidature
        candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
        if not candidature:
            logger.error(f"❌ Candidature {candidature_id} non trouvée")
            return {"success": False, "error": "Candidature non trouvée"}
        
        # Récupérer l'offre
        offre = None
        if candidature.offre_id:
            offre = db.query(Offre).filter(Offre.id == candidature.offre_id).first()
        
        offre_ref = "UNASSIGNED"
        if offre and hasattr(offre, 'job_ref'):
            offre_ref = offre.job_ref
        elif offre:
            offre_ref = f"offre_{offre.id}"
        
        logger.info(f"   📋 Offre référence: {offre_ref}")
        logger.info(f"   👤 Candidat: {candidature.email}")
        
        # Upload vers MinIO
        minio_path = minio_service.upload_cv(
            file_data=content,
            filename=filename,
            offre_ref=offre_ref,
            candidate_email=candidature.email
        )
        
        if minio_path:
            # Mettre à jour la candidature avec le chemin du CV
            candidature.cv_path = minio_path
            candidature.cv_filename = filename
            
            # Extraire le texte du CV
            try:
                text_sample = extract_text_sample(content, filename)
                if text_sample:
                    candidature.cv_text = text_sample[:2000]  # Limiter à 2000 caractères
                    logger.info(f"   📝 Texte extrait: {len(text_sample)} caractères")
                    
                    # 🔥 CORRECTION: Extraire les infos avec le parsing NLP
                    nlp_info = extract_info(text_sample)
                    
                    if nlp_info:
                        # Ajouter le score aux infos NLP
                        if offre and hasattr(offre, 'description') and offre.description:
                            score_result = calculate_cv_score(text_sample, offre.description)
                            if score_result and 'score_total' in score_result:
                                nlp_info['score'] = score_result['score_total']
                                logger.info(f"   🎯 Score calculé: {score_result['score_total']}%")
                        else:
                            # Score par défaut si pas d'offre
                            nlp_info['score'] = 50
                            logger.info(f"   ⚠️ Score par défaut: 50% (pas d'offre)")
                        
                        # 🔥 CORRECTION: Retourner les infos NLP avec le score
                        logger.info(f"   👤 Info NLP extraites")
                        
                        # Mettre à jour la candidature avec quelques infos de base
                        if nlp_info.get('fullname') and nlp_info['fullname'].strip():
                            candidature.fullname = nlp_info['fullname']
                        
                        if nlp_info.get('skills'):
                            candidature.competences = ', '.join(nlp_info['skills'][:5])
                        
                        # Sauvegarder toutes les infos NLP en JSON
                        candidature.nlp_data = nlp_info
                        
                        # Mettre à jour le score dans la candidature
                        candidature.score = nlp_info.get('score', 50)
                        
                    else:
                        logger.warning(f"   ⚠️ Aucune info NLP extraite")
                        # Score par défaut
                        candidature.score = 50
                        nlp_info = {'score': 50}
                        
                else:
                    logger.warning(f"   ⚠️ Impossible d'extraire le texte du CV")
                    candidature.score = 50
                    nlp_info = {'score': 50}
                    
            except Exception as e:
                logger.warning(f"   ⚠️ Extraction NLP échouée: {e}")
                candidature.score = 50
                nlp_info = {'score': 50}
            
            # Sauvegarder toutes les modifications
            db.commit()
            
            logger.info(f"✅ Candidature mise à jour avec CV")
            
            # 🔥 CORRECTION: Retourner les infos NLP pour que mail_listener puisse les utiliser
            return {
                "success": True,
                "minio_path": minio_path,
                "candidature_id": candidature_id,
                "filename": filename,
                "nlp_info": nlp_info  # 🔥 Ajout des infos NLP
            }
        else:
            logger.error(f"❌ Échec upload MinIO pour {filename}")
            return {"success": False, "error": "Échec upload MinIO"}
            
    except Exception as e:
        logger.error(f"❌ Erreur traitement CV: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}

def extract_text_sample(content: bytes, filename: str) -> str:
    """Extrait du texte d'un CV"""
    try:
        filename_lower = filename.lower()
        
        # PDF
        if filename_lower.endswith('.pdf'):
            try:
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ""
                for i, page in enumerate(pdf_reader.pages[:3]):  # 3 premières pages max
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                return text.strip()
            except Exception as e:
                logger.warning(f"⚠️ Extraction PDF échouée: {e}")
                pass
        
        # DOCX
        elif filename_lower.endswith('.docx'):
            try:
                from docx import Document
                doc = Document(io.BytesIO(content))
                paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
                return "\n".join(paragraphs[:50])  # 50 paragraphes max
            except Exception as e:
                logger.warning(f"⚠️ Extraction DOCX échouée: {e}")
                pass
        
        # DOC (ancien format)
        elif filename_lower.endswith('.doc'):
            try:
                # Tenter d'extraire comme texte brut
                import olefile
                ole = olefile.OleFileIO(io.BytesIO(content))
                if ole.exists('WordDocument'):
                    stream = ole.openstream('WordDocument')
                    content_bytes = stream.read()
                    # Extraction très basique
                    text = content_bytes.decode('latin-1', errors='ignore')
                    # Nettoyer
                    text = re.sub(r'[^\x20-\x7E\n\r\t]', ' ', text)
                    return text[:5000]
            except:
                pass
        
        # Texte brut
        try:
            text = content.decode('utf-8', errors='ignore')
            if len(text) > 100:
                return text[:3000]
            else:
                # Tenter d'autres encodages
                for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
                    try:
                        text = content.decode(encoding, errors='ignore')
                        if len(text) > 100:
                            return text[:3000]
                    except:
                        continue
        except:
            pass
        
        return ""
        
    except Exception as e:
        logger.warning(f"⚠️ Extraction texte échouée: {e}")
        return ""

def upload_files_to_minio(files: List[Tuple[str, bytes]], offre_ref: str, candidate_info: Dict[str, Any]) -> Dict[str, Any]:
    """Upload multiple de fichiers vers MinIO"""
    results = {
        "success": [],
        "failed": [],
        "total_files": len(files)
    }
    
    for filename, file_data in files:
        try:
            minio_path = minio_service.upload_cv(
                file_data=file_data,
                filename=filename,
                offre_ref=offre_ref,
                candidate_email=candidate_info.get('email', 'unknown@example.com')
            )
            
            if minio_path:
                results["success"].append({
                    "filename": filename,
                    "minio_path": minio_path,
                    "size_bytes": len(file_data)
                })
            else:
                results["failed"].append({
                    "filename": filename,
                    "error": "Upload échoué"
                })
                
        except Exception as e:
            results["failed"].append({
                "filename": filename,
                    "error": str(e)
            })
    
    results["success_count"] = len(results["success"])
    results["failed_count"] = len(results["failed"])
    
    return results
# Dans app/services/upload_service.py - AJOUTER CE CODE
def process_cv_from_bytes(db, content: bytes, filename: str, candidature_id: int) -> Dict[str, Any]:
    """Fonction principale pour traiter un CV"""
    try:
        from app.models.models import Candidature
        from app.models.offres import Offre
        from app.services.parsing import extract_info
        from app.services.scoring_auto import calculate_cv_score
        
        logger.info(f"📤 Début traitement CV: {filename} ({len(content)} bytes)")
        
        # Récupérer la candidature
        candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
        if not candidature:
            logger.error(f"❌ Candidature {candidature_id} non trouvée")
            return {"success": False, "error": "Candidature non trouvée"}
        
        # Récupérer l'offre
        offre = None
        if candidature.offre_id:
            offre = db.query(Offre).filter(Offre.id == candidature.offre_id).first()
        
        offre_ref = candidature.ref_offre or "UNASSIGNED"
        
        logger.info(f"   📋 Offre référence: {offre_ref}")
        logger.info(f"   👤 Candidat: {candidature.email}")
        
        # Upload vers MinIO
        minio_path = minio_service.upload_cv(
            file_data=content,
            filename=filename,
            offre_ref=offre_ref,
            candidate_email=candidature.email
        )
        
        if minio_path:
            # Mettre à jour la candidature avec le chemin du CV
            candidature.raw_cv_s3 = minio_path
            
            # Extraire le texte du CV
            try:
                text_sample = extract_text_sample(content, filename)
                if text_sample and len(text_sample) > 100:
                    logger.info(f"   📝 Texte extrait: {len(text_sample)} caractères")
                    
                    # 🔥 EXTRACTION NLP - AVEC GESTION D'ERREUR
                    nlp_info = {}
                    try:
                        nlp_info = extract_info(text_sample)
                        logger.info(f"   ✅ Extraction NLP terminée")
                    except Exception as e:
                        logger.error(f"   ❌ Erreur extraction NLP: {e}")
                        nlp_info = {
                            'fullname': None,
                            'email': None,
                            'phone': None,
                            'skills': [],
                            'summary': {'structure_score': 0}
                        }
                    
                    # 🔥 CALCUL DU SCORE
                    score = 50  # Score par défaut
                    try:
                        if offre and hasattr(offre, 'description') and offre.description:
                            score_result = calculate_cv_score(text_sample, offre.description)
                            if score_result and 'score_total' in score_result:
                                score = score_result['score_total']
                        else:
                            score_result = calculate_cv_score(text_sample, "")
                            if score_result and 'score_total' in score_result:
                                score = score_result['score_total']
                        
                        logger.info(f"   🎯 Score calculé: {score}%")
                    except Exception as e:
                        logger.error(f"   ❌ Erreur calcul score: {e}")
                        score = 50
                    
                    # 🔥 PRÉPARER LES DONNÉES POUR LA BASE
                    parsed_data = {
                        'extraction_date': datetime.now().isoformat(),
                        'source_file': filename,
                        'text_sample_length': len(text_sample),
                        'score': score,
                        'extracted_info': nlp_info
                    }
                    
                    # Mettre à jour les champs de la candidature
                    candidature.parsed_json = parsed_data
                    candidature.score = float(score)
                    
                    # Mettre à jour le nom si extrait
                    if nlp_info and nlp_info.get('fullname'):
                        candidature.fullname = nlp_info['fullname']
                        logger.info(f"   👤 Nom mis à jour: {nlp_info['fullname']}")
                    
                    # Mettre à jour le téléphone si extrait
                    if nlp_info and nlp_info.get('phone'):
                        candidature.phone = nlp_info['phone']
                    
                else:
                    logger.warning(f"   ⚠️ Texte trop court ou impossible à extraire")
                    parsed_data = {
                        'extraction_date': datetime.now().isoformat(),
                        'source_file': filename,
                        'error': 'Texte trop court',
                        'score': 10
                    }
                    candidature.parsed_json = parsed_data
                    candidature.score = 10.0
                    
            except Exception as e:
                logger.error(f"   ❌ Erreur traitement texte: {e}")
                parsed_data = {
                    'extraction_date': datetime.now().isoformat(),
                    'source_file': filename,
                    'error': str(e),
                    'score': 10
                }
                candidature.parsed_json = parsed_data
                candidature.score = 10.0
            
            # Sauvegarder
            db.commit()
            logger.info(f"✅ Candidature mise à jour avec CV")
            
            # Retourner les résultats
            return {
                "success": True,
                "minio_path": minio_path,
                "candidature_id": candidature_id,
                "filename": filename,
                "nlp_info": nlp_info if 'nlp_info' in locals() else {'score': candidature.score}
            }
        else:
            logger.error(f"❌ Échec upload MinIO")
            return {"success": False, "error": "Échec upload MinIO"}
            
    except Exception as e:
        logger.error(f"❌ Erreur traitement CV: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {"success": False, "error": str(e)}