from pydantic import BaseModel
from datetime import date

class CongeBase(BaseModel):
    employee_id: int
    date_debut: date
    date_fin: date
    motif: str
    statut: str = "en attente"

class CongeCreate(CongeBase):
    pass

class CongeUpdate(CongeBase):
    pass

class CongeOut(CongeBase):
    id: int
    class Config:
        orm_mode = True
