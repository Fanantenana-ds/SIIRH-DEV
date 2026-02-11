



# # app/crud.py - VERSION FENO SY HIFANENTANA AMIN'NY DISCIPLINE.PY
# from sqlalchemy.orm import Session
# from datetime import datetime
# import json

# # -----------------------------
# # IMPORTS MODELES
# # -----------------------------
# from app.models import Candidature, Employee

# try:
#     from app.models import DisciplineCase, DisciplineEvidence, DisciplineEvent
# except ImportError:
#     class DisciplineCase: pass
#     class DisciplineEvidence: pass
#     class DisciplineEvent: pass

# # Alias Event
# Event = DisciplineEvent

# # -----------------------------
# # CANDIDATURES
# # -----------------------------
# def create_candidature(db: Session, data: dict):
#     db_cand = Candidature(**data)
#     db.add(db_cand)
#     db.commit()
#     db.refresh(db_cand)
#     return db_cand

# def get_all_candidatures(db: Session, status: str = None):
#     query = db.query(Candidature)
#     if status:
#         query = query.filter(Candidature.statut == status)
#     return query.all()

# # -----------------------------
# # DISCIPLINE
# # -----------------------------
# def create_discipline_case(db: Session, case_data: dict):
#     """Créer un cas de discipline"""
#     if DisciplineCase is None:
#         raise ImportError("Module DisciplineCase non disponible")
    
#     db_case = DisciplineCase(
#         employee_id=case_data.employee_id,
#         case_number = case_data.case_number,
#         case_type = case_data.case_type,
#         description = case_data.description,
#         date_incident = case_data.date_incident,
#         status       = case_data.status or 'ouvert',
#         severity     = case_data.severity,    
#         created_at=datetime.now()
#     )
#     db.add(db_case)
#     db.commit()
#     db.refresh(db_case)
#     return db_case

# def add_evidence(db: Session, case_id: int, file_name: str, file_path: str, evidence_type: str = "document"):
#     """Ajouter une preuve"""
#     if DisciplineEvidence is None:
#         raise ImportError("Module DisciplineEvidence non disponible")
    
#     db_evidence = DisciplineEvidence(
#         case_id=case_id,
#         file_name=file_name,
#         file_path=file_path,
#         evidence_type=evidence_type,
#         uploaded_at=datetime.now()
#     )
#     db.add(db_evidence)
#     db.commit()
#     db.refresh(db_evidence)
#     return db_evidence

# def add_event(db: Session, case_id: int, event_type: str, description: str = "", participants: str = ""):
#     """Ajouter un événement disciplinaire"""
#     if Event is None:
#         raise ImportError("Module DisciplineEvent non disponible")
    
#     db_event = Event(
#         case_id=case_id,
#         event_type=event_type,
#         description=description,
#         participants=participants,
#         event_date=datetime.now(),
#         created_at=datetime.now()
#     )
#     db.add(db_event)
#     db.commit()
#     db.refresh(db_event)
#     return db_event

# # -----------------------------
# # LISTER / OBTENIR CAS
# # -----------------------------
# # app/crud.py - Fonction list_cases
# def list_cases(db: Session):
#     """Liste tous les cas de discipline"""
#     from app.models.discipline import DisciplineCase
#     from app.schemas.discipline import DisciplineCase as DisciplineCaseSchema
    
#     cases = db.query(DisciplineCase).all()
    
#     result = []
#     for case in cases:
#         # Convertir en schema
#         case_dict = {
#             "id": case.id,
#             "employee_id": case.employee_id,
#             "fault_type": case.fault_type or "Non spécifié",
#             "case_number": case.case_number or f"DISC-000{case.id}",
#             "case_type": case.case_type or "Général",
#             "description": case.description,
#             "date_incident": case.date_incident,
#             "status": case.status or "ouvert",
#             "severity": case.severity or "moyen",
#             "created_at": case.created_at,
#             "updated_at": case.updated_at
#         }
        
#         # Créer l'objet schema
#         case_schema = DisciplineCaseSchema(**case_dict)
#         result.append(case_schema)
    
#     return result  # Retourne liste d'objets Pydantic, pas de dicts


# def get_case(db: Session, case_id: int):
#     """Récupérer un cas par ID avec employee_name, evidences et compte-rendu"""
#     from app.models.discipline import DisciplineCase, DisciplineEvidence, DisciplineEvent
#     from app.models.models import Employee
#     from app.schemas.discipline import DisciplineCase as DisciplineCaseSchema, Evidence
#     import json

#     # Makà case SQLAlchemy
#     case = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
#     if not case:
#         return None

#     # Base case_dict
#     case_dict = {
#         "id": case.id,
#         "employee_id": case.employee_id,
#         "fault_type": case.fault_type or "Non spécifié",
#         "case_number": case.case_number or f"DISC-000{case.id}",
#         "case_type": case.case_type or "Général",
#         "description": case.description,
#         "date_incident": case.date_incident,
#         "status": case.status or "ouvert",
#         "severity": case.severity or "moyen",
#         "created_at": case.created_at,
#         "updated_at": case.updated_at
#     }

