from fastapi import FastAPI
from google.cloud import dialogflow_v2 as dialogflow

app = FastAPI()

@app.get("/test-dialogflow")
async def test_dialogflow():
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path("chatbot-reclamation-fsi-grpn", "test-session")

    text_input = dialogflow.TextInput(text="Bonjour", language_code="fr")
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(session=session, query_input=query_input)

    return {"query_text": response.query_result.query_text,
            "intent": response.query_result.intent.display_name,
            "response": response.query_result.fulfillment_text}
