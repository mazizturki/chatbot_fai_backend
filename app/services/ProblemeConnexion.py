from sqlalchemy.orm import Session
from app.crud.ligne import verifier_statut_ligne
from app.core.session_memory import get_param, store_param
from app.utils.extract import extract_param

async def handle_probleme_connexion(data: dict, db: Session):
    params = data.get("queryResult", {}).get("parameters", {})
    session = data.get("session")
    session_id = session.split("/")[-1]

    print(f"[DEBUG handle_probleme_connexion] params = {params}")

    # Extraction normalisée avec conversion
    type_connexion = extract_param(params, "TypeConnexion", session_id)
    type_probleme = extract_param(params, "TypeProbleme", session_id)
    date_probleme = extract_param(params, "date", session_id)

    # Sauvegarde en mémoire
    if type_connexion:
        store_param(session_id, "TypeConnexion", type_connexion)
    if type_probleme:
        store_param(session_id, "TypeProbleme", type_probleme)
    if date_probleme:
        store_param(session_id, "date", date_probleme)

    # Vérification minimale
    if not type_probleme:
        return {
            "fulfillmentText": "Merci de préciser le type de problème que vous rencontrez."
        }

    # Construction réponse
    response_text = f"Pour résoudre votre problème de {type_probleme}"
    if type_connexion:
        response_text += f" sur votre {type_connexion}"
    if date_probleme:
        response_text += f", survenu le {date_probleme}"
    response_text += ", merci de nous fournir votre numéro de ligne lié à votre abonnement."

    return {
        "fulfillmentText": response_text
    }
