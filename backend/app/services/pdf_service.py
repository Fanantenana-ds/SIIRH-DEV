from fpdf import FPDF
import os

EXPORT_DIR = "exports"
os.makedirs(EXPORT_DIR, exist_ok=True)

def generate_offre_pdf(offre: dict) -> str:
    """
    Génère un PDF à partir d'un dict 'offre'.
    Retourne le path du fichier PDF généré.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Offre d'emploi", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    for key, value in offre.items():
        if key.startswith("w_") or key in ["scoring_config_path"]: 
            continue  # on skip les poids techniques pour l'affichage publique
        pdf.ln(5)
        pdf.multi_cell(0, 8, f"{key.replace('_',' ').capitalize()}: {value}")

    filename = f"{EXPORT_DIR}/offre_{offre.get('job_ref','0')}.pdf"
    pdf.output(filename)
    return filename
