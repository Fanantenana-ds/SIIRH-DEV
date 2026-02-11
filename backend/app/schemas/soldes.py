from pydantic import BaseModel

class SoldeOut(BaseModel):
    employee_id: int
    nom: str
    prenom: str
    conges_pris: int
    absences_non_payees: int
    solde_conges: int

    class Config:
        orm_mode = True
