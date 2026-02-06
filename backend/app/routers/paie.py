# backend/app/routers/paie.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import extract
from datetime import date
from typing import List

from app.db import get_db
from app.models.models import Paie, Employee, Contrat, Absence
from app.schemas.paie import PaieCreate, PaieOut, PaieUpdate

router = APIRouter(
    prefix="/api/paies",
    tags=["Paies"]
)

# ------------------------
# Calcul automatique de la paie
# ------------------------
def compute_paie(employee: Employee, mois: str, annee: int, db: Session):
    contrat = (
        db.query(Contrat)
        .filter(Contrat.employee_id == employee.id)
        .order_by(Contrat.id.desc())
        .first()
    )
    if not contrat:
        raise HTTPException(400, f"Aucun contrat trouvé pour l'employé {employee.fullname}")

    salaire_base = contrat.salaire or 0.0

    mois_dict = {
        "Janvier": 1, "Février": 2, "Mars": 3, "Avril": 4,
        "Mai": 5, "Juin": 6, "Juillet": 7, "Août": 8,
        "Septembre": 9, "Octobre": 10, "Novembre": 11, "Décembre": 12
    }
    mois_number = mois_dict.get(mois)
    if not mois_number:
        raise HTTPException(400, f"Mois invalide : {mois}")

    absences = db.query(Absence).filter(
        Absence.employee_id == employee.id,
        extract("month", Absence.date_debut) == mois_number,
        extract("year", Absence.date_debut) == annee
    ).all()

    total_absence_days = sum((x.date_fin - x.date_debut).days + 1 for x in absences)
    absence_deduction = round((salaire_base / 30) * total_absence_days, 2)
    salaire_net = round(salaire_base - absence_deduction, 2)

    return salaire_base, absence_deduction, salaire_net

# ------------------------
# Routes
# ------------------------
@router.get("/", response_model=List[PaieOut])
def list_paies(db: Session = Depends(get_db)):
    paies = db.query(Paie).options(joinedload(Paie.employee)).all()
    return paies

@router.post("/", response_model=PaieOut)
def create_paie(data: PaieCreate, db: Session = Depends(get_db)):
    print("Payload reçu:", data.dict())
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(404, "Employé introuvable")

    # ------------------------
    # Détermination automatique du mois et de l'année si manquants
    # ------------------------
    today = date.today()
    mois = getattr(data, "mois", None) or today.strftime("%B")  # ex: "Novembre"
    annee = getattr(data, "annee", None) or today.year

    salaire_base, absence_deduction, salaire_net = compute_paie(employee, mois, annee, db)

    paie = Paie(
        employee_id=employee.id,
        employee=employee,
        salaire_base=salaire_base,
        absence_deduction=absence_deduction,
        net_a_payer=salaire_net, 
        montant=salaire_net,
        primes=getattr(data, "primes", 0.0),
        heures_supp=getattr(data, "heures_supp", 0.0),
        deductions=getattr(data, "deductions", 0.0),
        mois=mois,
        annee=annee,
        date_paiement=date.today()
    )

    db.add(paie)
    db.commit()
    db.refresh(paie)
    return paie

@router.put("/{paie_id}", response_model=PaieOut)
def update_paie(paie_id: int, data: PaieUpdate, db: Session = Depends(get_db)):
    paie = db.query(Paie).filter(Paie.id == paie_id).first()
    if not paie:
        raise HTTPException(404, "Paie introuvable")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(paie, field, value)

    db.commit()
    db.refresh(paie)
    return paie

@router.delete("/{paie_id}")
def delete_paie(paie_id: int, db: Session = Depends(get_db)):
    paie = db.query(Paie).filter(Paie.id == paie_id).first()
    if not paie:
        raise HTTPException(404, "Paie introuvable")
    db.delete(paie)
    db.commit()
    return {"message": "Paie supprimée"}
