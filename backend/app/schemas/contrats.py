from pydantic import BaseModel
from datetime import date
from typing import Optional

class ContratBase(BaseModel):
    employee_id: int
    type_contrat: str
    date_debut: date
    date_fin: Optional[date] = None
    salaire: float

    # Ajouts CDC
    poste: Optional[str] = None
    periode: Optional[str] = None
    avantages: Optional[str] = None
    clauses: Optional[str] = None
    type_travail: Optional[str] = None
    preavis: Optional[str] = None
    indemnites: Optional[str] = None


class ContratCreate(ContratBase):
    pass


class ContratUpdate(BaseModel):
    type_contrat: Optional[str] = None
    date_debut: Optional[date] = None
    date_fin: Optional[date] = None
    salaire: Optional[float] = None
    poste: Optional[str] = None
    periode: Optional[str] = None
    avantages: Optional[str] = None
    clauses: Optional[str] = None
    type_travail: Optional[str] = None
    preavis: Optional[str] = None
    indemnites: Optional[float] = None

class ContratOut(ContratBase):
    id: int

    class Config:
        orm_mode = True
