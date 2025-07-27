from datetime import datetime
from typing import Optional
from sqlalchemy import func
from app.models.models import Reclamation
from sqlalchemy.orm import Session

def creer_reclamation(db: Session, numligne: str, numtel: str, probleme: str, etat: str = "en cours", marque_modem: Optional[str] = None) -> Reclamation:
    current_year = datetime.now().year
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    reclamation = Reclamation(
        num_ligne=numligne,
        num_tel=numtel,
        date_reclamation=date_str,
        type_probleme=probleme,
        etat=etat,
        marque_modem=marque_modem
    )

    db.add(reclamation)
    db.commit()
    db.refresh(reclamation)
    print(reclamation.id_reclamation)
    return reclamation
