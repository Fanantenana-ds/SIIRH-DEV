
# models/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON, Date, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import date

# ===================== MODELS =====================

class Offre(Base):
    __tablename__ = "offres"
    # efa misy Base tokana ao amin'ny app.db
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    job_ref = Column(String, unique=True)
    department = Column(String)
    site = Column(String)
    contract_type = Column(String)
    creation_date = Column(DateTime)
    mission = Column(String)
    activities_public = Column(String)
    goals = Column(String)
    education_level = Column(String)
    exp_required_years = Column(Integer)
    tech_skills = Column(JSON)
    soft_skills = Column(JSON)
    langs_lvl = Column(JSON)
    w_skills = Column(Float)
    w_exp = Column(Float)
    w_edu = Column(Float)
    w_proj = Column(Float)
    threshold = Column(Float)
    deadline = Column(DateTime)
    apply_link = Column(String)

    candidatures = relationship("Candidature", back_populates="offre", cascade="all, delete-orphan")

