from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class CandidatureBase(BaseModel):
    nom: str
    prenom: str
    email: EmailStr
    poste: str
    telephone: Optional[str] = None
    date_candidature: Optional[datetime] = None
    statut: Optional[str] = "En attente"
    cv_path: Optional[str] = None
    score: Optional[float] = None
    ref_offre: str


class CandidatureCreate(CandidatureBase):
    pass

class CandidatureUpdate(CandidatureBase):
    pass

class CandidatureResponse(CandidatureBase):
    id: int

    class Config:
        from_attributes = True  # Remplace orm_mode = True
