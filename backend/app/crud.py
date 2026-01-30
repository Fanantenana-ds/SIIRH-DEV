# # app/crud.py
# from sqlalchemy.orm import Session
# from app.models import Candidature, Employee, DisciplineCase, Event, DisciplineEvidence
# from datetime import datetime
# import json

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
#     return query.all()

# # -----------------------------
# # DISCIPLINE
# # -----------------------------
# def create_discipline_case(db: Session, case_data):
#     db_case = DisciplineCase(
#         employee_id=case_data.employee_id,
#         fault_type=case_data.fault_type,
#         description=case_data.description,
#         status="En cours",
#         created_at=datetime.now()
#     )
#     db.add(db_case)
#     db.commit()
#     db.refresh(db_case)
#     return db_case

# def add_evidence(db: Session, case_id: int, file_name: str, file_url: str):
#     db_evidence = DisciplineEvidence(
#         discipline_case_id=case_id,  # ✅ mifanaraka amin'ny models.py
#         file_name=file_name,
#         file_url=file_url,
#         created_at=datetime.now()
#     )
#     db.add(db_evidence)
#     db.commit()
#     db.refresh(db_evidence)
#     return db_evidence

# def add_event(db: Session, case_id: int, event_type: str, event_data: dict):
#     """Ajoute un événement disciplinaire (JSON serialisé)."""
#     db_event = Event(
#         discipline_case_id=case_id,
#         event_type=event_type,
#         event_data=json.dumps(event_data),
#         created_at=datetime.now()
#     )
#     db.add(db_event)
#     db.commit()
#     db.refresh(db_event)
#     return db_event

# def list_cases(db: Session):
#     cases = db.query(DisciplineCase).order_by(DisciplineCase.created_at.desc()).all()
#     result = []
#     for c in cases:
#         emp = get_employee(db, c.employee_id)
#         c_dict = c.__dict__.copy()
#         c_dict["employee_name"] = f"{emp.nom} {emp.prenom}" if emp else "Inconnu"
#         # Ajouter evidences
#         c_dict["files"] = [
#             {"filename": f.file_name, "filepath": f.file_url}
#             for f in get_evidences(db, c.id)
#         ]
#         # Ajouter dernier decision si exist
#         last_decision_event = get_last_event_of_type(db, c.id, "decision")
#         if last_decision_event:
#             decision_data = json.loads(last_decision_event.event_data)
#             c_dict["decision"] = {
#                 "decision_type": decision_data.get("type", ""),
#                 "decision_notes": decision_data.get("notes", "")
#             }
#             c_dict["compte_rendu"] = decision_data.get("notes", "")
#         else:
#             c_dict["decision"] = None
#             c_dict["compte_rendu"] = ""
#         result.append(c_dict)
#     return result

# def get_case(db: Session, case_id: int):
#     c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
#     if not c:
#         return None
#     emp = get_employee(db, c.employee_id)
#     c_dict = c.__dict__.copy()
#     c_dict["employee_name"] = f"{emp.nom} {emp.prenom}" if emp else "Inconnu"

#     # Ajouter evidences
#     c_dict["files"] = [
#         {"filename": f.file_name, "filepath": f.file_url}
#         for f in get_evidences(db, c.id)
#     ]

#     # Ajouter dernier decision si exist
#     last_decision_event = get_last_event_of_type(db, case_id, "decision")
#     if last_decision_event:
#         decision_data = json.loads(last_decision_event.event_data)
#         c_dict["decision"] = {
#             "decision_type": decision_data.get("type", ""),
#             "decision_notes": decision_data.get("notes", "")
#         }
#         c_dict["compte_rendu"] = decision_data.get("notes", "")
#     else:
#         c_dict["decision"] = None
#         c_dict["compte_rendu"] = ""

#     return c_dict

# def get_employee(db: Session, employee_id: int):
#     return db.query(Employee).filter(Employee.id == employee_id).first()

# def list_employees(db: Session):
#     return db.query(Employee).all()

# def update_case_status(db: Session, case_id: int, new_status: str):
#     c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
#     if c:
#         c.status = new_status
#         db.commit()
#         db.refresh(c)
#     return c

