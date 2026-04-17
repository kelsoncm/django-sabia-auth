# Configuration

## Required Settings

| Setting | Description |
|---------|-------------|
| `SABIA_CLIENT_ID` | Your OAuth2 client ID from Sabiá |
| `SABIA_CLIENT_SECRET` | Your OAuth2 client secret from Sabiá |
| `SABIA_REDIRECT_URI` | The callback URL registered with Sabiá |

## Optional Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `SABIA_SCOPES` | `["cpf", "email"]` | OAuth2 scopes to request |
| `SABIA_BASE_URL` | `https://login.sabia.ufrn.br` | Sabiá OAuth2 base URL |
| `SABIA_API_URL` | `https://api.sabia.ufrn.br` | Sabiá user management API base URL |

## Authentication Backend

```python
AUTHENTICATION_BACKENDS = [
    "django_sabia_auth.backends.SabiaAuthBackend",
    "django.contrib.auth.backends.ModelBackend",  # optional, for admin
]
```

## Example

```python
SABIA_CLIENT_ID = "my-client-id"
SABIA_CLIENT_SECRET = "my-client-secret"
SABIA_REDIRECT_URI = "https://myapp.com/auth/sabia/callback/"
SABIA_SCOPES = ["cpf", "email"]
LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/login/"
```
