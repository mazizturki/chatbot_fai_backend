from sqlalchemy.orm import Session
from app.core.session_memory import store_param, get_param

async def handle_demander_marque_modem(data: dict, db: Session) -> dict:
    print("handle_demander_marque_modem called with data:", data)
    session_id = data.get("session")
    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()
    
    # Utiliser le paramètre marque_modem ou le texte brut
    marque = parameters.get("marque_modem") or query_text
    print(f"Marque détectée : {marque}")

    valid_marques = ["huawei", "tplink", "nokia", "zte", "cisco", "motorola"]
    if marque and marque.lower() in valid_marques:
        store_param(session_id, "marque_modem", marque)
        return {
            "fulfillmentText": f"Merci d'avoir indiqué que votre modem est un {marque}. Merci de me fournir l’état des voyants de votre modem pour bien diagnostiquer le problème.",
            "options": [],
            "endConversation": False
        }
    else:
        marques = ["Huawei", "TPLink", "Nokia", "ZTE", "Cisco", "Motorola"]
        return {
            "fulfillmentText": "Quel est la marque de votre modem ?",
            "options": marques,
            "endConversation": False
        }