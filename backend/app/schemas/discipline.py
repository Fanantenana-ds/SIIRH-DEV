from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# ============================
# 🔹 Base Schema
# ============================
class DisciplineBase(BaseModel):
    employee_id: int
    fault_category: str
    fault_nature: str
    description: str
    proof_files: List[str] = []
    convocation_model: str
    convocation_date: str       # "YYYY-MM-DD" format
    convocation_time: str       # "HH:MM"
    convocation_place: str
    convocation_manager: str

# ============================
# 🔹 Schema pour CREATE
# ============================
class DisciplineCreate(DisciplineBase):
    pass


# ============================
# 🔹 Schema pour RESPONSE
# ============================
class DisciplineResponse(BaseModel):
    id: int
    employee_id: int
    fault_category: str
    fault_nature: str
    description: str
    proof_files: Optional[str]
    convocation_model: Optional[str]
    convocation_date: Optional[date]
    convocation_time: Optional[str]
    convocation_place: Optional[str]
    convocation_manager: Optional[str]
    date_created: Optional[date]

    class Config:
        orm_mode = True
