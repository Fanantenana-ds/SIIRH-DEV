import os
from datetime import datetime
from fastapi import UploadFile

DISCIPLINE_UPLOAD_DIR = "uploads/discipline"


def save_discipline_file(file: UploadFile) -> str:
    """
    Sauvegarde un fichier preuve du module disciplinaire.
    Ne fait AUCUN parsing, ne dépend d'aucune table.
    Retourne le chemin du fichier à stocker dans la DB.
    """

    # 1️⃣ Créer dossier discipline si encore tsy misy
    os.makedirs(DISCIPLINE_UPLOAD_DIR, exist_ok=True)

    # 2️⃣ Mamorona anarana unik ho an’ny fichier
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    sanitized_name = file.filename.replace(" ", "_")
    filename = f"preuve_{timestamp}_{sanitized_name}"

    file_path = os.path.join(DISCIPLINE_UPLOAD_DIR, filename)

    # 3️⃣ Enregistrer ny fichier
    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    # 4️⃣ Mamerina ny path relatif ho an’ny DB
    return file_path
