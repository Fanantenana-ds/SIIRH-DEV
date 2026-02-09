from pydantic import BaseModel
from datetime import date, time

class TimeEntryCreate(BaseModel):
    employee_id: int
    date: date
    check_in: time
    check_out: time

class TimeEntryOut(TimeEntryCreate):
    id: int

    class Config:
        from_attributes = True