#     # Création objet Pydantic
#     case_obj = DisciplineCaseSchema(**case_dict)

#     # Employee name
#     emp = db.query(Employee).filter(Employee.id == case.employee_id).first()
#     case_obj.employee_name = emp.fullname if emp else "—"

#     # Evidences
#     evidences = db.query(DisciplineEvidence).filter(DisciplineEvidence.case_id == case.id).all()
#     case_obj.evidences = [
#         Evidence(id=f.id, file_name=f.file_name, file_url=f.file_path)
#         for f in evidences
#     ]

#     # Dernier decision event pour compte-rendu
#     last_decision_event = db.query(DisciplineEvent)\
#         .filter(DisciplineEvent.case_id == case.id)\
#         .filter(DisciplineEvent.event_type == "decision")\
#         .order_by(DisciplineEvent.created_at.desc())\
#         .first()

#     if last_decision_event:
#         decision_data = json.loads(last_decision_event.event_data)
#         case_obj.decision = {
#             "decision_type": decision_data.get("type", ""),
#             "decision_notes": decision_data.get("notes", "")
#         }
#         case_obj.compte_rendu = decision_data.get("notes", "")
#     else:
#         case_obj.decision = None
#         case_obj.compte_rendu = ""

#     # Evidences pour fichiers frontend
#     case_obj.files = [
#         {"filename": f.file_name, "filepath": f.file_path}
#         for f in evidences
#     ]

#     return case_obj



# app/crud.py - VERSION FENO VOAHITSY HO AN'NY DISCIPLINE.PY
from sqlalchemy.orm import Session
from datetime import datetime
import json

# -----------------------------
# IMPORTS MODELES
# -----------------------------
from app.models import Candidature, Employee

try:
    from app.models import DisciplineCase, DisciplineEvidence, DisciplineEvent
except ImportError:
    class DisciplineCase: pass
    class DisciplineEvidence: pass
    class DisciplineEvent: pass

# Alias Event
Event = DisciplineEvent

# -----------------------------
# CANDIDATURES
# -----------------------------
def create_candidature(db: Session, data: dict):
    db_cand = Candidature(**data)
    db.add(db_cand)
    db.commit()
    db.refresh(db_cand)
    return db_cand

def get_all_candidatures(db: Session, status: str = None):
    query = db.query(Candidature)
    if status:
        query = query.filter(Candidature.statut == status)
    return query.all()

