# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.db import get_db, engine
# from app.models.models import Candidature, Convocation
# from app.utils.pdf_generator import generate_convocation_pdf
# from datetime import datetime
# import sqlalchemy
# from sqlalchemy import text
# import os
# import logging
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# import json
# import traceback

# router = APIRouter()
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # ==========================================================
# # 🔹 GET candidatures (inchangé)
# # ==========================================================
# @router.get("/candidatures")
# async def get_candidatures():
#     try:
#         query = sqlalchemy.text("SELECT * FROM candidatures ORDER BY date_candidature DESC")
#         with engine.begin() as conn:
#             result = conn.execute(query)
#             candidatures = []

#             for row in result:
#                 r = dict(row._mapping)
#                 parsed_cv = r.get("parsed_json")

#                 if not parsed_cv:
#                     texte_cv = None
#                     if r.get("raw_cv_s3"):
#                         texte_cv = r["raw_cv_s3"]
#                     elif r.get("cv_path") and os.path.exists(r["cv_path"]):
#                         try:
#                             from PyPDF2 import PdfReader
#                             reader = PdfReader(r["cv_path"])
#                             texte_cv = " ".join([page.extract_text() or "" for page in reader.pages])
#                         except Exception:
#                             texte_cv = None

#                     if texte_cv:
#                         try:
#                             from app.utils.cv_parser import parse_cv_text
#                             parsed_cv = parse_cv_text(texte_cv)
#                             r["parsed_json"] = json.dumps(parsed_cv, ensure_ascii=False)
#                         except Exception:
#                             parsed_cv = {}
#                     else:
#                         parsed_cv = {}
#                 else:
#                     if isinstance(parsed_cv, str):
#                         parsed_cv = json.loads(parsed_cv)

#                 score_total, breakdown = calculate_score(parsed_cv)
#                 r["score_total"] = score_total
#                 r["score_breakdown"] = breakdown

#                 r["date"] = r.get("date_candidature").isoformat() if r.get("date_candidature") else None
#                 if r.get("date_convocation"):
#                     r["date_convocation"] = r["date_convocation"].isoformat()
#                 if r.get("heure_convocation"):
#                     r["heure_convocation"] = r["heure_convocation"].isoformat()

#                 candidatures.append(r)

#         candidatures.sort(key=lambda x: x.get("score_total", 0), reverse=True)
#         return candidatures

#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# # ==========================================================
# # 🔹 PUT sélection / désélection (maintenant mivantana SQL, taloha)
# # ==========================================================
# @router.put("/candidatures/{id}/select")
# async def select_candidature(id: int):
#     try:
#         query = sqlalchemy.text("UPDATE candidatures SET statut='Sélectionné' WHERE id=:id")
#         with engine.begin() as conn:
#             res = conn.execute(query, {"id": id})
#             if res.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         return {"message": "Candidature sélectionnée avec succès"}
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# @router.put("/candidatures/{id}/deselect")
# async def deselect_candidature(id: int):
#     try:
#         query = sqlalchemy.text("UPDATE candidatures SET statut='Désélectionné' WHERE id=:id")
#         with engine.begin() as conn:
#             res = conn.execute(query, {"id": id})
#             if res.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         return {"message": "Candidature désélectionnée avec succès"}
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# # ==========================================================
# # 🔹 POST convocation + mail automatique (mandefa fotsiny rehefa sélectionné)
# # ==========================================================
# @router.post("/candidatures/{id}/send-invitation")
# async def send_invitation(id: int, db: Session = Depends(get_db)):
#     try:
#         # --- Vérification candidat ---
#         candidature = db.query(Candidature).filter(Candidature.id == id).first()
#         if not candidature:
#             raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         if not candidature.email:
#             raise HTTPException(status_code=400, detail="Email du candidat manquant")
#         if candidature.statut != "Sélectionné":
#             raise HTTPException(status_code=400, detail="Seul les candidats sélectionnés peuvent recevoir une convocation")

#         # --- Création convocation si pas encore existante ---
#         now = datetime.now()
#         convocation = Convocation(
#             candidature_id=candidature.id,
#             date_entretien=now.strftime("%Y-%m-%d"),
#             heure_entretien=now.strftime("%H:%M"),
#             lieu_entretien="À définir",
#             status="en attente"
#         )
#         db.add(convocation)
#         db.commit()
#         db.refresh(convocation)

#         # --- Génération PDF ---
#         pdf_path = generate_convocation_pdf(candidature, convocation)
#         logger.info(f"✅ Convocation PDF généré : {pdf_path}")

#         # --- Récupération SMTP depuis DB ---
#         smtp_config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
#         if not smtp_config:
#             logger.error("❌ SMTP config non trouvée dans la DB")
#             raise HTTPException(status_code=500, detail="SMTP config tsy hita")

#         sender_email = smtp_config.email
#         sender_password = smtp_config.password
#         smtp_server = smtp_config.server or "smtp.gmail.com"
#         smtp_port = int(smtp_config.port or 587)
#         # --- Préparation email ---
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

