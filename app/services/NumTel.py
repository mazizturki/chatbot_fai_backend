from sqlalchemy.orm import Session
from app.core.session_memory import get_param, get_progression, store_param, update_progression
from app.services.MarqueModem import handle_demander_marque_modem
from app.utils.extract import extract_session_id

async def handle_fournir_num_tel(data: dict, db: Session) -> dict:
    print("handle_fournir_num_tel called with data:", data)
    session_id = extract_session_id(data)
    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()

    # Utiliser le paramètre numtel ou le texte brut
    numtel = parameters.get("numtel") or query_text
    progression = get_progression(session_id)

    print(f"Numéro détecté : {numtel}")

        # Si l'étape est déjà validée, ne pas recommencer
    if progression.get("num_tel_ok"):
        ancien_num = get_param(session_id, "numtel")
        return {
            "fulfillmentText": f"Le numéro de téléphone {ancien_num} est déjà enregistré. Poursuivons avec la suite du diagnostic.",
            "endConversation": False
        }

    # Validation simple du numéro (peut être améliorée selon vos besoins)
    if numtel and numtel.isdigit() and len(numtel) >= 8:
        store_param(session_id, "numtel", numtel)
        update_progression(session_id, "num_tel_ok", True)
        # Passer à la question sur la marque du modem
        return await handle_demander_marque_modem(data, db)
    else:
        return {
            "fulfillmentText": "Veuillez fournir un numéro de téléphone valide (au moins 8 chiffres).",
            "options": [],
            "endConversation": False
        }