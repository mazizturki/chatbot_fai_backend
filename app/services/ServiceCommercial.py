from sqlalchemy.orm import Session
from app.core.session_memory import store_param
from app.utils.extract import extract_param, extract_session_id

async def handle_service_commercial(data: dict, db: Session) -> dict:
    session_id = extract_session_id(data)
    print(f"[DEBUG - ServiceCommercial] session_id={session_id}, data={data}")
    parameters = data["queryResult"].get("parameters", {})
    query_text = data["queryResult"].get("queryText", "")
    
    motif_commercial = extract_param(parameters, "commercial", session_id) or ""
    
    if motif_commercial:
        store_param(session_id, "motif_commercial", motif_commercial)

    print(f"[DEBUG - ServiceCommercial] session={session_id}, motif={motif_commercial}, texte={query_text}")

    if motif_commercial:
        return {
            "fulfillmentText": (
                f"Votre demande concernant {motif_commercial} est de nature commerciale. "
                "Pour toute demande liée aux offres, factures ou abonnements, veuillez contacter notre service commercial "
                "au 1298 ou le 71001298, puis tapez 3. Merci de votre compréhension."
            ),
            "endConversation": True
        }
    else:
        return {
            "fulfillmentText": (
                "Votre demande semble concerner le service commercial. "
                "Pour toute question relative à la facturation, aux offres ou à votre contrat, contactez notre service commercial "
                "au 1298 ou le 71001298, puis tapez 3. Merci de votre compréhension."
            ),
            "endConversation": True
        }
