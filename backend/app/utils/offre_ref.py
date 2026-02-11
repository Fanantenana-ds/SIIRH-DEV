from sqlalchemy.orm import Session
from app.models.offres import Offre
from datetime import datetime

def generate_job_reference(db: Session):
    year = datetime.now().year
    last = db.query(Offre).order_by(Offre.id.desc()).first()

    number = 1 if not last else last.id + 1
    formatted = f"{number:05d}"  # 00001

    return f"REF_{year}_{formatted}"
