from sqlalchemy.orm import Session
from app.core.session_memory import store_param, get_param, get_progression, update_progression
from app.services.Diagnostique import diagnostic_probleme
from app.utils.extract import extract_session_id

async def handle_demander_marque_modem(data: dict, db: Session) -> dict:
    print("handle_demander_marque_modem called with data:", data)

    # Extraction de l'ID de session avec gestion des erreurs
    try:
        session_id = extract_session_id(data)
    except Exception as e:
        return {
            "fulfillmentText": "❗ Erreur : impossible de récupérer l'identifiant de session. Veuillez réessayer.",
            "endConversation": False
        }

    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()

    # Vérification de la progression
    progression = get_progression(session_id)
    if progression.get("marque_ok"):
        marque_existante = get_param(session_id, "marque_modem")
        return {
            "fulfillmentText": f"✅ La marque du modem ({marque_existante}) est déjà enregistrée. Poursuivons avec la suite du diagnostic.",
            "endConversation": False
        }

    # Mappage des marques valides
    marque_mapping = {
        "huawei": "Huawei",
        "tplink": "TPLink",
        "nokia": "Nokia",
        "zte": "ZTE",
        "cisco": "Cisco",
        "sagemcom": "Sagemcom",
        "netgear": "Netgear",
        "asus": "Asus",
        "dlink": "D-Link",
        "autre": "Autre"
    }
    valid_marques = list(marque_mapping.keys())
    marques_affichables = list(marque_mapping.values())

    # Récupération de la marque
    marque = parameters.get("marque_modem") or parameters.get("marque")
    if not marque:
        return {
            "fulfillmentText": "Pour mieux vous aider, Veuillez choisir la marque de votre modem.",
            "options": marques_affichables,
            "endConversation": False
        }

    # Validation de la marque
    if marque.lower() in valid_marques:
        marque_clean = marque_mapping[marque.lower()]
        store_param(session_id, "marque_modem", marque_clean)
        update_progression(session_id, "marque_ok", True)

        # Vérification des autres paramètres
        numligne = get_param(session_id, "numligne")
        numtel = get_param(session_id, "numtel")
        type_probleme = get_param(session_id, "TypeProbleme")

        print(f"[DEBUG] Infos actuelles - Ligne: {numligne}, Tel: {numtel}, Type: {type_probleme}")
        print(f"[DEBUG] numligne: {numligne}, type: {type(numligne)}")
        print(f"[DEBUG] numtel: {numtel}, type: {type(numtel)}")
        print(f"[DEBUG] type_probleme: {type_probleme}, type: {type(type_probleme)}")
        # Diagnostic si tous les champs sont remplis
        if numligne and numtel and type_probleme:
            return await diagnostic_probleme(session_id, db)

        # Messages pour les paramètres manquants
        if not numtel:
            return {
                "fulfillmentText": (
                    f"✅ Numéro de ligne : {numligne}\n"
                    f"📶 Marque du modem : {marque_clean}\n\n"
                    f"📞 Merci de me fournir votre numéro de téléphone pour continuer le diagnostic."
                ),
                "endConversation": False
            }

        if not numligne:
            return {
                "fulfillmentText": (
                    f"📞 Numéro de téléphone : {numtel}\n"
                    f"📶 Marque du modem : {marque_clean}\n\n"
                    f"☎️ Merci de me fournir le numéro relative à votre abonnement pour continuer."
                ),
                "endConversation": False
            }

        if not type_probleme:
            return {
                "fulfillmentText": (
                    f"✅ Informations enregistrées :\n"
                    f"- 🔢 Numéro de ligne : {numligne}\n"
                    f"- 📞 Téléphone : {numtel}\n"
                    f"- 📶 Modem : {marque_clean}\n\n"
                    f"📝 Merci de préciser le type de problème que vous rencontrez."
                ),
                "options": ["lenteur", "coupure", "instabilité"],
                "endConversation": False
            }
    else:
        return {
            "fulfillmentText": "❗ Aucune marque détectée. Veuillez choisir une marque valide parmi les suivantes :",
            "options": marques_affichables,
            "endConversation": False
        }