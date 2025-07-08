from sqlalchemy.orm import Session

async def handle_fin_discussion(data, db: Session):
    return {
        "fulfillmentText": "Merci pour votre visite. La discussion est terminée.",
        "endConversation": True
    }
