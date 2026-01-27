from fastapi import APIRouter
from fastapi_utils.tasks import repeat_every
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Candidature
from app.models.offres import Offre
from app.services.upload_service import process_cv_from_bytes

import imaplib, email, os, json, traceback, re, socket
from datetime import datetime
from email.header import decode_header, make_header

router = APIRouter()
SMTP_FILE = "smtp_config.json"
MAIL_CHECK_INTERVAL = 5  # secondes

# ================= HELPERS =================

def load_smtp_config():
    with open(SMTP_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_offre_ref(subject: str):
    try:
        decoded = str(make_header(decode_header(subject)))
    except Exception:
        decoded = subject
    match = re.search(r"REF[_-]2026[_-]\d{5}", decoded)
    return match.group(0) if match else None

def extract_name_from_email(addr: str):
    base = addr.split("@")[0]
    parts = re.split(r"[._\-]", base)
    prenom = parts[0].capitalize()
    nom = parts[-1].capitalize() if len(parts) > 1 else ""
    return f"{prenom} {nom}".strip()

def internet_available(host="imap.gmail.com", port=993, timeout=5):
    """Vérifie si le réseau/DNS est disponible"""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

# ================= BACKGROUND TASK =================

@router.on_event("startup")
@repeat_every(seconds=MAIL_CHECK_INTERVAL, wait_first=True)
def check_new_mails():
    if not internet_available():
        return

    db: Session = next(get_db())

    try:
        smtp = load_smtp_config()

        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(smtp["email"], smtp["password"])
        mail.select("inbox")

        status, messages = mail.search(None, "(UNSEEN)")
        if not messages or not messages[0]:
            mail.logout()
            return

        for num in messages[0].split()[::-1]:
            _, data = mail.fetch(num, "(RFC822)")
            msg = email.message_from_bytes(data[0][1])

            from_email = email.utils.parseaddr(msg.get("From"))[1]

            # Ignorer spam / réseaux sociaux
            if any(x in from_email for x in ["facebook", "linkedin", "instagram", "tiktok"]):
                mail.store(num, "+FLAGS", "\\Seen")
                continue

            subject = msg.get("Subject", "")
            ref = extract_offre_ref(subject)
            if not ref:
                mail.store(num, "+FLAGS", "\\Seen")
                continue

            offre = db.query(Offre).filter(Offre.job_ref == ref).first()
            if not offre:
                mail.store(num, "+FLAGS", "\\Seen")
                continue

            # 🔹 Nom par défaut avy amin'ny mail
            fullname = extract_name_from_email(from_email)

            candidature = Candidature(
                fullname=fullname,
                email=from_email,
                poste=offre.title,
                statut="En attente",
                offre_id=offre.id
            )
            db.add(candidature)
            db.commit()
            db.refresh(candidature)

            # Pièces jointes → MinIO & parsing CV
            for part in msg.walk():
                if part.get_filename():
                    filename = part.get_filename()
                    content = part.get_payload(decode=True)
                    if filename and filename.lower().endswith((".pdf", ".docx")):
                        cv_info = process_cv_from_bytes(
                            db,
                            content,
                            filename,
                            candidature.id
                        )

                        # 🔹 Fanavaozana ny fullname raha voaray avy amin'ny CV
                        firstname = cv_info.get("firstname")
                        lastname = cv_info.get("lastname")
                        if firstname or lastname:
                            candidature.fullname = f"{firstname or ''} {lastname or ''}".strip()
                            db.commit()

            print(f"✅ Candidature mail ID={candidature.id}")
            mail.store(num, "+FLAGS", "\\Seen")

        mail.logout()

    except Exception:
        traceback.print_exc()

    finally:
        db.close()

