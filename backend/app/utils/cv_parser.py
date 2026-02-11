import re
import json

def parse_cv_text(cv_text: str) -> dict:
    """
    Parse texte brut d’un CV pour extraire les infos principales :
    - competences
    - experience (en années)
    - diplome
    - projets

    Retourne un dictionnaire JSON compatible avec calculate_score().
    """

    # 🔹 Normalisation du texte
    text = cv_text.lower()

    # 🔹 Liste de mots-clés compétences communes (extensible)
    competences_keywords = [
        "python", "fastapi", "sql", "docker", "git", "javascript", "react", "html", "css",
        "linux", "windows", "machine learning", "pandas", "excel", "finance",
        "gestion de projet", "communication", "networking", "cloud", "powerbi",
        "recrutement", "formation", "paie"
    ]

    competences_trouvees = [c for c in competences_keywords if c in text]

    # 🔹 Expérience (nombre d’années détecté)
    exp_annees = 0
    exp_match = re.findall(r"(\d+)\s*(?:ans|an|année|années)", text)
    if exp_match:
        exp_annees = max([int(x) for x in exp_match if x.isdigit()] + [0])

    # 🔹 Diplôme (simplifié)
    diplome_match = None
    if "master" in text:
        diplome_match = "Master Informatique"
    elif "licence" in text:
        diplome_match = "Licence Informatique"
    elif "ingénieur" in text:
        diplome_match = "Diplôme d’Ingénieur"
    elif "bachelor" in text:
        diplome_match = "Bachelor"
    elif "doctorat" in text:
        diplome_match = "Doctorat"
    else:
        diplome_match = "Autre"

    # 🔹 Projets (mots-clés simples)
    projets = []
    for line in text.splitlines():
        if "projet" in line or "application" in line:
            projets.append(line.strip()[:120])  # tronqué pour éviter le texte long

    # 🔹 Construction du JSON final
    parsed_json = {
        "competences": list(set(competences_trouvees)),
        "experience_annees": exp_annees,
        "diplome": diplome_match,
        "projets": projets[:5],  # limiter à 5 projets
    }

    return parsed_json










# import re
# import fitz  # PyMuPDF
# from docx import Document
# import pytesseract
# from PIL import Image

# # -------------------
# # Lecture fichiers
# # -------------------

# def read_pdf(file_path):
#     text = ""
#     try:
#         doc = fitz.open(file_path)
#         for page in doc:
#             page_text = page.get_text("text") or ""
#             text += page_text + "\n"

#             # OCR si page quasi vide
#             if len(page_text.strip()) < 10:
#                 pix = page.get_pixmap()
#                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                 text += pytesseract.image_to_string(img) + "\n"
#     except Exception as e:
#         print(f"Erreur lecture PDF: {e}")
#     return text


# def read_docx(file_path):
#     text = ""
#     try:
#         doc = Document(file_path)
#         for para in doc.paragraphs:
#             text += para.text + "\n"

#         for table in doc.tables:
#             for row in table.rows:
#                 text += " ".join(cell.text for cell in row.cells) + "\n"
#     except Exception as e:
#         print(f"Erreur lecture DOCX: {e}")
#     return text


# def read_png(file_path):
#     try:
#         img = Image.open(file_path)
#         return pytesseract.image_to_string(img)
#     except Exception as e:
#         print(f"Erreur lecture image: {e}")
#         return ""


# def extract_text(file_path):
#     path = file_path.lower()
#     if path.endswith(".pdf"):
#         return read_pdf(file_path)
#     if path.endswith(".docx"):
#         return read_docx(file_path)
#     if path.endswith((".png", ".jpg", ".jpeg")):
#         return read_png(file_path)
#     return ""

# # -------------------
# # Extraction données
# # -------------------

# def extract_nom_prenom(text):
#     """
#     PRIORITÉ :
#     1) Ligne contenant 'Nom de expert'
#     2) Signature FULL CAPS
#     3) Sinon valeurs par défaut
#     """
#     text = text.replace('\xa0', ' ')
#     lines = [l.strip() for l in text.splitlines() if l.strip()]

