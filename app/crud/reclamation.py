from datetime import datetime
from sqlalchemy import func
from app.models.models import Reclamation
from sqlalchemy.orm import Session

def creer_reclamation(db: Session, numligne: str, numtel: str, probleme: str, etat: str = "en cours") -> Reclamation:
    current_year = datetime.now().year
    prefix = f"R/{current_year}/"

    count = db.query(func.count(Reclamation.id_reclamation)).filter(Reclamation.id_reclamation.like(f"{prefix}%")).scalar()
    id_genere = f"{prefix}{str(count + 1).zfill(6)}"

    # Vérification des paramètres
    reclamation = Reclamation(
        id_reclamation=id_genere,
        num_ligne=numligne,
        num_tel=numtel,
        date_reclamation=datetime.now(),
        type_probleme=probleme,
        etat=etat
    )

    db.add(reclamation)
    db.commit()
    #db.refresh(reclamation)
    return reclamation
