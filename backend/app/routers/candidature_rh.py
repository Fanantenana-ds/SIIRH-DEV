from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.models.models import Candidature, Convocation
from app.utils.pdf_generator import generate_convocation_pdf
from datetime import datetime
import sqlalchemy
import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import json
import traceback

router = APIRouter()
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# ==========================================================
# 🔹 GET candidatures (inchangé)
# ==========================================================
@router.get("/candidatures")
async def get_candidatures():
    try:
        query = sqlalchemy.text("SELECT * FROM candidatures ORDER BY date_candidature DESC")
        with engine.begin() as conn:
            result = conn.execute(query)
            candidatures = []

            for row in result:
                r = dict(row._mapping)
                parsed_cv = r.get("parsed_json")

                if not parsed_cv:
                    texte_cv = None
                    if r.get("raw_cv_s3"):
                        texte_cv = r["raw_cv_s3"]
                    elif r.get("cv_path") and os.path.exists(r["cv_path"]):
                        try:
                            from PyPDF2 import PdfReader
                            reader = PdfReader(r["cv_path"])
                            texte_cv = " ".join([page.extract_text() or "" for page in reader.pages])
                        except Exception:
                            texte_cv = None

                    if texte_cv:
                        try:
                            from app.utils.cv_parser import parse_cv_text
                            parsed_cv = parse_cv_text(texte_cv)
                            r["parsed_json"] = json.dumps(parsed_cv, ensure_ascii=False)
                        except Exception:
                            parsed_cv = {}
                    else:
                        parsed_cv = {}
                else:
                    if isinstance(parsed_cv, str):
                        parsed_cv = json.loads(parsed_cv)

                score_total, breakdown = calculate_score(parsed_cv)
                r["score_total"] = score_total
                r["score_breakdown"] = breakdown

                r["date"] = r.get("date_candidature").isoformat() if r.get("date_candidature") else None
                if r.get("date_convocation"):
                    r["date_convocation"] = r["date_convocation"].isoformat()
                if r.get("heure_convocation"):
                    r["heure_convocation"] = r["heure_convocation"].isoformat()

                candidatures.append(r)

        candidatures.sort(key=lambda x: x.get("score_total", 0), reverse=True)
        return candidatures

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# ==========================================================
# 🔹 PUT sélection / désélection (maintenant mivantana SQL, taloha)
# ==========================================================
@router.put("/candidatures/{id}/select")
async def select_candidature(id: int):
    try:
        query = sqlalchemy.text("UPDATE candidatures SET statut='Sélectionné' WHERE id=:id")
        with engine.begin() as conn:
            res = conn.execute(query, {"id": id})
            if res.rowcount == 0:
                raise HTTPException(status_code=404, detail="Candidature non trouvée")
        return {"message": "Candidature sélectionnée avec succès"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")

@router.put("/candidatures/{id}/deselect")
async def deselect_candidature(id: int):
    try:
        query = sqlalchemy.text("UPDATE candidatures SET statut='Désélectionné' WHERE id=:id")
        with engine.begin() as conn:
            res = conn.execute(query, {"id": id})
            if res.rowcount == 0:
                raise HTTPException(status_code=404, detail="Candidature non trouvée")
        return {"message": "Candidature désélectionnée avec succès"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# ==========================================================
# 🔹 POST convocation + mail automatique (mandefa fotsiny rehefa sélectionné)
# ==========================================================
@router.post("/candidatures/{id}/send-invitation")
async def send_invitation(id: int, db: Session = Depends(get_db)):
    try:
        # --- Vérification candidat ---
        candidature = db.query(Candidature).filter(Candidature.id == id).first()
        if not candidature:
            raise HTTPException(status_code=404, detail="Candidature non trouvée")
        if not candidature.email:
            raise HTTPException(status_code=400, detail="Email du candidat manquant")
        if candidature.statut != "Sélectionné":
            raise HTTPException(status_code=400, detail="Seul les candidats sélectionnés peuvent recevoir une convocation")

        # --- Création convocation si pas encore existante ---
        now = datetime.now()
        convocation = Convocation(
            candidature_id=candidature.id,
            date_entretien=now.strftime("%Y-%m-%d"),
            heure_entretien=now.strftime("%H:%M"),
            lieu_entretien="À définir",
            status="en attente"
        )
        db.add(convocation)
        db.commit()
        db.refresh(convocation)

        # --- Génération PDF ---
        pdf_path = generate_convocation_pdf(candidature, convocation)
        logger.info(f"✅ Convocation PDF généré : {pdf_path}")

        # --- Envoi email ---
        sender_email = os.getenv("SMTP_EMAIL")
        sender_password = os.getenv("SMTP_PASSWORD")
        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", 587))

        if not sender_email or not sender_password:
            logger.error("❌ SMTP credentials non trouvées")
            raise HTTPException(status_code=500, detail="SMTP credentials tsy hita")

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

        try:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(sender_email, sender_password)
                server.sendmail(sender_email, candidature.email, message.as_string())
            logger.info(f"✅ Convocation envoyée à {candidature.fullname} ({candidature.email})")
        except Exception as e:
            logger.error(f"❌ Erreur SMTP : {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi du mail : {str(e)}")

        # --- Mise à jour statut ---
        convocation.status = "envoyée"
        convocation.lien_fichier = pdf_path
        candidature.statut = "Convoqué"
        db.commit()

        return {
            "message": f"Bonjour {candidature.fullname}, votre convocation a été envoyée avec succès ✅",
            "pdf_path": pdf_path,
            "date_entretien": convocation.date_entretien,
            "heure_entretien": convocation.heure_entretien,
            "lieu_entretien": convocation.lieu_entretien,
            "status": convocation.status
        }

    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# ==========================================================
# 🔹 POST ajout candidat comme employé (inchangé)
# ==========================================================
@router.post("/employes/from-candidature/{id}")
async def add_employee_from_candidature(id: int):
    try:
        query = sqlalchemy.text("SELECT * FROM candidatures WHERE id=:id")
        with engine.begin() as conn:
            result = conn.execute(query, {"id": id})
            cand = result.fetchone()
            if not cand:
                raise HTTPException(status_code=404, detail="Candidature non trouvée")
            cand_dict = dict(cand._mapping)

            nom = cand_dict.get("nom") or "Employé"
            prenom = cand_dict.get("prenom") or "Inconnu"

            insert_query = sqlalchemy.text("""
                INSERT INTO employes (nom, prenom, email, tel, poste, candidature_id, date_embauche)
                VALUES (:nom, :prenom, :email, :tel, :poste, :candidature_id, NOW())
            """)
            conn.execute(insert_query, {
                "nom": nom,
                "prenom": prenom,
                "email": cand_dict.get("email"),
                "tel": cand_dict.get("tel"),
                "poste": cand_dict.get("poste"),
                "candidature_id": cand_dict["id"]
            })

            update_query = sqlalchemy.text("UPDATE candidatures SET statut='Employé' WHERE id=:id")
            conn.execute(update_query, {"id": id})

        return {"message": f"Candidat {nom} {prenom} ajouté comme employé avec succès"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# ==========================================================
# 🔹 Fonction calcul score (inchangé)
# ==========================================================
def calculate_score(parsed_cv: dict) -> tuple[int, dict]:
    try:
        with open("scoring_config.json", "r", encoding="utf-8") as f:
            all_configs = json.load(f)

        poste = parsed_cv.get("poste", "Developpeur Python")
        scoring_config = all_configs.get(poste, all_configs["Developpeur Python"])
    except Exception:
        scoring_config = {
            "competences": ["Python", "SQL", "FastAPI"],
            "experience_min": 3,
            "diplome_requis": "Master Informatique",
            "poids": {"competences": 0.4, "experience": 0.3, "formation": 0.2, "projets": 0.1},
        }

    competences_cv = set(parsed_cv.get("competences", []))
    match_comp = len(competences_cv & set(scoring_config["competences"])) / max(1, len(scoring_config["competences"]))
    exp_cv = parsed_cv.get("experience_annees", 0)
    match_exp = min(exp_cv / scoring_config["experience_min"], 1)
    formation_cv = parsed_cv.get("diplome", "")
    match_formation = 1 if formation_cv == scoring_config["diplome_requis"] else 0.5
    projets_cv = set(parsed_cv.get("projets", []))
    match_proj = min(len(projets_cv), 3) / 3

    poids = scoring_config["poids"]
    score_total = round(
        (match_comp * poids["competences"] + match_exp * poids["experience"]
         + match_formation * poids["formation"] + match_proj * poids["projets"]) * 100
    )

    breakdown = {
        "competences": round(match_comp * 100, 2),
        "experience": round(match_exp * 100, 2),
        "formation": round(match_formation * 100, 2),
        "projets": round(match_proj * 100, 2),
    }

    return score_total, breakdown
