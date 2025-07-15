import os
from google.cloud import dialogflow_v2 as dialogflow
from app.core.config import GOOGLE_APPLICATION_CREDENTIALS, DIALOGFLOW_PROJECT_ID

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_APPLICATION_CREDENTIALS

def detect_intent_with_params(session_id: str, text: str, language_code: str = "fr"):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(DIALOGFLOW_PROJECT_ID, session_id)

    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    fulfillment_text = response.query_result.fulfillment_text
    parameters = response.query_result.parameters

    return fulfillment_text, parameters