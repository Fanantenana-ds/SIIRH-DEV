# scripts/update_all_scores.py

import os
from io import BytesIO
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# Models & services
from app.models import CandidatureFile
from app.services.scoring_auto import calculer_score_auto
from app.services.parsing import parse_pdf, parse_docx

# --- DB Config ---
DB_USER = os.getenv("DB_USER", "siirh_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Jeremi123")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "siirh")

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# --- Exemple offre pour scoring ---
offre = {
    "tech_skills": ["python", "sql", "fastapi"],
    "soft_skills": ["communication"],
    "langs_lvl": {"anglais": "B2"},
    "education_level": "Master",
    "exp_required_years": 2,
    "w_skills": 0.4,
    "w_exp": 0.3,
    "w_edu": 0.2,
    "w_proj": 0.1,
    "threshold": 60
}

# --- Fonction parse automatique raha tsy misy text_preview ---
def parse_cv_file(file_path: str) -> str:
    if file_path.lower().endswith(".pdf"):
        with open(file_path, "rb") as f:
            return parse_pdf(BytesIO(f.read()))
    elif file_path.lower().endswith(".docx"):
        with open(file_path, "rb") as f:
            return parse_docx(BytesIO(f.read()))
    return ""

# --- Fonction principale ---
def update_all_scores():
    db = SessionLocal()
    try:
        all_files = db.query(CandidatureFile).all()
        for file in all_files:
            # Raha tsy misy text_preview → maka avy amin'ny filepath
            if not file.text_preview or file.text_preview.strip() == "":
                # filepath = cvs/<filename> (minio)
                local_path = os.path.join("backend", file.filepath)
                if os.path.exists(local_path):
                    text = parse_cv_file(local_path)
                    file.text_preview = text
                else:
                    print(f"⚠️ File not found for parsing: {file.filepath}")
                    text = ""
            else:
                text = file.text_preview

            # --- Calcul score automatique ---
            if text:
                score_result = calculer_score_auto(text, offre)
                file.score = score_result["score"]
                db.commit()
                print(f"✅ Updated {file.filename}: score={file.score}")
            else:
                print(f"❌ No text to score for {file.filename}")
    except SQLAlchemyError as e:
        print("❌ DB Error:", e)
    finally:
        db.close()
        print("🎯 Update all scores finished!")

if __name__ == "__main__":
    update_all_scores()
