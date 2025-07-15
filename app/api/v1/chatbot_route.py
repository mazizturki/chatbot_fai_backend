from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session
from app.services.dialogflow_sdk import detect_intent_with_params
from app.services.ProblemeConnexion import handle_probleme_connexion
from app.database import get_db

router = APIRouter()

@router.post("/chatbot")
def chatbot_endpoint(
    user_id: str = Body(...),
    message: str = Body(...),
    db: Session = Depends(get_db)
):
    intent, fulfillment, params = detect_intent_with_params(user_id, message)

    # Appelle le handler personnalisé
    if intent in ["ProblemeConnexion", "FournirNumLigne"]:
        return {"reply": handle_probleme_connexion(user_id, intent, params, db)}

    # Par défaut, retourne la réponse Dialogflow
    return {"reply": fulfillment}
