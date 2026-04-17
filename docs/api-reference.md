# API Reference

## `django_sabia_auth.client`

### `SabiaOAuth2Client`

Handles the OAuth2 authorization code flow.

```python
SabiaOAuth2Client(client_id, client_secret, redirect_uri, scopes=None, base_url=None)
```

#### Methods

- `get_authorization_url(state)` → `str`
  Returns the full authorization URL to redirect the user to.

- `exchange_code_for_token(code, timeout=30)` → `dict`
  Exchanges an authorization code for an access token dict. Raises `SabiaTokenError` on failure.

- `get_user_info(access_token, timeout=30)` → `dict`
  Fetches the user's profile. Raises `SabiaUserInfoError` on failure.

### `SabiaAPIClient`

Handles the Sabiá user management API.

```python
SabiaAPIClient(client_id, base_url=None)
```

#### Methods

- `get_user(cpf_or_email, timeout=30)` → `dict | None`
  Returns user dict on 200, `None` on 404, raises `SabiaAPIError` on 403.

- `list_users(cpfs, page=1, timeout=30)` → `list`
  Returns a list of user dicts.

- `create_user(cpf, email, nome, genero, data_de_nascimento, timeout=30)` → `(bool, dict)`
  Returns `(True, data)` on 201, `(False, data)` on 200.

## `django_sabia_auth.backends`

### `SabiaAuthBackend`

Django authentication backend.

- `authenticate(request, sabia_user_info=None, **kwargs)` → `User | None`
- `get_user(user_id)` → `User | None`

## `django_sabia_auth.utils`

- `get_sabia_settings()` → `dict`
- `get_oauth2_client()` → `SabiaOAuth2Client`
- `get_api_client()` → `SabiaAPIClient`
- `generate_state()` → `str`

## `django_sabia_auth.exceptions`

- `SabiaAuthError` — base exception
- `SabiaTokenError` — token exchange failed
- `SabiaUserInfoError` — user info fetch failed
- `SabiaAPIError(status_code=None)` — API error
- `SabiaStateMismatchError` — CSRF state mismatch
