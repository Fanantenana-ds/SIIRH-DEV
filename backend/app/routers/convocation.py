# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.db import get_db
# from app.models.models import Candidature, Convocation
# from app.utils.pdf_generator import generate_convocation_pdf
# from datetime import datetime, timedelta
# import logging
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# import os
# from dotenv import load_dotenv

# # Load .env
# current_dir = os.path.dirname(__file__)
# dotenv_path = os.path.join(current_dir, "../.env")
# load_dotenv(dotenv_path)

# router = APIRouter(prefix="/convocations", tags=["Convocations"])
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# from app.schemas.convocation import ConvocationCreate, ConvocationRead

# # --- Création convocation générique (POST) ---
# @router.post("/create-convocation", response_model=ConvocationRead)
# def create_convocation(form: ConvocationCreate, db: Session = Depends(get_db)):
#     """
#     Création d'une convocation générique, sans candidat associé.
#     """
#     # Récupération de la dernière convocation pour calculer l'heure suivante
#     last_conv = db.query(Convocation).order_by(Convocation.id.desc()).first()

#     try:
#         start_datetime = datetime.strptime(f"{form.date} {form.heure}", "%Y-%m-%d %H:%M")
#         if last_conv:
#             last_dt = datetime.strptime(f"{last_conv.date_entretien} {last_conv.heure_entretien}", "%Y-%m-%d %H:%M")
#             start_datetime = last_dt + timedelta(minutes=form.interval_minute or 15)
#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Format date/heure invalide : {str(e)}")

#     conv = Convocation(
#         date_entretien=start_datetime.strftime("%Y-%m-%d"),
#         heure_entretien=start_datetime.strftime("%H:%M"),
#         lieu_entretien=form.lieu,
#         status="en attente",
#         candidature_id=None  # Générique
#     )

#     db.add(conv)
#     db.commit()
#     db.refresh(conv)

#     logger.info(f"✅ Convocation générique créée à {conv.heure_entretien}")
#     return conv


# # --- Envoi convocation à un candidat sélectionné (POST) ---
# @router.post("/candidatures/{candidature_id}/send-invitation")
# def send_invitation(candidature_id: int, db: Session = Depends(get_db)):
#     """
#     Prend le dernier convocation générique et l'associe au candidat sélectionné,
#     ajoute l'interval si nécessaire, génère le PDF et envoie l'email.
#     """
#     candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
#     if not candidature:
#         raise HTTPException(status_code=404, detail=f"Candidat introuvable avec id {candidature_id}")

#     if candidature.statut != "Sélectionné":
#         raise HTTPException(status_code=400, detail="Seul les candidats sélectionnés peuvent recevoir une convocation")

#     if not candidature.email:
#         raise HTTPException(status_code=400, detail="Email du candidat manquant")

#     # Prendre la dernière convocation générique (candidature_id = None)
#     convocation = (
#         db.query(Convocation)
#         .filter(Convocation.candidature_id == None)
#         .order_by(Convocation.id.desc())
#         .first()
#     )

#     if not convocation:
#         raise HTTPException(
#             status_code=404,
#             detail="Aucune convocation créée. Veuillez d'abord créer une convocation générique."
#         )

#     # Associer la convocation au candidat
#     convocation.candidature_id = candidature.id

#     try:
#         pdf_path = generate_convocation_pdf(candidature, convocation)
#         logger.info(f"✅ Convocation PDF généré : {pdf_path}")

#         # SMTP
#         sender_email = os.getenv("SMTP_EMAIL")
#         sender_password = os.getenv("SMTP_PASSWORD")
#         smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
#         smtp_port = int(os.getenv("SMTP_PORT", 587))

#         if not sender_email or not sender_password:
#             logger.error("❌ SMTP credentials non trouvées")
#             raise HTTPException(status_code=500, detail="SMTP credentials mankany .env tsy hita")

#         message = MIMEMultipart()
#         message["Subject"] = "Convocation entretien - CODEL"
#         message["From"] = sender_email
#         message["To"] = candidature.email

