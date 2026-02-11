from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional

class PointageBase(BaseModel):
    employee_id: int
    date: date
    heure_entree: Optional[time]
    heure_sortie: Optional[time]

class PointageCreate(PointageBase):
    mode: Optional[str] = "manuel"

class PointageUpdate(BaseModel):
    date: Optional[date]
    heure_entree: Optional[time]
    heure_sortie: Optional[time]

class PointageOut(PointageBase):
    id: int
    mode: str

    class Config:
        from_attributes = True


# 🔹 NOUVEAU – Détail pointage résumé
class PointageDetail(BaseModel):
    date: date
    heure_entree: Optional[time]
    heure_sortie: Optional[time]


# 🔹 NOUVEAU – Résumé par employé
class PointageResume(BaseModel):
    employee_id: int
    nom: str
    prenom: str
    jours_travailles: int
    jours_theoriques: int
    absences: int
    pointages: List[PointageDetail]
