from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from app.database.session import get_db

# Exemple : à mettre dans .env et charger dynamiquement
DATABASE_URL = "postgresql://postgres:password@localhost:5432/chatbotdb"
engine = create_engine(DATABASE_URL)

def verifier_ligne(numero: str) -> str:
    """
    Vérifie si une ligne existe, et retourne son état :
    - "actif"
    - "inactif"
    - "inexistant"
    """
    import uvicorn
    from app.database.session import SessionLocal  
    # Test avec gestion propre de la session
    db = SessionLocal()
    try:
        with engine.connect() as conn:
            query = text("SELECT statut FROM lignes WHERE numero = :numero")
            result = conn.execute(query, {"numero": numero}).fetchone()

            if not result:
                return "inexistant"

            statut = result[0]  # supposé 'actif' ou 'inactif'
            return statut.lower()  # Retourne 'actif' ou 'inactif'
    except Exception as e:
        print(f"[Erreur DB] {e}")
        return "erreur"
