from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services.ProblemeConnexion import handle_probleme_connexion
"""from app.services.salutation import handle_salutation
from app.services.reclamation import handle_reclamation"""

app = FastAPI()

# Dictionnaire dynamique des intentions → fonctions de traitement
intent_handlers = {
    "ProblemeConnexion": handle_probleme_connexion,
    #"Salutation": handle_salutation,
    #"Reclamation": handle_reclamation,
}

'''@app.post("/webhook")
async def webhook(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    intent = data.get("queryResult", {}).get("intent", {}).get("displayName")

    print(f"[INFO] Intent reçu : {intent}")  # Log utile en debug

    handler = intent_handlers.get(intent)

    if handler:
        return await handler(data, db)
    else:
        return {"fulfillmentText": "Je n’ai pas compris votre demande."}'''
@app.get("/webhook_test")
async def webhook_test():
    return { "fulfillmentText": "Ceci est un test de webhook." }
@app.post("/webhook")
async def dialogflow_webhook(request: Request):
    body = await request.json()  # Récupère le JSON envoyé par Dialogflow

    intent = body.get("queryResult", {}).get("intent", {}).get("displayName", "")
    
    if intent == "salutation":
        return JSONResponse(content={"fulfillmentText": "ti winek ya remz"})
    elif intent == "au_revoir":
        return JSONResponse(content={"fulfillmentText": "Au revoir !"})
    else:
        return JSONResponse(content={"fulfillmentText": "Je n'ai pas compris votre demande."})