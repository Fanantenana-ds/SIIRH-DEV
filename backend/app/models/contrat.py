from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from app.db import Base

class Contrat(Base):
    __tablename__ = "contrats"

    id = Column(Integer, primary_key=True, index=True)
    
    # Champs de base
    type_contrat = Column(String(50), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    salaire = Column(Float, nullable=False)

    # Ajouts CDC
    periode = Column(String(50), nullable=True)           # ex: "CDI 6 mois renouvelable"
    avantages = Column(Text, nullable=True)               # liste d'avantages
    clauses = Column(Text, nullable=True)                 # clauses diverses
    horaire_travail = Column(String(50), nullable=True)   # plein temps / partiel
    preavis = Column(String(50), nullable=True)           # généré auto

    employee_id = Column(Integer, ForeignKey("employees.id"))

    employee = relationship("Employee", backref="contrats")
