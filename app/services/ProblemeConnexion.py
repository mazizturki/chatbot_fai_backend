from sqlalchemy.orm import Session
from app.crud.ligne import verifier_statut_ligne

async def handle_probleme_connexion(data: dict, db: Session):
    params = data.get("queryResult", {}).get("parameters", {})
    num_ligne = params.get("NumLigne")

    if not num_ligne:
        return {"fulfillmentText": "Merci de me fournir votre numéro de ligne."}

    statut = verifier_statut_ligne(db, num_ligne)

    if statut == "inexistant":
        return {"fulfillmentText": f"Le numéro {num_ligne} est erroné."}
    elif statut == "inactif":
        return {"fulfillmentText": "Votre ligne est inactive."}
    elif statut == "actif":
        return {"fulfillmentText": "Votre ligne est active. Comment puis-je vous aider ?"}
    else:
        return {"fulfillmentText": "Une erreur est survenue."}
