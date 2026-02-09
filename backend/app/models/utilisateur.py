from sqlalchemy import Column, Integer, String, Boolean
from app.db import Base

class Utilisateur(Base):
    __tablename__ = "utilisateurs"
    __table_args__ = {"extend_existing": True}  

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    role = Column(String(50), default="user")
    actif = Column(Boolean, default=True) 
