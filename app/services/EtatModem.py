from sqlalchemy.orm import Session
from app.core.session_memory import get_param, store_param, get_progression, update_progression
from app.crud.reclamation import creer_reclamation
from app.utils.extract import extract_param, extract_session_id

async def handle_demander_etat_modem(data: dict, db: Session) -> dict:
    session_id = extract_session_id(data)
    parameters = data["queryResult"].get("parameters", {})

    # Vérifier si le diagnostic a déjà été effectué
    progression = get_progression(session_id)
    if progression.get("etat_ok"):
        return {
            "fulfillmentText": "Nous avons déjà enregistré l’état du modem.",
            "endConversation": False
        }

    # Récupération des informations nécessaires
    num_ligne = get_param(session_id, "numligne")
    num_tel = get_param(session_id, "numtel")
    marque = get_param(session_id, "marque_modem")

    if not all([num_ligne, num_tel]):
        return {
            "fulfillmentText": "Des informations sont manquantes. Veuillez d’abord fournir votre numéro de ligne et votre numéro de téléphone.",
            "endConversation": False
        }

    # Extraction des paramètres envoyés par Dialogflow
    voyant = extract_param(parameters, "VoyantModem", session_id) or ""
    couleur = extract_param(parameters, "CouleurVoyant", session_id) or ""
    etat = extract_param(parameters, "etatvoyant", session_id) or ""

    print(f"[DEBUG Voyants] session={session_id} | Voyant={voyant}, Couleur={couleur}, État={etat}")

    # Normalisation des valeurs
    voyant = voyant.lower()
    couleur = couleur.lower()
    etat = etat.lower()

    # Cas 1 : Aucune information détectée
    if not any([voyant, couleur, etat]):
        return {
            "fulfillmentText": "Merci de m’indiquer l’état des voyants de votre modem.",
            "options": [
                "Le voyant ADSL clignote",
                "Le voyant Internet est éteint",
                "Le voyant WLAN est éteint",
            ],
            "endConversation": False
        }

    # Cas 2 : ADSL clignote → réclamation immédiate
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

    # Cas 3 : Internet rouge ou éteint → redémarrage demandé
    if voyant == "internet" and (couleur == "rouge" or etat == "éteint"):
        return {
            "fulfillmentText": (
                "Veuillez effectuer un redémarrage de votre modem en insérant un trombone dans le bouton RESET. "
                "Est-ce que le problème est résolu après cette manipulation ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }

    # Cas 4 : Wi-Fi éteint → vérifier activation du Wi-Fi
    if voyant == "wlan" and etat == "éteint":
        return {
            "fulfillmentText": (
                "Le voyant WLAN semble indiquer un problème de réseau sans fil. "
                "Veuillez vérifier si le Wi-Fi est activé sur votre modem ou redémarrez-le. "
                "Est-ce que le problème est résolu ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }

    # Cas 5 : Internet vert et stable → tout est normal
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

    # Cas 6 : Tous les voyants sont éteints → problème d’alimentation
    if etat == "éteint" and not voyant:
        return {
            "fulfillmentText": (
                "Il semble que votre modem ne soit pas alimenté. "
                "Veuillez vérifier que le câble d’alimentation est bien branché et que le modem est sous tension. "
                "Est-ce que le problème est résolu ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }

    # Cas par défaut : État non interprétable → créer réclamation par précaution
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
