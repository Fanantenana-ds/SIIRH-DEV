# # backend/app/routers/employees.py
# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from app.db import get_db
# from app.models.models import Candidature, Employee
# from app.schemas.employees import Employee as EmployeeSchema


# router = APIRouter(tags=["Employees"])

# # ==========================================================
# # 📌 Créer un Employee depuis une Candidature
# # ==========================================================
# @router.post("/from-candidature/{candidature_id}")
# def create_employee_from_candidature(candidature_id: int, db: Session = Depends(get_db)):
#     candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
#     if not candidature:
#         raise HTTPException(status_code=404, detail="Candidature non trouvée")

#     if candidature.employee:
#         return {"message": "ℹ️ Candidat déjà transformé en Employee", "employee_id": candidature.employee.id}

#     new_employee = Employee(
#         fullname=candidature.fullname or "Nom Inconnu",
#         email=candidature.email or "",
#         phone=candidature.phone or "Aucune",
#         poste=candidature.poste or "",
#         candidature_id=candidature.id
#     )

#     db.add(new_employee)
#     db.commit()
#     db.refresh(new_employee)

#     candidature.statut = "Employé"
#     db.commit()

#     return {"message": "✅ Candidat ajouté comme Employee !", "employee_id": new_employee.id}

# # ==========================================================
# # 📋 Liste de tous les Employees
# # ==========================================================
# @router.get("/")
# def list_employees(db: Session = Depends(get_db)):
#     employees = db.query(Employee).all()

#     result = []
#     for e in employees:
#         nom, prenom = None, None
#         if e.fullname:
#             parts = e.fullname.strip().split(" ", 1)
#             nom = parts[0]
#             prenom = parts[1] if len(parts) > 1 else ""

#         result.append(EmployeeSchema(
#             id=e.id,
#             nom=nom or "Inconnu",
#             prenom=prenom or "Inconnu",
#             email=e.email or "",
#             poste=e.poste or "",
#             phone = e.phone if e.phone else (e.candidature.telephone if e.candidature else "Aucune"),
#             candidature_id=e.candidature_id
#         ))

#     return result

# # ==========================================================
# # 📄 Détails d’un Employee
# # ==========================================================
# @router.get("/{employee_id}")
# def get_employee(employee_id: int, db: Session = Depends(get_db)):
#     employee = db.query(Employee).filter(Employee.id == employee_id).first()
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employee non trouvé")
#     return employee



# backend/app/routers/employees.py - VERSION CORRIGÉE
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Candidature, Employee
from app.schemas.employees import Employee as EmployeeSchema
from datetime import datetime
from app.utils.name_utils import split_fullname


router = APIRouter(tags=["Employees"])

# ==========================================================
# 🔹 CRÉER UN EMPLOYÉ DEPUIS UNE CANDIDATURE (CORRIGÉ)
    # ==========================================================
