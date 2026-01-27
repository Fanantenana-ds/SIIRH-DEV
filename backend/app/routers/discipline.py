# from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
# from sqlalchemy.orm import Session
# from typing import List
# from datetime import datetime
# import json
# import os
# from fastapi.responses import FileResponse

# from app.schemas.employees import Employee  
# from app import crud, schemas
# from app.db import get_db
# from app.utils.pdf_generator import (
#     generate_convocation_pdf,
#     generate_decision_pdf,
#     generate_licenciement_letter
# )
# from app.utils.mailer import send_mail

# router = APIRouter(prefix="/discipline", tags=["Discipline"])

# # ==========================================================
# # 1. CREER DOSSIER
# # ==========================================================
# @router.post("/cases", response_model=schemas.DisciplineCase)
# async def create_case(
#     employee_id: int = Form(...),
#     fault_type: str = Form(...),
#     description: str = Form(None),
#     files: List[UploadFile] = File([]),
#     db: Session = Depends(get_db)
# ):
#     emp = crud.get_employee(db, employee_id)
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employé non trouvé")

#     case_data = schemas.DisciplineCaseCreate(
#         employee_id=employee_id,
#         fault_type=fault_type,
#         description=description
#     )
#     db_case = crud.create_discipline_case(db, case_data)

#     # Save files
#     temp_dir = "/tmp/discipline_files"
#     os.makedirs(temp_dir, exist_ok=True)

#     for f in files:
#         file_path = os.path.join(temp_dir, f.filename)
#         with open(file_path, "wb") as buffer:
#             buffer.write(await f.read())

#         crud.add_evidence(db, db_case.id, f.filename, file_path)

#     return crud.get_case(db, db_case.id)

# # ==========================================================
# # 2. LISTE DES DOSSIERS
# # ==========================================================
# @router.get("/cases", response_model=List[schemas.DisciplineCase])
# def list_cases(db: Session = Depends(get_db)):
#     return crud.list_cases(db)

# # ==========================================================
# # 3. DETAILS
# # ==========================================================
# @router.get("/cases/{case_id}", response_model=schemas.DisciplineCase)
# def get_case(case_id: int, db: Session = Depends(get_db)):
#     case = crud.get_case(db, case_id)
#     if not case:
#         raise HTTPException(status_code=404, detail="Case non trouvé")

#     # --- Ajouter le compte_rendu depuis le dernier event de type 'decision' ---
#     last_decision_event = crud.get_last_event_of_type(db, case_id, "decision")
#     if last_decision_event:
#         decision_data = json.loads(last_decision_event.event_data)
#         case["decision"] = {
#             "decision_type": decision_data.get("type", ""),
#             "decision_notes": decision_data.get("notes", "")
#         }
#         case["compte_rendu"] = decision_data.get("notes", "")
#     else:
#         case["decision"] = None
#         case["compte_rendu"] = ""
        
#     # --- Ajouter les fichiers ---
#     case["files"] = [
#         {"filename": f.file_name, "filepath": f.file_url}
#         for f in crud.get_evidences(db, case_id)
#     ]

#     return case

# # ==========================================================
# # 4. PDF CONVOCATION
# # ==========================================================
# @router.post("/cases/{case_id}/convocation")
# def create_convocation(case_id: int, db: Session = Depends(get_db)):
#     case = crud.get_case(db, case_id)
#     if not case:
#         raise HTTPException(status_code=404, detail="Case non trouvé")

#     emp = crud.get_employee(db, case["employee_id"])
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employé non trouvé")

#     # Generate PDF
#     pdf_path = generate_convocation_pdf(
#         emp,
#         {
#             "date_entretien": datetime.now().strftime("%d/%m/%Y"),
#             "heure_entretien": "09:00",
#             "lieu_entretien": "Bureau RH"
#         }
#     )

#     crud.add_event(db, case_id, "convocation", {"pdf": pdf_path})

#     return FileResponse(pdf_path, media_type="application/pdf")

# # ==========================================================
# # 5. DECISION PDF
# # ==========================================================
# @router.post("/cases/{case_id}/decision")
# def create_decision(case_id: int, decision: schemas.Decision, db: Session = Depends(get_db)):

#     case = crud.get_case(db, case_id)
#     if not case:
#         raise HTTPException(status_code=404, detail="Case non trouvé")

#     emp = crud.get_employee(db, case["employee_id"])

#     pdf_path = generate_decision_pdf(emp, decision)

