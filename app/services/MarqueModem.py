from sqlalchemy.orm import Session
from app.core.session_memory import store_param, get_param, get_progression, update_progression
from app.services.Diagnostique import diagnostic_probleme
from app.utils.extract import extract_session_id

async def handle_demander_marque_modem(data: dict, db: Session) -> dict:
    print("handle_demander_marque_modem called with data:", data)
    
    session_id = extract_session_id(data)
    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()
    
    # Vérifier si la progression est déjà faite
    progression = get_progression(session_id)
    if progression.get("marque_ok"):
        return {
            "fulfillmentText": "Merci, nous avons déjà enregistré la marque de votre modem. Poursuivons avec la suite du diagnostic.",
            "endConversation": False
        }

    # Récupération marque
    marque = parameters.get("marque_modem") or query_text
    print(f"[DEBUG] Marque détectée : {marque}")

    valid_marques = ["huawei", "tplink", "nokia", "zte", "cisco", "sagemcom", "netgear", "asus", "dlink"]

    if marque and marque.lower() in valid_marques:
        store_param(session_id, "marque_modem", marque.capitalize())
        update_progression(session_id, "marque_ok", True)

        # Vérifier si tous les autres paramètres sont prêts
        type_probleme = get_param(session_id, "TypeProbleme")
        numligne = get_param(session_id, "numligne")
        numtel = get_param(session_id, "numtel")

        print(f"[DEBUG] Diagnostic check - type_probleme: {type_probleme}, numligne: {numligne}, numtel: {numtel}")


        if type_probleme and numligne and numtel:
            return await diagnostic_probleme(session_id, db)
        else:
            return {
                "fulfillmentText": f"Merci, la marque {marque} a bien été enregistrée. Veuillez maintenant fournir les informations manquantes.",
                "endConversation": False
            }
    else:
        # Demander à nouveau la marque si elle n'est pas valide
        marques = ["Huawei", "TPLink", "Nokia", "ZTE", "Cisco", "Sagemcom", "Netgear", "Asus", "D-Link"]
        return {
            "fulfillmentText": "Pouvez-vous préciser la marque de votre modem ?",
            "options": marques,
            "endConversation": False
        }