#         # --- Envoi email via SMTP DB ---
#         try:
#             with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
#                 server.starttls()
#                 server.login(sender_email, sender_password)
#                 server.sendmail(sender_email, candidature.email, message.as_string())
#             logger.info(f"✅ Convocation envoyée à {candidature.fullname} ({candidature.email})")
#         except Exception as e:
#             logger.error(f"❌ Erreur SMTP : {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi du mail : {str(e)}")

#         # --- Mise à jour statut ---
#         convocation.status = "envoyée"
#         convocation.lien_fichier = pdf_path
#         candidature.statut = "Convoqué"
#         db.commit()

#         return {
#             "message": f"Bonjour {candidature.fullname}, votre convocation a été envoyée avec succès ✅",
#             "pdf_path": pdf_path,
#             "date_entretien": convocation.date_entretien,
#             "heure_entretien": convocation.heure_entretien,
#             "lieu_entretien": convocation.lieu_entretien,
#             "status": convocation.status
#         }

#     except Exception as e:
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# # ==========================================================
# # 🔹 POST ajout candidat comme employé (inchangé)
# # ==========================================================
# @router.post("/employes/from-candidature/{id}")
# async def add_employee_from_candidature(id: int):
#     try:
#         query = sqlalchemy.text("SELECT * FROM candidatures WHERE id=:id")
#         with engine.begin() as conn:
#             result = conn.execute(query, {"id": id})
#             cand = result.fetchone()
#             if not cand:
#                 raise HTTPException(status_code=404, detail="Candidature non trouvée")
#             cand_dict = dict(cand._mapping)

#             nom = cand_dict.get("nom") or "Employé"
#             prenom = cand_dict.get("prenom") or "Inconnu"

#             insert_query = sqlalchemy.text("""
#                 INSERT INTO employes (nom, prenom, email, tel, poste, candidature_id, date_embauche)
#                 VALUES (:nom, :prenom, :email, :tel, :poste, :candidature_id, NOW())
#             """)
#             conn.execute(insert_query, {
#                 "nom": nom,
#                 "prenom": prenom,
#                 "email": cand_dict.get("email"),
#                 "tel": cand_dict.get("tel"),
#                 "poste": cand_dict.get("poste"),
#                 "candidature_id": cand_dict["id"]
#             })

#             update_query = sqlalchemy.text("UPDATE candidatures SET statut='Employé' WHERE id=:id")
#             conn.execute(update_query, {"id": id})

#         return {"message": f"Candidat {nom} {prenom} ajouté comme employé avec succès"}
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# # ==========================================================
# # 🔹 Fonction calcul score (inchangé)
# # ==========================================================
# def calculate_score(parsed_cv: dict) -> tuple[int, dict]:
#     try:
#         with open("scoring_config.json", "r", encoding="utf-8") as f:
#             all_configs = json.load(f)

#         poste = parsed_cv.get("poste", "Developpeur Python")
#         scoring_config = all_configs.get(poste, all_configs["Developpeur Python"])
#     except Exception:
#         scoring_config = {
#             "competences": ["Python", "SQL", "FastAPI"],
#             "experience_min": 3,
#             "diplome_requis": "Master Informatique",
#             "poids": {"competences": 0.4, "experience": 0.3, "formation": 0.2, "projets": 0.1},
#         }

#     competences_cv = set(parsed_cv.get("competences", []))
#     match_comp = len(competences_cv & set(scoring_config["competences"])) / max(1, len(scoring_config["competences"]))
#     exp_cv = parsed_cv.get("experience_annees", 0)
#     match_exp = min(exp_cv / scoring_config["experience_min"], 1)
#     formation_cv = parsed_cv.get("diplome", "")
#     match_formation = 1 if formation_cv == scoring_config["diplome_requis"] else 0.5
#     projets_cv = set(parsed_cv.get("projets", []))
#     match_proj = min(len(projets_cv), 3) / 3

#     poids = scoring_config["poids"]
#     score_total = round(
#         (match_comp * poids["competences"] + match_exp * poids["experience"]
#          + match_formation * poids["formation"] + match_proj * poids["projets"]) * 100
#     )

#     breakdown = {
#         "competences": round(match_comp * 100, 2),
#         "experience": round(match_exp * 100, 2),
#         "formation": round(match_formation * 100, 2),
#         "projets": round(match_proj * 100, 2),
#     }








# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.db import get_db, engine
# from app.models.models import Candidature, Convocation
# from app.utils.pdf_generator import generate_convocation_pdf
# from datetime import datetime
# import sqlalchemy
# from sqlalchemy import text
# import os
# import logging
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# import json
# import traceback
# from fastapi import Request


