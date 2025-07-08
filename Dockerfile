# Utilise une image Python légère
FROM python:3.11-slim

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Définir le dossier de travail
WORKDIR /app

# Copier les fichiers
COPY requirements.txt ./
COPY .env ./
COPY ./app ./app
COPY ./chatbot_dialogflow_key.json ./chatbot_dialogflow_key.json

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Télécharger le modèle spaCy en français
RUN python -m spacy download fr_core_news_md

# Exposer le port pour uvicorn
EXPOSE 8000

# Lancer l'application FastAPI avec uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
