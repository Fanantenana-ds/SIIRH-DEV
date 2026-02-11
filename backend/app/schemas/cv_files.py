from pydantic import BaseModel
from typing import Optional

class CVFileBase(BaseModel):
    candidature_id: int
    file_path: str

class CVFileCreate(CVFileBase):
    pass

class CVFileResponse(CVFileBase):
    id: int

    class Config:
        orm_mode = True
