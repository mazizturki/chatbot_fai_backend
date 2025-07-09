from sqlalchemy.orm import Session
from app.core.session_memory import get_param, store_param
from app.crud.reclamation import creer_reclamation
from app.utils.extract import extract_param

async def handle_demander_etat_modem(data: dict, db: Session) -> dict:
    session_id = data.get("session")
    parameters = data["queryResult"].get("parameters", {})

    num_ligne = get_param(session_id, "numligne")
    num_tel = get_param(session_id, "numtel")

    if not num_ligne or not num_tel:
        return {
            "fulfillmentText": "Des informations sont manquantes pour enregistrer la réclamation. Veuillez d’abord fournir votre numéro de ligne et votre numéro de téléphone.",
            "endConversation": False
        }

    voyant = extract_param(parameters, "VoyantModem", session_id)
    couleur = extract_param(parameters, "CouleurVoyant", session_id)
    etat = extract_param(parameters, "EtatVoyant", session_id)

    print(f"[DEBUG] Voyant={voyant}, Couleur={couleur}, État={etat}")

    # Cas 1 : Voyant ADSL clignote → réclamation immédiate
    if voyant.lower() == "adsl" and etat.lower() == "clignote":
        creer_reclamation(
            db=db,
            numligne=num_ligne,
            numtel=num_tel,
            probleme="coupure (voyant ADSL clignote)"
        )
        return {
            "fulfillmentText": "Le voyant ADSL clignote. Une réclamation a été enregistrée pour une coupure de service.",
            "endConversation": True
        }

    # Cas 2 : Voyant rouge → redémarrage manuel, on attend la réponse utilisateur
    if voyant.lower() == "rouge" and (etat.lower() == "éteint" or couleur.lower() == "rouge"):
        return {
            "fulfillmentText": (
                "Veuillez effectuer un redémarrage de votre modem en insérant un trombone dans le bouton RESET. "
                "Est-ce que le problème est résolu après cette manipulation ?"
            ),
            "options": ["Oui", "Non"],
            "endConversation": False
        }

    # Cas par défaut : état incertain → réclamation
    creer_reclamation(
        db=db,
        numligne=num_ligne,
        numtel=num_tel,
        probleme="coupure (état du voyant inconnu)"
    )
    return {
        "fulfillmentText": "Une réclamation a été enregistrée. Nous vous contacterons dans les plus brefs délais.",
        "endConversation": True
    }
