from unittest.mock import MagicMock

import pymysql
import pytest

import app as backend_app


def faux_connexion(ligne):
    """Fausse connexion dont le curseur renvoie `ligne` pour fetchone()."""
    curseur = MagicMock()
    curseur.fetchone.return_value = ligne
    connexion = MagicMock()
    connexion.cursor.return_value.__enter__.return_value = curseur
    return connexion, curseur


def test_nom_manquant(client):
    reponse = client.put("/files/1", json={})

    assert reponse.status_code == 400
    assert reponse.get_json() == {"error": "Missing filename"}


def test_fichier_introuvable(client, monkeypatch):
    connexion, _ = faux_connexion(None)
    monkeypatch.setattr(backend_app, "get_connection", lambda: connexion)

    reponse = client.put("/files/99", json={"filename": "bilan"})

    assert reponse.status_code == 404
    assert reponse.get_json() == {"error": "File not found"}
    connexion.close.assert_called_once()
    connexion.commit.assert_not_called()


@pytest.mark.parametrize(
    "ancien, saisi, attendu",
    [
        ("rapport.pdf", "bilan", "bilan.pdf"),         # extension réinjectée
        ("rapport.pdf", "bilan.docx", "bilan.docx"),   # extension fournie: on la garde
        ("notes", "memo", "memo"),                     # ancien nom sans extension
    ],
)
def test_renommage_et_extension(client, monkeypatch, ancien, saisi, attendu):
    connexion, curseur = faux_connexion((ancien,))
    monkeypatch.setattr(backend_app, "get_connection", lambda: connexion)

    reponse = client.put("/files/7", json={"filename": saisi})

    assert reponse.status_code == 200
    assert reponse.get_json() == {"success": True, "id": 7, "new_filename": attendu}
    # Le 2e appel à execute() est le UPDATE: on vérifie les valeurs envoyées à la base
    requete_update = curseur.execute.call_args_list[1]
    assert requete_update[0][1] == (attendu, 7)
    connexion.commit.assert_called_once()


def test_erreur_base_de_donnees(client, monkeypatch):
    def connexion_en_echec():
        raise pymysql.MySQLError("base indisponible")

    monkeypatch.setattr(backend_app, "get_connection", connexion_en_echec)

    reponse = client.put("/files/1", json={"filename": "bilan"})

    assert reponse.status_code == 500
    assert reponse.get_json() == {"error": "Database error"}