#         html_content = f"""
#         <html>
#         <body>
#             <p>Bonjour <strong>{candidature.fullname}</strong>,</p>
#             <p>Vous êtes cordialement invité(e) à votre entretien pour le poste.</p>
#             <p><strong>Date et heure :</strong> {convocation.date_entretien} {convocation.heure_entretien}<br>
#                <strong>Lieu :</strong> {convocation.lieu_entretien}</p>
#             <p>Veuillez consulter le PDF joint pour tous les détails et apporter les documents nécessaires.</p>
#             <p><em>Message automatique, ne pas répondre à ce mail.</em></p>
#             <p>Cordialement,<br><strong>Équipe RH</strong></p>
#         </body>
#         </html>
#         """
#         message.attach(MIMEText(html_content, "html", "utf-8"))

#         with open(pdf_path, "rb") as f:
#             part = MIMEBase("application", "octet-stream")
#             part.set_payload(f.read())
#             encoders.encode_base64(part)
#             part.add_header(
#                 "Content-Disposition",
#                 f'attachment; filename="{os.path.basename(pdf_path)}"'
#             )
#             message.attach(part)

#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()
#             server.login(sender_email, sender_password)
#             server.sendmail(sender_email, candidature.email, message.as_string())

#         # Mise à jour statut
#         convocation.status = "envoyée"
#         convocation.lien_fichier = pdf_path
#         candidature.statut = "Convoqué"
#         db.commit()

#         logger.info(f"✅ Convocation envoyée à {candidature.fullname} ({candidature.email})")

#         return {
#             "message": f"Bonjour {candidature.fullname}, votre convocation a été envoyée avec succès ✅",
#             "pdf_path": pdf_path,
#             "date_entretien": convocation.date_entretien,
#             "heure_entretien": convocation.heure_entretien,
#             "lieu_entretien": convocation.lieu_entretien,
#             "status": convocation.status
#         }

#     except Exception as e:
#         logger.error(f"❌ Erreur lors de l'envoi de convocation : {str(e)}")
#         raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi : {str(e)}")


# # --- GET route pour les candidats convoqués ---
# @router.get("/candidatures/convoques")
# def get_candidats_convoques(db: Session = Depends(get_db)):
#     convoques = db.query(Candidature).filter(Candidature.statut == "Convoqué").all()
#     result = []

#     for c in convoques:
#         conv = (
#             db.query(Convocation)
#             .filter(Convocation.candidature_id == c.id)
#             .order_by(Convocation.id.desc())
#             .first()
#         )

#         result.append({
#             "id": c.id,
#             "nom": getattr(c, "nom", ""),
#             "prenom": getattr(c, "prenom", ""),
#             "email": getattr(c, "email", ""),
#             "phone": getattr(c, "phone", ""),
#             "statut": getattr(c, "statut", ""),
#             "date_entretien": conv.date_entretien if conv else None,
#             "heure_entretien": conv.heure_entretien if conv else None,
#             "lieu_entretien": conv.lieu_entretien if conv else None
#         })

#     return result



# app/routers/convocation.py - VERSION CORRIGÉE
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Candidature, Convocation
from app.utils.pdf_generator import generate_convocation_pdf
from datetime import datetime, timedelta
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from dotenv import load_dotenv
from sqlalchemy import text

# Load .env
current_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(current_dir, "../.env")
load_dotenv(dotenv_path)

router = APIRouter(prefix="/convocations", tags=["Convocations"])
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from app.schemas.convocation import ConvocationCreate, ConvocationRead

# ==========================================================
# 🔹 CRÉATION CONVOCATION GÉNÉRIQUE - VERSION FIXED
# ==========================================================
@router.post("/create-convocation")
def create_convocation(form: ConvocationCreate, db: Session = Depends(get_db)):
    """
    Création d'une convocation générique - VERSION SQL DIRECT
    """
    try:
        print(f"📝 Création convocation: {form.date} {form.heure}")
        
        # Validation date/heure
        try:
            datetime.strptime(f"{form.date} {form.heure}", "%Y-%m-%d %H:%M")
        except ValueError:
            raise HTTPException(status_code=400, detail="Format date/heure invalide")
        
        # Utiliser SQL DIRECT pour éviter les problèmes de modèle
        insert_query = text("""
            INSERT INTO convocations 
            (date_entretien, heure_entretien, lieu_entretien, status, interval_minute)
            VALUES 
            (:date, :heure, :lieu, 'en attente', :interval)
            RETURNING id, date_entretien, heure_entretien, lieu_entretien, status
        """)
        
        result = db.execute(insert_query, {
            "date": form.date,
            "heure": form.heure,
            "lieu": form.lieu,
            "interval": form.interval_minute or 15
        })
        
        db.commit()
        row = result.fetchone()
        
        logger.info(f"✅ Convocation créée: ID {row[0]}")
        
        return {
            "success": True,
            "message": "Convocation générique créée",
            "convocation": {
                "id": row[0],
                "date_entretien": row[1],
                "heure_entretien": row[2],
                "lieu_entretien": row[3],
                "status": row[4]
            }
        }
        
    except Exception as e:
        logger.error(f"💥 Erreur création convocation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")

