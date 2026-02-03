

# app/models/models.py - VERSION COMPLÈTE
from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON, DateTime, Date, Time
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import datetime, date, time

# Import depuis les autres fichiers models
from .utilisateur import Utilisateur
from .offres import Offre
from .contrat import Contrat
from .paie import Paie

# ==================== CANDIDATURE ====================
class Candidature(Base):
    __tablename__ = "candidatures"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    telephone = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True)
    raw_cv_s3 = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    score = Column(Float, nullable=True)
    score_total = Column(Float, default=0)
    score_breakdown = Column(JSON, default={})
    statut = Column(String(50), default="nouveau")
    poste = Column(String(100), nullable=True)
    offre_id = Column(Integer, ForeignKey("offres.id", ondelete="CASCADE"), nullable=False)
    ref_offre = Column(String(100))
    
    # Champs NLP
    nlp_data = Column(JSON, nullable=True)
    competences = Column(Text, nullable=True)
    experience_years = Column(Integer, default=0)
    cv_text = Column(Text, nullable=True)
    
    # Dates
    date_candidature = Column(DateTime, default=datetime.utcnow)
    date_maj = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    offre = relationship("Offre", back_populates="candidatures")
    convocations = relationship("Convocation", back_populates="candidature", cascade="all, delete-orphan")
    employee = relationship("Employee", back_populates="candidature", uselist=False)


# ==================== EMPLOYEE ====================
class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {"extend_existing": True}
    
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(255))
    telephone = Column(String(20))
    poste = Column(String(100))
    salaire = Column(Float)
    fullname = Column(String(255))
    candidature_id = Column(Integer, ForeignKey('candidatures.id'))
    date_embauche = Column(Date, default=date.today)
    
    # ========== RELATIONS COMPLÈTES ==========
    candidature = relationship("Candidature", back_populates="employee", uselist=False)
    contrats = relationship("Contrat", back_populates="employee", cascade="all, delete-orphan")
    absences = relationship("Absence", back_populates="employee", cascade="all, delete-orphan")
    paies = relationship("Paie", back_populates="employee", cascade="all, delete-orphan")
    conges = relationship("Conge", back_populates="employee", cascade="all, delete-orphan")
    pointages = relationship("Pointage", back_populates="employee", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Employee {self.id}: {self.nom} {self.prenom}>"


# ==================== ABSENCE ====================
class Absence(Base):
    __tablename__ = "absences"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    type_absence = Column(String(50), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=False)
    motif = Column(String(255), nullable=True)
    statut = Column(String(50), default="en attente")

    # RELATION AVEC EMPLOYEE
    employee = relationship("Employee", back_populates="absences")


# ==================== CONGE ====================
class Conge(Base):
    __tablename__ = "conges"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date_debut = Column(Date)
    date_fin = Column(Date)
    motif = Column(String)
    statut = Column(String, default="en attente")
    
    # RELATION AVEC EMPLOYEE
    employee = relationship("Employee", back_populates="conges")


# ==================== POINTAGE ====================
class Pointage(Base):
    __tablename__ = "pointages"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    heure_entree = Column(Time)
    heure_sortie = Column(Time)
    mode = Column(String, default="manuel")
    
    # RELATION AVEC EMPLOYEE - CORRECTION ICI
    employee = relationship("Employee", back_populates="pointages")


# ==================== CONVOCATION ====================
class Convocation(Base):
    __tablename__ = "convocations"
    
    id = Column(Integer, primary_key=True, index=True)
    candidature_id = Column(Integer, ForeignKey("candidatures.id"), nullable=True)
    date_entretien = Column(String(50))
    heure_entretien = Column(String(50))
    lieu_entretien = Column(Text)
    status = Column(String(50), default="en attente")
    lien_fichier = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now)  # ⬅️ AJOUTÉ
    interval_minute = Column(Integer, default=15)        # ⬅️ AJOUTÉ
    
    # Relations
    candidature = relationship("Candidature", back_populates="convocations")

# ==================== SMTP CONFIG ====================
class SMTPConfig(Base):
    __tablename__ = "smtp_config"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False)
    password = Column(String, nullable=False)
    server = Column(String, default="smtp.gmail.com")
    port = Column(Integer, default=587)


# ==================== AUDIT LOG ====================
class AuditLog(Base):
    __tablename__ = "audit_logs"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    action = Column(String(100), nullable=False)
    table_concernee = Column(String(100), nullable=False)
    id_ligne = Column(Integer, nullable=True)
    ancienne_valeur = Column(JSON, nullable=True)
    nouvelle_valeur = Column(JSON, nullable=True)
    date_action = Column(DateTime, default=datetime.utcnow)
    ip_adresse = Column(String(50), nullable=True)


# ==================== NOTIFICATION ====================
class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    utilisateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=False)
    titre = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type_notification = Column(String(50), default="info")
    lue = Column(Integer, default=0)
    date_creation = Column(DateTime, default=datetime.utcnow)
    date_lecture = Column(DateTime, nullable=True)


# ==================== ENTREVIEN ====================
class Entretien(Base):
    __tablename__ = "entretiens"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    candidature_id = Column(Integer, ForeignKey("candidatures.id"), nullable=False)
    date_entretien = Column(DateTime, nullable=False)
    evaluateur_id = Column(Integer, ForeignKey("utilisateurs.id"), nullable=True)
    notes = Column(Text, nullable=True)
    score_entretien = Column(Integer, nullable=True)
    decision = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)