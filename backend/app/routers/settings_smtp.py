from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.models.models import Candidature, Convocation
from app.utils.pdf_generator import generate_convocation_pdf
import os, json, smtplib, traceback
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

router = APIRouter()
SMTP_FILE = "smtp_config.json"

# ------------------- Pydantic Model -------------------
class SMTPSettings(BaseModel):
    email: str
    password: str

# ------------------- GET SMTP -------------------
@router.get("/settings/smtp")
def get_smtp():
    if os.path.exists(SMTP_FILE):
        with open(SMTP_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return {"email": data.get("email"), "password": data.get("password")}
    return {"email": "", "password": ""}

# ------------------- POST SMTP -------------------
@router.post("/settings/smtp")
def save_smtp(settings: SMTPSettings):
    try:
        with open(SMTP_FILE, "w", encoding="utf-8") as f:
            json.dump({"email": settings.email, "password": settings.password}, f)
        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de l'enregistrement SMTP: {e}")

# ------------------- GET candidatures (inchangé) -------------------
@router.get("/candidatures")
async def get_candidatures():
    try:
        query = "SELECT * FROM candidatures ORDER BY date_candidature DESC"
        with engine.begin() as conn:
            result = conn.execute(query)
            candidatures = []
            for row in result:
                r = dict(row._mapping)
                # parsing et score...
                candidatures.append(r)
            return candidatures
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

# ------------------- POST envoyer convocation -------------------
@router.post("/candidatures/{id}/send-invitation")
async def send_invitation(id: int, db: Session = Depends(get_db)):
    try:
        candidature = db.query(Candidature).filter(Candidature.id == id).first()
        if not candidature:
            raise HTTPException(status_code=404, detail="Candidature non trouvée")
        if not candidature.email:
            raise HTTPException(status_code=400, detail="Email du candidat manquant")

        # Charger SMTP dynamique
        if os.path.exists(SMTP_FILE):
            with open(SMTP_FILE, "r", encoding="utf-8") as f:
                smtp_data = json.load(f)
            smtp_email = smtp_data.get("email")
            smtp_password = smtp_data.get("password")
        else:
            raise HTTPException(status_code=500, detail="SMTP non configuré")

        # Générer PDF
        now = datetime.now()
        convocation = Convocation(
            date_entretien=now.strftime("%Y-%m-%d"),
            heure_entretien=now.strftime("%H:%M"),
            lieu_entretien="À définir",
            status="en attente",
            candidature_id=candidature.id
        )
        db.add(convocation)
        db.commit()
        db.refresh(convocation)
        pdf_path = generate_convocation_pdf(candidature, convocation)

        # Préparer mail
        message = MIMEMultipart()
        message["Subject"] = "Convocation entretien - CODEL"
        message["From"] = smtp_email
        message["To"] = candidature.email

        html_content = f"""
        <html>
        <body>
        <p>Bonjour <strong>{candidature.fullname}</strong>,</p>
        <p>Vous êtes cordialement invité(e) à votre entretien pour le poste.</p>
        <p><strong>Date et heure :</strong> {convocation.date_entretien} {convocation.heure_entretien}<br>
        <strong>Lieu :</strong> {convocation.lieu_entretien}</p>
        <p>Veuillez consulter le PDF joint pour tous les détails.</p>
        </body>
        </html>
        """
        message.attach(MIMEText(html_content, "html", "utf-8"))

        with open(pdf_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f'attachment; filename="{os.path.basename(pdf_path)}"')
            message.attach(part)

        # Envoyer mail
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                server.login(smtp_email, smtp_password)
                server.sendmail(smtp_email, candidature.email, message.as_string())
        except Exception as e:
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=f"Erreur SMTP: {str(e)}")

        # Mettre à jour statut
        convocation.status = "envoyée"
        convocation.lien_fichier = pdf_path
        candidature.statut = "Convoqué"
        db.commit()

        return {"message": f"Convocation envoyée à {candidature.fullname}", "pdf_path": pdf_path}

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
