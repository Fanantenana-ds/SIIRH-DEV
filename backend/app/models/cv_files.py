from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.db import Base

class CVFile(Base):
    __tablename__ = "cv_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    path = Column(String, nullable=False)
    mimetype = Column(String, nullable=False)
    size = Column(Integer)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
