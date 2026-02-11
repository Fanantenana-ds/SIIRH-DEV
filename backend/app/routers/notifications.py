from fastapi import APIRouter, HTTPException
from app.db import engine
import sqlalchemy
from datetime import datetime
import traceback
from sqlalchemy.orm import Session 

router = APIRouter(tags=["Notifications"])


# ==========================================================
# 🔹 GET notifications
# ==========================================================
@router.get("/notifications")
async def get_notifications():
    try:
        query = sqlalchemy.text(
            "SELECT id, message, read, date FROM notifications ORDER BY date DESC"
        )
        with engine.begin() as conn:
            result = conn.execute(query)
            notifications = []
            for row in result:
                r = dict(row._mapping)
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


# ==========================================================
# 🔹 FONCTION UTILE: Ajouter notification automatique
# ==========================================================
def add_mail_notification(db: Session, message: str):
    try:
        now = datetime.now()
        query = sqlalchemy.text(
            "INSERT INTO notifications (message, read, date) VALUES (:message, false, :date)"
        )
        db.execute(query, {"message": message, "date": now})
        db.commit()
    except Exception:
        print("Erreur lors de la création de notification mail:")
        print(traceback.format_exc())
