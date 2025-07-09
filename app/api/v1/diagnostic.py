from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import diagnostic

router = APIRouter()

@router.post("/diagnostic")
async def post_diagnostic(data: dict, db: Session = Depends(get_db)):
    session = data.get("session")
    if not session:
        return {"fulfillmentText": "Session invalide."}

    session_id = session.split("/")[-1]

    result = await diagnostic.diagnostic_probleme(session_id=session_id, db=db)
    return result