# router = APIRouter()
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # ==========================================================
# # 🔹 GET candidatures (ORIGINAL + JOIN OFFRE + CONVOCATION)
# # ==========================================================
# @router.get("/candidatures")
# async def get_candidatures():
#     try:
#         query = sqlalchemy.text("""
#             SELECT 
#                 c.*,
#                 o.scoring_criteres,
#                 conv.date_entretien,
#                 conv.heure_entretien,
#                 conv.interval_minute,
#                 conv.lieu_entretien,
#                 c.telephone AS telephone_candidat,
#                 e.telephone AS telephone_employe
#             FROM candidatures c
#             LEFT JOIN offres o 
#                 ON o.id = c.offre_id
#             LEFT JOIN convocations conv
#                 ON conv.candidature_id = c.id
#             LEFT JOIN employes e 
#                 ON e.candidature_id = c.id
#             ORDER BY c.date_candidature DESC
#         """)

#         def clean_tel(tel):
#             if not tel:
#                 return None
#             if isinstance(tel, str) and tel.strip().lower() in [
#                 "non renseigné", "non renseigne", "n/a", "-", ""
#             ]:
#                 return None
#             return tel.strip()

#         with engine.begin() as conn:
#             result = conn.execute(query)
#             candidatures = []
#             nouvelles_candidates = []

#             for row in result:
#                 r = dict(row._mapping)

#                 # ---------- NOM / PRENOM depuis fullname ----------
#                 if r.get("fullname"):
#                     parts = r["fullname"].split()
#                     if len(parts) >= 2:
#                         r["nom"] = parts[-1].upper()           # 🔹 Nom = farany, grande lettre
#                         r["prenom"] = " ".join(parts[:-1])     # 🔹 Prenom = ambiny
#                     else:
#                         r["nom"] = parts[0].upper()
#                         r["prenom"] = ""
#                 else:
#                     r["nom"] = r.get("nom") or ""
#                     r["prenom"] = r.get("prenom") or ""


#                 # ---------- Candidature nouvelle ----------
#                 if not r.get("parsed_json"):
#                     nouvelles_candidates.append(r)

#                 # ---------- Téléphone ----------
#                 tel_candidat = clean_tel(r.get("telephone_candidat"))
#                 tel_employe = clean_tel(r.get("telephone_employe"))
#                 r["telephone"] = tel_candidat or tel_employe

#                 # ---------- Dates ----------
#                 r["date"] = (
#                     r["date_candidature"].isoformat()
#                     if r.get("date_candidature") else None
#                 )
#                 if r.get("date_entretien"):
#                     r["date_entretien"] = str(r["date_entretien"])
#                 if r.get("heure_entretien"):
#                     r["heure_entretien"] = str(r["heure_entretien"])

#                 candidatures.append(r)

#             # ---------- Parsing + scoring pour nouvelles candidatures ----------
#             for r in nouvelles_candidates:
#                 texte_cv = None

#                 if r.get("raw_cv_s3"):
#                     texte_cv = r["raw_cv_s3"]
#                 elif r.get("cv_path") and os.path.exists(r["cv_path"]):
#                     try:
#                         from PyPDF2 import PdfReader
#                         reader = PdfReader(r["cv_path"])
#                         texte_cv = " ".join(
#                             [page.extract_text() or "" for page in reader.pages]
#                         )
#                     except Exception:
#                         texte_cv = None

#                 if texte_cv:
#                     try:
#                         from app.utils.cv_parser import parse_cv_text
#                         parsed_cv = parse_cv_text(texte_cv)

#                         update_parsed = sqlalchemy.text(
#                             "UPDATE candidatures SET parsed_json=:parsed WHERE id=:id"
#                         )
#                         conn.execute(
#                             update_parsed,
#                             {
#                                 "parsed": json.dumps(parsed_cv, ensure_ascii=False),
#                                 "id": r["id"]
#                             }
#                         )
#                     except Exception:
#                         parsed_cv = {}
#                 else:
#                     parsed_cv = {}

#                 # ---------- Score ----------
#                 offre_criteres = r.get("scoring_criteres") or {}
#                 score_total, breakdown = calculate_score(parsed_cv, offre_criteres)

#                 update_score = sqlalchemy.text(
#                     "UPDATE candidatures SET score_total=:score, score_breakdown=:breakdown WHERE id=:id"
#                 )
#                 conn.execute(
#                     update_score,
#                     {
#                         "score": score_total,
#                         "breakdown": json.dumps(breakdown, ensure_ascii=False),
#                         "id": r["id"]
#                     }
#                 )

#                 # ---------- Update retour ----------
#                 r["parsed_json"] = parsed_cv
#                 r["score_total"] = score_total
#                 r["score_breakdown"] = breakdown
#                 r["score"] = score_total

#             # ---------- Sécurité pour anciennes candidatures ----------
#             # ---------- Sécurité pour anciennes candidatures ----------
#             for r in candidatures:
#                 if "score_total" not in r or r["score_total"] is None:
#                     r["score_total"] = r.get("score") or 0

#                 if "score_breakdown" not in r or not r["score_breakdown"]:
#                     r["score_breakdown"] = {}

#             # ✅ Champ simple pour le frontend
#                 r["score"] = r["score_total"]

#         # ---------- Classement ----------
#         candidatures.sort(key=lambda x: x.get("score_total", 0), reverse=True)
#         return candidatures

