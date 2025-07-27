from unittest import result
import pytest
from sqlalchemy.orm import Session
from app.services.Diagnostique import diagnostic_probleme
from app.core.session_memory import store_param

@pytest.mark.asyncio
async def test_diagnostic_lenteur(monkeypatch: pytest.MonkeyPatch):
    session_id = "test-session"
    db = None  

    store_param(session_id, "TypeProbleme", "lenteur")
    store_param(session_id, "numligne", "74120253")
    store_param(session_id, "numtel", "12345678")
    store_param(session_id, "marque_modem", "zte")

    async def fake_speedtest(numligne, db):
        return {
            "download": 1.5,
            "upload": 0.5,
            "ping": 110,
            "debit_attendu": 10
        }

    monkeypatch.setattr("app.services.Diagnostique.run_speedtest", fake_speedtest)

    result = await diagnostic_probleme(session_id, db)
    assert "fulfillmentText" in result
    assert "le débit est en dessous des attentes" in result["fulfillmentText"].lower()
    assert result["endConversation"] is True