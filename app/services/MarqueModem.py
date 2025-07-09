from sqlalchemy.orm import Session
from app.core.session_memory import store_param, get_param
from app.services.Diagnostique import diagnostic_probleme

async def handle_demander_marque_modem(data: dict, db: Session) -> dict:
    print("handle_demander_marque_modem called with data:", data)
    session_id = data.get("session")
    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()
    
    # Récupérer la marque modem
    marque = parameters.get("marque_modem") or query_text
    print(f"Marque détectée : {marque}")

    valid_marques = ["huawei", "tplink", "nokia", "zte", "cisco", "motorola"]

    if marque and marque.lower() in valid_marques:
        # Stocker la marque
        store_param(session_id, "marque_modem", marque)

        # Vérifier si on a toutes les infos pour faire un diagnostic
        type_probleme = get_param(session_id, "TypeProbleme")
        numligne = get_param(session_id, "numligne")
        numtel = get_param(session_id, "numtel")

        if type_probleme and numligne and numtel:
            # Tous les paramètres sont présents, lancer le diagnostic
            return await diagnostic_probleme(session_id, db)
        else:
            # Sinon, demander à l'utilisateur d'autres infos nécessaires
            return {
                "fulfillmentText": f"Merci d'avoir indiqué que votre modem est un {marque}. Veuillez fournir les informations manquantes.",
                "options": [],
                "endConversation": False
            }
    else:
        # Si la marque n'est pas reconnue, redemander
        marques = ["Huawei", "TPLink", "Nokia", "ZTE", "Cisco", "Motorola"]
        return {
            "fulfillmentText": "Quel est la marque de votre modem ?",
            "options": marques,
            "endConversation": False
        }
