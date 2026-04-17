import pytest
import responses as rsps_lib

from django_sabia_auth.client import SabiaAPIClient, SabiaOAuth2Client
from django_sabia_auth.exceptions import SabiaAPIError, SabiaTokenError, SabiaUserInfoError

CLIENT_ID = "test-client-id"
CLIENT_SECRET = "test-secret"
REDIRECT_URI = "http://localhost/callback/"
BASE_URL = "https://login.sabia.ufrn.br"
API_URL = "https://api.sabia.ufrn.br"


@pytest.fixture
def oauth_client():
    return SabiaOAuth2Client(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scopes=["cpf", "email"],
        base_url=BASE_URL,
    )


@pytest.fixture
def api_client():
    return SabiaAPIClient(client_id=CLIENT_ID, base_url=API_URL)


# --- SabiaOAuth2Client tests ---


def test_get_authorization_url(oauth_client):
    url = oauth_client.get_authorization_url("my-state-123")
    assert "https://login.sabia.ufrn.br/oauth/authorize/" in url
    assert "state=my-state-123" in url
    assert f"client_id={CLIENT_ID}" in url
    assert "response_type=code" in url


@rsps_lib.activate
def test_exchange_code_for_token_success(oauth_client):
    rsps_lib.add(
        rsps_lib.POST,
        f"{BASE_URL}/oauth/token/",
        json={"access_token": "tok123", "token_type": "Bearer"},
        status=200,
    )
    result = oauth_client.exchange_code_for_token("auth-code-abc")
    assert result["access_token"] == "tok123"


@rsps_lib.activate
def test_exchange_code_for_token_raises_on_error(oauth_client):
    rsps_lib.add(rsps_lib.POST, f"{BASE_URL}/oauth/token/", json={"error": "invalid_grant"}, status=400)
    with pytest.raises(SabiaTokenError):
        oauth_client.exchange_code_for_token("bad-code")


@rsps_lib.activate
def test_get_user_info_success(oauth_client):
    rsps_lib.add(
        rsps_lib.POST,
        f"{BASE_URL}/api/perfil/dados/",
        json={"cpf": "12345678901", "name": "Test User", "email": "test@example.com"},
        status=200,
    )
    result = oauth_client.get_user_info("tok123")
    assert result["cpf"] == "12345678901"
    assert result["email"] == "test@example.com"


@rsps_lib.activate
def test_get_user_info_raises_on_error(oauth_client):
    rsps_lib.add(rsps_lib.POST, f"{BASE_URL}/api/perfil/dados/", json={"error": "unauthorized"}, status=401)
    with pytest.raises(SabiaUserInfoError):
        oauth_client.get_user_info("bad-token")


# --- SabiaAPIClient tests ---


@rsps_lib.activate
def test_api_get_user_returns_user(api_client):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/usuarios/12345678901/",
        json={"cpf": "12345678901", "email": "user@example.com"},
        status=200,
    )
    result = api_client.get_user("12345678901")
    assert result["cpf"] == "12345678901"


@rsps_lib.activate
def test_api_get_user_returns_none_on_404(api_client):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/usuarios/00000000000/", json={}, status=404)
    result = api_client.get_user("00000000000")
    assert result is None


@rsps_lib.activate
def test_api_get_user_raises_on_403(api_client):
    rsps_lib.add(rsps_lib.GET, f"{API_URL}/usuarios/12345678901/", json={"detail": "forbidden"}, status=403)
    with pytest.raises(SabiaAPIError) as exc_info:
        api_client.get_user("12345678901")
    assert exc_info.value.status_code == 403


@rsps_lib.activate
def test_api_list_users(api_client):
    rsps_lib.add(
        rsps_lib.GET,
        f"{API_URL}/usuarios/",
        json=[{"cpf": "11111111111"}, {"cpf": "22222222222"}],
        status=200,
    )
    result = api_client.list_users(["11111111111", "22222222222"])
    assert len(result) == 2


@rsps_lib.activate
def test_api_create_user_returns_created_true(api_client):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/usuarios/",
        json={"cpf": "33333333333", "email": "new@example.com"},
        status=201,
    )
    created, data = api_client.create_user("33333333333", "new@example.com", "New User", "M", "1990-01-01")
    assert created is True
    assert data["cpf"] == "33333333333"


@rsps_lib.activate
def test_api_create_user_returns_created_false_on_200(api_client):
    rsps_lib.add(
        rsps_lib.POST,
        f"{API_URL}/usuarios/",
        json={"cpf": "33333333333", "email": "existing@example.com"},
        status=200,
    )
    created, data = api_client.create_user("33333333333", "existing@example.com", "Existing User", "F", "1985-05-20")
    assert created is False
