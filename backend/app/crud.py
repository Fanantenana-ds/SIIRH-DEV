# # app/crud.py - VERSION CORRIGÉE
# from sqlalchemy.orm import Session
# from datetime import datetime
# import json

# # -----------------------------
# # IMPORTS CORRIGÉS
# # -----------------------------
# from app.models import Candidature, Employee

# # Import discipline avec gestion d'erreur
# try:
#     from app.models import DisciplineCase, DisciplineEvidence, DisciplineEvent
#     # Créer un alias Event pour DisciplineEvent (pour compatibilité)
#     Event = DisciplineEvent
# except ImportError:
#     # Si les modèles n'existent pas, créer des classes vides
#     class DisciplineCase:
#         pass
#     class DisciplineEvidence:
#         pass
#     class DisciplineEvent:
#         pass
#     Event = None
#     print("⚠️ Modules discipline non trouvés - fonctionnement en mode limité")

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
# # DISCIPLINE - AVEC VÉRIFICATION
# # -----------------------------
# def create_discipline_case(db: Session, case_data):
#     """Créer un cas de discipline"""
#     # Vérifier si DisciplineCase est disponible
#     if DisciplineCase is None or DisciplineCase.__name__ == 'DisciplineCase':
#         raise ImportError("Module DisciplineCase non disponible")
    
#     db_case = DisciplineCase(
#         employee_id=case_data.get('employee_id'),
#         fault_type=case_data.get('fault_type'),
#         description=case_data.get('description'),
#         status="En cours",
#         created_at=datetime.now()
#     )
#     db.add(db_case)
#     db.commit()
#     db.refresh(db_case)
#     return db_case

# def add_evidence(db: Session, case_id: int, file_name: str, file_url: str):
#     """Ajouter une preuve à un cas de discipline"""
#     if DisciplineEvidence is None:
#         raise ImportError("Module DisciplineEvidence non disponible")
    
#     # Vérifier la structure du modèle
#     try:
#         # Essayer avec discipline_case_id (structure probable)
#         db_evidence = DisciplineEvidence(
#             discipline_case_id=case_id,
#             file_name=file_name,
#             file_url=file_url,
#             created_at=datetime.now()
#         )
#     except TypeError:
#         # Essayer avec case_id
#         db_evidence = DisciplineEvidence(
#             case_id=case_id,
#             file_name=file_name,
#             file_url=file_url,
#             created_at=datetime.now()
#         )
    
#     db.add(db_evidence)
#     db.commit()
#     db.refresh(db_evidence)
#     return db_evidence

# def add_event(db: Session, case_id: int, event_type: str, event_data: dict):
#     """Ajoute un événement disciplinaire (JSON serialisé)."""
#     if Event is None:
#         raise ImportError("Module Event/DisciplineEvent non disponible")
    
#     # Vérifier la structure
#     try:
#         # Essayer avec discipline_case_id
#         db_event = Event(
#             discipline_case_id=case_id,
#             event_type=event_type,
#             event_data=json.dumps(event_data),
#             created_at=datetime.now()
#         )
#     except TypeError:
#         try:
#             # Essayer avec case_id
#             db_event = Event(
#                 case_id=case_id,
#                 event_type=event_type,
#                 event_data=json.dumps(event_data),
#                 created_at=datetime.now()
#             )
#         except TypeError:
#             # Structure simple
#             db_event = Event(
#                 case_id=case_id,
#                 event_type=event_type,
#                 notes=json.dumps(event_data),
#                 created_at=datetime.now()
#             )
    
#     db.add(db_event)
#     db.commit()
#     db.refresh(db_event)
#     return db_event

# def list_cases(db: Session):
#     """Lister tous les cas de discipline"""
#     if DisciplineCase is None:
#         return []
    
#     cases = db.query(DisciplineCase).order_by(DisciplineCase.created_at.desc()).all()
#     result = []
    
#     for c in cases:
#         emp = get_employee(db, c.employee_id)
#         c_dict = {
#             "id": c.id,
#             "employee_id": c.employee_id,
#             "fault_type": getattr(c, 'fault_type', getattr(c, 'case_type', '')),
#             "description": c.description,
#             "status": c.status,
#             "created_at": c.created_at,
#             "employee_name": f"{emp.nom} {emp.prenom}" if emp else "Inconnu"
#         }
        
