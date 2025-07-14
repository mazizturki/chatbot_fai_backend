from sqlalchemy.orm import Session
from app.core.session_memory import get_param, get_progression, update_progression
from app.services.speedtest_service import run_speedtest
from app.services.EtatModem import handle_demander_etat_modem 
from app.crud.reclamation import creer_reclamation
from app.utils.extract import extract_param

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

    # Cas lenteur → test de vitesse
    if type_probleme == "lenteur":
        message_intro = f"Lancement du test de vitesse pour la ligne {numligne}... Veuillez patienter.\n"
        speed_data = await run_speedtest(numligne, db)
        if speed_data is None:
            return {"fulfillmentText": "❌ Impossible d'effectuer le test de vitesse pour le moment."}

        download_mbps = speed_data.get("download")
        upload_mbps = speed_data.get("upload")
        ping_ms = speed_data.get("ping")
        debit_attendu = speed_data.get("debit_attendu")

        if None in [download_mbps, upload_mbps, ping_ms, debit_attendu]:
            return {"fulfillmentText": "❌ Le test de vitesse a échoué. Données incomplètes."}

        difference = debit_attendu - download_mbps
        print(f"[DEBUG] Download: {download_mbps} Mbps | Upload: {upload_mbps} Mbps | Ping: {ping_ms} ms | Attendu: {debit_attendu} Mbps | Écart: {difference} Mbps")

        # ✅ Considéré comme terminé, éviter qu'on refasse ce test
        update_progression(session_id, "diagnostic_ok", True)

        # Analyse
        if difference < 2 and ping_ms < 100:
            return {
                "fulfillmentText": (
                    f"📶 Débit descendant : {download_mbps:.2f} Mbps\n"
                    f"🔼 Débit montant : {upload_mbps:.2f} Mbps\n"
                    f"📡 Ping : {ping_ms} ms\n\n"
                    f"✅ Ces valeurs sont conformes aux attentes (débit attendu : {debit_attendu:.2f} Mbps).\n"
                    "Votre ligne fonctionne normalement.\n\n"
                    "Nous restons à votre disposition pour toute autre demande.\nExcellente journée à vous."
                ),
                "endConversation": True
            }

        elif 2 <= difference < 6 or ping_ms >= 100:
            return {
                "fulfillmentText": (
                    f"📶 Débit descendant : {download_mbps:.2f} Mbps (attendu : {debit_attendu:.2f} Mbps)\n"
                    f"🔼 Débit montant : {upload_mbps:.2f} Mbps\n"
                    f"📡 Ping : {ping_ms} ms\n\n"
                    "⚠️ Le débit est en dessous des attentes ou la latence est élevée. "
                    "Merci de redémarrer votre modem et de vérifier si le problème persiste.\n\n"
                    "Nous restons à votre disposition pour toute autre demande.\nExcellente journée à vous."
                ),
                "endConversation": True
            }

        else:
            creer_reclamation(
                db=db,
                numligne=numligne,
                numtel=numtel,
                probleme="lenteur (débit très faible ou instabilité)",
                marque_modem=get_param(session_id, "marque_modem")
            )
            return {
                "fulfillmentText": (
                    f"📶 Débit descendant : {download_mbps:.2f} Mbps (attendu : {debit_attendu:.2f} Mbps)\n"
                    f"🔼 Débit montant : {upload_mbps:.2f} Mbps\n"
                    f"📡 Ping : {ping_ms} ms\n\n"
                    "❌ Le débit est largement en dessous de la normale.\n"
                    "Une réclamation a été enregistrée. Notre équipe technique vous contactera sous peu.\n\n"
                    "Nous restons à votre disposition pour toute autre demande.\nExcellente journée à vous."
                ),
                "endConversation": True
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
        creer_reclamation(
            db=db,
            numligne=numligne,
            numtel=numtel,
            probleme=type_probleme,
            marque_modem=get_param(session_id, "marque_modem")
        )
        return {
            "fulfillmentText": (
                f"Une réclamation pour le problème {type_probleme} a été enregistrée.\n\n"
                "Nous restons à votre disposition pour toute autre demande.\nExcellente journée à vous."
            ),
            "endConversation": True
        }