# # -----------------------------
# # LAST EVENT
# # -----------------------------
# def get_last_event_of_type(db: Session, case_id: int, event_type: str):
#     """Retourne le dernier Event d’un type donné."""
#     return (
#         db.query(Event)
#         .filter(
#             Event.discipline_case_id == case_id,
#             Event.event_type == event_type
#         )
#         .order_by(Event.created_at.desc())
#         .first()
#     )

# def get_evidences(db: Session, case_id: int):
#     return db.query(DisciplineEvidence).filter(DisciplineEvidence.discipline_case_id == case_id).all()













# app/crud.py - VERSION CORRIGÉE
from sqlalchemy.orm import Session
from datetime import datetime
import json

# -----------------------------
# IMPORTS CORRIGÉS
# -----------------------------
from app.models import Candidature, Employee

# Import discipline avec gestion d'erreur
try:
    from app.models import DisciplineCase, DisciplineEvidence, DisciplineEvent
    # Créer un alias Event pour DisciplineEvent (pour compatibilité)
    Event = DisciplineEvent
except ImportError:
    # Si les modèles n'existent pas, créer des classes vides
    class DisciplineCase:
        pass
    class DisciplineEvidence:
        pass
    class DisciplineEvent:
        pass
    Event = None
    print("⚠️ Modules discipline non trouvés - fonctionnement en mode limité")

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
# DISCIPLINE - AVEC VÉRIFICATION
# -----------------------------
def create_discipline_case(db: Session, case_data):
    """Créer un cas de discipline"""
    # Vérifier si DisciplineCase est disponible
    if DisciplineCase is None or DisciplineCase.__name__ == 'DisciplineCase':
        raise ImportError("Module DisciplineCase non disponible")
    
    db_case = DisciplineCase(
        employee_id=case_data.get('employee_id'),
        fault_type=case_data.get('fault_type'),
        description=case_data.get('description'),
        status="En cours",
        created_at=datetime.now()
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

def add_evidence(db: Session, case_id: int, file_name: str, file_url: str):
    """Ajouter une preuve à un cas de discipline"""
    if DisciplineEvidence is None:
        raise ImportError("Module DisciplineEvidence non disponible")
    
    # Vérifier la structure du modèle
    try:
        # Essayer avec discipline_case_id (structure probable)
        db_evidence = DisciplineEvidence(
            discipline_case_id=case_id,
            file_name=file_name,
            file_url=file_url,
            created_at=datetime.now()
        )
    except TypeError:
        # Essayer avec case_id
        db_evidence = DisciplineEvidence(
            case_id=case_id,
            file_name=file_name,
            file_url=file_url,
            created_at=datetime.now()
        )
    
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence

def add_event(db: Session, case_id: int, event_type: str, event_data: dict):
    """Ajoute un événement disciplinaire (JSON serialisé)."""
    if Event is None:
        raise ImportError("Module Event/DisciplineEvent non disponible")
    
    # Vérifier la structure
    try:
        # Essayer avec discipline_case_id
        db_event = Event(
            discipline_case_id=case_id,
            event_type=event_type,
            event_data=json.dumps(event_data),
            created_at=datetime.now()
        )
    except TypeError:
        try:
            # Essayer avec case_id
            db_event = Event(
                case_id=case_id,
                event_type=event_type,
                event_data=json.dumps(event_data),
                created_at=datetime.now()
            )
        except TypeError:
            # Structure simple
            db_event = Event(
                case_id=case_id,
                event_type=event_type,
                notes=json.dumps(event_data),
                created_at=datetime.now()
            )
    
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def list_cases(db: Session):
    """Lister tous les cas de discipline"""
    if DisciplineCase is None:
        return []
    
    cases = db.query(DisciplineCase).order_by(DisciplineCase.created_at.desc()).all()
    result = []
    
    for c in cases:
        emp = get_employee(db, c.employee_id)
        c_dict = {
            "id": c.id,
            "employee_id": c.employee_id,
            "fault_type": getattr(c, 'fault_type', getattr(c, 'case_type', '')),
            "description": c.description,
            "status": c.status,
            "created_at": c.created_at,
            "employee_name": f"{emp.nom} {emp.prenom}" if emp else "Inconnu"
        }
        
        # Ajouter evidences
        evidences = get_evidences(db, c.id)
        c_dict["files"] = [
            {
                "filename": getattr(f, 'file_name', ''),
                "filepath": getattr(f, 'file_url', getattr(f, 'file_path', ''))
            }
            for f in evidences
        ]
        
        # Ajouter dernière décision si existe
        last_decision_event = get_last_event_of_type(db, c.id, "decision")
        if last_decision_event:
            try:
                event_data = json.loads(getattr(last_decision_event, 'event_data', '{}'))
            except:
                event_data = {}
            
            c_dict["decision"] = {
                "decision_type": event_data.get("type", ""),
                "decision_notes": event_data.get("notes", "")
            }
            c_dict["compte_rendu"] = event_data.get("notes", "")
        else:
            c_dict["decision"] = None
            c_dict["compte_rendu"] = ""
        
        result.append(c_dict)
    
    return result

def get_case(db: Session, case_id: int):
    """Obtenir un cas spécifique"""
    if DisciplineCase is None:
        return None
    
    c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
    if not c:
        return None
    
    emp = get_employee(db, c.employee_id)
    c_dict = {
        "id": c.id,
        "employee_id": c.employee_id,
        "fault_type": getattr(c, 'fault_type', getattr(c, 'case_type', '')),
        "description": c.description,
        "status": c.status,
        "created_at": c.created_at,
        "employee_name": f"{emp.nom} {emp.prenom}" if emp else "Inconnu"
    }
    
    # Ajouter evidences
    evidences = get_evidences(db, c.id)
    c_dict["files"] = [
        {
            "filename": getattr(f, 'file_name', ''),
            "filepath": getattr(f, 'file_url', getattr(f, 'file_path', ''))
        }
        for f in evidences
    ]
    
    # Ajouter dernière décision
    last_decision_event = get_last_event_of_type(db, case_id, "decision")
    if last_decision_event:
        try:
            event_data = json.loads(getattr(last_decision_event, 'event_data', '{}'))
        except:
            event_data = {}
        
        c_dict["decision"] = {
            "decision_type": event_data.get("type", ""),
            "decision_notes": event_data.get("notes", "")
        }
        c_dict["compte_rendu"] = event_data.get("notes", "")
    else:
        c_dict["decision"] = None
        c_dict["compte_rendu"] = ""
    
    return c_dict

def get_employee(db: Session, employee_id: int):
    """Obtenir un employé par ID"""
    return db.query(Employee).filter(Employee.id == employee_id).first()

def list_employees(db: Session):
    """Lister tous les employés"""
    return db.query(Employee).all()

def update_case_status(db: Session, case_id: int, new_status: str):
    """Mettre à jour le statut d'un cas"""
    if DisciplineCase is None:
        return None
    
    c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
    if c:
        c.status = new_status
        db.commit()
        db.refresh(c)
    return c

# -----------------------------
# FONCTIONS UTILITAIRES
# -----------------------------
def get_last_event_of_type(db: Session, case_id: int, event_type: str):
    """Retourne le dernier Event d'un type donné"""
    if Event is None:
        return None
    
    # Essayer différents noms de colonnes
    try:
        return (
            db.query(Event)
            .filter(
                Event.discipline_case_id == case_id,
                Event.event_type == event_type
            )
            .order_by(Event.created_at.desc())
            .first()
        )
    except:
        try:
            return (
                db.query(Event)
                .filter(
                    Event.case_id == case_id,
                    Event.event_type == event_type
                )
                .order_by(Event.created_at.desc())
                .first()
            )
        except:
            return None

def get_evidences(db: Session, case_id: int):
    """Obtenir toutes les preuves d'un cas"""
    if DisciplineEvidence is None:
        return []
    
    # Essayer différents noms de colonnes
    try:
        return db.query(DisciplineEvidence).filter(DisciplineEvidence.discipline_case_id == case_id).all()
    except:
        try:
            return db.query(DisciplineEvidence).filter(DisciplineEvidence.case_id == case_id).all()
        except:
            return []

# -----------------------------
# FONCTIONS COMPATIBILITÉ
# -----------------------------
def case_exists(db: Session, case_id: int):
    """Vérifier si un cas existe"""
    if DisciplineCase is None:
        return False
    return db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first() is not None

def delete_case(db: Session, case_id: int):
    """Supprimer un cas de discipline"""
    if DisciplineCase is None:
        return False
    
    case = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
    if case:
        db.delete(case)
        db.commit()
        return True
    return False