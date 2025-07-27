import os
import tempfile
from dotenv import load_dotenv

load_dotenv()

GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

if GOOGLE_CREDENTIALS_JSON:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp:
        temp.write(GOOGLE_CREDENTIALS_JSON)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp.name

FLASK_MAINTENANCE_URL = os.getenv("FLASK_MAINTENANCE_URL")
FLASK_API_KEY = os.getenv("FLASK_API_KEY")