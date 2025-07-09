from sqlalchemy.orm import Session

from app.core.session_memory import clear_session

async def handle_fin_discussion(data: dict, db: Session):
    session_id = data.get("session")
    clear_session(session_id)
    return {
        "fulfillmentText": "Merci pour votre temps. À bientôt !",
        "endConversation": True
    }

