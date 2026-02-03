# backend/app/utils/pdf_generator.py - VERSION CORRIGÉE
from fpdf import FPDF
from datetime import datetime
import os
import re

# ==========================================================
# Mapping mois en français
# ==========================================================
MOIS_FR = {
    1: "Janvier",
    2: "Février",
    3: "Mars",
    4: "Avril",
    5: "Mai",
    6: "Juin",
    7: "Juillet",
    8: "Août",
    9: "Septembre",
    10: "Octobre",
    11: "Novembre",
    12: "Décembre"
}

def date_fr(date_obj: datetime, lieu: str = "Antananarivo"):
    return f"{lieu}, le {date_obj.day} {MOIS_FR[date_obj.month]} {date_obj.year}"

# ==========================================================
# FONCTION POUR NETTOYER LE TEXTE (AJOUTÉE)
# ==========================================================
def clean_text(text):
    """Nettoyer le texte pour éviter les problèmes d'encoding dans PDF"""
    if not text:
        return ""
    
    # Supprimer les emojis
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    
    text = emoji_pattern.sub('', text)
    
    # Normaliser les caractères français
    replacements = {
        'à': 'a', 'â': 'a', 'ä': 'a',
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c',
        'œ': 'oe', 'æ': 'ae',
        'À': 'A', 'Â': 'A', 'Ä': 'A',
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'Î': 'I', 'Ï': 'I',
        'Ô': 'O', 'Ö': 'O',
        'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C',
        'Œ': 'OE', 'Æ': 'AE',
    }
    
    for old, new in replacements.items():
        text = text.replace(old, new)
    
    # Encoder en latin-1 safe
    try:
        text = text.encode('latin-1', 'ignore').decode('latin-1')
    except:
        try:
            text = text.encode('utf-8', 'ignore').decode('utf-8')
        except:
            text = text.encode('ascii', 'ignore').decode('ascii')
    
    return text.strip()

# ==========================================================
# PDF CONVOCATION ENTRETIEN (CORRIGÉ)
# ==========================================================
def generate_convocation_pdf(candidat, convocation):
    pdf = FPDF()
    pdf.add_page()

    # Logo
    logo_path = os.path.join("app", "assets", "codel_logo1.png")
    if os.path.exists(logo_path):
        page_width = pdf.w - 2 * pdf.l_margin
        logo_width = 33
        x_logo = (page_width - logo_width) / 2 + pdf.l_margin
        pdf.image(logo_path, x=x_logo, y=30, w=logo_width)
    pdf.ln(55)

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Convocation à l'entretien", ln=True, align="C")
    pdf.ln(12)

    # Content - UTILISER clean_text
    pdf.set_font("Arial", "", 12)
    
    # Nettoyer les données
    nom_complet_raw = getattr(candidat, "fullname", None) or \
                      f"{getattr(candidat, 'prenom', '')} {getattr(candidat, 'nom', '')}".strip() \
                      or "Candidat"
    nom_complet = clean_text(nom_complet_raw)
    
    poste_raw = getattr(candidat, "poste", "poste non défini")
    poste = clean_text(poste_raw)
    
    date_entretien = getattr(convocation, "date_entretien", "à définir")
    heure_entretien = getattr(convocation, "heure_entretien", "à définir")
    
    lieu_entretien_raw = getattr(convocation, "lieu_entretien", "à définir")
    lieu_entretien = clean_text(lieu_entretien_raw)

    corps = f"""
Bonjour {nom_complet},

Vous êtes cordialement invité(e) à notre entretien pour le poste de {poste}.

Date de l'entretien : {date_entretien}
Heure : {heure_entretien}
Lieu : {lieu_entretien}

Veuillez apporter tous les documents nécessaires.

Cordialement,
Équipe RH
"""
    pdf.multi_cell(0, 8, corps)
    pdf.ln(15)

    # Footer date
    date_str = date_fr(datetime.now(), "Antananarivo")
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 10, date_str, ln=True)
    pdf.ln(5)

    # File with timestamp - UTILISER nom nettoyé pour le nom de fichier
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nom_fichier = re.sub(r'[^\w\s-]', '', nom_complet.replace(' ', '_'))
    file_path = f"/tmp/convocation_{nom_fichier}_{timestamp}.pdf"
    pdf.output(file_path, 'F')
    return file_path

