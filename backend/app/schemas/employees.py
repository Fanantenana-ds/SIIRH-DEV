# from pydantic import BaseModel
# from typing import Optional
# from datetime import date

# class EmployeeBase(BaseModel):
#     nom: str
#     prenom: str
#     email: str
#     poste: Optional[str] = None
#     date_embauche: Optional[date] = None

# class EmployeeCreate(EmployeeBase):
#     pass

# class EmployeeUpdate(EmployeeBase):
#     pass

# class EmployeeResponse(EmployeeBase):
#     id: int

#     class Config:
#         orm_mode = True
# # -------------------------------
# # Schema fohy ho an'ny Discipline (autocomplete, tableau, sns)
# # -------------------------------
# class Employee(BaseModel):
#     id: int
#     nom: str
#     prenom: str
#     email: Optional[str] = None
#     poste: Optional[str] = None

#     class Config:
#         from_attributes = True   # Pydantic v2











from pydantic import BaseModel
from typing import Optional
from datetime import date

# ==========================================================
# Base schemas ho an'ny CRUD
# ==========================================================
class EmployeeBase(BaseModel):
    nom: Optional[str] = "Inconnu"
    prenom: Optional[str] = "Inconnu"
    email: Optional[str] = None
    poste: Optional[str] = None
    phone: Optional[str] = None
    date_embauche: Optional[date] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    pass

class EmployeeResponse(EmployeeBase):
    id: int

    class Config:
        orm_mode = True

# ==========================================================
# Schema fohy ho an'ny Discipline / Tableau / Autocomplete
# ==========================================================
class Employee(BaseModel):
    id: int
    nom: Optional[str] = "Inconnu"
    prenom: Optional[str] = "Inconnu"
    email: Optional[str] = None
    poste: Optional[str] = None
    phone: Optional[str] = None
    candidature_id: Optional[int] = None  # ✅ ilaina ho an'ny référence
    fullname: Optional[str] = None

    class Config:
        from_attributes = True   # Pydantic v2

    def __init__(self, **data):
        super().__init__(**data)
        # Raha tsy misy fullname, atao automatique
        if not self.fullname:
            self.fullname = f"{self.nom} {self.prenom}"
