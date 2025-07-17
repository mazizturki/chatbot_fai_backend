from fastapi import APIRouter, Query
from app.core.session_memory import get_param

router = APIRouter()

@router.get("/session_param")
async def session_param(session_id: str = Query(...), key: str = Query(...)):
    value = get_param(session_id, key)
    if value is None:
        return {"error": f"Paramètre '{key}' non trouvé pour la session {session_id}"}
    return {"value": value}
