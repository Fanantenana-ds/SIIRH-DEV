from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import date, datetime

# -----------------------------
# Schemas pour les preuves
# -----------------------------
class Evidence(BaseModel):
    id: Optional[int] = None
    file_name: str
    file_url: str

# -----------------------------
# Schemas pour les événements
# -----------------------------
class Event(BaseModel):
    id: Optional[int] = None
    event_type: str
    description: Optional[str] = None  # ovaina avy amin'ny event_data taloha
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True  # Pydantic v2
        populate_by_name = True

# -----------------------------
# Schema pour la décision
# -----------------------------
class Decision(BaseModel):
    decision_type: str
    decision_notes: str
    letter_url: Optional[str] = None

# -----------------------------
# Base schemas
# -----------------------------
class DisciplineCaseBase(BaseModel):
    employee_id: int
    fault_type: str
    description: Optional[str] = None

class DisciplineCaseCreate(DisciplineCaseBase):
    case_type: str = "Général"
    case_number: Optional[str] = None
    date_incident: Optional[date] = None
    status: Optional[str] = "ouvert"
    severity: Optional[str] = None
    description: Optional[str] = None

# -----------------------------
# Full schema pour response
# -----------------------------
class DisciplineCase(DisciplineCaseBase):
    id: int
    case_type: str = "Général"
    case_number: str
    status: str = "ouvert"
    date_incident: Optional[date] = None
    severity: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    # Relations
    evidences: List[Evidence] = []
    events: List[Event] = []
    
    # Champs calculés/ajoutés
    decision: Optional[Dict[str, Any]] = None
    compte_rendu: Optional[str] = None
    employee_name: Optional[str] = None
    files: Optional[List[Dict[str, str]]] = None  
    
    class Config:
        from_attributes = True
        populate_by_name = True

# -----------------------------
# Schema pour mise à jour
# -----------------------------
class DisciplineCaseUpdate(BaseModel):
    fault_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    severity: Optional[str] = None
    date_incident: Optional[date] = None

# -----------------------------
# Schema pour convocation
# -----------------------------
class ConvocationData(BaseModel):
    date_convocation: str
    heure_convocation: str
    lieu_convocation: Optional[str] = "Bureau RH"

# -----------------------------
# Schema pour recherche/filtre
# -----------------------------
class CaseFilter(BaseModel):
    status: Optional[str] = None
    fault_type: Optional[str] = None
    employee_id: Optional[int] = None
    date_from: Optional[date] = None
    date_to: Optional[date] = None
