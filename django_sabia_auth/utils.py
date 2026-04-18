import secrets

from django.core.exceptions import ImproperlyConfigured

# Default mapping: user model field → Sabiá response key.
# A tuple key means "split the Sabiá value on the first space and assign
# the first part to key[0] and the remainder to key[1]".
DEFAULT_USER_ATTR_MAP = {
    "username": "cpf",
    "email": "email",
    ("first_name", "last_name"): "name",
}


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
        "user_lookup_field": getattr(settings, "SABIA_USER_LOOKUP_FIELD", "username"),
        "user_attr_map": getattr(settings, "SABIA_USER_ATTR_MAP", DEFAULT_USER_ATTR_MAP),
    }


def _extract_nested(data, dotted_key):
    """Extract a value from a (possibly nested) dict using a dotted key path.

    Example: _extract_nested(data, "receita_federal.dtNascimento")
    """
    keys = dotted_key.split(".")
    value = data
    for key in keys:
        if not isinstance(value, dict):
            return None
        value = value.get(key)
        if value is None:
            return None
    return value


def apply_user_attr_map(user_info, attr_map):
    """Translate a Sabiá user_info dict into a flat dict of user model field→value pairs.

    The ``attr_map`` uses the convention ``{model_field: sabia_key}``:

    - **Plain string key**: maps the Sabiá field to the given user model field.
    - **Tuple key** ``(field_a, field_b)``: splits the Sabiá value on the first space;
      the part before the space goes to ``field_a`` and everything after to ``field_b``.
    - **Dotted Sabiá key** (e.g. ``"receita_federal.dtNascimento"``): traverses nested
      dicts in the Sabiá response.
    - Special key ``"fulljson"``: maps the entire raw Sabiá response dict to the field.
      Suitable for a ``JSONField`` or any field that accepts a dict.
    - If the Sabiá value is ``None``, absent, or an error dict, the field is skipped.
    """
    result = {}
    for model_field, sabia_key in attr_map.items():
        if sabia_key == "fulljson":
            result[model_field] = user_info
            continue
        value = _extract_nested(user_info, sabia_key)
        if value is None:
            continue
        # If the extracted value is a dict with an error, skip it.
        if isinstance(value, dict) and "erro" in value:
            continue
        if isinstance(model_field, (list, tuple)) and len(model_field) == 2:
            field_a, field_b = model_field
            parts = str(value).split(" ", 1)
            result[field_a] = parts[0]
            result[field_b] = parts[1] if len(parts) > 1 else ""
        else:
            result[model_field] = value
    return result


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
