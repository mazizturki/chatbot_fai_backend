from sqlalchemy.orm import Session
from app.core.session_memory import get_param
from app.crud.reclamation import creer_reclamation
from app.utils.extract import extract_session_id

async def handle_confirmation_redemarrage(data: dict, db: Session) -> dict:
    session_id = extract_session_id(data)
    print(f"[DEBUG handle_confirmation_redemarrage] session={session_id}, data={data}")
    parameters = data["queryResult"].get("parameters", {})

    confirmation = parameters.get("reponseYN", "").lower()

    if confirmation in ["oui", "yes", "ok", "d'accord"]:
        return {
            "fulfillmentText": "Merci de nous avoir informés que le problème est résolu. N'hésitez pas à revenir si vous avez d'autres questions.",
            "endConversation": True
        }

    elif confirmation in ["non", "toujours", "pas résolu"]:
        reclamation = creer_reclamation(
            db=db,
            numligne=get_param(session_id, "numligne"),
            numtel=get_param(session_id, "numtel"),
            probleme=get_param(session_id, "TypeProbleme"),
            marque_modem=get_param(session_id, "marque_modem")
        )
        return {
            "fulfillmentText": (
                f"D'accord, une réclamation a été enregistrée sous le numéro {reclamation.id_reclamation}. Un expert vous contactera dans les plus brefs délais.\n \n"
                "Nous restons à votre disposition pour toute autre demande. \n" "Excellente journée à vous."
            ),
            "endConversation": True
        }

    return {
        "fulfillmentText": "Je n’ai pas compris votre réponse. Le problème est-il résolu ?",
        "options": ["Oui", "Non"],
        "endConversation": False
    }