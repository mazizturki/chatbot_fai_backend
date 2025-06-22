# Utilise une image officielle Python légère
FROM python:3.11-slim

# Définit le dossier de travail dans le container
WORKDIR /app

# Copier les fichiers requirements et .env dans le container
COPY requirements.txt ./
COPY .env ./

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le code de l’application dans le container
COPY ./app ./app
COPY ./chatbot_dialogflow_key.json ./chatbot_dialogflow_key.json

# Expose le port 8000 (port par défaut pour uvicorn)
EXPOSE 8000

# Commande pour lancer le serveur FastAPI avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
