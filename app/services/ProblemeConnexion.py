from sqlalchemy.orm import Session
from app.crud.ligne import verifier_statut_ligne
from app.core.session_memory import get_param, get_progression, store_param, update_progression
from app.utils.extract import extract_param
from typing import Dict

async def handle_probleme_connexion(data: dict, db: Session) -> Dict:
    params = data.get("queryResult", {}).get("parameters", {})
    session = data.get("session")
    session_id = session.split("/")[-1]

    print(f"[DEBUG handle_probleme_connexion] session={session_id}, params={params}")

    # Extraction normalisée
    type_connexion = extract_param(params, "TypeConnexion", session_id)
    type_probleme = extract_param(params, "TypeProbleme", session_id)
    date_probleme = extract_param(params, "date", session_id)

    progression = get_progression(session_id)


    print(f"[SESSION: {session_id}] TypeConnexion={type_connexion}, TypeProbleme={type_probleme}, Date={date_probleme}")

    # Stockage
    if type_connexion:
        store_param(session_id, "TypeConnexion", type_connexion)
    if type_probleme:
        store_param(session_id, "TypeProbleme", type_probleme)
    if date_probleme:
        store_param(session_id, "date", date_probleme)

    if progression.get("probleme_ok") and type_probleme:
        ancien_probleme = get_param(session_id, "TypeProbleme")
        if ancien_probleme != type_probleme:
            # L’utilisateur essaie de changer le problème
            store_param(session_id, "TypeProbleme", type_probleme)
            return {
                "fulfillmentText": f"Vous avez modifié le problème en {type_probleme}. D'accord, nous allons continuer avec ce nouveau souci. "
                                   f"Merci maintenant de fournir votre numéro de ligne.",
                "endConversation": False
            }


    if not type_probleme and not progression.get("probleme_ok"):
        return {
            "fulfillmentText": (
                "Quel est le type de problème que vous rencontrez ? (par exemple : lenteur, coupure, instabilité)"
            ),
            "options": ["Lenteur", "Coupure", "Instabilité"],
            "endConversation": False
    }


    update_progression(session_id, "probleme_ok", True)

    # Construction message
    response_text = f"Suite à un problème de {type_probleme}"
    if type_connexion:
        response_text += f" sur votre {type_connexion}"
    if date_probleme:
        response_text += f", survenu le {date_probleme} \n"
    response_text += ".\n\nMerci de nous fournir votre numéro de ligne associé à cet abonnement afin de poursuivre le diagnostic."

    return {
        "fulfillmentText": response_text,
        "endConversation": False
    }