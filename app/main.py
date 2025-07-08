from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.auth.jwt_handler import create_jwt_token, decode_jwt_token
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from app.core.config import DIALOGFLOW_PROJECT_ID
from app.database.session import get_db
from app.services.NumTel import handle_fournir_num_tel
from app.services.ProblemeConnexion import handle_probleme_connexion
from app.services.NumLigne import handle_verifier_ligne
from app.services.FinDiscussion import handle_fin_discussion
from google.cloud import dialogflow_v2 as dialogflow
from app.core.session_memory import clear_session
from app.services.MarqueModem import handle_demander_marque_modem
# app/main.py
app = FastAPI()
security = HTTPBearer()

def verify_jwt_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Vérifie le token JWT fourni dans l'en-tête Authorization.
    Si le token est valide, il retourne les données décodées.
    """
    try:
        token = credentials.credentials
        payload = decode_jwt_token(token)
        return payload
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

# Endpoint pour générer un token JWT
@app.get("/generate_token") 
async def generate_token():
    """
    Génère un token JWT pour l'utilisateur.
    """ 
    try:
        token = create_jwt_token()
        return {"token": token}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# Modèle de données pour la requête
class Query(BaseModel):
    text: str

# Fonction Dialogflow pour détecter intent + fulfillment
def detect_intent(project_id, session_id, text, language_code="fr"):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    response = session_client.detect_intent(session=session, query_input=query_input)
    print(f"Dialogflow response: {response.query_result}")
    return response.query_result

# Mapping intent => handler (les handlers doivent renvoyer dict avec fulfillmentText)
intent_handlers = {
    "ProblemeConnexion": handle_probleme_connexion,
    "FournirNumLigne": handle_verifier_ligne,
    "FournirNumTel": handle_fournir_num_tel,
    "FinDiscussion": handle_fin_discussion,
    "FournirMarqueModem": handle_demander_marque_modem,
}

@app.post("/chat")
async def chat(query: Query, 
               db: Session = Depends(get_db), 
               payload: dict = Depends(verify_jwt_token)
               ):
    try:
        session_id = payload.get("jti")  # ID sécurisé du JWT
        result = detect_intent(DIALOGFLOW_PROJECT_ID, session_id, query.text)
        intent_name = result.intent.display_name

        print(f"Texte reçu : {query.text}")
        print(f"Session : {session_id}")
        print(f"Intent détecté : {intent_name}")
        print(f"Paramètres détectés : {result.parameters}")

        handler = intent_handlers.get(intent_name)
        if handler:
            data = {
                "queryResult": {
                    "parameters": result.parameters,
                    "intent": {
                        "displayName": intent_name
                    },
                    "queryText": query.text
                },
                "session": session_id
            }
            response = await handler(data, db)

            # Nettoyage mémoire si fin de discussion
            if response.get("endConversation") is True:
                clear_session(session_id)

            return {
                "fulfillmentText": response.get("fulfillmentText", "Pas de réponse."),
                "options": response.get("options", []),
                "endConversation": response.get("endConversation", False)
            }

        else:
            return {"fulfillmentText": result.fulfillment_text}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))