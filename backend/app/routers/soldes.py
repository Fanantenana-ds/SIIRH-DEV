from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.models import Employee, Absence, Conge
from app.schemas.soldes import SoldeOut

router = APIRouter(tags=["Soldes"], prefix="/api/soldes")

def calculate_solde(emp: Employee, db: Session):
    # Total congés validés pris
    conges = db.query(Conge).filter(
        Conge.employee_id == emp.id,
        Conge.statut == "validée"
    ).all()

    conges_pris = sum(
        (c.date_fin - c.date_debut).days + 1
        for c in conges
    )

    # Total absences non payées
    absences_non_payees = db.query(Absence).filter(
        Absence.employee_id == emp.id,
        Absence.type_absence == "non_justifiee"
    ).count()

    # Calcul solde restant
    SOLDE_ANNUEL = 30
    solde_conges_restant = max(SOLDE_ANNUEL - conges_pris, 0)


    # Mise à jour automatique si le solde a changé
    if emp.solde_conges != solde_conges_restant:
        emp.solde_conges = solde_conges_restant
        db.add(emp)
        db.commit()

    return {
        "employee_id": emp.id,
        "nom": emp.nom or "",
        "prenom": emp.prenom or "",
        "conges_pris": conges_pris,
        "absences_non_payees": absences_non_payees,
        "solde_conges": solde_conges_restant
    }


@router.get("/", response_model=List[SoldeOut])
def list_soldes(db: Session = Depends(get_db)):
    employees = db.query(Employee).all()
    result = [calculate_solde(emp, db) for emp in employees]
    return result





