# app/services/NumTel.py
from sqlalchemy.orm import Session
from app.core.session_memory import store_param
from app.services.MarqueModem import handle_demander_marque_modem

async def handle_fournir_num_tel(data: dict, db: Session) -> dict:
    print("handle_fournir_num_tel called with data:", data)
    session_id = data.get("session")
    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()

    # Utiliser le paramètre phone-number ou le texte brut
    phone_number = parameters.get("phone-number") or query_text
    print(f"Numéro détecté : {phone_number}")

    # Validation simple du numéro (peut être améliorée selon vos besoins)
    if phone_number and phone_number.isdigit() and len(phone_number) >= 8:
        store_param(session_id, "phone_number", phone_number)
        # Passer à la question sur la marque du modem
        return await handle_demander_marque_modem(data, db)
    else:
        return {
            "fulfillmentText": "Veuillez fournir un numéro de téléphone valide (au moins 8 chiffres).",
            "options": [],
            "endConversation": False
        }