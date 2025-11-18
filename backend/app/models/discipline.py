from sqlalchemy import Column, Integer, String, Date, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db import Base
from datetime import date

class Discipline(Base):
    __tablename__ = "discipline"
    __table_args__ = {"extend_existing": True}

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey("employees.id"), nullable=False)

    fault_category = Column(String(50), nullable=False)
    fault_nature = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    proof_files = Column(Text, nullable=True)  # chemin fichiers concaténés ou JSON list

    convocation_model = Column(String(50), nullable=True)
    convocation_date = Column(Date, nullable=True)
    convocation_time = Column(String(20), nullable=True)
    convocation_place = Column(String(255), nullable=True)
    convocation_manager = Column(String(255), nullable=True)

    date_created = Column(Date, default=date.today)

    employee = relationship("Employee", back_populates="discipline_entries")