#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# # ==========================================================
# # 🔹 PUT sélection / désélection (ORIGINAL)
# # ==========================================================
# @router.put("/candidatures/{id}/select")
# async def select_candidature(id: int):
#     try:
#         query = sqlalchemy.text(
#             "UPDATE candidatures SET statut='Sélectionné' WHERE id=:id"
#         )
#         with engine.begin() as conn:
#             res = conn.execute(query, {"id": id})
#             if res.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         return {"message": "Candidature sélectionnée avec succès"}
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# @router.put("/candidatures/{id}/deselect")
# async def deselect_candidature(id: int):
#     try:
#         query = sqlalchemy.text(
#             "UPDATE candidatures SET statut='Désélectionné' WHERE id=:id"
#         )
#         with engine.begin() as conn:
#             res = conn.execute(query, {"id": id})
#             if res.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         return {"message": "Candidature désélectionnée avec succès"}
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# #
# # ==========================================================
# # 🔹 POST convocation + mail automatique (mandefa fotsiny rehefa sélectionné)
# # ==========================================================
# @router.post("/candidatures/{id}/send-invitation")
# async def send_invitation(id: int, db: Session = Depends(get_db)):
#     try:
#         # --- Vérification candidat ---
#         candidature = db.query(Candidature).filter(Candidature.id == id).first()
#         if not candidature:
#             raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         if not candidature.email:
#             raise HTTPException(status_code=400, detail="Email du candidat manquant")
#         if candidature.statut != "Sélectionné":
#             raise HTTPException(status_code=400, detail="Seul les candidats sélectionnés peuvent recevoir une convocation")

#         # --- Création convocation si pas encore existante ---
#         now = datetime.now()
#         convocation = Convocation(
#             candidature_id=candidature.id,
#             date_entretien=now.strftime("%Y-%m-%d"),
#             heure_entretien=now.strftime("%H:%M"),
#             lieu_entretien="À définir",
#             status="en attente"
#         )
#         db.add(convocation)
#         db.commit()
#         db.refresh(convocation)

#         # --- Génération PDF ---
#         pdf_path = generate_convocation_pdf(candidature, convocation)
#         logger.info(f"✅ Convocation PDF généré : {pdf_path}")

#         # --- Récupération SMTP depuis DB ---
#         smtp_config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
#         if not smtp_config:
#             logger.error("❌ SMTP config non trouvée dans la DB")
#             raise HTTPException(status_code=500, detail="SMTP config tsy hita")

#         sender_email = smtp_config.email
#         sender_password = smtp_config.password
#         smtp_server = smtp_config.server or "smtp.gmail.com"
#         smtp_port = int(smtp_config.port or 587)
#         # --- Préparation email ---
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

#         # --- Envoi email via SMTP DB ---
#         try:
#             with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
#                 server.starttls()
#                 server.login(sender_email, sender_password)
#                 server.sendmail(sender_email, candidature.email, message.as_string())
#             logger.info(f"✅ Convocation envoyée à {candidature.fullname} ({candidature.email})")
#         except Exception as e:
#             logger.error(f"❌ Erreur SMTP : {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi du mail : {str(e)}")

#         # --- Mise à jour statut ---
#         convocation.status = "envoyée"
#         convocation.lien_fichier = pdf_path
#         candidature.statut = "Convoqué"
#         db.commit()

#         return {
#             "message": f"Bonjour {candidature.fullname}, votre convocation a été envoyée avec succès ✅",
#             "pdf_path": pdf_path,
#             "date_entretien": convocation.date_entretien,
#             "heure_entretien": convocation.heure_entretien,
#             "lieu_entretien": convocation.lieu_entretien,
#             "status": convocation.status
#         }

#     except Exception as e:
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# # ==========================================================
# # 🔹 CALCUL SCORE (SEUL CHANGEMENT)
# # ==========================================================
# def calculate_score(parsed_cv: dict, offre_criteres: dict) -> tuple[int, dict]:
#     """
#     ✔ Score basé sur critères OFFRE
#     ✔ Fallback automatique = logique originale
#     """

#     if not parsed_cv:
#         return 0, {}

#     scoring_config = offre_criteres if offre_criteres else {
#         "competences": ["Python", "SQL", "FastAPI"],
#         "experience_min": 3,
#         "diplome_requis": "Master Informatique",
#         "poids": {
#             "competences": 0.4,
#             "experience": 0.3,
#             "formation": 0.2,
#             "projets": 0.1
#         }
#     }

#     competences_cv = set(parsed_cv.get("competences", []))
#     competences_offre = set(scoring_config.get("competences", []))
#     match_comp = len(competences_cv & competences_offre) / max(1, len(competences_offre))

#     exp_cv = parsed_cv.get("experience_annees", 0)
#     exp_min = scoring_config.get("experience_min", 1)
#     match_exp = min(exp_cv / exp_min, 1)

#     formation_cv = parsed_cv.get("diplome", "")
#     match_formation = (
#         1 if formation_cv == scoring_config.get("diplome_requis") else 0.5
#     )