#     crud.add_event(db, case_id, "decision", {
#         "type": decision.decision_type,
#         "notes": decision.decision_notes,
#         "pdf": pdf_path
#     })

#     crud.update_case_status(db, case_id, decision.decision_type)

#     if decision.decision_type == "Licenciement":
#         lettre_path = generate_licenciement_letter(emp, None)
#         crud.add_event(db, case_id, "lettre_licenciement", {"pdf": lettre_path})

#     return FileResponse(pdf_path, media_type="application/pdf")

# # ==========================================================
# # 6. ENVOI MAIL CONVOCATION
# # ==========================================================
# @router.post("/cases/{case_id}/send-convocation-mail")
# def send_convocation_email(case_id: int, db: Session = Depends(get_db)):

#     case = crud.get_case(db, case_id)
#     if not case:
#         raise HTTPException(status_code=404, detail="Case non trouvé")

#     emp = crud.get_employee(db, case["employee_id"])

#     event = crud.get_last_event_of_type(db, case_id, "convocation")
#     if not event:
#         raise HTTPException(status_code=400, detail="Aucune convocation générée")

#     data = json.loads(event.event_data)
#     pdf_path = data["pdf"]

#     send_mail(
#         to=emp.email,
#         subject="Convocation entretien disciplinaire",
#         body=f"Bonjour {emp.nom},\nVeuillez trouver ci-joint votre convocation.",
#         attachments=[pdf_path]
#     )

#     return {"message": "Email envoyé", "pdf": pdf_path}

# # ==========================================================
# # 7. LISTE EMPLOYES
# # ==========================================================
# @router.get("/employees", response_model=List[Employee])
# def list_employees(db: Session = Depends(get_db)):
#     employees = crud.list_employees(db)
#     return [
#         Employee(
#             id=e.id,
#             nom=e.nom,
#             prenom=e.prenom,
#             fullname=f"{e.nom} {e.prenom}",
#             email=e.email,
#             poste=e.poste
#         )
#         for e in employees
#     ]
# # ==========================================================
# # 4b. PDF CONVOCATION DISCIPLINE (NOUVEAU)
# # ==========================================================
# from fastapi import Body  # ampio ao amin'ny imports

# @router.post("/cases/{case_id}/convocation-discipline")
# def create_convocation_discipline(
#     case_id: int,
#     convocation: dict = Body(...),  # mandray date sy heure avy amin'ny frontend
#     db: Session = Depends(get_db)
# ):
#     case = crud.get_case(db, case_id)
#     if not case:
#         raise HTTPException(status_code=404, detail="Case non trouvé")

#     emp = crud.get_employee(db, case["employee_id"])
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employé non trouvé")

#     # Générer PDF discipline mifanaraka amin'ny type de faute
#     convocation_data = {
#         "fault_type": case["fault_type"],
#         "date_convocation": convocation.get("date_convocation", "à définir"),
#         "heure_convocation": convocation.get("heure_convocation", "à définir"),
#         "lieu_convocation": "Bureau RH"
#     }

#     from app.utils.pdf_generator import generate_convocation_discipline_pdf
#     pdf_path = generate_convocation_discipline_pdf(emp, convocation_data)

#     crud.add_event(db, case_id, "convocation_discipline", {"pdf": pdf_path})

#     return FileResponse(pdf_path, media_type="application/pdf")


# # ==========================================================
# # ENVOI MAIL CONVOCATION DISCIPLINE
# # ==========================================================
# @router.post("/cases/{case_id}/send-convocation-discipline-mail")
# def send_convocation_discipline_email(
#     case_id: int,
#     convocation: dict = Body(...),  # mandray date sy heure avy amin'ny frontend
#     db: Session = Depends(get_db)
# ):

#     case = crud.get_case(db, case_id)
#     if not case:
#         raise HTTPException(status_code=404, detail="Case non trouvé")

#     emp = crud.get_employee(db, case["employee_id"])
#     if not emp:
#         raise HTTPException(status_code=404, detail="Employé non trouvé")

#     # Générer PDF discipline
#     from app.utils.pdf_generator import generate_convocation_discipline_pdf
#     convocation_data = {
#         "fault_type": case["fault_type"],
#         "date_convocation": convocation.get("date_convocation", "à définir"),
#         "heure_convocation": convocation.get("heure_convocation", "à définir"),
#         "lieu_convocation": "Bureau RH"
#     }
#     pdf_path = generate_convocation_discipline_pdf(emp, convocation_data)

