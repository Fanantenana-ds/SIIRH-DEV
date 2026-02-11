from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime


class DisciplineCase(Base):
    """Cas de discipline"""
    __tablename__ = "discipline_cases"
    __table_args__ = {"extend_existing": True} 
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    case_number = Column(String(50), unique=True)
    case_type = Column(String(100))  # avertissement, suspension, licenciement
    description = Column(Text)
    date_incident = Column(Date)
    date_reported = Column(Date, default=datetime.utcnow().date)
    fault_type = Column(String, nullable=True)
    status = Column(String(50), default="ouvert")  # ouvert, en investigation, clos
    severity = Column(String(50))  # léger, moyen, grave
    decision = Column(Text, nullable=True)
    decision_date = Column(Date, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


    # Relations
    employee = relationship("Employee")
    evidences = relationship("DisciplineEvidence", back_populates="case", cascade="all, delete-orphan")
    events = relationship("DisciplineEvent", back_populates="case", cascade="all, delete-orphan")


class DisciplineEvidence(Base):
    """Preuves pour un cas de discipline"""
    __tablename__ = "discipline_evidences"
    __table_args__ = {"extend_existing": True} 
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("discipline_cases.id"))
    evidence_type = Column(String(50))  # document, photo, témoignage, email
    file_path = Column(Text, nullable=True)
    file_name = Column(String(255), nullable=True)
    description = Column(Text)
    uploaded_by = Column(Integer, ForeignKey("utilisateurs.id"))
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    case = relationship("DisciplineCase", back_populates="evidences")


class DisciplineEvent(Base):
    """Événements liés à un cas de discipline"""
    __tablename__ = "discipline_events"
    __table_args__ = {"extend_existing": True} 
     
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("discipline_cases.id"))
    event_type = Column(String(50))  # réunion, audition, décision
    event_date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    participants = Column(Text, nullable=True)  # liste des participants
    created_by = Column(Integer, ForeignKey("utilisateurs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    case = relationship("DisciplineCase", back_populates="events")


class Discipline:
    """Classe helper pour la gestion globale des disciplines"""
    
    @staticmethod
    def case_status_options():
        return ["ouvert", "en investigation", "clos"]

    @staticmethod
    def severity_levels():
        return ["léger", "moyen", "grave"]

    @staticmethod
    def case_types():
        return ["avertissement", "suspension", "licenciement"]
