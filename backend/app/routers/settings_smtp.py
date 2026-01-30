# # app/routers/settings_smtp.py
# from fastapi import APIRouter, HTTPException, Depends
# from pydantic import BaseModel
# from sqlalchemy.orm import Session
# from app.db import get_db, engine
# from app.models.models import Candidature, Convocation
# from app.utils.pdf_generator import generate_convocation_pdf
# import os, json, smtplib, traceback
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# from datetime import datetime
# from sqlalchemy import text

# router = APIRouter()

# # ------------------- Pydantic Model -------------------
# class SMTPSettings(BaseModel):
#     email: str
#     password: str

# # ------------------- GET SMTP -------------------
# @router.get("/settings/smtp")
# def get_smtp(db: Session = Depends(get_db)):
#     try:
#         smtp_config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
#         if smtp_config:
#             return {
#                 "email": smtp_config.email,
#                 "password": smtp_config.password,
#                 "server": smtp_config.server,
#                 "port": smtp_config.port
#             }
#         return {"email": "", "password": "", "server": "smtp.gmail.com", "port": 587}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération SMTP: {e}")

# # ------------------- POST SMTP -------------------
# @router.post("/settings/smtp")
# def save_smtp(settings: SMTPSettings, db: Session = Depends(get_db)):
#     try:
#         # Fafao taloha raha misy
#         db.execute(text("DELETE FROM smtp_config"))
#         # Ampidiro vaovao
#         db.execute(
#             text("""
#                 INSERT INTO smtp_config (email, password, server, port) 
#                 VALUES (:email, :password, :server, :port)
#             """),
#             {
#                 "email": settings.email,
#                 "password": settings.password,
#                 "server": "smtp.gmail.com",
#                 "port": 587
#             }
#         )
#         db.commit()
#         return {"success": True, "message": "SMTP settings saved in DB!"}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement SMTP: {e}")

# # ------------------- GET candidatures -------------------
# @router.get("/candidatures")
# async def get_candidatures():
#     try:
#         query = "SELECT * FROM candidatures ORDER BY date_candidature DESC"
#         with engine.begin() as conn:
#             result = conn.execute(query)
#             candidatures = []
#             for row in result:
#                 r = dict(row._mapping)
#                 # parsing et score...
#                 candidatures.append(r)
#             return candidatures
#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))

# # ------------------- POST envoyer convocation -------------------
# @router.post("/candidatures/{id}/send-invitation")
# async def send_invitation(id: int, db: Session = Depends(get_db)):
#     try:
#         candidature = db.query(Candidature).filter(Candidature.id == id).first()
#         if not candidature:
#             raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         if not candidature.email:
#             raise HTTPException(status_code=400, detail="Email du candidat manquant")

#         # Charger SMTP depuis DB
#         smtp_config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
#         if not smtp_config:
#             raise HTTPException(status_code=500, detail="SMTP non configuré")
#         smtp_email = smtp_config.email
#         smtp_password = smtp_config.password
#         smtp_server = smtp_config.server or "smtp.gmail.com"
#         smtp_port = int(smtp_config.port or 587)

#         # Générer PDF
#         now = datetime.now()
#         convocation = Convocation(
#             date_entretien=now.strftime("%Y-%m-%d"),
#             heure_entretien=now.strftime("%H:%M"),
#             lieu_entretien="À définir",
#             status="en attente",
#             candidature_id=candidature.id
#         )
#         db.add(convocation)
#         db.commit()
#         db.refresh(convocation)
#         pdf_path = generate_convocation_pdf(candidature, convocation)

#         # Préparer mail
#         message = MIMEMultipart()
#         message["Subject"] = "Convocation entretien - CODEL"
#         message["From"] = smtp_email
#         message["To"] = candidature.email

#         html_content = f"""
#         <html>
#         <body>
#         <p>Bonjour <strong>{candidature.fullname}</strong>,</p>
#         <p>Vous êtes cordialement invité(e) à votre entretien pour le poste.</p>
#         <p><strong>Date et heure :</strong> {convocation.date_entretien} {convocation.heure_entretien}<br>
#         <strong>Lieu :</strong> {convocation.lieu_entretien}</p>
#         <p>Veuillez consulter le PDF joint pour tous les détails.</p>
#         </body>
#         </html>
#         """
#         message.attach(MIMEText(html_content, "html", "utf-8"))

