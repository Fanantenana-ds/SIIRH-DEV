from pydantic import BaseModel
from datetime import date


# ======================
#   CREATE
# ======================
class LeaveCreate(BaseModel):
    employee_id: int
    type_conge: str               
    date_debut: date
    date_fin: date
    motif: str | None = None


# ======================
#   UPDATE
# ======================
class LeaveUpdate(BaseModel):
    type_conge: str | None = None   
    date_debut: date | None = None
    date_fin: date | None = None
    motif: str | None = None
    statut: str | None = None


# ======================
#   OUTPUT
# ======================
class LeaveOut(BaseModel):
    id: int
    employee_id: int
    date_debut: date
    date_fin: date
    type: str                     
    motif: str | None = None
    statut: str

    class Config:
        orm_mode = True
        from_attributes = True
