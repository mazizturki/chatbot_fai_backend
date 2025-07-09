from sqlalchemy.orm import Session
from app.models.models import LigneTelephonique

# 🔍 Récupérer une ligne par numéro
def get_ligne(db: Session, num: str) -> LigneTelephonique | None:
    return db.query(LigneTelephonique).filter_by(num_ligne=num).first()

# ❓ Vérifie si la ligne existe
def ligne_exists(db: Session, num: str) -> bool:
    return get_ligne(db, num) is not None

# ✅ Vérifie si la ligne est active
def ligne_actif(db: Session, num: str) -> bool:
    ligne = get_ligne(db, num)
    return ligne is not None and ligne.etat.lower() == "actif"

# 🔁 Retourne le statut en clair : "actif" / "inactif" / "inexistant"
def verifier_statut_ligne(db: Session, num: str) -> str:
    ligne = get_ligne(db, num)
    if not ligne:
        return "inexistant"
    return ligne.etat.lower()

def get_debit_attendu(db: Session, num: str) -> float | None:
    ligne = get_ligne(db, num)
    if ligne:
        return ligne.debit_internet
    return None