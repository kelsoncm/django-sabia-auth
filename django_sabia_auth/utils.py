import secrets

from django.core.exceptions import ImproperlyConfigured


def get_sabia_settings():
    """Read and validate Sabiá settings from Django settings."""
    from django.conf import settings

    client_id = getattr(settings, "SABIA_CLIENT_ID", None)
    client_secret = getattr(settings, "SABIA_CLIENT_SECRET", None)
    redirect_uri = getattr(settings, "SABIA_REDIRECT_URI", None)

    missing = []
    if not client_id:
        missing.append("SABIA_CLIENT_ID")
    if not client_secret:
        missing.append("SABIA_CLIENT_SECRET")
    if not redirect_uri:
        missing.append("SABIA_REDIRECT_URI")

    if missing:
        raise ImproperlyConfigured(f"Missing required Sabiá settings: {', '.join(missing)}")

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "scopes": getattr(settings, "SABIA_SCOPES", ["cpf", "email"]),
        "base_url": getattr(settings, "SABIA_BASE_URL", "https://login.sabia.ufrn.br"),
        "api_url": getattr(settings, "SABIA_API_URL", "https://api.sabia.ufrn.br"),
    }


def get_oauth2_client():
    """Return a SabiaOAuth2Client configured from Django settings."""
    from .client import SabiaOAuth2Client

    cfg = get_sabia_settings()
    return SabiaOAuth2Client(
        client_id=cfg["client_id"],
        client_secret=cfg["client_secret"],
        redirect_uri=cfg["redirect_uri"],
        scopes=cfg["scopes"],
        base_url=cfg["base_url"],
    )


def get_api_client():
    """Return a SabiaAPIClient configured from Django settings."""
    from .client import SabiaAPIClient

    cfg = get_sabia_settings()
    return SabiaAPIClient(client_id=cfg["client_id"], base_url=cfg["api_url"])


def generate_state():
    """Generate a cryptographically secure random state token for OAuth2 CSRF protection."""
    return secrets.token_urlsafe(32)