# -----------------------------
# DISCIPLINE
# -----------------------------
def create_discipline_case(db: Session, case_data):
    db_case = DisciplineCase(
        employee_id=case_data.employee_id,
        case_number=case_data.case_number,
        case_type=case_data.case_type,
        description=case_data.description,
        fault_type=getattr(case_data, "fault_type", "Non spécifié"),
        date_incident=case_data.date_incident,
        status=case_data.status or "ouvert",
        severity=case_data.severity,
        created_at=datetime.now()
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

def add_evidence(db: Session, case_id: int, file_name: str, file_path: str, evidence_type: str = "document"):
    db_evidence = DisciplineEvidence(
        case_id=case_id,
        file_name=file_name,
        file_path=file_path,
        evidence_type=evidence_type,
        uploaded_at=datetime.now()
    )
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence

def add_event(db: Session, case_id: int, event_type: str, description: str = "", participants: str = ""):
    db_event = Event(
        case_id=case_id,
        event_type=event_type,
        description=description,
        participants=participants,
        event_date=datetime.now(),
        created_at=datetime.now()
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

# -----------------------------
# LISTER / OBTENIR CAS
# -----------------------------
def list_cases(db: Session):
    from app.models.discipline import DisciplineCase
    from app.schemas.discipline import DisciplineCase as DisciplineCaseSchema
    from app.models.discipline import DisciplineEvidence, DisciplineEvent

    cases = db.query(DisciplineCase).all()
    result = []

    for case in cases:
        # Evidences sous forme de dictionnaires
        evidences = db.query(DisciplineEvidence).filter(DisciplineEvidence.case_id == case.id).all()
        evidences_dicts = [
            {
                "id": ev.id,
                "case_id": ev.case_id,
                "file_name": ev.file_name,
                "file_path": ev.file_path,
                "evidence_type": ev.evidence_type,
                "uploaded_at": ev.uploaded_at
            }
            for ev in evidences
        ]

        # Events sous forme de dictionnaires - manampy champ event_data
        events = db.query(DisciplineEvent).filter(DisciplineEvent.case_id == case.id).all()
        events_dicts = []
        for ev in events:
            event_dict = {
                "id": ev.id,
                "case_id": ev.case_id,
                "event_type": ev.event_type,
                "description": ev.description,
                "participants": ev.participants,
                "event_date": ev.event_date,
                "created_at": ev.created_at,
                # Mampiditra event_data - raha JSON string dia convert
                "event_data": json.loads(ev.event_data) if hasattr(ev, 'event_data') and ev.event_data else {}
            }
            events_dicts.append(event_dict)

        case_dict = {
            "id": case.id,
            "employee_id": case.employee_id,
            "fault_type": case.fault_type or "Non spécifié",
            "case_number": case.case_number or f"DISC-000{case.id}",
            "case_type": case.case_type or "Général",
            "description": case.description,
            "date_incident": case.date_incident,
            "status": case.status or "ouvert",
            "severity": case.severity or "moyen",
            "created_at": case.created_at,
            "updated_at": case.updated_at,
            "evidences": evidences_dicts,
            "events": events_dicts
        }

        # Last decision event
        last_decision_event = db.query(DisciplineEvent)\
            .filter(DisciplineEvent.case_id == case.id)\
            .filter(DisciplineEvent.event_type == "decision")\
            .order_by(DisciplineEvent.created_at.desc())\
            .first()

        if last_decision_event:
            case_dict["decision"] = {
                "decision_type": last_decision_event.event_type,
                "decision_notes": last_decision_event.description
            }
            case_dict["compte_rendu"] = last_decision_event.description
        else:
            case_dict["decision"] = None
            case_dict["compte_rendu"] = ""

        # Convert to Pydantic object
        result.append(DisciplineCaseSchema(**case_dict))

    return result

def get_case(db: Session, case_id: int):
    from app.models.discipline import DisciplineCase
    from app.schemas.discipline import DisciplineCase as DisciplineCaseSchema
    from app.models.discipline import DisciplineEvidence, DisciplineEvent
    from app.models.models import Employee

    case = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
    if not case:
        return None

    # Evidences sous forme de dictionnaires
    evidences = db.query(DisciplineEvidence).filter(DisciplineEvidence.case_id == case.id).all()
    evidences_dicts = [
        {
            "id": ev.id,
            "case_id": ev.case_id,
            "file_name": ev.file_name,
            "file_path": ev.file_path,
            "evidence_type": ev.evidence_type,
            "uploaded_at": ev.uploaded_at
        }
        for ev in evidences
    ]

    # Events sous forme de dictionnaires
    events = db.query(DisciplineEvent).filter(DisciplineEvent.case_id == case.id).all()
    events_dicts = []
    for ev in events:
        event_dict = {
            "id": ev.id,
            "case_id": ev.case_id,
            "event_type": ev.event_type,
            "description": ev.description,
            "participants": ev.participants,
            "event_date": ev.event_date,
            "created_at": ev.created_at,
            "event_data": json.loads(ev.event_data) if hasattr(ev, 'event_data') and ev.event_data else {}
        }
        events_dicts.append(event_dict)

    # Construction du dict principal
    case_dict = {
        "id": case.id,
        "employee_id": case.employee_id,
        "fault_type": case.fault_type or "Non spécifié",
        "case_number": case.case_number or f"DISC-000{case.id}",
        "case_type": case.case_type or "Général",
        "description": case.description,
        "date_incident": case.date_incident,
        "status": case.status or "ouvert",
        "severity": case.severity or "moyen",
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "evidences": evidences_dicts,
        "events": events_dicts
    }

    # Ajouter employee_name
    emp = db.query(Employee).filter(Employee.id == case.employee_id).first()
    case_dict["employee_name"] = emp.fullname if emp else "—"

    # Last decision event
    last_decision_event = db.query(DisciplineEvent)\
        .filter(DisciplineEvent.case_id == case.id)\
        .filter(DisciplineEvent.event_type == "decision")\
        .order_by(DisciplineEvent.created_at.desc())\
        .first()

    if last_decision_event:
        case_dict["decision"] = {
            "decision_type": last_decision_event.event_type,
            "decision_notes": last_decision_event.description
        }
        case_dict["compte_rendu"] = last_decision_event.description
    else:
        case_dict["decision"] = None
        case_dict["compte_rendu"] = ""

    return DisciplineCaseSchema(**case_dict)
# -----------------------------

def get_last_event(db: Session, case_id: int):
    return db.query(Event)\
        .filter(Event.case_id == case_id)\
        .order_by(Event.created_at.desc())\
        .first()

def get_last_event_of_type(db: Session, case_id: int, event_type: str):
    return db.query(Event)\
        .filter(Event.case_id == case_id)\
        .filter(Event.event_type == event_type)\
        .order_by(Event.created_at.desc())\
        .first()

def get_evidences(db: Session, case_id: int):
    return db.query(DisciplineEvidence).filter(DisciplineEvidence.case_id == case_id).all()

# -----------------------------
# EMPLOYÉS
# -----------------------------
def get_employee(db: Session, employee_id: int):
    return db.query(Employee).filter(Employee.id == employee_id).first()

def list_employees(db: Session):
    return db.query(Employee).all()

# -----------------------------
# METTRE À JOUR / SUPPRIMER CAS
# -----------------------------
def update_case_status(db: Session, case_id: int, new_status: str):
    c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
    if c:
        c.status = new_status
        db.commit()
        db.refresh(c)
    return c

def delete_case(db: Session, case_id: int):
    c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
    if c:
        db.delete(c)
        db.commit()
        return True
    return False

def case_exists(db: Session, case_id: int):
    return db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first() is not None