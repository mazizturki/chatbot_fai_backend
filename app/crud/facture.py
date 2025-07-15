from sqlalchemy.orm import Session
from app.models.models import Facture

# 🔍 Récupérer une facture par numéro de ligne
def get_facture(db: Session, num: str) -> Facture | None:
    return db.query(Facture).filter_by(num_ligne=num).first()

# ❓ Vérifie si la facture existe
def facture_exists(db: Session, num: str) -> bool:
    return get_facture(db, num) is not None

# ✅ Vérifie si la facture est payée
def facture_paye(db: Session, num: str) -> bool:
    facture = get_facture(db, num)
    return facture is not None and facture.statut_paiement.lower() == "payée"

def nbr_factures(db: Session, num: str) -> int:
    return db.query(Facture).filter_by(num_ligne=num).count()

# 🔁 Retourne toutes les factures associées à un numéro de ligne
def get_factures(db: Session, num: str) -> list[Facture]:
    return db.query(Facture).filter_by(num_ligne=num).all()

def somme_montant_factures(db: Session, num: str) -> float:
    factures = get_factures(db, num)
    return sum(facture.montant for facture in factures if facture.montant is not None)