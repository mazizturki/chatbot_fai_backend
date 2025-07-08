from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.session_memory import get_param, store_param

async def handle_verifier_ligne(data: dict, db: Session) -> dict:
    params = data.get("queryResult", {}).get("parameters", {})
    session = data.get("session")
    session_id = session.split("/")[-1]

    print(f"[DEBUG] Paramètres reçus dans handle_verifier_ligne: {params}")

    # Récupération du numéro de ligne fourni maintenant OU précédemment
    numero = params.get("numligne") or get_param(session_id, "numligne")

    if not numero:
        return {"fulfillmentText": "Merci de fournir votre numéro de ligne."}

    # Stocker le numéro de ligne si fourni dans cette requête
    store_param(session_id, "numligne", numero)

    try:
        query = text("SELECT etat FROM lignetelephonique WHERE num_ligne = :numero")
        query2 = text(
            "SELECT id_facture, montant, date_emission, statut_paiement "
            "FROM facture WHERE num_ligne = :numero "
            "ORDER BY date_emission DESC LIMIT 1"
        )

        result = db.execute(query, {"numero": numero}).fetchone()
        result2 = db.execute(query2, {"numero": numero}).fetchone()

        if not result:
            return {
                "fulfillmentText": f"Le numéro {numero} est inexistant. Merci de saisir un numéro valide."
            }

        etat = result[0].lower()

        if etat == "actif":
            return {"fulfillmentText": "Veuillez fournir votre numéro de téléphone."}

        elif etat == "inactif":
            if result2:
                id_facture, montant, date_emission, statut_paiement = result2
                statut_paiement = statut_paiement.lower()

                if statut_paiement == "impayée":
                    return {
                        "fulfillmentText": (
                            f"Votre ligne est inactive suite au non-paiement. \n"
                            f"Dernière facture n° {id_facture} de montant {montant} DT du {date_emission}, "
                            f"est {statut_paiement.capitalize()}.\n"
                            f"Merci de le régler."
                        ),
                        "endConversation": True
                    }

                elif statut_paiement == "payée":
                    return {
                        "fulfillmentText": (
                            f"Votre ligne est inactive malgré le paiement de la dernière facture n° {id_facture}.\n"
                            f"Veuillez contacter notre service commercial pour plus d’informations."
                        ),
                        "endConversation": True
                    }

            return {
                "fulfillmentText": (
                    "Votre ligne est inactive.\n"
                    "Veuillez contacter notre service client pour plus d’informations.\n"
                    "Merci, fin de la discussion."
                ),
                "endConversation": True
            }

        else:
            return {"fulfillmentText": "Le statut de votre ligne est inconnu."}

    except Exception as e:
        print(f"[Erreur DB] {e}")
        return {"fulfillmentText": "Une erreur est survenue lors de la vérification de la ligne."}
