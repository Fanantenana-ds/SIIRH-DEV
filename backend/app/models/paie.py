from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class Paie(Base):
    __tablename__ = "paie"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    mois = Column(String(20))
    salaire_base = Column(Float)
    primes = Column(Float, default=0.0)
    net_a_payer = Column(Float, default=0)
    montant = Column(Float, default=0)
    statut = Column(String(20))
    date_paiement = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    deductions = Column(Float, default=0.0)
    absence_deduction = Column(Float, default=0)
    heures_supp = Column(Float, default=0)
    annee = Column(Integer, default=datetime.now().year)
    

    # Relation
    employee = relationship("Employee", back_populates="paies")