# ==========================================================
# 🔹 ENVOI CONVOCATION À CANDIDAT - VERSION FIXED
# ==========================================================
@router.post("/candidatures/{candidature_id}/send-invitation")
def send_invitation(candidature_id: int, db: Session = Depends(get_db)):
    """
    Associe une convocation générique à un candidat
    """
    try:
        logger.info(f"📤 Envoi convocation à candidat ID: {candidature_id}")
        
        # 1. Vérifier candidature avec SQL direct
        candidat_query = text("""
            SELECT id, fullname, email, statut 
            FROM candidatures 
            WHERE id = :id
        """)
        
        candidat_result = db.execute(candidat_query, {"id": candidature_id})
        candidat = candidat_result.fetchone()
        
        if not candidat:
            raise HTTPException(status_code=404, detail=f"Candidat ID {candidature_id} non trouvé")
        
        if candidat[3] != "Sélectionné":
            raise HTTPException(status_code=400, detail="Seul les candidats sélectionnés peuvent recevoir une convocation")
        
        if not candidat[2]:
            raise HTTPException(status_code=400, detail="Email du candidat manquant")

        # 2. Prendre la dernière convocation générique
        conv_query = text("""
            SELECT id, date_entretien, heure_entretien, lieu_entretien
            FROM convocations 
            WHERE candidature_id IS NULL 
            ORDER BY id DESC 
            LIMIT 1
        """)
        
        conv_result = db.execute(conv_query)
        conv = conv_result.fetchone()
        
        if not conv:
            raise HTTPException(
                status_code=404,
                detail="Aucune convocation créée. Créez d'abord une convocation générique."
            )

        # 3. Associer la convocation au candidat
        update_query = text("""
            UPDATE convocations 
            SET candidature_id = :candidature_id 
            WHERE id = :convocation_id
        """)
        
        db.execute(update_query, {
            "candidature_id": candidature_id,
            "convocation_id": conv[0]
        })

        # 4. Mettre à jour statut candidat
        update_candidat_query = text("""
            UPDATE candidatures 
            SET statut = 'Convoqué' 
            WHERE id = :id
        """)
        
        db.execute(update_candidat_query, {"id": candidature_id})
        
        # 5. Récupérer objet Candidature pour générer PDF
        candidature_obj = db.query(Candidature).filter(Candidature.id == candidature_id).first()
        
        # 6. Générer PDF
        try:
            pdf_path = generate_convocation_pdf(candidature_obj, {
                "date_entretien": conv[1],
                "heure_entretien": conv[2],
                "lieu_entretien": conv[3]
            })
            logger.info(f"✅ PDF généré: {pdf_path}")
        except Exception as pdf_error:
            logger.warning(f"⚠️ Erreur génération PDF: {pdf_error}")
            pdf_path = None

        # 7. Envoyer email (optionnel)
        try:
            # SMTP depuis DB
            smtp_query = text("SELECT email, password FROM smtp_config ORDER BY id DESC LIMIT 1")
            smtp_result = db.execute(smtp_query)
            smtp_row = smtp_result.fetchone()
            
            if smtp_row and candidat[2]:
                sender_email = smtp_row[0]
                sender_password = smtp_row[1]
                
                message = MIMEMultipart()
                message["Subject"] = "Convocation entretien - CODEL"
                message["From"] = sender_email
                message["To"] = candidat[2]

                html_content = f"""
                <html>
                <body>
                    <p>Bonjour <strong>{candidat[1]}</strong>,</p>
                    <p>Vous êtes cordialement invité(e) à votre entretien.</p>
                    <p><strong>Date et heure :</strong> {conv[1]} {conv[2]}<br>
                       <strong>Lieu :</strong> {conv[3]}</p>
                    <p>Cordialement,<br><strong>Équipe RH</strong></p>
                </body>
                </html>
                """
                message.attach(MIMEText(html_content, "html", "utf-8"))
                
                if pdf_path and os.path.exists(pdf_path):
                    with open(pdf_path, "rb") as f:
                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            "Content-Disposition",
                            f'attachment; filename="convocation_{candidat[1]}.pdf"'
                        )
                        message.attach(part)
                
                with smtplib.SMTP("smtp.gmail.com", 587) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, candidat[2], message.as_string())
                
                logger.info(f"✅ Email envoyé à {candidat[1]}")
                
                # Mettre à jour status convocation
                update_status_query = text("""
                    UPDATE convocations 
                    SET status = 'envoyée', lien_fichier = :pdf_path
                    WHERE id = :convocation_id
                """)
                db.execute(update_status_query, {
                    "pdf_path": pdf_path,
                    "convocation_id": conv[0]
                })
                
        except Exception as mail_error:
            logger.warning(f"⚠️ Erreur email: {mail_error}")
        
        db.commit()
        
        return {
            "success": True,
            "message": f"Convocation attribuée à {candidat[1]}",
            "candidat": {
                "id": candidat[0],
                "nom": candidat[1],
                "email": candidat[2]
            },
            "convocation": {
                "date": conv[1],
                "heure": conv[2],
                "lieu": conv[3]
            },
            "pdf_generated": pdf_path is not None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"💥 Erreur: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# ==========================================================
# 🔹 LISTE CONVOCATIONS
# ==========================================================
@router.get("/")
def get_convocations(db: Session = Depends(get_db)):
    """Liste toutes les convocations"""
    query = text("""
        SELECT 
            c.id,
            c.date_entretien,
            c.heure_entretien,
            c.lieu_entretien,
            c.status,
            c.candidature_id,
            ca.fullname as candidat_nom
        FROM convocations c
        LEFT JOIN candidatures ca ON c.candidature_id = ca.id
        ORDER BY c.id DESC
    """)
    
    result = db.execute(query)
    convocations = []
    
    for row in result:
        convocations.append({
            "id": row[0],
            "date_entretien": row[1],
            "heure_entretien": row[2],
            "lieu_entretien": row[3],
            "status": row[4],
            "candidature_id": row[5],
            "candidat_nom": row[6]
        })
    
    return convocations

# ==========================================================
# 🔹 CANDIDATS CONVOQUÉS
# ==========================================================
@router.get("/candidatures/convoques")
def get_candidats_convoques(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            c.id,
            c.fullname,
            c.email,
            c.phone,
            c.statut,
            conv.date_entretien,
            conv.heure_entretien,
            conv.lieu_entretien
        FROM candidatures c
        INNER JOIN convocations conv ON c.id = conv.candidature_id
        WHERE c.statut = 'Convoqué'
        ORDER BY conv.date_entretien DESC, conv.heure_entretien DESC
    """)
    
    result = db.execute(query)
    candidats = []
    
    for row in result:
        candidats.append({
            "id": row[0],
            "fullname": row[1],
            "email": row[2],
            "phone": row[3],
            "statut": row[4],
            "date_entretien": row[5],
            "heure_entretien": row[6],
            "lieu_entretien": row[7]
        })
    
    return candidats

# ==========================================================
# 🔹 VÉRIFIER STRUCTURE TABLE
# ==========================================================
@router.get("/check-structure")
def check_table_structure(db: Session = Depends(get_db)):
    """Vérifier la structure de la table"""
    query = text("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default
        FROM information_schema.columns
        WHERE table_name = 'convocations'
        ORDER BY ordinal_position
    """)
    
    result = db.execute(query)
    structure = []
    
    for row in result:
        structure.append({
            "column": row[0],
            "type": row[1],
            "nullable": row[2] == "YES",
            "default": row[3]
        })
    
    return structure