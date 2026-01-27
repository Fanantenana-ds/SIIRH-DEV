from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db import get_db
from app import models
from datetime import date
import io
import pandas as pd
from fastapi.responses import StreamingResponse
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

router = APIRouter(tags=["Rapports RH"])

# ----------------------------
# Fonctions d'export
# ----------------------------
def export_excel(data, filename: str):
    df = pd.DataFrame(data)
    buffer = io.BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return StreamingResponse(buffer,
                             media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

def export_pdf(data, filename: str):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    margin = 40
    y = height - margin
    if data:
        columns = list(data[0].keys())
        col_width = max(70, int((width - 2*margin) / len(columns)))
        x_positions = [margin + i*col_width for i in range(len(columns))]

        # Header
        c.setFont("Helvetica-Bold", 10)
        for i, col in enumerate(columns):
            c.drawString(x_positions[i], y, str(col))
        y -= 20
        c.setFont("Helvetica", 9)

        for row in data:
            for i, col in enumerate(columns):
                value = row[col]
                if hasattr(value, "isoformat"):
                    value = value.isoformat()
                c.drawString(x_positions[i], y, str(value))
            y -= 20
            if y < margin:
                c.showPage()
                y = height - margin
                c.setFont("Helvetica-Bold", 10)
                for i, col in enumerate(columns):
                    c.drawString(x_positions[i], y, str(col))
                y -= 20
                c.setFont("Helvetica", 9)
    c.save()
    buffer.seek(0)
    return StreamingResponse(buffer,
                             media_type="application/pdf",
                             headers={"Content-Disposition": f"attachment; filename={filename}"})

# ----------------------------
# Employés
# ----------------------------
@router.get("/employes")
def rapport_employes(db: Session = Depends(get_db), export: str = Query(None)):
    employes = db.query(models.Employee).all()
    data = []
    for e in employes:
        data.append({
            "ID": e.id,
            "Nom complet": e.fullname,
            "Email": e.email,
            "Poste": e.poste,
            "Solde congés": e.solde_conges,
            "Date solde update": e.date_solde_update,
        })
    if export == "excel":
        return export_excel(data, "rapport_employes.xlsx")
    elif export == "pdf":
        return export_pdf(data, "rapport_employes.pdf")
    return {"employes": data}

# ----------------------------
# Contrats
# ----------------------------
@router.get("/contrats")
def rapport_contrats(db: Session = Depends(get_db), export: str = Query(None)):
    contrats = db.query(models.Contrat).all()
    data = []
    for c in contrats:
        data.append({
            "ID": c.id,
            "Employé": c.employee.fullname if c.employee else "—",
            "Type": c.type_contrat,
            "Date début": c.date_debut,
            "Date fin": c.date_fin,
            "Salaire": c.salaire,
            "Poste": c.poste,
            "Période": c.periode,
            "Avantages": c.avantages,
            "Clauses": c.clauses,
            "Type travail": c.type_travail,
            "Préavis": c.preavis,
            "Indemnités": c.indemnites,
        })
    if export == "excel":
        return export_excel(data, "rapport_contrats.xlsx")
    elif export == "pdf":
        return export_pdf(data, "rapport_contrats.pdf")
    return {"contrats": data}

# ----------------------------
# Contrats expirés
# ----------------------------
@router.get("/contrats/expirés")
def contrats_expired(db: Session = Depends(get_db)):
    today = date.today()
    contrats = db.query(models.Contrat).filter(models.Contrat.date_fin < today).all()
    data = []
    for c in contrats:
        data.append({
            "Employé": c.employee.fullname if c.employee else "—",
            "Date fin": c.date_fin,
            "Salaire": c.salaire,
        })
    return {"contrats_expirés": data}

# ----------------------------
# Paies
# ----------------------------
@router.get("/paies")
def rapport_paies(db: Session = Depends(get_db), export: str = Query(None)):
    paies = db.query(models.Paie).all()
    data = []
    for p in paies:
        data.append({
            "ID": p.id,
            "Employé": p.employee.fullname if p.employee else "—",
            "Mois / Année": f"{p.mois} {p.annee}",
            "Salaire de base": p.salaire_base,
            "Primes": p.primes,
            "Déductions": (p.deductions or 0) + (p.absence_deduction or 0),
            "Salaire net": p.salaire_net,
        })
    if export == "excel":
        return export_excel(data, "rapport_paies.xlsx")
    elif export == "pdf":
        return export_pdf(data, "rapport_paies.pdf")
    return {"paies": data}
