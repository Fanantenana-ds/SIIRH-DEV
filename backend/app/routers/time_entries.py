from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.time_entry import TimeEntry
from app.models.models import Employee
from app.schemas.time_entry import TimeEntryCreate, TimeEntryOut
import csv
from io import StringIO

router = APIRouter(prefix="/api/pointages", tags=["Pointage"])

@router.get("/", response_model=list[TimeEntryOut])
def list_entries(db: Session = Depends(get_db)):
    return db.query(TimeEntry).all()


@router.post("/manual", response_model=TimeEntryOut)
def manual_entry(data: TimeEntryCreate, db: Session = Depends(get_db)):
    emp = db.query(Employee).filter(Employee.id == data.employee_id).first()
    if not emp:
        raise HTTPException(404, "Employé introuvable")

    entry = TimeEntry(**data.dict())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry


@router.post("/import")
def import_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    csv_reader = csv.DictReader(StringIO(content))

    for row in csv_reader:
        entry = TimeEntry(
            employee_id=row["employee_id"],
            date=row["date"],
            check_in=row["check_in"],
            check_out=row["check_out"]
        )
        db.add(entry)

    db.commit()
    return {"message": "Import réussi"}
