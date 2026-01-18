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

# Load .env
current_dir = os.path.dirname(__file__)
dotenv_path = os.path.join(current_dir, "../.env")
load_dotenv(dotenv_path)

router = APIRouter(prefix="/convocations", tags=["Convocations"])
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

from app.schemas.convocation import ConvocationCreate, ConvocationRead

# --- Création convocation générique (POST) ---
@router.post("/create-convocation", response_model=ConvocationRead)
def create_convocation(form: ConvocationCreate, db: Session = Depends(get_db)):
    """
    Création d'une convocation générique, sans candidat associé.
    """
    # Récupération de la dernière convocation pour calculer l'heure suivante
    last_conv = db.query(Convocation).order_by(Convocation.id.desc()).first()

    try:
        start_datetime = datetime.strptime(f"{form.date} {form.heure}", "%Y-%m-%d %H:%M")
        if last_conv:
            last_dt = datetime.strptime(f"{last_conv.date_entretien} {last_conv.heure_entretien}", "%Y-%m-%d %H:%M")
            start_datetime = last_dt + timedelta(minutes=form.interval_minute or 15)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Format date/heure invalide : {str(e)}")

    conv = Convocation(
        date_entretien=start_datetime.strftime("%Y-%m-%d"),
        heure_entretien=start_datetime.strftime("%H:%M"),
        lieu_entretien=form.lieu,
        status="en attente",
        candidature_id=None  # Générique
    )

    db.add(conv)
    db.commit()
    db.refresh(conv)

    logger.info(f"✅ Convocation générique créée à {conv.heure_entretien}")
    return conv


# --- Envoi convocation à un candidat sélectionné (POST) ---
@router.post("/candidatures/{candidature_id}/send-invitation")
def send_invitation(candidature_id: int, db: Session = Depends(get_db)):
    """
    Prend le dernier convocation générique et l'associe au candidat sélectionné,
    ajoute l'interval si nécessaire, génère le PDF et envoie l'email.
    """
    candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
    if not candidature:
        raise HTTPException(status_code=404, detail=f"Candidat introuvable avec id {candidature_id}")

    if candidature.statut != "Sélectionné":
        raise HTTPException(status_code=400, detail="Seul les candidats sélectionnés peuvent recevoir une convocation")

    if not candidature.email:
        raise HTTPException(status_code=400, detail="Email du candidat manquant")

    # Prendre la dernière convocation générique (candidature_id = None)
    convocation = (
        db.query(Convocation)
        .filter(Convocation.candidature_id == None)
        .order_by(Convocation.id.desc())
        .first()
    )

    if not convocation:
        raise HTTPException(
            status_code=404,
            detail="Aucune convocation créée. Veuillez d'abord créer une convocation générique."
        )

    # Associer la convocation au candidat
    convocation.candidature_id = candidature.id

    try:
        pdf_path = generate_convocation_pdf(candidature, convocation)
        logger.info(f"✅ Convocation PDF généré : {pdf_path}")

        # SMTP
        sender_email = os.getenv("SMTP_EMAIL")
        sender_password = os.getenv("SMTP_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))

        if not sender_email or not sender_password:
            logger.error("❌ SMTP credentials non trouvées")
            raise HTTPException(status_code=500, detail="SMTP credentials mankany .env tsy hita")

        message = MIMEMultipart()
        message["Subject"] = "Convocation entretien - CODEL"
        message["From"] = sender_email
        message["To"] = candidature.email

        html_content = f"""
        <html>
        <body>
            <p>Bonjour <strong>{candidature.fullname}</strong>,</p>
            <p>Vous êtes cordialement invité(e) à votre entretien pour le poste.</p>
            <p><strong>Date et heure :</strong> {convocation.date_entretien} {convocation.heure_entretien}<br>
               <strong>Lieu :</strong> {convocation.lieu_entretien}</p>
            <p>Veuillez consulter le PDF joint pour tous les détails et apporter les documents nécessaires.</p>
            <p><em>Message automatique, ne pas répondre à ce mail.</em></p>
            <p>Cordialement,<br><strong>Équipe RH</strong></p>
        </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html", "utf-8"))

        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f'attachment; filename="{os.path.basename(pdf_path)}"'
            )
            message.attach(part)

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, candidature.email, message.as_string())

        # Mise à jour statut
        convocation.status = "envoyée"
        convocation.lien_fichier = pdf_path
        candidature.statut = "Convoqué"
        db.commit()

        logger.info(f"✅ Convocation envoyée à {candidature.fullname} ({candidature.email})")

        return {
            "message": f"Bonjour {candidature.fullname}, votre convocation a été envoyée avec succès ✅",
            "pdf_path": pdf_path,
            "date_entretien": convocation.date_entretien,
            "heure_entretien": convocation.heure_entretien,
            "lieu_entretien": convocation.lieu_entretien,
            "status": convocation.status
        }

    except Exception as e:
        logger.error(f"❌ Erreur lors de l'envoi de convocation : {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi : {str(e)}")


# --- GET route pour les candidats convoqués ---
@router.get("/candidatures/convoques")
def get_candidats_convoques(db: Session = Depends(get_db)):
    convoques = db.query(Candidature).filter(Candidature.statut == "Convoqué").all()
    result = []

    for c in convoques:
        conv = (
            db.query(Convocation)
            .filter(Convocation.candidature_id == c.id)
            .order_by(Convocation.id.desc())
            .first()
        )

        result.append({
            "id": c.id,
            "nom": getattr(c, "nom", ""),
            "prenom": getattr(c, "prenom", ""),
            "email": getattr(c, "email", ""),
            "phone": getattr(c, "phone", ""),
            "statut": getattr(c, "statut", ""),
            "date_entretien": conv.date_entretien if conv else None,
            "heure_entretien": conv.heure_entretien if conv else None,
            "lieu_entretien": conv.lieu_entretien if conv else None
        })

    return result
