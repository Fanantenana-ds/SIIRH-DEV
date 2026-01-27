from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from app.db import get_db
from app.models.models import Pointage, Employee
from app.schemas.pointage import (
    PointageCreate,
    PointageUpdate,
    PointageOut,
    PointageResume,
    PointageDetail
)

router = APIRouter(
    prefix="/api/pointages",
    tags=["Pointages"]
)

# ===============================
# ROUTES EXISTANTES (INCHANGÉES)
# ===============================

@router.get("/", response_model=List[PointageOut])
def list_pointages(db: Session = Depends(get_db)):
    return db.query(Pointage).all()


@router.post("/", response_model=PointageOut)
def create_pointage(pointage: PointageCreate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == pointage.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee non trouvé")

    new_pointage = Pointage(
        employee_id=pointage.employee_id,
        date=pointage.date,
        heure_entree=pointage.heure_entree,
        heure_sortie=pointage.heure_sortie,
        mode=pointage.mode
    )
    db.add(new_pointage)
    db.commit()
    db.refresh(new_pointage)
    return new_pointage


@router.put("/{ptg_id}", response_model=PointageOut)
def update_pointage(ptg_id: int, data: PointageUpdate, db: Session = Depends(get_db)):
    ptg = db.query(Pointage).filter(Pointage.id == ptg_id).first()
    if not ptg:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(ptg, field, value)

    db.commit()
    db.refresh(ptg)
    return ptg


@router.delete("/{ptg_id}")
def delete_pointage(ptg_id: int, db: Session = Depends(get_db)):
    ptg = db.query(Pointage).filter(Pointage.id == ptg_id).first()
    if not ptg:
        raise HTTPException(status_code=404, detail="Pointage non trouvé")

    db.delete(ptg)
    db.commit()
    return {"message": "Pointage supprimé avec succès"}


# ===============================
# 🚀 NOUVELLE ROUTE PRO (RÉSUMÉ)
# ===============================

@router.get("/resume", response_model=List[PointageResume])
def pointage_resume(
    mois: int,
    annee: int,
    db: Session = Depends(get_db)
):
    employees = db.query(Employee).all()
    results = []

    JOURS_THEORIQUES = 30  # mensuel standard (modifiable plus tard)

    for emp in employees:
        pts = db.query(Pointage).filter(
            Pointage.employee_id == emp.id,
            Pointage.date.month == mois,
            Pointage.date.year == annee
        ).order_by(Pointage.date).all()

        jours_travailles = len(pts)
        absences = JOURS_THEORIQUES - jours_travailles

        details = [
            PointageDetail(
                date=p.date,
                heure_entree=p.heure_entree,
                heure_sortie=p.heure_sortie
            )
            for p in pts
        ]

        results.append(
            PointageResume(
                employee_id=emp.id,
                nom=emp.nom,
                prenom=emp.prenom,
                jours_travailles=jours_travailles,
                jours_theoriques=JOURS_THEORIQUES,
                absences=absences,
                pointages=details
            )
        )

    return results
