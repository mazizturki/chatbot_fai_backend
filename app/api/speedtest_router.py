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

@router.post("/verifier_speedtest")
async def verifier_speedtest(data: SpeedtestResult, db: Session = Depends(get_db)):
    debit_attendu = get_debit_attendu(db, data.num_ligne)
    ecart = abs(data.download - debit_attendu)
    connexion_normale = ecart < 3

    return {
        "connexion_normale": connexion_normale,
        "debit_attendu": debit_attendu,
        "download": data.download,
        "upload": data.upload,
        "ping": data.ping,
    }