#     # 1️⃣ Nom explicite
#     for line in lines:
#         m = re.search(
#             r'nom\s*(?:de l[’\']expert)?\s*[:\-]?\s*([A-ZÉÈÀÂÊÎÔÛÙ][A-ZÉÈÀÂÊÎÔÛÙ\'\-\s]+)',
#             line,
#             re.IGNORECASE
#         )
#         if m:
#             full = m.group(1).strip()
#             parts = full.split()
#             if len(parts) >= 2:
#                 nom = parts[0].title()
#                 prenom = " ".join(parts[1:]).title()
#                 return nom, prenom

#     # 2️⃣ Signature en majuscules
#     for line in lines:
#         if line.isupper() and len(line.split()) >= 2:
#             parts = line.split()
#             nom = parts[0].title()
#             prenom = " ".join(parts[1:]).title()
#             return nom, prenom

#     # 3️⃣ Fallback propre
#     return "Employé", "Inconnu"


# def extract_phone(text):
#     match = re.search(r'(\+?\d[\d\s]{7,}\d)', text)
#     if match:
#         return re.sub(r'\s+', '', match.group(1))
#     return None


# def extract_experience(text):
#     matches = re.findall(r'(\d+)\s*(?:ans|an|année|années)', text, re.IGNORECASE)
#     return max([int(x) for x in matches], default=0)


# def extract_diplome(text):
#     diplome_map = {
#         'doctorat': 'Doctorat',
#         'ingénieur': 'Ingénieur',
#         'master': 'Master',
#         'licence': 'Licence',
#         'bachelor': 'Bachelor'
#     }
#     for k, v in diplome_map.items():
#         if re.search(k, text, re.IGNORECASE):
#             return v
#     return "Autre"


# def extract_competences(text):
#     competences_keywords = [
#         "python", "fastapi", "sql", "docker", "git", "javascript", "react",
#         "html", "css", "linux", "windows", "machine learning", "pandas",
#         "excel", "finance", "gestion de projet", "communication",
#         "networking", "cloud", "powerbi", "recrutement", "formation", "paie"
#     ]
#     t = text.lower()
#     return list({c for c in competences_keywords if c in t})


# def extract_projets(text):
#     projets = []
#     for line in text.splitlines():
#         if re.search(r'projet|application', line, re.IGNORECASE):
#             projets.append(line.strip()[:120])
#     return projets[:5]

# # -------------------
# # Fonction principale
# # -------------------

# def parse_candidature(files: list) -> dict:
#     combined_text = ""
#     for f in files:
#         combined_text += extract_text(f) + "\n"

#     nom, prenom = extract_nom_prenom(combined_text)

#     return {
#         "nom": nom,
#         "prenom": prenom,
#         "phone": extract_phone(combined_text),
#         "experience_annees": extract_experience(combined_text),
#         "diplome": extract_diplome(combined_text),
#         "competences": extract_competences(combined_text),
#         "projets": extract_projets(combined_text),
#     }




















# import re
# import json
# import fitz  # PyMuPDF
# from docx import Document
# import pytesseract
# from PIL import Image

# # -------------------
# # Lecture fichiers (PDF/DOCX/PNG)
# # -------------------

# def read_pdf(file_path):
#     text = ""
#     try:
#         doc = fitz.open(file_path)
#         for page in doc:
#             page_text = page.get_text("text") or ""
#             text += page_text + "\n"

#             # OCR si page quasi vide
#             if len(page_text.strip()) < 10:
#                 pix = page.get_pixmap()
#                 img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#                 text += pytesseract.image_to_string(img) + "\n"
#     except Exception as e:
#         print(f"Erreur lecture PDF: {e}")
#     return text

# def read_docx(file_path):
#     text = ""
#     try:
#         doc = Document(file_path)
#         for para in doc.paragraphs:
#             text += para.text + "\n"
#         for table in doc.tables:
#             for row in table.rows:
#                 text += " ".join(cell.text for cell in row.cells) + "\n"
#     except Exception as e:
#         print(f"Erreur lecture DOCX: {e}")
#     return text