#     projets_cv = set(parsed_cv.get("projets", []))
#     match_proj = min(len(projets_cv), 3) / 3

#     poids = scoring_config.get("poids", {})
#     score_total = round(
#         (
#             match_comp * poids.get("competences", 0) +
#             match_exp * poids.get("experience", 0) +
#             match_formation * poids.get("formation", 0) +
#             match_proj * poids.get("projets", 0)
#         ) * 100
#     )

#     breakdown = {
#         "competences": round(match_comp * 100, 2),
#         "experience": round(match_exp * 100, 2),
#         "formation": round(match_formation * 100, 2),
#         "projets": round(match_proj * 100, 2),
#     }

#     return score_total, breakdown




















# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.db import get_db, engine
# from app.models.models import Candidature, Convocation
# from app.utils.pdf_generator import generate_convocation_pdf
# from datetime import datetime
# import sqlalchemy
# from sqlalchemy import text
# import os
# import logging
# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# import json
# import traceback
# from fastapi import Request


# router = APIRouter()
# logger = logging.getLogger(__name__)
# logging.basicConfig(level=logging.INFO)

# # ==========================================================
# # 🔹 GET candidatures (ORIGINAL + JOIN OFFRE + CONVOCATION)
# # ==========================================================
# @router.get("/candidatures")
# async def get_candidatures():
#     try:
#         query = sqlalchemy.text("""
#             SELECT 
#                 c.*,
#                 o.scoring_criteres,
#                 conv.date_entretien,
#                 conv.heure_entretien,
#                 conv.interval_minute,
#                 conv.lieu_entretien,
#                 c.telephone AS telephone_candidat,
#                 e.telephone AS telephone_employe
#             FROM candidatures c
#             LEFT JOIN offres o 
#                 ON o.id = c.offre_id
#             LEFT JOIN convocations conv
#                 ON conv.candidature_id = c.id
#             LEFT JOIN employes e 
#                 ON e.candidature_id = c.id
#             ORDER BY c.date_candidature DESC
#         """)

#         def clean_tel(tel):
#             if not tel:
#                 return None
#             if isinstance(tel, str) and tel.strip().lower() in [
#                 "non renseigné", "non renseigne", "n/a", "-", ""
#             ]:
#                 return None
#             return tel.strip()

#         with engine.begin() as conn:
#             result = conn.execute(query)
#             candidatures = []
#             nouvelles_candidates = []

#             for row in result:
#                 r = dict(row._mapping)

#                 # ---------- NOM / PRENOM (FORMULAIRE PRIORITAIRE) ----------
#                 if r.get("fullname"):  # mail
#                     parts = r["fullname"].split()
#                     if len(parts) >= 2:
#                         r["nom"] = parts[0].upper()             # Nom = voalohany
#                         r["prenom"] = " ".join(parts[1:])       # Prenom = ambiny
#                     else:
#                         r["nom"] = parts[0].upper()
#                         r["prenom"] = ""

#                 # ---------- Candidature nouvelle ----------
#                 if not r.get("parsed_json"):
#                     nouvelles_candidates.append(r)

#                 # ---------- Téléphone ----------
#                 tel_candidat = clean_tel(r.get("telephone_candidat"))
#                 tel_employe = clean_tel(r.get("telephone_employe"))
#                 r["telephone"] = tel_candidat or tel_employe

#                 # ---------- Dates ----------
#                 r["date"] = (
#                     r["date_candidature"].isoformat()
#                     if r.get("date_candidature") else None
#                 )
#                 if r.get("date_entretien"):
#                     r["date_entretien"] = str(r["date_entretien"])
#                 if r.get("heure_entretien"):
#                     r["heure_entretien"] = str(r["heure_entretien"])

#                 candidatures.append(r)

#             # ---------- Parsing + scoring pour nouvelles candidatures ----------
#             for r in nouvelles_candidates:
#                 texte_cv = None

#                 if r.get("raw_cv_s3"):
#                     texte_cv = r["raw_cv_s3"]
#                 elif r.get("cv_path") and os.path.exists(r["cv_path"]):
#                     try:
#                         from PyPDF2 import PdfReader
#                         reader = PdfReader(r["cv_path"])
#                         texte_cv = " ".join(
#                             [page.extract_text() or "" for page in reader.pages]
#                         )
#                     except Exception:
#                         texte_cv = None

#                 if texte_cv:
#                     try:
#                         from app.utils.cv_parser import parse_cv_text
#                         parsed_cv = parse_cv_text(texte_cv)

#                         update_parsed = sqlalchemy.text(
#                             "UPDATE candidatures SET parsed_json=:parsed WHERE id=:id"
#                         )
#                         conn.execute(
#                             update_parsed,
#                             {
#                                 "parsed": json.dumps(parsed_cv, ensure_ascii=False),
#                                 "id": r["id"]
#                             }
#                         )
#                     except Exception:
#                         parsed_cv = {}
#                 else:
#                     parsed_cv = {}