#         with open(pdf_path, "rb") as f:
#             part = MIMEBase("application", "octet-stream")
#             part.set_payload(f.read())
#             encoders.encode_base64(part)
#             part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(pdf_path)}"')
#             message.attach(part)

#         # Envoyer mail
#         try:
#             with smtplib.SMTP(smtp_server, smtp_port) as server:
#                 server.starttls()
#                 server.login(smtp_email, smtp_password)
#                 server.sendmail(smtp_email, candidature.email, message.as_string())
#         except Exception as e:
#             traceback.print_exc()
#             raise HTTPException(status_code=500, detail=f"Erreur SMTP: {str(e)}")

#         # Mettre à jour statut
#         convocation.status = "envoyée"
#         convocation.lien_fichier = pdf_path
#         candidature.statut = "Convoqué"
#         db.commit()

#         return {"message": f"Convocation envoyée à {candidature.fullname}", "pdf_path": pdf_path}

#     except Exception as e:
#         traceback.print_exc()
#         raise HTTPException(status_code=500, detail=str(e))


# app/routers/settings_smtp.py - VERSION AVEC LOGS DÉTAILLÉS

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from datetime import datetime
from app.db import get_db
import traceback
import logging
from sqlalchemy import text

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()

# ------------------- Pydantic Model -------------------
class SMTPSettings(BaseModel):
    email: str = Field(..., example="votre.email@gmail.com")
    password: str = Field(..., description="⚠️ Utilisez MOT DE PASSE D'APPLICATION pour Gmail (16 caractères)")

# ------------------- GET SMTP -------------------
@router.get("/settings/smtp")
def get_smtp(db: Session = Depends(get_db)):
    """Récupérer la configuration SMTP actuelle"""
    logger.info("🔍 GET /api/settings/smtp - Début")
    
    try:
        # Essayer d'abord avec ORM
        try:
            from app.models.models import SMTPConfig
            logger.info("📦 Tentative avec ORM (SMTPConfig model)")
            
            smtp_config = db.query(SMTPConfig).order_by(SMTPConfig.id.desc()).first()
            if smtp_config:
                logger.info(f"✅ SMTP trouvé via ORM: {smtp_config.email[:3]}***")
                
                # Vérifier si le modèle a les attributs
                host_value = getattr(smtp_config, 'host', None) or getattr(smtp_config, 'server', 'smtp.gmail.com')
                
                return {
                    "email": smtp_config.email,
                    "password": "********",  # Masqué pour sécurité
                    "host": host_value,
                    "port": smtp_config.port,
                    "use_tls": getattr(smtp_config, 'use_tls', True)
                }
        except ImportError as e:
            logger.warning(f"⚠️ Modèle SMTPConfig non trouvé: {e}")
        except Exception as e:
            logger.warning(f"⚠️ Erreur ORM, fallback SQL: {str(e)[:100]}")

        # Fallback: SQL direct
        logger.info("🔄 Fallback vers SQL direct")
        try:
            smtp_config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
            if smtp_config:
                logger.info(f"✅ SMTP trouvé via SQL: {smtp_config.email[:3]}***")
                
                return {
                    "email": smtp_config.email,
                    "password": "********",
                    "host": smtp_config.host if hasattr(smtp_config, 'host') else "smtp.gmail.com",
                    "port": smtp_config.port,
                    "use_tls": getattr(smtp_config, 'use_tls', True)
                }
        except Exception as e:
            logger.warning(f"⚠️ Erreur SQL: {str(e)[:100]}")

        # Aucune configuration trouvée
        logger.info("ℹ️ Aucune configuration SMTP trouvée, retour valeurs par défaut")
        return {
            "email": "",
            "password": "",
            "host": "smtp.gmail.com",
            "port": 587,
            "use_tls": True,
            "note": "Aucune configuration enregistrée"
        }

    except Exception as e:
        logger.error(f"❌ GET /settings/smtp - Erreur critique: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération SMTP: {str(e)[:200]}")

