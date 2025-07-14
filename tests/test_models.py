import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.models.models import Reclamation
from app.models.models import LigneTelephonique
from datetime import datetime

# Base temporaire SQLite en mémoire
DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

def test_reclamation_model(db_session):
    # Créer d'abord une ligne téléphonique (clé étrangère)
    ligne = LigneTelephonique(
        num_ligne="74120253",
        id_client="C/2025/000001",
        debit_internet="10Mbps",
        etat="active",
    )
    db_session.add(ligne)
    db_session.commit()

    # Créer une réclamation associée
    reclamation = Reclamation(
        id_reclamation="R/2025/000001",
        num_ligne="74120253",
        date_reclamation=datetime(2025, 7, 9, 15, 0, 0),
        type_probleme="lenteur",
        etat="en attente",
        num_tel="22345678",
        marque_modem="ZTE"
    )
    db_session.add(reclamation)
    db_session.commit()

    # Vérification
    result = db_session.query(Reclamation).filter_by(id_reclamation="R/2025/000001").first()
    assert result is not None
    assert result.num_ligne == "74120253"
    assert result.type_probleme == "lenteur"
    assert result.etat == "en attente"
    assert result.marque_modem == "ZTE"
    assert result.num_tel == "22345678"