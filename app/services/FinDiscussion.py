from sqlalchemy.orm import Session
from app.core.session_memory import clear_session
from app.utils.extract import extract_session_id

async def handle_fin_discussion(data: dict, db: Session):
    session_id = extract_session_id(data)
    print(f"[DEBUG handle_fin_discussion] session={session_id}, data={data}")
    clear_session(session_id)
    return {
        "fulfillmentText": "Merci pour votre temps. À bientôt !",
        "endConversation": True
    }

