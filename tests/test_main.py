import pytest
from fastapi.testclient import TestClient
from app.main import app, verify_jwt_token, detect_intent, intent_handlers

client = TestClient(app)

# Fake JWT verifier
def fake_verify_jwt_token():
    return {"jti": "test-session"}

# Fake Dialogflow response
def fake_detect_intent(project_id, session_id, text, language_code="fr"):
    class FakeIntent:
        display_name = "ProblemeConnexion"

    class FakeQueryResult:
        intent = FakeIntent()
        parameters = {}
        fulfillment_text = "Réponse simulée"

    return FakeQueryResult()

# Fake handler
async def fake_handler(data, db):
    return {
        "fulfillmentText": "Réponse testée avec succès",
        "options": [],
        "endConversation": False
    }

def test_chat_endpoint():
    # Remplacement des dépendances
    app.dependency_overrides[verify_jwt_token] = fake_verify_jwt_token

    # Override du handler et du detect_intent
    intent_handlers["ProblemeConnexion"] = fake_handler
    app.detect_intent = fake_detect_intent  

    response = client.post(
        "/chat",
        json={"text": "cnx ma9sousa"},
        headers={"Authorization": "Bearer fake-token"}
    )

    assert response.status_code == 200
    assert response.json()["fulfillmentText"] == "Réponse testée avec succès"
        