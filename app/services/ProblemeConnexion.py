from sqlalchemy.orm import Session
from app.crud.ligne import verifier_statut_ligne
from app.core.session_memory import get_param, store_param

async def handle_probleme_connexion(data: dict, db: Session):
    params = data.get("queryResult", {}).get("parameters", {})
    session = data.get("session")
    session_id = session.split("/")[-1]  # Extraire ID pur de session

    print(f"[DEBUG handle_probleme_connexion] params = {params}")

    # Utiliser les valeurs fournies ou celles stockées en mémoire
    type_connexion = params.get("TypeConnexion") or get_param(session_id, "TypeConnexion")
    type_probleme = params.get("TypeProbleme") or get_param(session_id, "TypeProbleme")
    date_probleme = params.get("date") or get_param(session_id, "date")
    numligne = get_param(session_id, "numligne")
    
    # Stocker ce qui est présent maintenant
    if type_connexion:
        store_param(session_id, "TypeConnexion", type_connexion)
    if type_probleme:
        store_param(session_id, "TypeProbleme", type_probleme)
    if date_probleme:
        store_param(session_id, "date", date_probleme)
        
    # Vérification que type_probleme est obligatoire
    if not type_probleme:
        return {
            "fulfillmentText": "Merci de préciser le type de problème que vous rencontrez."
        }

    # Construire la réponse
    response_text = f"Pour résoudre votre problème de {type_probleme}"

    if type_connexion:
        response_text += f" sur votre {type_connexion}"

    if date_probleme:
        response_text += f", survenu le {date_probleme}"

    response_text += ", merci de nous fournir votre numéro de ligne lié à votre abonnement."

    return {
        "fulfillmentText": response_text
    }