# ------------------- POST SMTP -------------------
@router.post("/settings/smtp")
def save_smtp(settings: SMTPSettings, db: Session = Depends(get_db)):
    """Enregistrer une nouvelle configuration SMTP"""
    logger.info("💾 POST /api/settings/smtp - Début")
    logger.info(f"📧 Email: {settings.email[:3]}***, Password length: {len(settings.password)}")
    
    try:
        # VÉRIFICATION 1: Table existe?
        logger.info("🔍 Vérification table smtp_config...")
        try:
            table_exists = db.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'smtp_config')")
            ).scalar()
            
            if not table_exists:
                logger.error("❌ Table 'smtp_config' n'existe pas!")
                return {
                    "success": False,
                    "error": "Table smtp_config n'existe pas",
                    "solution": "Exécutez: CREATE TABLE smtp_config (id SERIAL PRIMARY KEY, email VARCHAR(255), password VARCHAR(255), host VARCHAR(255) DEFAULT 'smtp.gmail.com', port INTEGER DEFAULT 587, use_tls BOOLEAN DEFAULT true, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
                }
            logger.info("✅ Table smtp_config existe")
        except Exception as e:
            logger.warning(f"⚠️ Erreur vérification table: {str(e)}")

        # VÉRIFICATION 2: Colonnes existent?
        logger.info("🔍 Vérification colonnes...")
        try:
            columns = db.execute(text(
                "SELECT column_name FROM information_schema.columns WHERE table_name = 'smtp_config'"
            )).fetchall()
            column_names = [c[0] for c in columns]
            logger.info(f"📋 Colonnes disponibles: {column_names}")
            
            if 'host' not in column_names and 'server' not in column_names:
                logger.warning("⚠️ Colonne 'host' ou 'server' non trouvée")
        except Exception as e:
            logger.warning(f"⚠️ Erreur vérification colonnes: {str(e)}")

        # ESSAI 1: Avec ORM si disponible
        logger.info("🔄 Tentative 1: Avec ORM...")
        try:
            from app.models.models import SMTPConfig
            logger.info("📦 Modèle SMTPConfig importé avec succès")
            
            # Vérifier les attributs du modèle
            import inspect
            attrs = [attr for attr in dir(SMTPConfig) if not attr.startswith('_')]
            logger.info(f"🔧 Attributs du modèle: {attrs}")
            
            # Créer instance
            smtp_kwargs = {
                'email': settings.email,
                'password': settings.password,
                'created_at': datetime.now()
            }
            
            # Ajouter host ou server selon disponibilité
            if hasattr(SMTPConfig, 'host'):
                smtp_kwargs['host'] = "smtp.gmail.com"
            elif hasattr(SMTPConfig, 'server'):
                smtp_kwargs['server'] = "smtp.gmail.com"
                
            if hasattr(SMTPConfig, 'port'):
                smtp_kwargs['port'] = 587
            if hasattr(SMTPConfig, 'use_tls'):
                smtp_kwargs['use_tls'] = True
                
            logger.info(f"⚙️ Paramètres pour SMTPConfig: {list(smtp_kwargs.keys())}")
            
            new_smtp = SMTPConfig(**smtp_kwargs)
            
            # Supprimer anciens
            db.query(SMTPConfig).delete()
            db.commit()
            
            # Ajouter nouveau
            db.add(new_smtp)
            db.commit()
            db.refresh(new_smtp)
            
            logger.info("✅ SMTP enregistré avec succès via ORM")
            return {
                "success": True,
                "message": "Configuration SMTP enregistrée avec succès!",
                "method": "ORM",
                "email": settings.email[:3] + "***" + settings.email[settings.email.find("@"):]
            }
            
        except ImportError:
            logger.warning("📦 Modèle SMTPConfig non importable")
        except TypeError as e:
            logger.error(f"❌ Erreur Type avec ORM: {str(e)}")
            logger.error("📋 Vérifiez les attributs du modèle SMTPConfig")
        except Exception as e:
            logger.error(f"❌ Erreur ORM: {str(e)}")
            logger.error(traceback.format_exc())

        # ESSAI 2: SQL direct (fallback garanti)
        logger.info("🔄 Tentative 2: SQL direct...")
        try:
            # Supprimer ancienne configuration
            db.execute(text("DELETE FROM smtp_config"))
            logger.info("🗑️ Anciennes configurations supprimées")
            
            # Déterminer les colonnes disponibles
            try:
                column_info = db.execute(text(
                    "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'smtp_config'"
                )).fetchall()
                
                columns_dict = {col[0]: col[1] for col in column_info}
                logger.info(f"📊 Structure table: {columns_dict}")
                
                # Construire INSERT dynamique
                insert_cols = ['email', 'password']
                insert_vals = [':email', ':password']
                
                if 'host' in columns_dict:
                    insert_cols.append('host')
                    insert_vals.append("'smtp.gmail.com'")
                elif 'server' in columns_dict:
                    insert_cols.append('server')
                    insert_vals.append("'smtp.gmail.com'")
                    
                if 'port' in columns_dict:
                    insert_cols.append('port')
                    insert_vals.append('587')
                    
                if 'use_tls' in columns_dict:
                    insert_cols.append('use_tls')
                    insert_vals.append('true')
                    
                if 'created_at' in columns_dict:
                    insert_cols.append('created_at')
                    insert_vals.append('CURRENT_TIMESTAMP')
                
                insert_query = f"""
                    INSERT INTO smtp_config ({', '.join(insert_cols)}) 
                    VALUES ({', '.join(insert_vals)})
                """
                
                logger.info(f"📝 Query INSERT: {insert_query[:200]}...")
                
                # Exécuter
                db.execute(
                    text(insert_query),
                    {"email": settings.email, "password": settings.password}
                )
                
            except Exception as e:
                logger.warning(f"⚠️ Erreur détection colonnes, INSERT simple: {str(e)}")
                # Version ultra-simple
                db.execute(
                    text("INSERT INTO smtp_config (email, password) VALUES (:email, :password)"),
                    {"email": settings.email, "password": settings.password}
                )
            
            db.commit()
            logger.info("💾 SMTP enregistré avec succès via SQL")
            
            return {
                "success": True,
                "message": "Configuration SMTP enregistrée avec succès!",
                "method": "SQL direct",
                "note": "Utilisez un MOT DE PASSE D'APPLICATION pour Gmail",
                "email": settings.email[:3] + "***" + settings.email[settings.email.find("@"):]
            }
            
        except Exception as e:
            logger.error(f"❌ Erreur SQL direct: {str(e)}")
            logger.error(traceback.format_exc())
            db.rollback()
            
            return {
                "success": False,
                "error": f"Erreur SQL: {str(e)[:200]}",
                "solution": "Vérifiez: 1) Table smtp_config existe, 2) Connexion DB"
            }

    except Exception as e:
        logger.error(f"❌ POST /settings/smtp - Erreur critique: {str(e)}")
        logger.error(traceback.format_exc())
        
        return {
            "success": False,
            "error": f"Erreur interne: {str(e)[:200]}",
            "trace": traceback.format_exc()[-500:] if logger.level <= logging.DEBUG else None
        }