#         # Ajouter evidences
#         evidences = get_evidences(db, c.id)
#         c_dict["files"] = [
#             {
#                 "filename": getattr(f, 'file_name', ''),
#                 "filepath": getattr(f, 'file_url', getattr(f, 'file_path', ''))
#             }
#             for f in evidences
#         ]
        
#         # Ajouter dernière décision si existe
#         last_decision_event = get_last_event_of_type(db, c.id, "decision")
#         if last_decision_event:
#             try:
#                 event_data = json.loads(getattr(last_decision_event, 'event_data', '{}'))
#             except:
#                 event_data = {}
            
#             c_dict["decision"] = {
#                 "decision_type": event_data.get("type", ""),
#                 "decision_notes": event_data.get("notes", "")
#             }
#             c_dict["compte_rendu"] = event_data.get("notes", "")
#         else:
#             c_dict["decision"] = None
#             c_dict["compte_rendu"] = ""
        
#         result.append(c_dict)
    
#     return result

# def get_case(db: Session, case_id: int):
#     """Obtenir un cas spécifique"""
#     if DisciplineCase is None:
#         return None
    
#     c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
#     if not c:
#         return None
    
#     emp = get_employee(db, c.employee_id)
#     c_dict = {
#         "id": c.id,
#         "employee_id": c.employee_id,
#         "fault_type": getattr(c, 'fault_type', getattr(c, 'case_type', '')),
#         "description": c.description,
#         "status": c.status,
#         "created_at": c.created_at,
#         "employee_name": f"{emp.nom} {emp.prenom}" if emp else "Inconnu"
#     }
    
#     # Ajouter evidences
#     evidences = get_evidences(db, c.id)
#     c_dict["files"] = [
#         {
#             "filename": getattr(f, 'file_name', ''),
#             "filepath": getattr(f, 'file_url', getattr(f, 'file_path', ''))
#         }
#         for f in evidences
#     ]
    
#     # Ajouter dernière décision
#     last_decision_event = get_last_event_of_type(db, case_id, "decision")
#     if last_decision_event:
#         try:
#             event_data = json.loads(getattr(last_decision_event, 'event_data', '{}'))
#         except:
#             event_data = {}
        
#         c_dict["decision"] = {
#             "decision_type": event_data.get("type", ""),
#             "decision_notes": event_data.get("notes", "")
#         }
#         c_dict["compte_rendu"] = event_data.get("notes", "")
#     else:
#         c_dict["decision"] = None
#         c_dict["compte_rendu"] = ""
    
#     return c_dict

# def get_employee(db: Session, employee_id: int):
#     """Obtenir un employé par ID"""
#     return db.query(Employee).filter(Employee.id == employee_id).first()

# def list_employees(db: Session):
#     """Lister tous les employés"""
#     return db.query(Employee).all()

# def update_case_status(db: Session, case_id: int, new_status: str):
#     """Mettre à jour le statut d'un cas"""
#     if DisciplineCase is None:
#         return None
    
#     c = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
#     if c:
#         c.status = new_status
#         db.commit()
#         db.refresh(c)
#     return c

# # -----------------------------
# # FONCTIONS UTILITAIRES
# # -----------------------------
# def get_last_event_of_type(db: Session, case_id: int, event_type: str):
#     """Retourne le dernier Event d'un type donné"""
#     if Event is None:
#         return None
    
#     # Essayer différents noms de colonnes
#     try:
#         return (
#             db.query(Event)
#             .filter(
#                 Event.discipline_case_id == case_id,
#                 Event.event_type == event_type
#             )
#             .order_by(Event.created_at.desc())
#             .first()
#         )
#     except:
#         try:
#             return (
#                 db.query(Event)
#                 .filter(
#                     Event.case_id == case_id,
#                     Event.event_type == event_type
#                 )
#                 .order_by(Event.created_at.desc())
#                 .first()
#             )
#         except:
#             return None

# def get_evidences(db: Session, case_id: int):
#     """Obtenir toutes les preuves d'un cas"""
#     if DisciplineEvidence is None:
#         return []
    
