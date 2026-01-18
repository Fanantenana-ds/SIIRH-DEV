from sqlalchemy import Column, Integer, String, Float, ForeignKey, Text, JSON, Date, Time
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import date


class Candidature(Base):
    __tablename__ = "candidatures"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    fullname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    phone = Column(String(50), nullable=True)
    source = Column(String(100), nullable=True)
    raw_cv_s3 = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    score = Column(Float, nullable=True)
    statut = Column(String(50), default="nouveau")
    poste = Column(String(100), nullable=True)

    offre_id = Column(Integer, ForeignKey("offres.id", ondelete="CASCADE"), nullable=False)

    offre = relationship("Offre", back_populates="candidatures")
    convocations = relationship(
        "Convocation",
        back_populates="candidature",
        cascade="all, delete-orphan"
    )
    employee = relationship("Employee", back_populates="candidature", uselist=False)


class Employee(Base):
    __tablename__ = "employees"
    __table_args__ = {"extend_existing": True}  # hisorohana olana raha efa misy

    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    fullname = Column(String(255), nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    poste = Column(String(100), nullable=True)
    candidature_id = Column(Integer, ForeignKey("candidatures.id"), nullable=True)

    solde_conges = Column(Integer, default=0, nullable=False)
    date_solde_update = Column(Date, nullable=True)

    # Relations
    candidature = relationship("Candidature", back_populates="employee")
    paies = relationship("Paie", back_populates="employee")
    contrats = relationship("Contrat", back_populates="employee")
    absences = relationship("Absence", back_populates="employee", cascade="all, delete-orphan")


class Paie(Base):
    __tablename__ = "paies"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    montant = Column(Float, nullable=False)
    salaire_base = Column(Float, nullable=True)
    primes = Column(Float, default=0.0)
    heures_supp = Column(Float, default=0.0)
    deductions = Column(Float, default=0.0)
    absence_deduction = Column(Float, default=0.0)
    salaire_net = Column(Float, nullable=True)

    mois = Column(String(20), nullable=False)
    annee = Column(Integer, nullable=False)

    date_paie = Column(Date, nullable=False, default=date.today)

    employee = relationship("Employee", back_populates="paies")


class Contrat(Base):
    __tablename__ = "contrats"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)
    type_contrat = Column(String(50), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date, nullable=True)
    salaire = Column(Float, nullable=True)

    # ✅ Nouvelles colonnes pour CDC
    poste = Column(String(100), nullable=True)
    periode = Column(String(50), nullable=True)
    avantages = Column(String(255), nullable=True)
    clauses = Column(String(255), nullable=True)
    type_travail = Column(String(50), default="Temps plein", nullable=True)
    preavis = Column(String(50), nullable=True)
    indemnites = Column(String(255), nullable=True)

    # Relationship
    employee = relationship("Employee", back_populates="contrats")



class ConvocationTemplate(Base):
    __tablename__ = "convocation_templates"

    id = Column(Integer, primary_key=True)
    date_entretien = Column(String, nullable=False)
    heure_entretien = Column(String, nullable=False)
    lieu_entretien = Column(String, nullable=False)
    interval_minute = Column(Integer, default=15)


class Convocation(Base):
    __tablename__ = "convocations"

    id = Column(Integer, primary_key=True)
    candidature_id = Column(Integer, ForeignKey("candidatures.id"), nullable=False)
    date_entretien = Column(String, nullable=False)
    heure_entretien = Column(String, nullable=False)
    lieu_entretien = Column(String, nullable=False)
    status = Column(String, default="en attente")
    lien_fichier = Column(String, nullable=True)

    candidature = relationship("Candidature", back_populates="convocations")


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

    employee = relationship("Employee", back_populates="absences")


class Conge(Base):
    __tablename__ = "conges"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date_debut = Column(Date)
    date_fin = Column(Date)
    motif = Column(String)
    statut = Column(String, default="en attente")  # en attente / validée / refusée


class Pointage(Base):
    __tablename__ = "pointages"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"))
    date = Column(Date)
    heure_entree = Column(Time)
    heure_sortie = Column(Time)
    mode = Column(String, default="manuel")


__all__ = [
    "Employee",
    "Paie",
    "Contrat",
    "Utilisateur",
    "Candidature",
    "Convocation",
    "Absence",
    "Conge",
    "Pointage",
]
