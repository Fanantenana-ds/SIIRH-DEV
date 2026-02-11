from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db import get_db
from app.models.models import Conge, Employee
from app.schemas.conge import CongeCreate, CongeUpdate, CongeOut

router = APIRouter(tags=["Congés"])

@router.get("/", response_model=List[CongeOut])
def list_conges(db: Session = Depends(get_db)):
    return db.query(Conge).all()

@router.post("/", response_model=CongeOut)
def create_conge(conge: CongeCreate, db: Session = Depends(get_db)):
    employee = db.query(Employee).filter(Employee.id == conge.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employee non trouvé")
    new_conge = Conge(**conge.dict())
    db.add(new_conge)
    db.commit()
    db.refresh(new_conge)
    return new_conge

@router.put("/{conge_id}", response_model=CongeOut)
def update_conge(conge_id: int, data: CongeUpdate, db: Session = Depends(get_db)):
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(status_code=404, detail="Congé non trouvé")
    for field, value in data.dict(exclude_unset=True).items():
        setattr(conge, field, value)
    db.commit()
    db.refresh(conge)
    return conge

@router.delete("/{conge_id}")
def delete_conge(conge_id: int, db: Session = Depends(get_db)):
    conge = db.query(Conge).filter(Conge.id == conge_id).first()
    if not conge:
        raise HTTPException(status_code=404, detail="Congé non trouvé")
    db.delete(conge)
    db.commit()
    return {"message": "Congé supprimé avec succès"}
