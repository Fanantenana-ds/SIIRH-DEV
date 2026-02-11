from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# 🔹 Schema création convocation
class ConvocationCreate(BaseModel):
    date: str              # YYYY-MM-DD
    heure: str             # HH:MM
    lieu: str
    interval_minute: Optional[int] = 15  # default 15 min

# 🔹 Schema lecture convocation (GET/response)
class ConvocationRead(BaseModel):
    id: int
    date_entretien: str
    heure_entretien: str
    lieu_entretien: str
    status: str
    candidature_id: Optional[int]
    created_at: Optional[datetime]

    class Config:
        from_attributes = True  # Pydantic v2 equivalent de orm_mode
