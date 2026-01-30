

# from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime
# from sqlalchemy.orm import relationship
# from app.db import Base
# from datetime import datetime

# # ==========================================================
# # DisciplineCase
# # ==========================================================
# class DisciplineCase(Base):
#     __tablename__ = "discipline_cases"

#     id = Column(Integer, primary_key=True, index=True)
#     employee_id = Column(Integer, nullable=False)
#     fault_type = Column(String(50), nullable=False)
#     description = Column(Text)
#     status = Column(String(50), default="En cours")
#     created_at = Column(DateTime, default=datetime.now)
#     updated_at = Column(DateTime, default=datetime.now)

#     # Relations
#     evidences = relationship("DisciplineEvidence", back_populates="discipline_case", cascade="all, delete-orphan")
#     events = relationship("Event", back_populates="discipline_case", cascade="all, delete-orphan")


# # ==========================================================
# # DisciplineEvidence
# # ==========================================================
# class DisciplineEvidence(Base):
#     __tablename__ = "discipline_evidences"
#     __table_args__ = {"extend_existing": True}  # ➡️ mba tsy hiteraka duplication

#     id = Column(Integer, primary_key=True, index=True)
#     discipline_case_id = Column(Integer, ForeignKey("discipline_cases.id"), nullable=False)
#     file_name = Column(String(255), nullable=False)
#     file_url = Column(String(500), nullable=False)
#     created_at = Column(DateTime, default=datetime.now)

#     # Relation miverina amin'ny DisciplineCase
#     discipline_case = relationship("DisciplineCase", back_populates="evidences")


# # ==========================================================
# # Event
# # ==========================================================
# class Event(Base):
#     __tablename__ = "discipline_events"

#     id = Column(Integer, primary_key=True, index=True)
#     discipline_case_id = Column(Integer, ForeignKey("discipline_cases.id"))
#     event_type = Column(String(50))
#     event_data = Column(Text)
#     created_at = Column(DateTime, default=datetime.now)

#     discipline_case = relationship("DisciplineCase", back_populates="events")


# app/models/discipline.py - VERSION AVEC DisciplineCase
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date, Boolean
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime

class DisciplineCase(Base):
    """Cas de discipline"""
    __tablename__ = "discipline_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    case_number = Column(String(50), unique=True)
    case_type = Column(String(100))  # avertissement, suspension, licenciement
    description = Column(Text)
    date_incident = Column(Date)
    date_reported = Column(Date, default=datetime.utcnow().date)
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
    
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("discipline_cases.id"))
    event_type = Column(String(50))  # réunion, audition, décision
    event_date = Column(DateTime)
    description = Column(Text)
    participants = Column(Text, nullable=True)  # liste des participants
    created_by = Column(Integer, ForeignKey("utilisateurs.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relations
    case = relationship("DisciplineCase", back_populates="events")


# Classe de base Discipline (si elle existe déjà)
class Discipline(Base):
    __tablename__ = "disciplines"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    type_sanction = Column(String(100))
    motif = Column(Text)
    date_sanction = Column(DateTime)
    duree = Column(String(50))
    statut = Column(String(50), default="actif")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    employee = relationship("Employee")