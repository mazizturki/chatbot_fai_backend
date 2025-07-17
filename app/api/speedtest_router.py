from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.database.session import get_db

router = APIRouter()

class SpeedtestResult(BaseModel):
    num_ligne: str
    download: float
    upload: float
    ping: float

def get_debit_attendu(db: Session, num_ligne: str) -> float:
    result = db.execute(
        "SELECT debit_attendu FROM lignetelephonique WHERE num_ligne = :numligne",
        {"numligne": num_ligne}
    ).fetchone()
    return float(result[0]) if result else 10.0
