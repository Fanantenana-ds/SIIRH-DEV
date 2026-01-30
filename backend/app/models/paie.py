# app/models/paie.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class Paie(Base):
    """Modèle pour la gestion de la paie"""
    __tablename__ = "paie"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    mois = Column(String(7))  # Format: YYYY-MM
    salaire_base = Column(Float)
    prime = Column(Float, default=0.0)
    deduction = Column(Float, default=0.0)
    net_a_payer = Column(Float)
    statut = Column(String(20), default="en attente")  # payé, en attente
    date_paiement = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text, nullable=True)
    
    # Relation
    employee = relationship("Employee", back_populates="paies")