#     # Ajouter événement
#     crud.add_event(db, case_id, "convocation_discipline", {"pdf": pdf_path})

#     # Envoyer mail
#     send_mail(
#         to=emp.email,
#         subject="Convocation disciplinaire",
#         body=f"Bonjour {emp.nom},\nVeuillez trouver ci-joint votre convocation disciplinaire.\n\nDate : {convocation_data['date_convocation']}\nHeure : {convocation_data['heure_convocation']}\nLieu : {convocation_data['lieu_convocation']}",
#         attachments=[pdf_path]
#     )

#     return {"message": "Email envoyé", "pdf": pdf_path}














from app.models.models import Employee as EmployeeModel
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import json
import os
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.schemas.employees import Employee  
from app import crud, schemas
from app.db import get_db
from app.utils.pdf_generator import (
    generate_convocation_pdf,
    generate_decision_pdf,
    generate_licenciement_letter
)
from app.utils.mailer import send_mail

router = APIRouter(prefix="/discipline", tags=["Discipline"])

# ==========================================================
# 1. CREER DOSSIER
# ==========================================================
@router.post("/cases", response_model=schemas.DisciplineCase)
async def create_case(
    employee_id: int = Form(...),
    fault_type: str = Form(...),
    description: str = Form(None),
    files: List[UploadFile] = File([]),
    db: Session = Depends(get_db)
):
    emp = crud.get_employee(db, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    case_data = schemas.DisciplineCaseCreate(
        employee_id=employee_id,
        fault_type=fault_type,
        description=description
    )
    db_case = crud.create_discipline_case(db, case_data)

    # Save files
    temp_dir = "/tmp/discipline_files"
    os.makedirs(temp_dir, exist_ok=True)

    for f in files:
        file_path = os.path.join(temp_dir, f.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await f.read())

        crud.add_evidence(db, db_case.id, f.filename, file_path)

    return crud.get_case(db, db_case.id)

# ==========================================================
# 2. LISTE DES DOSSIERS
# ==========================================================
@router.get("/cases", response_model=List[schemas.DisciplineCase])
def list_cases(db: Session = Depends(get_db)):
    cases = crud.list_cases(db)

    for c in cases:
        emp = crud.get_employee(db, c["employee_id"])
        if emp:
            c["employee_name"] = emp.fullname
        else:
            c["employee_name"] = "—"

    return cases

# ==========================================================
# 3. DETAILS
# ==========================================================
@router.get("/cases/{case_id}", response_model=schemas.DisciplineCase)
def get_case(case_id: int, db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case non trouvé")

    last_decision_event = crud.get_last_event_of_type(db, case_id, "decision")
    if last_decision_event:
        decision_data = json.loads(last_decision_event.event_data)
        case["decision"] = {
            "decision_type": decision_data.get("type", ""),
            "decision_notes": decision_data.get("notes", "")
        }
        case["compte_rendu"] = decision_data.get("notes", "")
    else:
        case["decision"] = None
        case["compte_rendu"] = ""
        
    case["files"] = [
        {"filename": f.file_name, "filepath": f.file_url}
        for f in crud.get_evidences(db, case_id)
    ]

    return case

# ==========================================================
# 4. PDF CONVOCATION
# ==========================================================
@router.post("/cases/{case_id}/convocation")
def create_convocation(case_id: int, db: Session = Depends(get_db)):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case non trouvé")

    emp = crud.get_employee(db, case["employee_id"])
    if not emp:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    pdf_path = generate_convocation_pdf(
        emp,
        {
            "date_entretien": datetime.now().strftime("%d/%m/%Y"),
            "heure_entretien": "09:00",
            "lieu_entretien": "Bureau RH"
        }
    )

    crud.add_event(db, case_id, "convocation", {"pdf": pdf_path})

    return FileResponse(pdf_path, media_type="application/pdf")

# ==========================================================
# 5. DECISION PDF
# ==========================================================
@router.post("/cases/{case_id}/decision")
def create_decision(case_id: int, decision: schemas.Decision, db: Session = Depends(get_db)):

    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case non trouvé")

    emp = crud.get_employee(db, case["employee_id"])

    pdf_path = generate_decision_pdf(emp, decision)

    crud.add_event(db, case_id, "decision", {
        "type": decision.decision_type,
        "notes": decision.decision_notes,
        "pdf": pdf_path
    })

    crud.update_case_status(db, case_id, decision.decision_type)

    if decision.decision_type == "Licenciement":
        lettre_path = generate_licenciement_letter(emp, None)
        crud.add_event(db, case_id, "lettre_licenciement", {"pdf": lettre_path})

    return FileResponse(pdf_path, media_type="application/pdf")

# ==========================================================
# 6. ENVOI MAIL CONVOCATION
# ==========================================================
@router.post("/cases/{case_id}/send-convocation-mail")
def send_convocation_email(case_id: int, db: Session = Depends(get_db)):

    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case non trouvé")

    emp = crud.get_employee(db, case["employee_id"])

    event = crud.get_last_event_of_type(db, case_id, "convocation")
    if not event:
        raise HTTPException(status_code=400, detail="Aucune convocation générée")

    data = json.loads(event.event_data)
    pdf_path = data["pdf"]

    send_mail(
        to=emp.email,
        subject="Convocation entretien disciplinaire",
        body=f"Bonjour {emp.nom},\nVeuillez trouver ci-joint votre convocation.",
        attachments=[pdf_path]
    )

    return {"message": "Email envoyé", "pdf": pdf_path}

# ==========================================================
# 7. LISTE EMPLOYES (PATCHED)
# ==========================================================
@router.get("/employees", response_model=List[Employee])
def list_employees(db: Session = Depends(get_db)):
    employees = db.query(EmployeeModel).all()

    result = []
    for e in employees:
        nom = "Inconnu"
        prenom = "Inconnu"

        if e.fullname:
            parts = e.fullname.strip().split(" ", 1)
            nom = parts[0]
            prenom = parts[1] if len(parts) > 1 else ""

        result.append(
            Employee(
                id=e.id,
                nom=nom,
                prenom=prenom,
                email=e.email,
                poste=e.poste,
                phone=e.phone,
                candidature_id=e.candidature_id,
                fullname=e.fullname,
            )
        )

    return result



# ==========================================================
# 4b. PDF CONVOCATION DISCIPLINE (NOUVEAU) AVEC Pydantic
# ==========================================================
class ConvocationData(BaseModel):
    date_convocation: str
    heure_convocation: str

@router.post("/cases/{case_id}/convocation-discipline")
def create_convocation_discipline(
    case_id: int,
    convocation: ConvocationData,
    db: Session = Depends(get_db)
):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case non trouvé")

    emp = crud.get_employee(db, case["employee_id"])
    if not emp:
        raise HTTPException(status_code=404, detail="Employé non trouvé")

    convocation_data = {
        "fault_type": case["fault_type"],
        "date_convocation": convocation.date_convocation,
        "heure_convocation": convocation.heure_convocation,
        "lieu_convocation": "Bureau RH"
    }

    from app.utils.pdf_generator import generate_convocation_discipline_pdf
    pdf_path = generate_convocation_discipline_pdf(emp, convocation_data)

    crud.add_event(db, case_id, "convocation_discipline", {"pdf": pdf_path})

    return FileResponse(pdf_path, media_type="application/pdf")


# ==========================================================
# ENVOI MAIL CONVOCATION DISCIPLINE AVEC Pydantic
# ==========================================================
@router.post("/cases/{case_id}/send-convocation-discipline-mail")
def send_convocation_discipline_email(
    case_id: int,
    convocation: ConvocationData,
    db: Session = Depends(get_db)
):
    case = crud.get_case(db, case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Case non trouvé")
    
    emp = crud.get_employee(db, case["employee_id"])
    case["employee_name"] = emp.fullname if emp else "—"

    convocation_data = {
        "fault_type": case["fault_type"],
        "date_convocation": convocation.date_convocation,
        "heure_convocation": convocation.heure_convocation,
        "lieu_convocation": "Bureau RH"
    }

    from app.utils.pdf_generator import generate_convocation_discipline_pdf
    pdf_path = generate_convocation_discipline_pdf(emp, convocation_data)

    crud.add_event(db, case_id, "convocation_discipline", {"pdf": pdf_path})

    send_mail(
        to=emp.email,
        subject="Convocation disciplinaire",
        body=f"Bonjour {emp.nom},\nVeuillez trouver ci-joint votre convocation disciplinaire.\n\nDate : {convocation_data['date_convocation']}\nHeure : {convocation_data['heure_convocation']}\nLieu : {convocation_data['lieu_convocation']}",
        attachments=[pdf_path]
    )

    return {"message": "Email envoyé", "pdf": pdf_path}



