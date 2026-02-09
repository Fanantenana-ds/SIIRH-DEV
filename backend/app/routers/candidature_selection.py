import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.models.models import Candidature

# Créer un logger
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rh/candidatures", tags=["Candidature Selection"])

@router.put("/{candidature_id}/selection")
def update_selection(candidature_id: int, selected: bool, db: Session = Depends(get_db)):
    """Endpoint pour sélectionner/désélectionner une candidature"""
    
    logger.info(f"🔄 PUT /rh/candidatures/{candidature_id}/selection?selected={selected}")
    
    # 1. Rechercher la candidature
    candidature = db.query(Candidature).filter(Candidature.id == candidature_id).first()
    
    if not candidature:
        logger.error(f"❌ Candidature {candidature_id} non trouvée")
        raise HTTPException(status_code=404, detail="Candidat introuvable")
    
    logger.info(f"📊 Avant: ID={candidature.id}, Nom={candidature.fullname}, "
                f"is_selected={candidature.is_selected}, statut={candidature.statut}")
    
    # 2. Mettre à jour
    try:
        candidature.is_selected = selected
        
        # Mettre à jour le statut aussi
        if selected:
            candidature.statut = "Sélectionné"
        else:
            candidature.statut = "Nouveau"
        
        db.commit()
        db.refresh(candidature)
        
        logger.info(f"✅ Après: is_selected={candidature.is_selected}, statut={candidature.statut}")
        
        return {
            "success": True,
            "id": candidature.id,
            "fullname": candidature.fullname,
            "is_selected": candidature.is_selected,
            "statut": candidature.statut,
            "message": f"Candidature {'sélectionnée' if selected else 'désélectionnée'}"
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur mise à jour: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erreur base: {str(e)}")

# Ajouter un endpoint pour vérifier
@router.get("/test")
def test_endpoint():
    return {"message": "✅ Candidature selection router actif!"}