#                 # ---------- Score ----------
#                 offre_criteres = r.get("scoring_criteres") or {}
#                 score_total, breakdown = calculate_score(parsed_cv, offre_criteres)

#                 update_score = sqlalchemy.text(
#                     "UPDATE candidatures SET score_total=:score, score_breakdown=:breakdown WHERE id=:id"
#                 )
#                 conn.execute(
#                     update_score,
#                     {
#                         "score": score_total,
#                         "breakdown": json.dumps(breakdown, ensure_ascii=False),
#                         "id": r["id"]
#                     }
#                 )

#                 # ---------- Update retour ----------
#                 r["parsed_json"] = parsed_cv
#                 r["score_total"] = score_total
#                 r["score_breakdown"] = breakdown
#                 r["score"] = score_total

#             # ---------- Sécurité pour anciennes candidatures ----------
#             # ---------- Sécurité pour anciennes candidatures ----------
#             for r in candidatures:
#                 if "score_total" not in r or r["score_total"] is None:
#                     r["score_total"] = r.get("score") or 0

#                 if "score_breakdown" not in r or not r["score_breakdown"]:
#                     r["score_breakdown"] = {}

#             # ✅ Champ simple pour le frontend
#                 r["score"] = r["score_total"]

#         # ---------- Classement ----------
#         candidatures.sort(key=lambda x: x.get("score_total", 0), reverse=True)
#         return candidatures

#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# # ==========================================================
# # 🔹 PUT sélection / désélection (ORIGINAL)
# # ==========================================================
# @router.put("/candidatures/{id}/select")
# async def select_candidature(id: int):
#     try:
#         query = sqlalchemy.text(
#             "UPDATE candidatures SET statut='Sélectionné' WHERE id=:id"
#         )
#         with engine.begin() as conn:
#             res = conn.execute(query, {"id": id})
#             if res.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         return {"message": "Candidature sélectionnée avec succès"}
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# @router.put("/candidatures/{id}/deselect")
# async def deselect_candidature(id: int):
#     try:
#         query = sqlalchemy.text(
#             "UPDATE candidatures SET statut='Désélectionné' WHERE id=:id"
#         )
#         with engine.begin() as conn:
#             res = conn.execute(query, {"id": id})
#             if res.rowcount == 0:
#                 raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         return {"message": "Candidature désélectionnée avec succès"}
#     except Exception as e:
#         print(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur : {e}")

# #
# # ==========================================================
# # 🔹 POST convocation + mail automatique (mandefa fotsiny rehefa sélectionné)
# # ==========================================================
# @router.post("/candidatures/{id}/send-invitation")
# async def send_invitation(id: int, db: Session = Depends(get_db)):
#     try:
#         # --- Vérification candidat ---
#         candidature = db.query(Candidature).filter(Candidature.id == id).first()
#         if not candidature:
#             raise HTTPException(status_code=404, detail="Candidature non trouvée")
#         if not candidature.email:
#             raise HTTPException(status_code=400, detail="Email du candidat manquant")
#         if candidature.statut != "Sélectionné":
#             raise HTTPException(status_code=400, detail="Seul les candidats sélectionnés peuvent recevoir une convocation")

#         # --- Création convocation si pas encore existante ---
#         now = datetime.now()
#         convocation = Convocation(
#             candidature_id=candidature.id,
#             date_entretien=now.strftime("%Y-%m-%d"),
#             heure_entretien=now.strftime("%H:%M"),
#             lieu_entretien="À définir",
#             status="en attente"
#         )
#         db.add(convocation)
#         db.commit()
#         db.refresh(convocation)

#         # --- Génération PDF ---
#         pdf_path = generate_convocation_pdf(candidature, convocation)
#         logger.info(f"✅ Convocation PDF généré : {pdf_path}")

#         # --- Récupération SMTP depuis DB ---
#         smtp_config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
#         if not smtp_config:
#             logger.error("❌ SMTP config non trouvée dans la DB")
#             raise HTTPException(status_code=500, detail="SMTP config tsy hita")

#         sender_email = smtp_config.email
#         sender_password = smtp_config.password
#         smtp_server = smtp_config.server or "smtp.gmail.com"
#         smtp_port = int(smtp_config.port or 587)
#         # --- Préparation email ---
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

#         # --- Envoi email via SMTP DB ---
#         try:
#             with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
#                 server.starttls()
#                 server.login(sender_email, sender_password)
#                 server.sendmail(sender_email, candidature.email, message.as_string())
#             logger.info(f"✅ Convocation envoyée à {candidature.fullname} ({candidature.email})")
#         except Exception as e:
#             logger.error(f"❌ Erreur SMTP : {str(e)}")
#             raise HTTPException(status_code=500, detail=f"Erreur lors de l'envoi du mail : {str(e)}")

#         # --- Mise à jour statut ---
#         convocation.status = "envoyée"
#         convocation.lien_fichier = pdf_path
#         candidature.statut = "Convoqué"
#         db.commit()