#     # Essayer différents noms de colonnes
#     try:
#         return db.query(DisciplineEvidence).filter(DisciplineEvidence.discipline_case_id == case_id).all()
#     except:
#         try:
#             return db.query(DisciplineEvidence).filter(DisciplineEvidence.case_id == case_id).all()
#         except:
#             return []

# # -----------------------------
# # FONCTIONS COMPATIBILITÉ
# # -----------------------------
# def case_exists(db: Session, case_id: int):
#     """Vérifier si un cas existe"""
#     if DisciplineCase is None:
#         return False
#     return db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first() is not None

# def delete_case(db: Session, case_id: int):
#     """Supprimer un cas de discipline"""
#     if DisciplineCase is None:
#         return False
    
#     case = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
#     if case:
#         db.delete(case)
#         db.commit()
#         return True
#     return False




# app/crud.py - VERSION FENO SY HIFANENTANA AMIN'NY DISCIPLINE.PY
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
def create_discipline_case(db: Session, case_data: dict):
    """Créer un cas de discipline"""
    if DisciplineCase is None:
        raise ImportError("Module DisciplineCase non disponible")
    
    db_case = DisciplineCase(
        employee_id=case_data.employee_id,
        case_number = case_data.case_number,
        case_type = case_data.case_type,
        description = case_data.description,
        date_incident = case_data.date_incident,
        status       = case_data.status or 'ouvert',
        severity     = case_data.severity,    
        created_at=datetime.now()
    )
    db.add(db_case)
    db.commit()
    db.refresh(db_case)
    return db_case

def add_evidence(db: Session, case_id: int, file_name: str, file_path: str, evidence_type: str = "document"):
    """Ajouter une preuve"""
    if DisciplineEvidence is None:
        raise ImportError("Module DisciplineEvidence non disponible")
    
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
    """Ajouter un événement disciplinaire"""
    if Event is None:
        raise ImportError("Module DisciplineEvent non disponible")
    
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
# app/crud.py - Fonction list_cases
def list_cases(db: Session):
    """Liste tous les cas de discipline"""
    from app.models.discipline import DisciplineCase
    from app.schemas.discipline import DisciplineCase as DisciplineCaseSchema
    
    cases = db.query(DisciplineCase).all()
    
    result = []
    for case in cases:
        # Convertir en schema
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
            "updated_at": case.updated_at
        }
        
        # Créer l'objet schema
        case_schema = DisciplineCaseSchema(**case_dict)
        result.append(case_schema)
    
    return result  # Retourne liste d'objets Pydantic, pas de dicts

# Fonction get_case
def get_case(db: Session, case_id: int):
    """Récupérer un cas par ID"""
    from app.models.discipline import DisciplineCase
    from app.schemas.discipline import DisciplineCase as DisciplineCaseSchema
    
    case = db.query(DisciplineCase).filter(DisciplineCase.id == case_id).first()
    if not case:
        return None
    
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
        "updated_at": case.updated_at
    }
    
    return DisciplineCaseSchema(**case_dict)  # Retourne objet Pydantic

def get_last_event(db: Session, case_id: int):
    if Event is None:
        return None
    return (
        db.query(Event)
        .filter(Event.case_id == case_id)
        .order_by(Event.created_at.desc())
        .first()
    )

def get_evidences(db: Session, case_id: int):
    if DisciplineEvidence is None:
        return []
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
    c = get_case(db, case_id)
    if c:
        c.status = new_status
        db.commit()
        db.refresh(c)
    return c

def delete_case(db: Session, case_id: int):
    c = get_case(db, case_id)
    if c:
        db.delete(c)
        db.commit()
        return True
    return False

def case_exists(db: Session, case_id: int):
    return get_case(db, case_id) is not None





def get_last_event_of_type(db: Session, case_id: int, event_type: str):
    """
    Mamerina ny event farany amin'ny case_id sy event_type
    """
    return (
        db.query(DisciplineEvent)
        .filter(DisciplineEvent.case_id == case_id)
        .filter(DisciplineEvent.event_type == event_type)
        .order_by(DisciplineEvent.created_at.desc())
        .first()
    )