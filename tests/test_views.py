from unittest.mock import MagicMock, patch

import pytest
from django.test import Client, RequestFactory


@pytest.fixture
def client():
    return Client()


@pytest.mark.django_db
def test_login_view_redirects_to_sabia(client):
    response = client.get("/auth/sabia/login/")
    assert response.status_code == 302
    assert "login.sabia.ufrn.br" in response["Location"]


@pytest.mark.django_db
def test_login_view_stores_state_in_session(client):
    response = client.get("/auth/sabia/login/")
    assert response.status_code == 302
    assert "sabia_oauth2_state" in client.session


@pytest.mark.django_db
def test_callback_view_handles_error_param(client):
    response = client.get("/auth/sabia/callback/?error=access_denied")
    assert response.status_code == 302
    assert response["Location"] == "/login/"


@pytest.mark.django_db
def test_callback_view_handles_state_mismatch(client):
    session = client.session
    session["sabia_oauth2_state"] = "correct-state"
    session.save()

    response = client.get("/auth/sabia/callback/?code=abc&state=wrong-state")
    assert response.status_code == 302
    assert response["Location"] == "/login/"


@pytest.mark.django_db
@patch("django_sabia_auth.views.get_oauth2_client")
@patch("django_sabia_auth.views.authenticate")
@patch("django_sabia_auth.views.login")
def test_callback_view_logs_in_user(mock_login, mock_auth, mock_get_client, client):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="12345678901", email="test@example.com")

    mock_oauth = MagicMock()
    mock_oauth.exchange_code_for_token.return_value = {"access_token": "tok123"}
    mock_oauth.get_user_info.return_value = {
        "cpf": "12345678901",
        "name": "Test User",
        "email": "test@example.com",
    }
    mock_get_client.return_value = mock_oauth
    mock_auth.return_value = user

    session = client.session
    session["sabia_oauth2_state"] = "valid-state"
    session.save()

    response = client.get("/auth/sabia/callback/?code=auth-code&state=valid-state")
    assert response.status_code == 302
    assert response["Location"] == "/dashboard/"
    mock_login.assert_called_once()


@pytest.mark.django_db
@patch("django_sabia_auth.views.get_oauth2_client")
def test_callback_view_handles_token_error(mock_get_client, client):
    from django_sabia_auth.exceptions import SabiaTokenError

    mock_oauth = MagicMock()
    mock_oauth.exchange_code_for_token.side_effect = SabiaTokenError("Token failed")
    mock_get_client.return_value = mock_oauth

    session = client.session
    session["sabia_oauth2_state"] = "valid-state"
    session.save()

    response = client.get("/auth/sabia/callback/?code=bad-code&state=valid-state")
    assert response.status_code == 302
    assert response["Location"] == "/login/"


@pytest.mark.django_db
@patch("django_sabia_auth.views.get_oauth2_client")
@patch("django_sabia_auth.views.authenticate")
@patch("django_sabia_auth.views.login")
def test_callback_view_authenticate_returns_none(mock_login, mock_auth, mock_get_client, client):
    mock_oauth = MagicMock()
    mock_oauth.exchange_code_for_token.return_value = {"access_token": "tok"}
    mock_oauth.get_user_info.return_value = {"cpf": "12345678901"}
    mock_get_client.return_value = mock_oauth
    mock_auth.return_value = None

    session = client.session
    session["sabia_oauth2_state"] = "valid-state"
    session.save()

    response = client.get("/auth/sabia/callback/?code=code&state=valid-state")
    assert response.status_code == 302
    assert response["Location"] == "/login/"
    mock_login.assert_not_called()


@pytest.mark.django_db
@patch("django_sabia_auth.views.get_oauth2_client")
def test_callback_view_handles_user_info_error(mock_get_client, client):
    from django_sabia_auth.exceptions import SabiaUserInfoError

    mock_oauth = MagicMock()
    mock_oauth.exchange_code_for_token.return_value = {"access_token": "tok"}
    mock_oauth.get_user_info.side_effect = SabiaUserInfoError("Failed")
    mock_get_client.return_value = mock_oauth

    session = client.session
    session["sabia_oauth2_state"] = "valid-state"
    session.save()

    response = client.get("/auth/sabia/callback/?code=code&state=valid-state")
    assert response.status_code == 302
    assert response["Location"] == "/login/"


@pytest.mark.django_db
@patch("django_sabia_auth.views.get_oauth2_client")
@patch("django_sabia_auth.views.authenticate")
@patch("django_sabia_auth.views.login")
def test_callback_view_redirects_to_safe_next_url(mock_login, mock_auth, mock_get_client, client):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username="12345678901", email="test@example.com")

    mock_oauth = MagicMock()
    mock_oauth.exchange_code_for_token.return_value = {"access_token": "tok"}
    mock_oauth.get_user_info.return_value = {"cpf": "12345678901"}
    mock_get_client.return_value = mock_oauth
    mock_auth.return_value = user

    session = client.session
    session["sabia_oauth2_state"] = "valid-state"
    session.save()

    response = client.get("/auth/sabia/callback/?code=code&state=valid-state&next=/dashboard/")
    assert response.status_code == 302
    assert response["Location"] == "/dashboard/"
