import httpx
from sqlalchemy.orm import Session
from app.core.session_memory import get_param, get_progression, update_progression
from app.services.speedtest_service import run_speedtest
from app.services.EtatModem import handle_demander_etat_modem 
from app.crud.reclamation import creer_reclamation
from app.utils.extract import extract_param

API_SPEEDTEST_URL = "http://localhost:8000/verifier_speedtest"  # ou l’URL de ton backend FastAPI

async def diagnostic_probleme(session_id: str, db: Session) -> dict:
    progression = get_progression(session_id)
    if progression.get("diagnostic_ok"):
        return {
            "fulfillmentText": "✅ Le diagnostic a déjà été effectué. Souhaitez-vous faire une autre demande ?",
            "endConversation": False
        }

    type_probleme = get_param(session_id, "TypeProbleme")
    numligne = get_param(session_id, "numligne")
    numtel = get_param(session_id, "numtel")
    marque_modem = get_param(session_id, "marque_modem")

    if not all([type_probleme, numligne, numtel, marque_modem]):
        return {
            "fulfillmentText": "Des informations sont manquantes pour procéder au diagnostic."
        }

    if type_probleme == "lenteur":
        return {
            "fulfillmentText": (
                f"Pour diagnostiquer la lenteur, veuillez lancer un test de vitesse sur votre appareil. "   
            ),
            "endConversation": False
        }

    # Cas coupure → voyants modem
    elif type_probleme == "coupure" or type_probleme == "instabilité":
        data = {
            "session": session_id,
            "queryResult": {
                "parameters": {}
            }
        }
        return await handle_demander_etat_modem(data, db)

    # Autre cas → réclamation directe
    else:
        update_progression(session_id, "diagnostic_ok", True)
        reclamation = creer_reclamation(
            db=db,
            numligne=numligne,
            numtel=numtel,
            probleme=type_probleme,
            marque_modem=get_param(session_id, "marque_modem")
        )
        return {
            "fulfillmentText": (
                f"✅ Une réclamation pour le problème {type_probleme} a été enregistrée sous le numéro {reclamation.id_reclamation}.\n\n"
                "Nous restons à votre disposition pour toute autre demande.\nExcellente journée à vous."
            ),
            "endConversation": True
        }