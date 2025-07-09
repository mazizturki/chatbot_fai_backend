import random
import asyncio

async def run_speedtest(numligne: str) -> dict:
    """
    Simule un test de vitesse asynchrone.
    En vrai, tu peux appeler une API externe ou déclencher un test client.
    Ici on retourne un débit mesuré aléatoire et un débit attendu fictif.
    """
    await asyncio.sleep(2)  # simule délai test
    # Simuler des valeurs
    debit_attendu = 50.0  # Mbps attendu en base, tu peux charger depuis ta BDD via numligne
    download_mesure = random.uniform(20.0, 60.0)  # Mbps mesuré aléatoire
    
    return {
        "download": download_mesure,
        "debit_attendu": debit_attendu
    }
