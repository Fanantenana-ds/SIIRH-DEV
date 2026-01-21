# from docx import Document
# import pdfplumber
# import re

# # --- 1️⃣ Parser DOCX ---
# def parse_docx(path: str) -> str:
#     doc = Document(path)
#     text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
#     return text

# # --- 2️⃣ Parser PDF ---
# def parse_pdf(path: str) -> str:
#     text = ""
#     with pdfplumber.open(path) as pdf:
#         for page in pdf.pages:
#             page_text = page.extract_text()
#             if page_text:
#                 text += page_text + "\n"
#     return text

# # --- 3️⃣ Extraction automatique d'informations ---
# def extract_info(text: str, project_keywords: list = None) -> dict:
#     """
#     Extrait les informations principales du CV.
#     Optionnel: project_keywords pour extraire mots-clés projets spécifiques.
#     """
#     # Email
#     email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)

#     # Téléphone
#     phone = re.search(r"\+?\d[\d\s().-]{7,}", text)

#     # Nom/Prénom
#     name_match = re.findall(r"([A-Z][a-z]+)", text)
#     firstname, lastname = (name_match[0], name_match[1]) if len(name_match) >= 2 else (None, None)

#     # Compétences générales
#     skill_keywords = [
#         "Python", "Django", "FastAPI", "React", "SQL", "Docker", "Kubernetes",
#         "Machine Learning", "Data Analysis", "Excel", "Communication", "Leadership"
#     ]
#     skills = [kw for kw in skill_keywords if re.search(rf"\b{kw}\b", text, re.IGNORECASE)]

#     # Diplômes
#     diploma_keywords = ["Licence", "Master", "Doctorat", "Ingénieur", "Bachelor"]
#     diplomes = [d for d in diploma_keywords if re.search(rf"\b{d}\b", text, re.IGNORECASE)]

#     # Langues
#     langues_keywords = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Malgache"]
#     langues = [l for l in langues_keywords if re.search(rf"\b{l}\b", text, re.IGNORECASE)]

#     # Expérience
#     exp_years_match = re.findall(r"(\d+)\s+(ans|années|an)", text.lower())
#     exp_years = max([int(e[0]) for e in exp_years_match], default=0)

#     # --- Extraction mots-clés projets spécifiques ---
#     project_matches = []
#     if project_keywords:
#         for kw in project_keywords:
#             if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE):
#                 project_matches.append(kw)

#     return {
#         "firstname": firstname,
#         "lastname": lastname,
#         "email": email.group() if email else None,
#         "phone": phone.group() if phone else None,
#         "skills": skills,
#         "diplomes": diplomes,
#         "langues": langues,
#         "exp_years": exp_years,
#         "projects": project_matches,  # nouveauté pour scoring automatique
#         "text": text[:3000],  # résumé pour scoring
#     }




















from docx import Document
import pdfplumber
import re

# --- 1️⃣ Parser DOCX ---
def parse_docx(path: str) -> str:
    doc = Document(path)
    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    return text

# --- 2️⃣ Parser PDF ---
def parse_pdf(path: str) -> str:
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# --- 3️⃣ Extraction automatique d'informations ---
def extract_info(text: str, project_keywords: list = None) -> dict:
    """
    Extrait les informations principales du CV.
    Optionnel: project_keywords pour extraire mots-clés projets spécifiques.
    """
    # Email
    email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", text)

    # Téléphone
    phone = re.search(r"\+?\d[\d\s().-]{7,}", text)

    # Nom/Prénom
    name_match = re.findall(r"([A-Z][a-z]+)", text)
    firstname, lastname = (name_match[0], name_match[1]) if len(name_match) >= 2 else (None, None)

    # Compétences générales
    skill_keywords = [
        "Python", "Django", "FastAPI", "React", "SQL", "Docker", "Kubernetes",
        "Machine Learning", "Data Analysis", "Excel", "Communication", "Leadership"
    ]
    skills = [kw for kw in skill_keywords if re.search(rf"\b{kw}\b", text, re.IGNORECASE)]

    # Diplômes
    diploma_keywords = ["Licence", "Master", "Doctorat", "Ingénieur", "Bachelor"]
    diplomes = [d for d in diploma_keywords if re.search(rf"\b{d}\b", text, re.IGNORECASE)]

    # Langues
    langues_keywords = ["Français", "Anglais", "Espagnol", "Allemand", "Italien", "Malgache"]
    langues = [l for l in langues_keywords if re.search(rf"\b{l}\b", text, re.IGNORECASE)]

    # Expérience
    exp_years_match = re.findall(r"(\d+)\s+(ans|années|an)", text.lower())
    exp_years = max([int(e[0]) for e in exp_years_match], default=0)

    # --- Extraction mots-clés projets spécifiques ---
    project_matches = []
    if project_keywords:
        for kw in project_keywords:
            if re.search(rf"\b{re.escape(kw)}\b", text, re.IGNORECASE):
                project_matches.append(kw)

    return {
        "firstname": firstname,
        "lastname": lastname,
        "email": email.group() if email else None,
        "phone": phone.group() if phone else None,
        "skills": skills,
        "diplomes": diplomes,
        "langues": langues,
        "exp_years": exp_years,
        "projects": project_matches,  # nouveauté pour scoring automatique
        "text": text[:3000],  # résumé pour scoring
    }

# --- 4️⃣ Extraction nom + téléphone simple ---
def extract_name_phone(text: str) -> dict:
    """
    Fonction dédiée pour extraire le nom complet et le téléphone.
    Nécessaire pour upload_service.py afin d'éviter ImportError.
    """
    name = None
    phone = None

    # Exemple rapide: prend les 2 premiers mots avec majuscule pour nom/prénom
    name_match = re.findall(r"[A-Z][a-z]+", text)
    if len(name_match) >= 2:
        name = f"{name_match[0]} {name_match[1]}"

    # Téléphone simple
    phone_match = re.search(r"\+?\d[\d\s().-]{7,}", text)
    if phone_match:
        phone = phone_match.group()

    return {
        "fullname": name,
        "phone": phone
    }
