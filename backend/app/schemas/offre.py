from pydantic import BaseModel, Field, EmailStr
from typing import List, Dict, Optional
from datetime import date

class OffreCreate(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None
    site: Optional[str] = None
    contract_type: Optional[str] = None
    creation_date: Optional[date] = None
    
    # Description
    mission: Optional[str] = None
    activities_public: Optional[str] = None
    goals: Optional[str] = None
    
    # Profil
    education_level: Optional[str] = None
    exp_required_years: Optional[int] = None
    
    # Scoring
    tech_skills: List[str] = []
    soft_skills: List[str] = []
    langs_lvl: Dict[str, str] = {}
    w_skills: float = 0.4
    w_exp: float = 0.3
    w_edu: float = 0.2
    w_proj: float = 0.1
    threshold: float = 60.0
    scoring_config_path: str = "/configs/scoring_default.json"

    # 🔹 Ampiana saha optional ho an'ny scoring criteres
    scoring_criteres: Optional[Dict] = None
    
    # Deadline & apply link
    deadline: Optional[date] = None
    apply_link: Optional[EmailStr] = None

    class Config:
        from_attributes = True  # Pydantic V2: ORM mode

# 🔹 Schema ho an'ny response (GET /offres)
class OffreResponse(BaseModel):
    id: int
    job_ref: str
    title: Optional[str] = None
    department: Optional[str] = None
    site: Optional[str] = None
    contract_type: Optional[str] = None
    creation_date: Optional[date] = None
    
    # Description
    mission: Optional[str] = None
    activities_public: Optional[str] = None
    goals: Optional[str] = None
    
    # Profil
    education_level: Optional[str] = None
    exp_required_years: Optional[int] = None
    
    # Scoring - convert JSON string ho lisitra
    tech_skills: List[str] = []
    soft_skills: List[str] = []
    langs_lvl: Dict[str, str] = {}
    w_skills: float
    w_exp: float
    w_edu: float
    w_proj: float
    threshold: float
    scoring_config_path: str
    scoring_criteres: Optional[Dict] = None  

    # Deadline & apply link
    deadline: Optional[date] = None
    apply_link: Optional[EmailStr] = None
    job_title_display: Optional[str] = None
    department_display: Optional[str] = None
    creation_date_display: Optional[str] = None
    deadline_display: Optional[str] = None

    class Config:
        from_attributes = True  # Pydantic V2: ORM mode
