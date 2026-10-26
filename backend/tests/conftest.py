import os
import sys
import types

import pytest

# Le vrai config.py n'existe que sur les serveurs (il est dans .gitignore).
# On le remplace par un faux module AVANT d'importer app.py.
fake_config = types.ModuleType("config")
fake_config.DB_HOST = "localhost"
fake_config.DB_USER = "test"
fake_config.DB_PASSWORD = "test"
fake_config.DB_NAME = "test"
fake_config.S3_BUCKET = "test-bucket"
fake_config.S3_REGION = "ca-central-1"
sys.modules["config"] = fake_config

# Permet d'importer backend/app.py depuis le dossier tests/
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


@pytest.fixture
def client():
    import app as backend_app
    backend_app.app.config["TESTING"] = True
    return backend_app.app.test_client()
