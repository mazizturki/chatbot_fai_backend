from google.cloud import dialogflow_v2 as dialogflow
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\\ChatBot Reclamations FSI\\chatbot_backend\\chatbot_dialogflow_key.json"

def test_dialogflow():
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path("chatbot-reclamation-fsi-grpn", "test-session")

    text_input = dialogflow.TextInput(text="adsl yeclingoti w internet 7amra", language_code="fr")
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)

    print("➡️ Texte envoyé :", response.query_result.query_text)
    print("➡️ Intent détecté :", response.query_result.intent.display_name)
    print("➡️ Réponse :", response.query_result.fulfillment_text)

    assert response.query_result.fulfillment_text is not None
    assert response.query_result.intent.display_name != ""  # le nom de l'intent doit être détecté