# ------------------- TEST SMTP -------------------
@router.post("/settings/smtp/test")
def test_smtp(db: Session = Depends(get_db)):
    """Tester la connexion SMTP"""
    logger.info("🧪 POST /api/settings/smtp/test - Test connexion")
    
    try:
        # Récupérer config
        result = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
        
        if not result:
            logger.warning("⚠️ Aucune configuration SMTP pour test")
            return {
                "success": False,
                "message": "Aucune configuration SMTP trouvée"
            }
        
        logger.info(f"🔧 Test avec: {result.email[:3]}***, host: {getattr(result, 'host', 'smtp.gmail.com')}")
        
        # Tester connexion (optionnel - commenter si problèmes)
        try:
            import smtplib
            
            host = getattr(result, 'host', None) or getattr(result, 'server', 'smtp.gmail.com')
            port = getattr(result, 'port', 587)
            
            logger.info(f"🔌 Connexion à {host}:{port}")
            
            with smtplib.SMTP(host, port, timeout=10) as server:
                server.starttls()
                server.login(result.email, result.password)
                server.quit()
            
            logger.info("✅ Test SMTP réussi")
            
            return {
                "success": True,
                "message": "Connexion SMTP réussie!",
                "host": host,
                "port": port,
                "email": result.email[:3] + "***" + result.email[result.email.find("@"):]
            }
            
        except ImportError:
            logger.warning("📦 smtplib non disponible")
        except Exception as e:
            logger.error(f"❌ Erreur test SMTP: {str(e)}")
            return {
                "success": False,
                "message": f"Erreur connexion: {str(e)[:200]}",
                "help": "Vérifiez: 1) App password, 2) Validation 2 étapes, 3) Internet"
            }
        
    except Exception as e:
        logger.error(f"❌ Erreur test endpoint: {str(e)}")
        return {
            "success": False,
            "message": f"Erreur: {str(e)}"
        }