from enum import Enum
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .base import Base
import os
import logging

# Configuration du logging pour diagnostiquer les erreurs
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AppEnvironment(Enum):
    DEV = "dev"
    PROD = "prod"

# Déterminer l'environnement
ENVIRONMENT = os.getenv("APP_ENV", AppEnvironment.DEV.value)
logger.info(f"Environnement détecté : {ENVIRONMENT}")

# URLs de la base de données
DATABASE_URLS = {
    AppEnvironment.DEV.value: "postgresql://postgres:14774368@localhost:5432/fsi",
    AppEnvironment.PROD.value: os.getenv(
        "DATABASE_URL",
        "postgresql://postgres.chsxzmsnjiqkzsgpxvgm:14774368@aws-0-eu-central-1.pooler.supabase.com:6543/postgres"
    )
}

# Sélection de l'URL
DATABASE_URL = DATABASE_URLS[ENVIRONMENT]
logger.info(f"URL de la base de données : {DATABASE_URL}")

# Configuration de SQLAlchemy
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    logger.info("Connexion à la base de données établie avec succès")
except Exception as e:
    logger.error(f"Erreur lors de la connexion à la base de données : {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()