from sqlalchemy.orm import Session
from app.core.session_memory import get_param
from app.crud.reclamation import creer_reclamation

async def handle_confirmation_redemarrage(data: dict, db: Session) -> dict:
    session_id = data.get("session")
    parameters = data["queryResult"].get("parameters", {})

    confirmation = parameters.get("confirmation", "").lower()

    if confirmation in ["oui", "yes", "ok", "d'accord"]:
        return {
            "fulfillmentText": "Merci de nous avoir informés que le problème est résolu. N'hésitez pas à revenir si vous avez d'autres questions.",
            "endConversation": True
        }

    elif confirmation in ["non", "toujours", "pas résolu"]:
        await creer_reclamation(
            db=db,
            numligne=get_param(session_id, "numligne"),
            numtel=get_param(session_id, "numtel"),
            probleme="coupure persistante après redémarrage modem"
        )
        return {
            "fulfillmentText": "D'accord, une réclamation a été enregistrée. Un technicien vous contactera dans les plus brefs délais.",
            "endConversation": True
        }

    # Si la réponse est ambiguë
    return {
        "fulfillmentText": "Je n’ai pas compris votre réponse. Le problème est-il résolu après le redémarrage du modem ?",
        "options": ["Oui", "Non"],
        "endConversation": False
    }
