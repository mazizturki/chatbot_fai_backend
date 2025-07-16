import os
import tempfile
from dotenv import load_dotenv

# Charge les variables d'environnement depuis .env (utile en local)
load_dotenv()

# Récupère la clé JSON sous forme de chaîne depuis une variable d'environnement
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS_JSON")
DIALOGFLOW_PROJECT_ID = os.getenv("DIALOGFLOW_PROJECT_ID")

# Écrit la chaîne JSON dans un fichier temporaire et définit la variable attendue par Dialogflow
if GOOGLE_CREDENTIALS_JSON:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".json", mode="w") as temp:
        temp.write(GOOGLE_CREDENTIALS_JSON)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = temp.name
