from pydantic import BaseModel
from datetime import datetime

class ReportBase(BaseModel):
    titre: str
    contenu: str
    date_creation: datetime

class ReportCreate(ReportBase):
    pass

class ReportResponse(ReportBase):
    id: int

    class Config:
        orm_mode = True
