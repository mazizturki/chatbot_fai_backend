from sqlalchemy.orm import Session
from app.core.session_memory import get_param, store_param, get_progression, update_progression
from app.crud.reclamation import creer_reclamation
from app.utils.extract import extract_param, extract_session_id

async def handle_demander_etat_modem(data: dict, db: Session) -> dict:
    session_id = extract_session_id(data)
    parameters = data["queryResult"].get("parameters", {})

    # Vérifier si le diagnostic est déjà effectué
    progression = get_progression(session_id)
    if progression.get("etat_ok"):
        return {
            "fulfillmentText": "Nous avons déjà enregistré l’état du modem.",
            "endConversation": False
        }

    # Vérifier les paramètres requis
    num_ligne = get_param(session_id, "numligne")
    num_tel = get_param(session_id, "numtel")
    marque = get_param(session_id, "marque_modem")

    if not all([num_ligne, num_tel]):
        return {
            "fulfillmentText": "Des informations sont manquantes. Veuillez d’abord fournir votre numéro de ligne et votre numéro de téléphone.",
            "endConversation": False
        }

    # Extraire les informations des voyants
    voyant = extract_param(parameters, "VoyantModem", session_id) or ""
    couleur = extract_param(parameters, "CouleurVoyant", session_id) or ""
    etat = extract_param(parameters, "EtatVoyant", session_id) or ""

    print(f"[DEBUG Voyants] session={session_id} | Voyant={voyant}, Couleur={couleur}, État={etat}")

    # Normalisation
    voyant = voyant.lower()
    couleur = couleur.lower()
    etat = etat.lower()

    # Cas 1 : Aucune info détectée → poser la question
    if not any([voyant, couleur, etat]):
        return {
            "fulfillmentText": "Merci de m’indiquer l’état des voyants de votre modem.",
            "options": [
                "Le voyant ADSL clignote",
                "Le voyant Internet est rouge",
                "Le voyant Internet est éteint",
                "Le voyant Wi-Fi est éteint",
                "Tous les voyants sont éteints"
            ],
            "endConversation": False
        }

    # Cas 2 : Voyant ADSL clignote → réclamation immédiate
    if voyant == "adsl" and etat == "clignote":
        update_progression(session_id, "etat_ok", True)
        reclamation = creer_reclamation(
            db=db,
            numligne=num_ligne,
            numtel=num_tel,
            probleme="Synchronisation (voyant ADSL clignote)",
            marque_modem=marque
        )
        return {
            "fulfillmentText": (
                "Les voyants indiquent une 🔌 Perte de synchronisation DSL. "
                f"Une réclamation a été enregistrée sous le numéro {reclamation.id_reclamation}.\n\n"
                "Nous restons à votre disposition pour toute autre demande. Excellente journée à vous."
            ),
            "endConversation": True
        }

    # Cas 3 : Internet rouge ou éteint → demander redémarrage
    if voyant == "internet" and (couleur == "rouge" or etat == "eteint"):
        return {
            "fulfillmentText": (
                "Veuillez effectuer un redémarrage de votre modem en insérant un trombone dans le bouton RESET. "
                "Est-ce que le problème est résolu après cette manipulation ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }

    # Cas 4 : Voyant Wi-Fi éteint → problème potentiel de Wi-Fi
    if voyant == "wlan" and (couleur == "éteint" or etat == "éteint"):
        return {
            "fulfillmentText": (
                "Le voyant Wi-Fi semble indiquer un problème de réseau sans fil. "
                "Veuillez vérifier si Monk-0-le Wi-Fi est activé sur votre modem ou redémarrez-le. "
                "Le problème persiste-t-il ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }

    # Cas 5 : Voyant normal (Internet vert et stable)
    if voyant == "internet" and couleur == "vert" and etat == "stable":
        update_progression(session_id, "etat_ok", True)
        return {
            "fulfillmentText": (
                "✅ Les voyants indiquent que votre modem fonctionne correctement. "
                "Votre connexion semble normale.\n\n"
                "Nous restons à votre disposition pour toute autre demande. Excellente journée à vous."
            ),
            "endConversation": True
        }

    # Cas 6 : Tous les voyants éteints → problème d’alimentation
    if etat == "éteint" and not voyant:
        return {
            "fulfillmentText": (
                "Il semble que votre modem ne soit pas alimenté. "
                "Veuillez vérifier que le câble d’alimentation est bien branché et que le modem est sous tension. "
                "Le problème persiste-t-il ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }

    # Cas par défaut : État inconnu ou non critique → réclamation
    update_progression(session_id, "etat_ok", True)
    reclamation = creer_reclamation(
        db=db,
        numligne=num_ligne,
        numtel=num_tel,
        probleme="Coupure (état des voyants non interprétable)",
        marque_modem=marque
    )
    return {
        "fulfillmentText": (
            "Nous n’avons pas pu interpréter précisément l’état des voyants. "
            f"Par précaution, une réclamation a été enregistrée sous le numéro {reclamation.id_reclamation}.\n\n"
            "Nous restons à votre disposition pour toute autre demande. Excellente journée à vous."
        ),
        "endConversation": True
    }