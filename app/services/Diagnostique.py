from sqlalchemy.orm import Session
from app.core.session_memory import get_param
from app.services.speedtest_service import run_speedtest
from app.services.EtatModem import handle_demander_etat_modem 
from app.crud.reclamation import creer_reclamation

async def diagnostic_probleme(session_id: str, db: Session) -> dict:
    type_probleme = get_param(session_id, "TypeProbleme")
    numligne = get_param(session_id, "numligne")
    numtel = get_param(session_id, "numtel")
    marque_modem = get_param(session_id, "marque_modem")

    if not all([type_probleme, numligne, numtel, marque_modem]):
        return {
            "fulfillmentText": "Des informations sont manquantes pour procéder au diagnostic."
        }

    if type_probleme == "lenteur":
        speed_data = await run_speedtest(numligne)
        if speed_data is None:
            return {"fulfillmentText": "Impossible d'effectuer le test de vitesse pour le moment."}

        download_mbps = speed_data.get("download")
        debit_attendu = speed_data.get("debit_attendu")

        if download_mbps is None or debit_attendu is None:
            return {"fulfillmentText": "Le test de vitesse a échoué. Données incomplètes."}

        difference = debit_attendu - download_mbps

        if difference < 3:
            return {
                "fulfillmentText": (
                    f"Le test indique un débit de {download_mbps:.2f} Mbps, "
                    f"ce qui est proche du débit attendu ({debit_attendu:.2f} Mbps). "
                    "Votre ligne fonctionne normalement."
                )
            }
        else:
            creer_reclamation(db=db, numligne=numligne, numtel=numtel, probleme=type_probleme)
            return {
                "fulfillmentText": (
                    f"Votre débit est de {download_mbps:.2f} Mbps, "
                    f"soit bien en dessous du débit attendu ({debit_attendu:.2f} Mbps). "
                    "Une réclamation a été enregistrée."
                )
            }

    elif type_probleme == "coupure":
        # Construire un data minimal à passer au handler
        data = {
            "session": session_id,
            "queryResult": {
                "parameters": {}
            }
        }
        await handle_demander_etat_modem(data, db)
        return {
            "fulfillmentText": "Merci de m’indiquer l’état des voyants de votre modem. Par exemple : le voyant ADSL clignote, les autres sont allumés."
        }

    else:
        creer_reclamation(db=db, numligne=numligne, numtel=numtel, probleme=type_probleme)
        return {
            "fulfillmentText": f"Votre réclamation pour le problème '{type_probleme}' a été enregistrée."
        }
