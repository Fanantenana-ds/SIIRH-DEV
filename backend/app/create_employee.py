from app.db import SessionLocal
from app.models.models import Candidature, Employee

# Crée une session DB
db = SessionLocal()

try:
    # Misy ohatra: mitady candidature miaraka amin'ny ID = 11
    candidature = db.query(Candidature).filter(Candidature.id == 11).first()

    if candidature is None:
        print("Candidature tsy hita")
    else:
        # Mamorona Employee vaovao avy amin'ny candidature
        employee = Employee(
            fullname=f"{candidature.nom} {candidature.prenom}" if hasattr(candidature, "nom") else candidature.fullname,
            email=candidature.email,
            phone=getattr(candidature, "phone", None),  # raha misy phone, raha tsy misy dia None
            poste=getattr(candidature, "poste", None),
            candidature_id=candidature.id
        )
        db.add(employee)
        db.commit()
        print(f"Employee {employee.fullname} no voasoratra tamin'ny DB!")

except Exception as e:
    db.rollback()
    print("Error:", e)

finally:
    db.close()