@router.post("/from-candidature/{candidature_id}")
def create_employee_from_candidature(candidature_id: int, db: Session = Depends(get_db)):
    try:
        print(f"👔 Création employé depuis candidature ID: {candidature_id}")
        
        # 1. Trouver la candidature
        candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
        if not candidature:
            raise HTTPException(status_code=404, detail="Candidature non trouvée")
        
        print(f"✅ Candidature trouvée: {candidature.fullname}")
        
        # 2. Vérifier si déjà employé
        if candidature.employee:
            return {
                "warning": True,
                "message": f"ℹ️ {candidature.fullname} déjà transformé en Employee",
                "employee_id": candidature.employee.id
            }
        
        # 3. Extraire téléphone CORRECTEMENT (utiliser 'telephone' pas 'phone')
        telephone = None
        if hasattr(candidature, 'telephone') and candidature.telephone:
            telephone = candidature.telephone
        elif hasattr(candidature, 'phone') and candidature.phone:
            telephone = candidature.phone
        else:
            telephone = "Non renseigné"
        
        print(f"📞 Téléphone extrait: {telephone}")

        # ✅ ======= FANITSINA ICI (OLANA NOT NULL nom/prenom) =======
        nom, prenom = split_fullname(candidature.fullname)
        # ===========================================================
        
        # 4. Créer l'employé avec 'telephone' au lieu de 'phone'
        new_employee = Employee(
            nom=nom,
            prenom=prenom,
            fullname=candidature.fullname or "Nom Inconnu",
            email=candidature.email or "",
            telephone=telephone,
            poste=candidature.poste or "",
            candidature_id=candidature.id,
            date_embauche=datetime.now()
        )
        
        db.add(new_employee)
        db.commit()
        db.refresh(new_employee)
        
        # 5. Mettre à jour statut candidature
        candidature.statut = "Employé"
        db.commit()
        
        print(f"✅ Employé créé: ID {new_employee.id}")
        
        return {
            "success": True,
            "message": f"✅ {candidature.fullname} ajouté comme Employee !",
            "employee_id": new_employee.id,
            "employee": {
                "id": new_employee.id,
                "fullname": new_employee.fullname,
                "email": new_employee.email,
                "telephone": new_employee.telephone,
                "poste": new_employee.poste
            }
        }
        
    except Exception as e:
        print(f"💥 Erreur création employé: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
# ==========================================================
# 🔹 LISTE DE TOUS LES EMPLOYÉS (CORRIGÉ)
# ==========================================================
@router.get("/")
def list_employees(db: Session = Depends(get_db)):
    try:
        employees = db.query(Employee).all()
        
        result = []
        for e in employees:
            nom, prenom = None, None
            if e.fullname:
                parts = e.fullname.strip().split(" ", 1)
                nom = parts[0]
                prenom = parts[1] if len(parts) > 1 else ""
            
            # Utiliser 'telephone' au lieu de 'phone'
            phone_value = e.telephone
            if not phone_value or phone_value == "Non renseigné":
                if e.candidature and hasattr(e.candidature, 'telephone'):
                    phone_value = e.candidature.telephone
            
            result.append(EmployeeSchema(
                id=e.id,
                nom=nom or "Inconnu",
                prenom=prenom or "",
                email=e.email or "",
                poste=e.poste or "",
                phone=phone_value or "Aucune",
                candidature_id=e.candidature_id
            ))
        
        # ✅ FANITSINA TOKANA: frontend miandry array mivantana
        return result
        
    except Exception as e:
        print(f"❌ Erreur liste employés: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")
# ==========================================================
# 🔹 DÉTAILS D'UN EMPLOYÉ (CORRIGÉ)
# ==========================================================
@router.get("/{employee_id}")
def get_employee(employee_id: int, db: Session = Depends(get_db)):
    try:
        employee = db.query(Employee).filter(Employee.id == employee_id).first()
        if not employee:
            raise HTTPException(status_code=404, detail="Employee non trouvé")
        
        # Formatage de la réponse
        nom, prenom = None, None
        if employee.fullname:
            parts = employee.fullname.strip().split(" ", 1)
            nom = parts[0]
            prenom = parts[1] if len(parts) > 1 else ""
        
        return {
            "employee": {
                "id": employee.id,
                "nom": nom or "Inconnu",
                "prenom": prenom or "",
                "fullname": employee.fullname,
                "email": employee.email,
                "telephone": employee.telephone,  # ⬅️ CORRECTION
                "poste": employee.poste,
                "date_embauche": employee.date_embauche.isoformat() if employee.date_embauche else None,
                "candidature_id": employee.candidature_id
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Erreur détails employé: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erreur serveur: {str(e)}")

# ==========================================================
# 🔹 TEST ENDPOINT
# ==========================================================
@router.get("/test")
def test_endpoint():
    return {"message": "✅ Endpoint employees fonctionnel!", "status": "OK"}