#         return {
#             "message": f"Bonjour {candidature.fullname}, votre convocation a été envoyée avec succès ✅",
#             "pdf_path": pdf_path,
#             "date_entretien": convocation.date_entretien,
#             "heure_entretien": convocation.heure_entretien,
#             "lieu_entretien": convocation.lieu_entretien,
#             "status": convocation.status
#         }

#     except Exception as e:
#         logger.error(traceback.format_exc())
#         raise HTTPException(status_code=500, detail=f"Erreur interne : {str(e)}")

# # ==========================================================
# # 🔹 CALCUL SCORE (SEUL CHANGEMENT)
# # ==========================================================
# def calculate_score(parsed_cv: dict, offre_criteres: dict) -> tuple[int, dict]:
#     """
#     ✔ Score basé sur critères OFFRE
#     ✔ Fallback automatique = logique originale
#     """

#     if not parsed_cv:
#         return 0, {}

#     scoring_config = offre_criteres if offre_criteres else {
#         "competences": ["Python", "SQL", "FastAPI"],
#         "experience_min": 3,
#         "diplome_requis": "Master Informatique",
#         "poids": {
#             "competences": 0.4,
#             "experience": 0.3,
#             "formation": 0.2,
#             "projets": 0.1
#         }
#     }

#     competences_cv = set(parsed_cv.get("competences", []))
#     competences_offre = set(scoring_config.get("competences", []))
#     match_comp = len(competences_cv & competences_offre) / max(1, len(competences_offre))

#     exp_cv = parsed_cv.get("experience_annees", 0)
#     exp_min = scoring_config.get("experience_min", 1)
#     match_exp = min(exp_cv / exp_min, 1)

#     formation_cv = parsed_cv.get("diplome", "")
#     match_formation = (
#         1 if formation_cv == scoring_config.get("diplome_requis") else 0.5
#     )

#     projets_cv = set(parsed_cv.get("projets", []))
#     match_proj = min(len(projets_cv), 3) / 3

#     poids = scoring_config.get("poids", {})
#     score_total = round(
#         (
#             match_comp * poids.get("competences", 0) +
#             match_exp * poids.get("experience", 0) +
#             match_formation * poids.get("formation", 0) +
#             match_proj * poids.get("projets", 0)
#         ) * 100
#     )

#     breakdown = {
#         "competences": round(match_comp * 100, 2),
#         "experience": round(match_exp * 100, 2),
#         "formation": round(match_formation * 100, 2),
#         "projets": round(match_proj * 100, 2),
#     }

#     return score_total, breakdown










from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db, engine
from app.models.models import Candidature, Convocation
from app.utils.pdf_generator import generate_convocation_pdf
from datetime import datetime
import sqlalchemy
from sqlalchemy import text
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
# 🔹 GET candidatures avec scoring automatique précis
# ==========================================================
@router.get("/candidatures")
async def get_candidatures():
    import os, json, traceback
    from datetime import datetime
    from fastapi import HTTPException
    from sqlalchemy.orm import Session
    from app.db import get_db
    from app.models import Candidature
    from app.services import scoring_auto  # <- scoring_auto.py
    from PyPDF2 import PdfReader

    try:
        db: Session = next(get_db())

        # Récupérer toutes les candidatures
        candidatures_db = db.query(Candidature).order_by(Candidature.id.desc()).all()
        candidatures = []
        nouvelles_candidates = []

        for candidat in candidatures_db:
            r = {
                "id": candidat.id,
                "fullname": candidat.fullname,
                "email": candidat.email,
                "phone": candidat.telephone,
                "poste": candidat.poste,
                "statut": candidat.statut,
                "score": candidat.score,        # score déjà existant
                "score_total": candidat.score,  # idem
                "offre_id": candidat.offre_id,
                "ref_offre": candidat.ref_offre,
                "source": candidat.source,
                "raw_cv_s3": candidat.raw_cv_s3,
                "parsed_json": candidat.parsed_json,
                "date": datetime.now().isoformat(),
                "date_candidature": datetime.now().isoformat(),
            }

            # ---------- NOM / PRENOM ----------
            if candidat.fullname:
                parts = candidat.fullname.split()
                if len(parts) >= 2:
                    r["nom"] = parts[0].upper()
                    r["prenom"] = " ".join(parts[1:])
                else:
                    r["nom"] = candidat.fullname
                    r["prenom"] = ""
            else:
                r["nom"] = ""
                r["prenom"] = ""

            # ---------- Candidatures sans parsed_json ----------
            if not candidat.parsed_json:
                nouvelles_candidates.append(r)

            candidatures.append(r)

        # ---------- Parsing + scoring automatique ----------
        for r in nouvelles_candidates:
            texte_cv = None

            # Récupérer texte CV
            if r.get("raw_cv_s3"):
                texte_cv = r["raw_cv_s3"]
            elif hasattr(r, "cv_path") and r.get("cv_path") and os.path.exists(r["cv_path"]):
                try:
                    reader = PdfReader(r["cv_path"])
                    texte_cv = " ".join([page.extract_text() or "" for page in reader.pages])
                except Exception:
                    texte_cv = None

            parsed_cv = {}
            score_total = r.get("score") or 0
            breakdown = {}

            if texte_cv:
                try:
                    from app.utils.cv_parser import parse_cv_text
                    parsed_cv = parse_cv_text(texte_cv)

                    # Mise à jour parsed_json DB
                    update_parsed = f"UPDATE candidatures SET parsed_json=:parsed WHERE id=:id"
                    db.execute(
                        update_parsed,
                        {"parsed": json.dumps(parsed_cv, ensure_ascii=False), "id": r["id"]}
                    )

                    # ---------- Score automatique ----------
                    # Récupérer l'offre correspondante (ici simplifié)
                    offre_dict = json.loads(candidat.offre.scoring_criteres) if candidat.offre and candidat.offre.scoring_criteres else {}
                    score_result = scoring_auto.calculer_score_auto(texte_cv, offre_dict)

                    score_total = score_result["score"]
                    breakdown = score_result

                    # Mise à jour score DB
                    update_score = f"""
                        UPDATE candidatures
                        SET score_total=:score, score_breakdown=:breakdown
                        WHERE id=:id
                    """
                    db.execute(
                        update_score,
                        {"score": score_total, "breakdown": json.dumps(breakdown, ensure_ascii=False), "id": r["id"]}
                    )

                except Exception as e:
                    print(f"⚠️ Erreur parsing/scoring: {e}")
                    parsed_cv = {}
                    score_total = r.get("score") or 0
                    breakdown = {}

            # ---------- Update retour ----------
            r["parsed_json"] = parsed_cv
            r["score_total"] = score_total
            r["score_breakdown"] = breakdown
            r["score"] = score_total

        # ---------- Sécurité anciennes candidatures ----------
        for r in candidatures:
            if "score_total" not in r or r["score_total"] is None:
                r["score_total"] = r.get("score") or 0
            if "score_breakdown" not in r or not r["score_breakdown"]:
                r["score_breakdown"] = {}
            r["score"] = r["score_total"]

        # ---------- Classement ----------
        candidatures.sort(key=lambda x: x.get("score_total", 0), reverse=True)

        return candidatures

    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# ==========================================================
