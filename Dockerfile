# Utilise une image Python légère
FROM python:3.11-slim

# Évite les interactions pendant les installations
ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système nécessaires
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Définir le dossier de travail
WORKDIR /app

# Copier uniquement requirements.txt pour optimiser le cache Docker
COPY requirements.txt .

# Installer les dépendances Python en avance (optimise la couche cache Docker)
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Télécharger le modèle spaCy en français (mieux ici que dans un autre layer)
RUN python -m spacy download fr_core_news_md

# Copier les autres fichiers de l'application
COPY . .

# Assure-toi que la variable d'environnement est chargée automatiquement (optionnel)
ENV GOOGLE_APPLICATION_CREDENTIALS="chatbot_dialogflow_key.json"

# Exposer le port utilisé par uvicorn
EXPOSE 8000

# Lancer l'application FastAPI
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
