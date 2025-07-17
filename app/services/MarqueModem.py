from sqlalchemy.orm import Session
from app.core.session_memory import store_param, get_param, get_progression, update_progression
from app.services.Diagnostique import diagnostic_probleme
from app.utils.extract import extract_session_id

async def handle_demander_marque_modem(data: dict, db: Session) -> dict:
    print("handle_demander_marque_modem called with data:", data)

    session_id = extract_session_id(data)
    parameters = dict(data["queryResult"]["parameters"])
    query_text = data["queryResult"].get("queryText", "").lower()

    # Vérification de progression
    progression = get_progression(session_id)
    if progression.get("marque_ok"):
        marque_existante = get_param(session_id, "marque_modem")
        return {
            "fulfillmentText": f"✅ La marque du modem (**{marque_existante}**) est déjà enregistrée. Poursuivons avec la suite du diagnostic.",
            "endConversation": False
        }

    # Récupération de la marque
    marque = parameters.get("marque_modem") or query_text
    print(f"[DEBUG] Marque détectée : {marque}")

    valid_marques = ["huawei", "tplink", "nokia", "zte", "cisco", "sagemcom", "netgear", "asus", "dlink"]

    if marque and marque.lower() in valid_marques:
        marque_clean = marque.capitalize()
        store_param(session_id, "marque_modem", marque_clean)
        update_progression(session_id, "marque_ok", True)

        # Vérifier si tous les autres paramètres sont prêts
        numligne = get_param(session_id, "numligne")
        numtel = get_param(session_id, "numtel")
        type_probleme = get_param(session_id, "TypeProbleme")

        print(f"[DEBUG] Infos actuelles - Ligne: {numligne}, Tel: {numtel}, Type: {type_probleme}")

        # Diagnostic si tous les champs sont remplis
        if numligne and numtel and type_probleme:
            return await diagnostic_probleme(session_id, db)

        # Messages en fonction de ce qui manque
        if not numtel:
            return {
                "fulfillmentText": (
                    f"✅ Numéro de ligne : **{numligne}**\n"
                    f"📶 Marque du modem : **{marque_clean}**\n\n"
                    f"📞 Merci de me fournir votre **numéro de téléphone** pour continuer le diagnostic."
                ),
                "endConversation": False
            }

        if not numligne:
            return {
                "fulfillmentText": (
                    f"📞 Numéro de téléphone : **{numtel}**\n"
                    f"📶 Marque du modem : **{marque_clean}**\n\n"
                    f"🔢 Merci de me fournir votre **numéro de ligne** (abonnement) pour continuer."
                ),
                "endConversation": False
            }

        if not type_probleme:
            return {
                "fulfillmentText": (
                    f"✅ Informations enregistrées :\n"
                    f"- 🔢 Numéro de ligne : **{numligne}**\n"
                    f"- 📞 Téléphone : **{numtel}**\n"
                    f"- 📶 Modem : **{marque_clean}**\n\n"
                    f"📝 Merci de préciser **le type de problème** que vous rencontrez."
                ),
                "options": ["lenteur", "coupure", "instabilité"],
                "endConversation": False
            }

    # Si la marque est invalide
    marques_affichables = ["Huawei", "TPLink", "Nokia", "ZTE", "Cisco", "Sagemcom", "Netgear", "Asus", "D-Link"]
    return {
        "fulfillmentText": "❗ Marque non reconnue. Veuillez choisir une marque valide parmi les suivantes :",
        "options": marques_affichables,
        "endConversation": False
    }