# def read_png(file_path):
#     try:
#         img = Image.open(file_path)
#         return pytesseract.image_to_string(img)
#     except Exception as e:
#         print(f"Erreur lecture image: {e}")
#         return ""

# def extract_text(file_path):
#     path = file_path.lower()
#     if path.endswith(".pdf"):
#         return read_pdf(file_path)
#     if path.endswith(".docx"):
#         return read_docx(file_path)
#     if path.endswith((".png", ".jpg", ".jpeg")):
#         return read_png(file_path)
#     return ""

# # -------------------
# # Extraction nom/prenom/tel (logique nouvelle)
# # -------------------

# def extract_nom_prenom(text):
#     text = text.replace('\xa0', ' ')
#     lines = [l.strip() for l in text.splitlines() if l.strip()]

#     # 1️⃣ Ligne explicite
#     for line in lines:
#         m = re.search(
#             r'nom\s*(?:de l[’\']expert)?\s*[:\-]?\s*([A-ZÉÈÀÂÊÎÔÛÙ][A-ZÉÈÀÂÊÎÔÛÙ\'\-\s]+)',
#             line,
#             re.IGNORECASE
#         )
#         if m:
#             full = m.group(1).strip()
#             parts = full.split()
#             if len(parts) >= 2:
#                 nom = parts[0].title()
#                 prenom = " ".join(parts[1:]).title()
#                 return nom, prenom

#     # 2️⃣ Signature FULL CAPS
#     for line in lines:
#         if line.isupper() and len(line.split()) >= 2:
#             parts = line.split()
#             nom = parts[0].title()
#             prenom = " ".join(parts[1:]).title()
#             return nom, prenom

#     # 3️⃣ fallback
#     return "Employé", "Inconnu"

# def extract_phone(text):
#     match = re.search(r'(\+?\d[\d\s]{7,}\d)', text)
#     if match:
#         return re.sub(r'\s+', '', match.group(1))
#     return None

# # -------------------
# # Parser original pour score (parse_cv_text)
# # -------------------

# def parse_cv_text(cv_text: str) -> dict:
#     text = cv_text.lower()

#     competences_keywords = [
#         "python", "fastapi", "sql", "docker", "git", "javascript", "react", "html", "css",
#         "linux", "windows", "machine learning", "pandas", "excel", "finance",
#         "gestion de projet", "communication", "networking", "cloud", "powerbi",
#         "recrutement", "formation", "paie"
#     ]
#     competences_trouvees = [c for c in competences_keywords if c in text]

#     exp_annees = 0
#     exp_match = re.findall(r"(\d+)\s*(?:ans|an|année|années)", text)
#     if exp_match:
#         exp_annees = max([int(x) for x in exp_match if x.isdigit()] + [0])

#     diplome_match = None
#     if "master" in text:
#         diplome_match = "Master Informatique"
#     elif "licence" in text:
#         diplome_match = "Licence Informatique"
#     elif "ingénieur" in text:
#         diplome_match = "Diplôme d’Ingénieur"
#     elif "bachelor" in text:
#         diplome_match = "Bachelor"
#     elif "doctorat" in text:
#         diplome_match = "Doctorat"
#     else:
#         diplome_match = "Autre"

#     projets = []
#     for line in text.splitlines():
#         if "projet" in line or "application" in line:
#             projets.append(line.strip()[:120])

#     return {
#         "competences": list(set(competences_trouvees)),
#         "experience_annees": exp_annees,
#         "diplome": diplome_match,
#         "projets": projets[:5],
#     }

# # -------------------
# # Fonction principale parse_candidature
# # -------------------

# def parse_candidature(files: list) -> dict:
#     combined_text = ""
#     for f in files:
#         combined_text += extract_text(f) + "\n"

#     # 🔹 Nom/Prénom/Tel → mail/pdf logique nouvelle
#     nom, prenom = extract_nom_prenom(combined_text)
#     phone = extract_phone(combined_text)

#     # 🔹 Données pour score → parser original
#     score_data = parse_cv_text(combined_text)

#     return {
#         "nom": nom,
#         "prenom": prenom,
#         "phone": phone,
#         **score_data  # competences, experience_annees, diplome, projets
#     }
