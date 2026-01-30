# app/models/__init__.py - AMPIO NY DISCIPLINE
from app.db import Base

# Modules essentiels
from .models import Candidature, Employee, Convocation, Absence, Conge, Pointage
from .utilisateur import Utilisateur
from .offres import Offre
from .contrat import Contrat

# Paie
try:
    from .paie import Paie
except ImportError:
    from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
    class Paie(Base):
        __tablename__ = "paie"
        id = Column(Integer, primary_key=True)
        employee_id = Column(Integer, ForeignKey("employees.id"))
        mois = Column(String(7))
        salaire_base = Column(Float)
        prime = Column(Float, default=0.0)
        deduction = Column(Float, default=0.0)
        net_a_payer = Column(Float)
        statut = Column(String(20), default="en attente")

# Discipline - si le fichier existe
try:
    from .discipline import DisciplineCase, DisciplineEvidence, DisciplineEvent, Discipline
    DISCIPLINE_AVAILABLE = True
except ImportError:
    # Créer des classes vides si nécessaire
    from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Date
    
    class DisciplineCase(Base):
        __tablename__ = "discipline_cases"
        id = Column(Integer, primary_key=True)
        employee_id = Column(Integer, ForeignKey("employees.id"))
        case_type = Column(String(100))
        description = Column(Text)
        status = Column(String(50), default="ouvert")
    
    class DisciplineEvidence(Base):
        __tablename__ = "discipline_evidences"
        id = Column(Integer, primary_key=True)
        case_id = Column(Integer, ForeignKey("discipline_cases.id"))
        evidence_type = Column(String(50))
        description = Column(Text)
    
    class DisciplineEvent(Base):
        __tablename__ = "discipline_events"
        id = Column(Integer, primary_key=True)
        case_id = Column(Integer, ForeignKey("discipline_cases.id"))
        event_type = Column(String(50))
        description = Column(Text)
    
    class Discipline(Base):
        __tablename__ = "disciplines"
        id = Column(Integer, primary_key=True)
        employee_id = Column(Integer, ForeignKey("employees.id"))
        type_sanction = Column(String(100))
        motif = Column(Text)
    
    DISCIPLINE_AVAILABLE = False
    print("⚠️ Module discipline créé en mode fallback")

# Autres modules optionnels
try:
    from .cv_data import CVData
except ImportError:
    CVData = None

try:
    from .email_models import EmailModels
except ImportError:
    EmailModels = None

try:
    from .leave import Leave
except ImportError:
    Leave = None

try:
    from .time_entry import TimeEntry
except ImportError:
    TimeEntry = None

# SMTPConfig, AuditLog, Notification, Entretien depuis models.py
from .models import SMTPConfig, AuditLog, Notification, Entretien

__all__ = [
    "Base",
    "Utilisateur",
    "Employee",
    "Paie",
    "Contrat",
    "Candidature",
    "Offre",
    "Convocation",
    "Absence",
    "Conge",
    "Pointage",
    "SMTPConfig",
    "AuditLog",
    "Notification",
    "Entretien",
    "DisciplineCase",
    "DisciplineEvidence",
    "DisciplineEvent",
    "Discipline",
]

# Ajouter les modules optionnels s'ils existent
if CVData:
    __all__.append("CVData")
if EmailModels:
    __all__.append("EmailModels")
if Leave:
    __all__.append("Leave")
if TimeEntry:
    __all__.append("TimeEntry")