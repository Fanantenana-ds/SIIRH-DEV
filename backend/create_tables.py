from app.db import Base, engine
from app.models import Employee, Contrat, Paie, Utilisateur, Candidature  # raha efa ireo no modely misy

print("🛠️ Création des tables dans la base de données...")
Base.metadata.create_all(bind=engine)
print("✅ Tables créées avec succès !")
