import speedtest
from sqlalchemy.orm import Session
from app.models.models import LigneTelephonique

async def run_speedtest(numligne: str, db: Session) -> dict:
    try:
        print(f"[DEBUG] Lancement du speedtest pour la ligne {numligne}...")

        st = speedtest.Speedtest()
        st.get_best_server()

        download_bps = st.download()
        upload_bps = st.upload()
        ping = st.results.ping

        # Conversion en Mbps
        download_mbps = round(download_bps / 1_000_000, 2)
        upload_mbps = round(upload_bps / 1_000_000, 2)

        print(f"[DEBUG] Résultats speedtest - Download: {download_mbps} Mbps, Upload: {upload_mbps} Mbps, Ping: {ping} ms")

        debit_attendu = get_debit_attendu_par_ligne(db, numligne)

        return {
            "download": download_mbps,
            "upload": upload_mbps,
            "ping": round(ping, 0),
            "debit_attendu": debit_attendu
        }

    except Exception as e:
        print(f"[ERROR] Speedtest échoué : {e}")
        return None


def get_debit_attendu_par_ligne(db: Session, numligne: str) -> float:
    """
    Récupère le débit internet attendu d'une ligne téléphonique depuis la base de données.
    Retourne None si la ligne n'existe pas ou si le débit est inconnu.
    """
    ligne = db.query(LigneTelephonique).filter_by(num_ligne=numligne).first()
    if ligne and ligne.debit_internet:
        try:
            return float(''.join(filter(str.isdigit, ligne.debit_internet)))
        except ValueError:
            return None
    return None
