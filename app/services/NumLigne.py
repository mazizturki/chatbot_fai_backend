from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.session_memory import get_param, get_progression, store_param, update_progression

async def handle_verifier_ligne(data: dict, db: Session) -> dict:
    params = data.get("queryResult", {}).get("parameters", {})
    session = data.get("session")
    session_id = session.split("/")[-1]

    print(f"[DEBUG] Paramètres reçus dans handle_verifier_ligne: {params}")

    # Récupération du numéro de ligne fourni maintenant OU précédemment
    numero = params.get("numligne") or get_param(session_id, "numligne")
    progression = get_progression(session_id)

    # Si l'étape est déjà validée, ne pas recommencer
    if progression.get("num_ligne_ok"):
        ancien_num = get_param(session_id, "numligne")
        return {
            "fulfillmentText": f"Le numéro de ligne {ancien_num} est déjà enregistré. Poursuivons avec la suite du diagnostic.",
            "endConversation": False
        }

    if not numero:
        return {"fulfillmentText": "Merci de fournir votre numéro de ligne."}

    # Stocker le numéro de ligne si fourni dans cette requête
    store_param(session_id, "numligne", numero)
    update_progression(session_id, "num_ligne_ok", True)


    try:
        query = text("SELECT etat FROM lignetelephonique WHERE num_ligne = :numero")
        query2 = text(
            "SELECT id_facture, montant, date_emission, statut_paiement "
            "FROM facture WHERE num_ligne = :numero "
            "ORDER BY date_emission DESC LIMIT 3"
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
                            f"Vous pouvez consulter vos factures sur le site web via le lien suivant : [Consulter ma facture](https://myttauth.tunisietelecom.tn/realms/selfcareportal/protocol/openid-connect/auth?client_id=b97c87f6-7d4f-4b04-8d09-49f105dfc5b8&redirect_uri=https%3A%2F%2Fmytt.tunisietelecom.tn%2Fmyspace&state=6bbcbbe0-e666-416b-86b5-7500502dc51b&response_mode=fragment&response_type=code&scope=openid&nonce=88d342c0-29ba-427d-8137-466858370168&code_challenge=hBUELPfr5SeztCvooqytax1hmvtAUHU_x5VVb1wFHF0&code_challenge_method=S256). "
                            f"Merci de le régler."
                        ),
                        "endConversation": True
                    }

                elif statut_paiement == "payée":
                    return {
                        "fulfillmentText": (
                            f"Votre ligne est inactive malgré le paiement de la dernière facture n° {id_facture}.\n"
                            f"Veuillez contacter notre service commercial sur le numéro 1298 ou le 71001298 pour plus d’informations."
                        ),
                        "endConversation": True
                    }

            return {
                "fulfillmentText": (
                    "Votre ligne est inactive.\n"
                    "Veuillez contacter notre service client sur le numéro 1298 ou le 71001298 pour plus d’informations.\n"
                    "Merci, fin de la discussion."
                ),
                "endConversation": True
            }

        else:
            return {"fulfillmentText": "Le statut de votre ligne est inconnu."}

    except Exception as e:
        print(f"[Erreur DB] {e}")
        return {"fulfillmentText": "Une erreur est survenue lors de la vérification de la ligne."}
