from pydantic import BaseModel, Field
from typing import Optional

# ------------------------
# Pour l'employé lié à la paie
# ------------------------
class EmployeeOut(BaseModel):
    id: int
    fullname: str  # Efa manana property fullname ao amin'ny model Employee

    class Config:
        orm_mode = True

# ------------------------
# Base pour shared fields avec alias
# ------------------------
class PaieBase(BaseModel):
    employee_id: int
    salaire_base: Optional[float] = None
    prime: Optional[float] = Field(0.0, alias="primes")
    heures_supp: Optional[float] = 0.0
    deduction: Optional[float] = Field(0.0, alias="deductions")
    absence_deduction: Optional[float] = 0.0
    net_a_payer: Optional[float] = Field(None, alias="salaire_net")
    montant: Optional[float] = 0.0
    mois: str
    annee: int

    class Config:
        from_attributes = True  # pour Pydantic v2 compatibility
        allow_population_by_field_name = True  # permet d'utiliser "primes" dans payload

# ------------------------
# Pour création
# ------------------------
class PaieCreate(PaieBase):
    pass

# ------------------------
# Pour mise à jour
# ------------------------
class PaieUpdate(BaseModel):
    salaire_base: Optional[float] = None
    prime: Optional[float] = Field(None, alias="primes")
    heures_supp: Optional[float] = None
    deduction: Optional[float] = Field(None, alias="deductions")
    absence_deduction: Optional[float] = None
    net_a_payer: Optional[float] = Field(None, alias="salaire_net")
    montant: Optional[float] = None
    mois: Optional[str] = None
    annee: Optional[int] = None

    class Config:
        from_attributes = True
        allow_population_by_field_name = True

# ------------------------
# Pour lecture (avec id et employé lié)
# ------------------------
class PaieOut(PaieBase):
    id: int
    employee: Optional[EmployeeOut]

    class Config:
        orm_mode = True
        from_attributes = True

# ------------------------
# Pour export CSV / Excel
# ------------------------
class PaieExportOut(BaseModel):
    employee_id: int
    nom: str
    prenom: str
    heures_normales: float
    heures_supplementaires: float
    absences_non_payees: int

    class Config:
        orm_mode = True
