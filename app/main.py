from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import httpx

from app.auth.jwt_handler import create_jwt_token, decode_jwt_token
from app.core.config import DIALOGFLOW_PROJECT_ID
from app.database.session import get_db
from app.services.NumTel import handle_fournir_num_tel
from app.services.ProblemeConnexion import handle_probleme_connexion
from app.services.NumLigne import handle_verifier_ligne
from app.services.FinDiscussion import handle_fin_discussion
from app.services.MarqueModem import handle_demander_marque_modem
from app.services.EtatModem import handle_demander_etat_modem
from app.services.ServiceCommercial import handle_service_commercial
from app.services.confirmation_redemarrage import handle_confirmation_redemarrage
from app.core.session_memory import clear_session
from google.cloud import dialogflow_v2 as dialogflow
from app.core.config import FLASK_MAINTENANCE_URL, FLASK_API_KEY

app = FastAPI()
security = HTTPBearer()

# ✅ Vérification du token JWT
def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        return decode_jwt_token(token)
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

@app.get("/generate_token")
async def generate_token():
    try:
        token = create_jwt_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ Classe requête
class Query(BaseModel):
    text: str

# ✅ Fonction Dialogflow
def detect_intent(project_id, session_id, text, language_code="fr"):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    return response.query_result

# ✅ Mapping intents
intent_handlers = {
    "ProblemeConnexion": handle_probleme_connexion,
    "FournirNumLigne": handle_verifier_ligne,
    "FournirNumTel": handle_fournir_num_tel,
    "FinDiscussion": handle_fin_discussion,
    "FournirMarqueModem": handle_demander_marque_modem,
    "EtatVoyantModem": handle_demander_etat_modem,
    "ConfirmationRedemarrage": handle_confirmation_redemarrage,
    "ServiceCommercial": handle_service_commercial,
}

# ✅ Récupérer état maintenance depuis Flask
async def get_maintenance_status():
    async with httpx.AsyncClient() as client:
        try:
            r = await client.get(FLASK_MAINTENANCE_URL, timeout=5.0)
            if r.status_code == 200:
                return r.json()
            else:
                # Si Flask renvoie autre chose (ex: erreur serveur)
                return {"isActive": False, "message": "Erreur API Maintenance"}
        except httpx.RequestError:
            # Si l'API Flask est down
            return {"isActive": False, "message": "Impossible de joindre l'API Maintenance"}

@app.get("/api/maintenance")
async def get_maintenance():
    return await get_maintenance_status()

@app.post("/api/maintenance")
async def update_maintenance(isActive: bool, message: str):
    async with httpx.AsyncClient() as client:
        r = await client.post(
            FLASK_MAINTENANCE_URL,
            json={"isActive": isActive, "message": message},
            headers={"X-API-Key": FLASK_API_KEY}
        )
        return r.json()

# ✅ Middleware → Bloque /chat si maintenance active
@app.middleware("http")
async def maintenance_middleware(request: Request, call_next):
    if request.url.path.startswith("/chat"):
        status = await get_maintenance_status()
        if status.get("isActive", False):
            return JSONResponse(
                status_code=503,
                content={"message": status.get("message", "Maintenance en cours..."),
                         "maintenance": True}
            )
    return await call_next(request)

# ✅ Endpoint chatbot
@app.post("/chat")
async def chat(query: Query, db: Session = Depends(get_db), payload: dict = Depends(verify_jwt_token)):
    try:
        session_id = payload.get("jti")
        result = detect_intent(DIALOGFLOW_PROJECT_ID, session_id, query.text)
        intent_name = result.intent.display_name
        params_dict = dict(result.parameters)

        handler = intent_handlers.get(intent_name)
        if handler:
            data = {
                "queryResult": {
                    "parameters": params_dict,
                    "intent": {"displayName": intent_name},
                    "queryText": query.text
                },
                "session": session_id
            }
            response = await handler(data, db)
            reply = {
                "fulfillmentText": response.get("fulfillmentText", "Pas de réponse."),
                "options": response.get("options", []),
                "endConversation": response.get("endConversation", False)
            }
            if reply["endConversation"]:
                clear_session(session_id)
            return reply
        else:
            return {"fulfillmentText": result.fulfillment_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
