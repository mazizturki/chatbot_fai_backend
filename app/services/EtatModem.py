from sqlalchemy.orm import Session
from app.core.session_memory import get_param, store_param, get_progression, update_progression
from app.crud.reclamation import creer_reclamation
from app.utils.extract import extract_param, extract_session_id

async def handle_demander_etat_modem(data: dict, db: Session) -> dict:
    session_id = extract_session_id(data)
    parameters = data["queryResult"].get("parameters", {})

    progression = get_progression(session_id)
    if progression.get("etat_ok"):
        return {
            "fulfillmentText": "Nous avons déjà enregistré l’état du modem. Passons à l'étape suivante.",
            "endConversation": False
        }

    num_ligne = get_param(session_id, "numligne")
    num_tel = get_param(session_id, "numtel")
    marque = get_param(session_id, "marque_modem")

    if not all([num_ligne, num_tel]):
        return {
            "fulfillmentText": "Des informations sont manquantes. Veuillez d’abord fournir votre numéro de ligne et votre numéro de téléphone.",
            "endConversation": False
        }

    voyant = extract_param(parameters, "VoyantModem", session_id)
    couleur = extract_param(parameters, "CouleurVoyant", session_id)
    etat = extract_param(parameters, "EtatVoyant", session_id)

    print(f"[DEBUG Voyants] session={session_id} | Voyant={voyant}, Couleur={couleur}, État={etat}")

    # 🛑 Aucune info détectée → poser la question
    if not any([voyant, couleur, etat]):
        return {
            "fulfillmentText": (
                "Merci de m’indiquer l’état des voyants de votre modem. "
                "Par exemple : le voyant ADSL clignote, ou Internet est rouge."
            ),
            "options": [
                "Le voyant ADSL clignote",
                "Le voyant Internet est rouge",
                "Le voyant Internet est éteint",
                "Tous les voyants sont allumés"
            ],
            "endConversation": False
        }

    # Normalisation (évite erreur si valeur absente)
    voyant = (voyant or "").lower()
    couleur = (couleur or "").lower()
    etat = (etat or "").lower()

    # ✅ Cas 1 : Voyant ADSL clignote → réclamation immédiate
    if "adsl" in voyant and "clignote" in etat:
        update_progression(session_id, "etat_ok", True)
        creer_reclamation(
            db=db,
            numligne=num_ligne,
            numtel=num_tel,
            probleme="Synchronisation (voyant ADSL clignote)",
            marque_modem=marque
        )
        return {
            "fulfillmentText": (
                "Les voyants indiquent une 🔌 Perte de synchronisation DSL. "
                "Une réclamation a été enregistrée.\n\n"
                "Nous restons à votre disposition pour toute autre demande. Excellente journée à vous."
            ),
            "endConversation": True
        }

    # ✅ Cas 2 : Internet rouge ou éteint → demander redémarrage
    if "internet" in voyant and ("rouge" in couleur or "eteint" in etat):
        return {
            "fulfillmentText": (
                "Veuillez effectuer un redémarrage de votre modem en insérant un trombone dans le bouton RESET. "
                "Est-ce que le problème est résolu après cette manipulation ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }
    
    # ✅ Cas combiné : ADSL clignote + Internet rouge ou éteint → réclamation immédiate
    if (
        ("adsl" in voyant and "clignote" in etat) and
        ("internet" in voyant and ("rouge" in couleur or "eteint" in etat))
    ):
        update_progression(session_id, "etat_ok", True)
        creer_reclamation(
            db=db,
            numligne=num_ligne,
            numtel=num_tel,
            probleme="Synchronisation (ADSL clignote + Internet rouge/éteint)",
            marque_modem=marque
        )
        return {
            "fulfillmentText": (
                "Les voyants indiquent une 🔌 Perte de synchronisation DSL. "
                "Une réclamation urgente a été enregistrée auprès de notre service technique.\n\n"
                "Nous vous contacterons dans les plus brefs délais. Excellente journée à vous."
            ),
            "endConversation": True
        }
    
    # 🟠 Cas inconnu ou non critique → réclamation par défaut
    update_progression(session_id, "etat_ok", True)
    creer_reclamation(
        db=db,
        numligne=num_ligne,
        numtel=num_tel,
        probleme="coupure (état des voyants non interprétable)",
        marque_modem=marque
    )
    return {
        "fulfillmentText": (
            "Nous n’avons pas pu interpréter précisément l’état des voyants. "
            "Par précaution, une réclamation a été enregistrée.\n\n"
            "Nous restons à votre disposition pour toute autre demande. Excellente journée à vous."
        ),
        "endConversation": True
    }