# 🔹 GET candidatures (SIMPLE / FRONTEND)
# ==========================================================
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import traceback
from app.db import get_db
from app.models import Candidature
import logging

logger = logging.getLogger("app")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

@router.get("/candidatures")
def get_candidatures(db: Session = Depends(get_db)):
    try:
        candidatures_db = db.query(Candidature).order_by(Candidature.id.desc()).all()
        
        candidatures = []
        for candidat in candidatures_db:
            r = {
                "id": candidat.id,
                "fullname": candidat.fullname,
                "email": candidat.email,
                "phone": getattr(candidat, "telephone", None),      # fallback
                "poste": candidat.poste,
                "statut": candidat.statut,
                "score": float(candidat.score) if candidat.score is not None else 10.0,
                "score_total": float(candidat.score) if candidat.score is not None else 10.0,
                "offre_id": getattr(candidat, "offre_id", None),
                "ref_offre": getattr(candidat, "offre_id", None),
                "source": getattr(candidat, "source", None),
                "raw_cv_s3": getattr(candidat, "raw_cv_s3", None),
                "parsed_json": getattr(candidat, "parsed_json", None),
                "date": datetime.now().isoformat(),
                "date_candidature": datetime.now().isoformat(),
            }

            # Nom / Prénom
            if candidat.fullname:
                parts = candidat.fullname.split()
                if len(parts) >= 2:
                    r["nom"] = parts[0]
                    r["prenom"] = " ".join(parts[1:])
                else:
                    r["nom"] = candidat.fullname
                    r["prenom"] = ""
            else:
                r["nom"] = ""
                r["prenom"] = ""
            
            candidatures.append(r)
        
        # Trier par score_total
        candidatures.sort(key=lambda x: x.get("score_total", 0), reverse=True)
        
        logger.info(f"✅ {len(candidatures)} candidatures récupérées")
        return candidatures

    except Exception as e:
        logger.error(f"❌ Erreur get_candidatures: {e}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# ==========================================================
# 🔹 PUT sélection / désélection
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
# 🔹 POST convocation + mail automatique
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

        # --- Récupération SMTP depuis DB ---
        smtp_config = db.execute(text("SELECT * FROM smtp_config ORDER BY id DESC LIMIT 1")).fetchone()
        if not smtp_config:
            logger.error("❌ SMTP config non trouvée dans la DB")
            raise HTTPException(status_code=500, detail="SMTP config tsy hita")

        sender_email = smtp_config.email
        sender_password = smtp_config.password
        smtp_server = smtp_config.server or "smtp.gmail.com"
        smtp_port = int(smtp_config.port or 587)
        
        # --- Préparation email ---
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

        # --- Envoi email via SMTP DB ---
        try:
            with smtplib.SMTP(smtp_server, int(smtp_port)) as server:
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
# 🔹 POST ajout candidat comme employé
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
    