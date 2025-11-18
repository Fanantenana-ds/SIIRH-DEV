# # app/routers/discipline.py

# from fastapi import APIRouter, HTTPException, Depends
# from sqlalchemy.orm import Session
# from typing import List
# from app.db import get_db
# from app.models.discipline import Discipline
# from app.models.offres import Employee
# from datetime import datetime
# from app.schemas.discipline import DisciplineCreate, DisciplineResponse
# from fastapi import UploadFile, File, Form
# from app.services.upload_discipline import save_discipline_file


# router = APIRouter(prefix="/api/discipline", tags=["Gestion Disciplinaire"])


# # ============================================================
# # CREATE
# # ============================================================
# @router.post("/", response_model=DisciplineResponse)
# def create_discipline(data: DisciplineCreate, db: Session = Depends(get_db)):
#     employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
#     if not employee:
#         raise HTTPException(status_code=404, detail="Employé non trouvé")

#     discipline = Discipline(
#         employee_id=data.employee_id,
#         fault_category=data.fault_category,
#         fault_nature=data.fault_nature,
#         description=data.description,
#         proof_files=",".join(data.proof_files) if data.proof_files else None,
#         convocation_model=data.convocation_model,
#         convocation_date=datetime.strptime(data.convocation_date, "%Y-%m-%d").date(),
#         convocation_time=data.convocation_time,
#         convocation_place=data.convocation_place,
#         convocation_manager=data.convocation_manager,
#     )

#     db.add(discipline)
#     db.commit()
#     db.refresh(discipline)

#     return discipline


# # ============================================================
# # GET ALL DISCIPLINES
# # ============================================================
# @router.get("/", response_model=List[DisciplineResponse])
# def list_disciplines(db: Session = Depends(get_db)):
#     return db.query(Discipline).all()


# # ============================================================
# # GET ONE DISCIPLINE BY ID
# # ============================================================
# @router.get("/{id}", response_model=DisciplineResponse)
# def get_discipline(id: int, db: Session = Depends(get_db)):
#     discipline = db.query(Discipline).filter(Discipline.id == id).first()

#     if not discipline:
#         raise HTTPException(status_code=404, detail="Dossier disciplinaire introuvable")

#     return discipline


# # ============================================================
# # DELETE DISCIPLINE
# # ============================================================
# @router.delete("/{id}", response_model=dict)
# def delete_discipline(id: int, db: Session = Depends(get_db)):
#     discipline = db.query(Discipline).filter(Discipline.id == id).first()

#     if not discipline:
#         raise HTTPException(status_code=404, detail="Dossier introuvable")

#     db.delete(discipline)
#     db.commit()

#     return {"message": "🗑️ Dossier disciplinaire supprimé avec succès"}


# app/routers/discipline.py

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.db import get_db
from app.models.discipline import Discipline
from app.models.models import Employee
from app.schemas.discipline import DisciplineCreate, DisciplineResponse
from app.services.upload_discipline import save_discipline_file


router = APIRouter(prefix="/api/discipline", tags=["Gestion Disciplinaire"])


# ============================================================
# 1️⃣ CREATE DISCIPLINE (JSON VERSION — sans upload)
# ============================================================
@router.post("/", response_model=DisciplineResponse)
def create_discipline(data: DisciplineCreate, db: Session = Depends(get_db)):

    # Vérifier employé
    employee = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    discipline = Discipline(
        employee_id=data.employee_id,
        fault_category=data.fault_category,
        fault_nature=data.fault_nature,
        description=data.description,
        proof_files=",".join(data.proof_files) if data.proof_files else None,
        convocation_model=data.convocation_model,
        convocation_date=datetime.strptime(data.convocation_date, "%Y-%m-%d").date(),
        convocation_time=data.convocation_time,
        convocation_place=data.convocation_place,
        convocation_manager=data.convocation_manager,
    )

    db.add(discipline)
    db.commit()
    db.refresh(discipline)

    return discipline



# ============================================================
# 2️⃣ CREATE DISCIPLINE WITH FILES (multipart/form-data)
# ============================================================
@router.post("/with-files", response_model=DisciplineResponse)
def create_discipline_with_files(
    employee_id: int = Form(...),
    fault_category: str = Form(...),
    fault_nature: str = Form(...),
    description: str = Form(...),
    convocation_model: str = Form(...),
    convocation_date: str = Form(...),
    convocation_time: str = Form(...),
    convocation_place: str = Form(...),
    convocation_manager: str = Form(...),
    proofs: Optional[List[UploadFile]] = File(None),
    db: Session = Depends(get_db)
):

    # Vérifier employé
    employee = db.query(Employee).filter(Employee.id == employee_id).first()
    if not employee:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    # Upload fichiers preuves
    saved_files = []
    if proofs:
        for f in proofs:
            path = save_discipline_file(f)
            saved_files.append(path)

    discipline = Discipline(
        employee_id=employee_id,
        fault_category=fault_category,
        fault_nature=fault_nature,
        description=description,
        proof_files=",".join(saved_files) if saved_files else None,
        convocation_model=convocation_model,
        convocation_date=datetime.strptime(convocation_date, "%Y-%m-%d").date(),
        convocation_time=convocation_time,
        convocation_place=convocation_place,
        convocation_manager=convocation_manager,
    )

    db.add(discipline)
    db.commit()
    db.refresh(discipline)

    return discipline



# ============================================================
# 3️⃣ GET ALL DISCIPLINES
# ============================================================
@router.get("/", response_model=List[DisciplineResponse])
def list_disciplines(db: Session = Depends(get_db)):
    return db.query(Discipline).all()



# ============================================================
# 4️⃣ GET DISCIPLINE BY ID
# ============================================================
@router.get("/{id}", response_model=DisciplineResponse)
def get_discipline(id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id == id).first()

    if not discipline:
        raise HTTPException(status_code=404, detail="Dossier disciplinaire introuvable")

    return discipline



# ============================================================
# 5️⃣ DELETE DISCIPLINE
# ============================================================
@router.delete("/{id}", response_model=dict)
def delete_discipline(id: int, db: Session = Depends(get_db)):
    discipline = db.query(Discipline).filter(Discipline.id == id).first()

    if not discipline:
        raise HTTPException(status_code=404, detail="Dossier introuvable")

    db.delete(discipline)
    db.commit()

    return {"message": "🗑️ Dossier disciplinaire supprimé avec succès"}
