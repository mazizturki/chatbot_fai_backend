from sqlalchemy import text
from sqlalchemy.orm import Session
from app.crud.facture import nbr_factures, somme_montant_factures
from app.core.session_memory import get_param, get_progression, store_param, update_progression
from app.services.Diagnostique import diagnostic_probleme

async def handle_verifier_ligne(data: dict, db: Session) -> dict:
    params = data.get("queryResult", {}).get("parameters", {})
    session = data.get("session")
    session_id = session.split("/")[-1]

    print(f"[DEBUG] Paramètres reçus dans handle_verifier_ligne: {params}")

    # Récupération du numéro de ligne fourni maintenant
    numero = params.get("numligne")

    # Si aucun numéro n’est fourni et aucun n’est stocké
    if not numero and not get_param(session_id, "numligne"):
        return {"fulfillmentText": "☎️ Veuillez saisir le numéro relative à votre abonnement."}

    # Si un nouveau numéro est fourni, l’utiliser
    if numero:
        try:
            query = text("SELECT etat FROM lignetelephonique WHERE num_ligne = :numero")
            result = db.execute(query, {"numero": numero}).fetchone()

            if not result:
                # Ne pas stocker le numéro ni marquer l’étape comme validée si inexistant
                return {
                    "fulfillmentText": f"Le numéro {numero} est inexistant. Merci de saisir un numéro valide."
                }

            # Si le numéro existe, le stocker et marquer l’étape comme validée
            store_param(session_id, "numligne", numero)
            update_progression(session_id, "num_ligne_ok", True)

            etat = result[0].lower()
            nombre_factures = nbr_factures(db, numero)
            somme_factures = somme_montant_factures(db, numero)

            if etat == "actif":
                return {"fulfillmentText": "📞 Veuillez saisir votre numéro de téléphone."}

            elif etat == "inactif":
                query2 = text(
                    "SELECT id_facture, montant, date_emission, statut_paiement "
                    "FROM facture WHERE num_ligne = :numero "
                    "ORDER BY date_emission DESC LIMIT 3"
                )
                result2 = db.execute(query2, {"numero": numero}).fetchone()

                if result2:
                    id_facture, montant, date_emission, statut_paiement = result2
                    statut_paiement = statut_paiement.lower()

                    if statut_paiement == "impayée":
                        return {
                            "fulfillmentText": (
                                f"Votre ligne est inactive suite au non-paiement. \n\n"
                                f"Vous avez {nombre_factures} facture(s) non payée(s) de total {somme_factures} DT.\n"
                                f"Dernière facture n° {id_facture} de montant {montant} DT du {date_emission}, "
                                f"est {statut_paiement.capitalize()}.\n\n"
                                f"Vous pouvez consulter vos factures sur le site web via le lien suivant : https://mytt.tunisietelecom.tn/anonymous/paiement-facture.\n\n"
                                f"Merci de le(s) régler."
                            ),
                            "endConversation": True
                        }

                    elif statut_paiement == "payée":
                        return {
                            "fulfillmentText": (
                                f"Votre ligne est inactive malgré le paiement de votre dernière facture n° {id_facture}.\n"
                                f"Veuillez contacter notre service commercial sur le numéro 1298 ou le 71001298 pour plus d’informations."
                            ),
                            "endConversation": True
                        }

                return {
                    "fulfillmentText": (
                        "Votre ligne est inactive.\n"
                        "Veuillez contacter notre service client sur le numéro 1298 ou le 71001298 pour plus d’informations.\n"
                        "Nous restons à votre disposition pour toute autre demande.\nExcellente journée à vous."
                    ),
                    "endConversation": True
                }

            else:
                return {"fulfillmentText": "Le statut de votre ligne est inconnu."}

        except Exception as e:
            print(f"[Erreur DB] {e}")
            return {"fulfillmentText": "Une erreur est survenue lors de la vérification de la ligne."}

    # Si aucun nouveau numéro n’est fourni mais un numéro est déjà stocké et validé
    progression = get_progression(session_id)
    if progression.get("num_ligne_ok"):
        ancien_num = get_param(session_id, "numligne")
        numtel = get_param(session_id, "numtel")
        marque_modem = get_param(session_id, "marque_modem")
        type_probleme = get_param(session_id, "TypeProbleme")

        if numtel and marque_modem and type_probleme:
            return await diagnostic_probleme(data, db)

        if not numtel:
            return {
                "fulfillmentText": (
                    f"📞 Veuillez saisir votre numéro de portable."
                ),
                "endConversation": False
            }

        if not marque_modem:
            return {
                "fulfillmentText": (
                    f"✅ Le numéro de ligne {ancien_num} et le numéro de téléphone {numtel} sont déjà enregistrés.\n\n"
                    f"📶 Veuillez maintenant me communiquer la **marque de votre modem**."
                ),
                "options": ["Huawei", "TPLink", "Nokia", "ZTE", "Cisco", "Sagemcom", "Netgear", "Asus", "D-Link"],
                "endConversation": False
            }

        if not type_probleme:
            return {
                "fulfillmentText": (
                    f"✅ Les informations suivantes sont déjà enregistrées :\n"
                    f"- ☎️ Numéro de ligne : {ancien_num}\n"
                    f"- 📞 Numéro de téléphone : {numtel}\n"
                    f"- 📶 Modem : {marque_modem}\n\n"
                    f"📝 Merci de préciser le type de problème de connexion que vous rencontrez."
                ),
                "options": ["lenteur", "coupure", "instabilité"],
                "endConversation": False
            }

    return {"fulfillmentText": "Merci de fournir votre numéro de ligne."}