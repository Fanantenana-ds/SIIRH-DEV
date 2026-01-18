# app/models/__init__.py

# Import avy amin'ny discipline.py
from .discipline import DisciplineCase, DisciplineEvidence, Event

# Import avy amin'ny models hafa
from .models import (
    Candidature,
    Employee,
    Paie,
    Contrat,
    Convocation
)

# Lisitry ny exports raha manao from app.models import *
__all__ = [
    "Candidature",
    "Employee",
    "Paie",
    "Contrat",
    "Utilisateur",
    "Convocation",
    "DisciplineCase",
    "DisciplineEvidence",
    "Event"
]