# ==========================================================
# PDF CONVOCATION DISCIPLINE (CORRIGÉ)
# ==========================================================
def generate_convocation_discipline_pdf(candidat, convocation):
    pdf = FPDF()
    pdf.add_page()

    # Logo
    logo_path = os.path.join("app", "assets", "codel_logo1.png")
    if os.path.exists(logo_path):
        page_width = pdf.w - 2 * pdf.l_margin
        logo_width = 33
        x_logo = (page_width - logo_width) / 2 + pdf.l_margin
        pdf.image(logo_path, x=x_logo, y=30, w=logo_width)
    pdf.ln(55)

    # Title
    pdf.set_font("Arial", "B", 16)
    titre_raw = f"Convocation disciplinaire - {convocation.get('fault_type', 'Faute')}"
    titre = clean_text(titre_raw)
    pdf.cell(0, 10, titre, ln=True, align="C")
    pdf.ln(12)

    # Content
    pdf.set_font("Arial", "", 12)
    nom_complet_raw = getattr(candidat, "fullname", None) or \
                      f"{getattr(candidat, 'prenom','')} {getattr(candidat,'nom','')}".strip() or "Employé"
    nom_complet = clean_text(nom_complet_raw)
    
    type_faute_raw = convocation.get("fault_type", "à définir")
    type_faute = clean_text(type_faute_raw)
    
    date_conv = convocation.get("date_convocation", "à définir")
    heure_conv = convocation.get("heure_convocation", "à définir")
    
    lieu_corps_raw = convocation.get("lieu_convocation", "Bureau RH")
    lieu_corps = clean_text(lieu_corps_raw)

    corps = f"""
Bonjour {nom_complet},

Vous êtes convoqué(e) à une convocation disciplinaire concernant : {type_faute}.

Date : {date_conv}
Heure : {heure_conv}
Lieu : {lieu_corps}

Veuillez vous présenter avec tous les documents nécessaires et préparer vos explications.

Cordialement,
Équipe RH
"""
    pdf.multi_cell(0, 8, corps)
    pdf.ln(15)

    # Footer date avec lieu dynamique
    lieu_footer_raw = convocation.get("lieu_convocation", "Antananarivo")
    lieu_footer = clean_text(lieu_footer_raw)
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 10, date_fr(datetime.now(), lieu_footer), ln=True)
    pdf.ln(5)

    # File with timestamp
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nom_fichier = re.sub(r'[^\w\s-]', '', nom_complet.replace(' ', '_'))
    file_path = f"/tmp/convocation_discipline_{nom_fichier}_{timestamp}.pdf"
    pdf.output(file_path, 'F')
    return file_path

# ==========================================================
# PDF DECISION DISCIPLINAIRE (CORRIGÉ)
# ==========================================================
def generate_decision_pdf(candidat, decision):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Décision disciplinaire", ln=True, align="C")
    pdf.ln(10)

    nom_complet_raw = getattr(candidat, "fullname", None) or \
                      f"{getattr(candidat, 'prenom','')} {getattr(candidat,'nom','')}".strip() \
                      or "Candidat"
    nom_complet = clean_text(nom_complet_raw)

    pdf.set_font("Arial", "", 12)
    
    decision_type_raw = getattr(decision, 'decision_type', '—')
    decision_type = clean_text(decision_type_raw)
    
    decision_notes_raw = getattr(decision, 'decision_notes', '—')
    decision_notes = clean_text(decision_notes_raw)
    
    pdf.multi_cell(
        0, 8,
        f"Employé : {nom_complet}\n"
        f"Sanction : {decision_type}\n"
        f"Explication : {decision_notes}"
    )
    pdf.ln(15)

    date_str = date_fr(datetime.now())
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 10, date_str, ln=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nom_fichier = re.sub(r'[^\w\s-]', '', nom_complet.replace(' ', '_'))
    file_path = f"/tmp/decision_{nom_fichier}_{timestamp}.pdf"
    pdf.output(file_path, 'F')
    return file_path

# ==========================================================
# PDF LETTRE DE LICENCIEMENT (CORRIGÉ)
# ==========================================================
def generate_licenciement_letter(candidat, data):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Lettre de licenciement", ln=True, align="C")
    pdf.ln(12)

    # Employee
    nom_complet_raw = getattr(candidat, "fullname", None) or \
                      f"{getattr(candidat, 'prenom','')} {getattr(candidat,'nom','')}".strip() \
                      or "Candidat"
    nom_complet = clean_text(nom_complet_raw)

    pdf.set_font("Arial", "", 12)

    motif_raw = data.get("motif", "Non précisé") if data else "Non précisé"
    motif = clean_text(motif_raw)
    
    date_effet = data.get("date", datetime.now().strftime("%d/%m/%Y")) if data else datetime.now().strftime("%d/%m/%Y")

    corps = f"""
Madame/Monsieur {nom_complet},

Par la présente, nous vous informons officiellement de votre licenciement.

Motif : {motif}
Date d'effet : {date_effet}

Vous serez contacté(e) par le service RH pour les formalités administratives.

Cordialement,
Équipe RH
"""
    pdf.multi_cell(0, 8, corps)

    pdf.ln(10)
    date_str = date_fr(datetime.now())
    pdf.set_font("Arial", "I", 11)
    pdf.cell(0, 10, date_str, ln=True)

    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    nom_fichier = re.sub(r'[^\w\s-]', '', nom_complet.replace(' ', '_'))
    file_path = f"/tmp/lettre_licenciement_{nom_fichier}_{timestamp}.pdf"
    pdf.output(file_path, 'F')
    return file_path

# ==========================================================
# FONCTION UTILITAIRE SUPPLEMENTAIRE
# ==========================================================
def clean_candidate_name(candidat):
    """Nettoyer le nom d'un candidat pour usage PDF"""
    nom_complet_raw = getattr(candidat, "fullname", None) or \
                      f"{getattr(candidat, 'prenom', '')} {getattr(candidat, 'nom', '')}".strip() \
                      or "Candidat"
    return clean_text(nom_complet_raw)
