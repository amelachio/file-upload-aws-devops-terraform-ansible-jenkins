from datetime import datetime
from unittest.mock import MagicMock

import pymysql

import app as backend_app


def faux_connexion(lignes):
    """Construit une fausse connexion dont le curseur renvoie `lignes`."""
    curseur = MagicMock()
    curseur.fetchall.return_value = lignes
    connexion = MagicMock()
    # app.py fait: with connection.cursor() as cursor
    # Le "with" appelle __enter__(), donc on règle ce qu'il renvoie.
    connexion.cursor.return_value.__enter__.return_value = curseur
    return connexion, curseur


def test_liste_fichiers(client, monkeypatch):
    date = datetime(2026, 10, 25, 21, 30, 0)
    lignes = [
        (1, "rapport.pdf", "abc-rapport.pdf", "application/pdf", date),
        (2, "photo.png", "def-photo.png", "image/png", date),
    ]
    connexion, curseur = faux_connexion(lignes)
    monkeypatch.setattr(backend_app, "get_connection", lambda: connexion)

    reponse = client.get("/files")

    assert reponse.status_code == 200
    fichiers = reponse.get_json()["files"]
    assert len(fichiers) == 2
    assert fichiers[0] == {
        "id": 1,
        "filename": "rapport.pdf",
        "url": f"https://{backend_app.CLOUDFRONT_DOMAIN}/abc-rapport.pdf",
        "file_type": "application/pdf",
        "uploaded_at": "2026-10-25T21:30:00",
    }
    assert "FROM files" in curseur.execute.call_args[0][0]
    connexion.close.assert_called_once()


def test_liste_vide(client, monkeypatch):
    connexion, _ = faux_connexion([])
    monkeypatch.setattr(backend_app, "get_connection", lambda: connexion)

    reponse = client.get("/files")

    assert reponse.status_code == 200
    assert reponse.get_json() == {"files": []}


def test_erreur_base_de_donnees(client, monkeypatch):
    def connexion_en_echec():
        raise pymysql.MySQLError("base indisponible")

    monkeypatch.setattr(backend_app, "get_connection", connexion_en_echec)

    reponse = client.get("/files")

    assert reponse.status_code == 500
    assert reponse.get_json() == {"error": "Database error"}