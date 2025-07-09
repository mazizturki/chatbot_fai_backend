# 🤖 Chatbot FSI - Backend Intelligent avec FastAPI + Dialogflow

Ce projet constitue un backend intelligent pour un assistant de réclamations, conçu avec **FastAPI**, intégrant **Dialogflow**, **PostgreSQL**, **authentification JWT**, et un système complet d’historique utilisateur.

---

## 🚀 Fonctionnalités Clés

* ✅ Connexion à une base de données **PostgreSQL**
* ✅ Détection automatique des **intents** via **Dialogflow**
* ✅ Gestion de l'**historique utilisateur** avec stockage en base
* ✅ Réponses enrichies (suggestions, boutons)
* ✅ **Authentification JWT** avec stockage sécurisé (Flutter Secure Storage)
* ✅ Architecture modulaire et scalable

---

## 📊 Stack Technique

| Technologie | Rôle Principal                       |
| ----------- | ------------------------------------ |
| FastAPI     | Framework principal pour l’API REST  |
| PostgreSQL  | Base de données relationnelle        |
| SQLAlchemy  | ORM pour PostgreSQL                  |
| Dialogflow  | Traitement NLP & détection d'intents |
| Uvicorn     | Serveur ASGI rapide pour FastAPI     |
| JWT         | Authentification utilisateur         |

---

## 📂 Structure du Projet

```bash
chatbot-backend/
├── app/
│   ├── api/                # Fichiers de routage API
│   ├── core/               # Authentification, session, NLP
│   ├── db/                 # Modèles SQLAlchemy, connexion DB
│   ├── services/            # Gestionnaires personnalisés d’intents
│   └── main.py             # Point d'entrée principal
├── .env                    # Variables d’environnement
├── requirements.txt        # Dépendances Python
└── README.md               # Ce fichier
```

---

## 🚧 Installation Locale

### 1. Cloner le dépôt

```bash
git clone https://github.com/mazizturki/chatbot_fsi_backend.git
cd chatbot_fsi_backend
```

### 2. Créer un environnement virtuel

```bash
python -m venv .venv
source .venv/bin/activate  # sous Windows: .venv\Scripts\activate
```

### 3. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 4. Configurer les variables d'environnement

Crée un fichier `.env` à la racine :

```env
DATABASE_URL=postgresql://user:password@localhost/fsi
DIALOGFLOW_PROJECT_ID=****************
GOOGLE_APPLICATION_CREDENTIALS=****************
JWT_SECRET=*******************
```

### 5. Lancer l’API

```bash
uvicorn app.main:app --reload
```

---

## 🔐 Authentification JWT

* Endpoint : `GET /generate_token`
* Usage :

```http
Authorization: Bearer <ton_token_jwt>
```

Les tokens JWT sont générés dynamiquement et stockés dans le client Flutter via `flutter_secure_storage`.

---

## 🔌 Endpoint Principal : /chat

### ➔ POST `/chat`

**Requête JSON** :

```json
{
  "text": "J’ai un problème avec ma connexion Internet"
}
```

**Réponse JSON** :

```json
{
  "fulfillmentText": "Quel est votre problème ?",
  "options": ["Connexion lente", "Pas de signal"],
  "endConversation": false
}
```

---

## 🤖 Exemple d’Intent Handler

```python
async def handle_demander_marque_modem(data: dict, db: Session) -> dict:
    marques = ["Huawei", "TPLink", "Nokia", "ZTE"]
    return {
        "fulfillmentText": "Quel est la marque de votre modem ?",
        "options": marques
    }
```

---

## 📊 Historique des Conversations

Chaque message utilisateur est stocké en base avec :

* ID utilisateur (issu du JWT)
* Texte du message
* Intent détecté
* Timestamp de création

---

## 📦 Exemple d’appel avec curl

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ton_token>" \
  -d '{"text": "j’ai un souci avec mon modem"}'
```

---

## 🤝 Contributions

Les contributions sont les bienvenues :

* Forkez le projet
* Créez une branche `feature/nom`
* Envoyez une pull request descriptive

---

## 📄 Licence

Ce projet est sous licence **MIT** © Mohamed Aziz Turki | Vierund.