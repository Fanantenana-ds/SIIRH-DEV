# from sqlalchemy.orm import Session
# from sqlalchemy import text
# from models.candidatures import Candidature
# from schemas.candidatures import CandidatureCreate
# import json

# def create_candidature(db: Session, candidature: CandidatureCreate):
#     query = text("""
#         INSERT INTO candidatures (
#             job_ref, lastname, firstname, email, phone, address, city, birthdate,
#             cv_file_id, lm_file_id, diplomes_zip_id,
#             last_job, last_company, exp_years, skills, langs_lvl, mobility_sites,
#             avail_date, sal_expectation, contract_accepted, work_permit_status,
#             consent_bool
#         ) VALUES (
#             :job_ref, :lastname, :firstname, :email, :phone, :address, :city, :birthdate,
#             :cv_file_id, :lm_file_id, :diplomes_zip_id,
#             :last_job, :last_company, :exp_years, :skills, :langs_lvl, :mobility_sites,
#             :avail_date, :sal_expectation, :contract_accepted, :work_permit_status,
#             :consent_bool
#         ) RETURNING id
#     """)

#     result = db.execute(query, {
#         "job_ref": candidature.job_ref,
#         "lastname": candidature.lastname,
#         "firstname": candidature.firstname,
#         "email": candidature.email,
#         "phone": candidature.phone,
#         "address": candidature.address,
#         "city": candidature.city,
#         "birthdate": candidature.birthdate,
#         "cv_file_id": candidature.cv_file_id,
#         "lm_file_id": candidature.lm_file_id,
#         "diplomes_zip_id": candidature.diplomes_zip_id,
#         "last_job": candidature.last_job,
#         "last_company": candidature.last_company,
#         "exp_years": candidature.exp_years,
#         "skills": json.dumps(candidature.skills) if candidature.skills else None,
#         "langs_lvl": json.dumps(candidature.langs_lvl) if candidature.langs_lvl else None,
#         "mobility_sites": json.dumps(candidature.mobility_sites) if candidature.mobility_sites else None,
#         "avail_date": candidature.avail_date,
#         "sal_expectation": candidature.sal_expectation,
#         "contract_accepted": candidature.contract_accepted,
#         "work_permit_status": candidature.work_permit_status,
#         "consent_bool": candidature.consent_bool
#     })

#     db.commit()
#     return result.fetchone()[0]

from sqlalchemy.orm import Session
from sqlalchemy import text
from models.candidatures import Candidature
from schemas.candidatures import CandidatureCreate
import json
from datetime import datetime

def create_candidature(db: Session, candidature: CandidatureCreate):
    query = text("""
        INSERT INTO candidatures (
            nom,
            prenom,
            email,
            phone,
            adresse,
            ville,
            date_naissance,
            poste,
            disponibilite,
            salaire,
            type_contrat,
            mobilite,
            autorisation,
            cv_path,
            lettre_path,
            diplomes_path,
            ref_offre,
            statut,
            score,
            langues,
            created_at,
            date_candidature
        ) VALUES (
            :nom,
            :prenom,
            :email,
            :phone,
            :adresse,
            :ville,
            :date_naissance,
            :poste,
            :disponibilite,
            :salaire,
            :type_contrat,
            :mobilite,
            :autorisation,
            :cv_path,
            :lettre_path,
            :diplomes_path,
            :ref_offre,
            :statut,
            :score,
            :langues,
            NOW(),
            :date_candidature
        ) RETURNING id
    """)

    result = db.execute(query, {
        "nom": candidature.nom,
        "prenom": candidature.prenom,
        "email": candidature.email,
        "phone": candidature.phone,
        "adresse": candidature.adresse,
        "ville": getattr(candidature, "ville", None),
        "date_naissance": getattr(candidature, "date_naissance", None),
        "poste": candidature.poste,
        "disponibilite": getattr(candidature, "disponibilite", None),
        "salaire": getattr(candidature, "salaire", None),
        "type_contrat": getattr(candidature, "type_contrat", None),
        "mobilite": getattr(candidature, "mobilite", None),
        "autorisation": getattr(candidature, "autorisation", None),
        "cv_path": getattr(candidature, "cv_path", None),
        "lettre_path": getattr(candidature, "lettre_path", None),
        "diplomes_path": getattr(candidature, "diplomes_path", None),
        "ref_offre": candidature.ref_offre,
        "statut": candidature.statut or "En attente",
        "score": candidature.score or 0.0,
        "langues": json.dumps(getattr(candidature, "langues", {})) if getattr(candidature, "langues", None) else None,
        "date_candidature": candidature.date_candidature or datetime.now()
    })

    db.commit()
    return result.fetchone()[0]
