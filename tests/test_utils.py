import pytest
from django.core.exceptions import ImproperlyConfigured

from django_sabia_auth.utils import generate_state, get_sabia_settings


def test_get_sabia_settings_returns_dict():
    cfg = get_sabia_settings()
    assert cfg["client_id"] == "test-client-id"
    assert cfg["client_secret"] == "test-client-secret"
    assert cfg["redirect_uri"] == "http://localhost:8000/auth/sabia/callback/"
    assert cfg["scopes"] == ["cpf", "email"]
    assert cfg["base_url"] == "https://login.sabia.ufrn.br"
    assert cfg["api_url"] == "https://api.sabia.ufrn.br"


def test_get_sabia_settings_raises_on_missing(settings):
    del settings.SABIA_CLIENT_ID
    with pytest.raises(ImproperlyConfigured):
        get_sabia_settings()


def test_generate_state_returns_string():
    state = generate_state()
    assert isinstance(state, str)
    assert len(state) > 20


def test_generate_state_is_unique():
    states = {generate_state() for _ in range(10)}
    assert len(states) == 10
