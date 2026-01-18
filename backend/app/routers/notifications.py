from fastapi import APIRouter, HTTPException
from app.db import engine
import sqlalchemy
from datetime import datetime
import traceback

router = APIRouter()

# ==========================================================
# 🔹 GET notifications
# ==========================================================
@router.get("/notifications")
async def get_notifications():
    """
    Retourne toutes les notifications triées par date décroissante.
    Convert 'read' en boolean pour que le frontend puisse gérer le badge.
    """
    try:
        query = sqlalchemy.text("SELECT id, message, read, date FROM notifications ORDER BY date DESC")
        with engine.begin() as conn:
            result = conn.execute(query)
            notifications = []
            for row in result:
                r = dict(row._mapping)
                # Formatage de la date en ISO
                if r.get("date"):
                    r["date"] = r["date"].isoformat()
                # Assurer que read dia boolean
                r["read"] = bool(r.get("read"))
                notifications.append(r)
        return notifications
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# ==========================================================
# 🔹 PUT read/unread notification
# ==========================================================
@router.put("/notifications/{id}/read")
async def mark_notification_as_read(id: int):
    """
    Marque une notification comme lue.
    """
    try:
        query = sqlalchemy.text("UPDATE notifications SET read=true WHERE id=:id")
        with engine.begin() as conn:
            res = conn.execute(query, {"id": id})
            if res.rowcount == 0:
                raise HTTPException(status_code=404, detail="Notification non trouvée")
        return {"message": "Notification marquée comme lue"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")

# ==========================================================
# 🔹 POST nouvelle notification
# ==========================================================
@router.post("/notifications")
async def create_notification(message: str):
    """
    Crée une nouvelle notification.
    """
    try:
        now = datetime.now()
        query = sqlalchemy.text(
            "INSERT INTO notifications (message, read, date) VALUES (:message, false, :date)"
        )
        with engine.begin() as conn:
            conn.execute(query, {"message": message, "date": now})
        return {"message": "Notification créée avec succès"}
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Erreur interne : {e}")
