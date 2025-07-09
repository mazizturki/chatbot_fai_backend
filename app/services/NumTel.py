from sqlalchemy.orm import Session
from app.core.session_memory import store_param
from app.services.MarqueModem import handle_demander_marque_modem

async def handle_fournir_num_tel(data: dict, db: Session) -> dict:
    print("handle_fournir_num_tel called with data:", data)
    session_id = data.get("session")
    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()

    # Utiliser le paramètre numtel ou le texte brut
    numtel = parameters.get("numtel") or query_text
    print(f"Numéro détecté : {numtel}")

    # Validation simple du numéro (peut être améliorée selon vos besoins)
    if numtel and numtel.isdigit() and len(numtel) >= 8:
        store_param(session_id, "numtel", numtel)
        # Passer à la question sur la marque du modem
        return await handle_demander_marque_modem(data, db)
    else:
        return {
            "fulfillmentText": "Veuillez fournir un numéro de téléphone valide (au moins 8 chiffres).",
            "options": [],
            "endConversation": False
        }