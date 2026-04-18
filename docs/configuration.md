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
| `SABIA_SCOPES` | `["cpf", "email"]` | OAuth2 scopes to request. See [Scopes](scopes.md) for all options. |
| `SABIA_BASE_URL` | `https://login.sabia.ufrn.br` | Sabiá OAuth2 base URL |
| `SABIA_API_URL` | `https://api.sabia.ufrn.br` | Sabiá user management API base URL |
| `SABIA_USER_LOOKUP_FIELD` | `"username"` | User model field used to look up/create users |
| `SABIA_USER_ATTR_MAP`     | see below | Maps Sabiá response keys to user model fields |

## Authentication Backend

```python
AUTHENTICATION_BACKENDS = [
    "django_sabia_auth.backends.SabiaAuthBackend",
    "django.contrib.auth.backends.ModelBackend",  # optional, for admin
]
```

## Basic Example

```python
SABIA_CLIENT_ID = "my-client-id"
SABIA_CLIENT_SECRET = "my-client-secret"
SABIA_REDIRECT_URI = "https://myapp.com/auth/sabia/callback/"
SABIA_SCOPES = ["cpf", "email"]
LOGIN_REDIRECT_URL = "/dashboard/"
LOGIN_URL = "/login/"
```

---

## User Model Mapping

### Default behavior

When using Django's default `User` model (no custom `AUTH_USER_MODEL`), the library works
out of the box. It looks up users by `username` (storing the CPF there) and maps:

| Sabiá field | User model field | Notes                       |
|-------------|------------------|-----------------------------|
| `cpf`       | `username`       | Used as the lookup key      |
| `email`     | `email`          |                             |
| `name`      | `first_name` + `last_name` | Split on the first space |

### Custom `AUTH_USER_MODEL`

If your user model has different field names or a `cpf` field instead of `username`,
configure `SABIA_USER_LOOKUP_FIELD` and `SABIA_USER_ATTR_MAP`.

**`SABIA_USER_LOOKUP_FIELD`** — the user model field used in `get_or_create` as the unique key.

**`SABIA_USER_ATTR_MAP`** — a dict with the convention `{model_field: sabia_key}`:

- **Plain string key**: maps the Sabiá field directly to the given user model field.
- **Tuple key** `("field_a", "field_b")`: splits the Sabiá value on the first space —
  the part before the space goes to `field_a`, everything after to `field_b`.
- **Dotted Sabiá value** (e.g. `"receita_federal.dtNascimento"`): navigates nested dicts
  in the Sabiá response. Works for `receita_federal`, which returns an object. Nested
  scopes that returned an error object are silently skipped.
- **`"fulljson"`**: maps the entire raw Sabiá response dict to the field. Useful for
  persisting data from list-based scopes (`cnes`, `experiencia_profissional`,
  `formacao_academica`, `cursos_cdp`) that do not support dot-notation.

### Example: model with a `cpf` field and a single `nome` field

```python
# myapp/models.py
class Usuario(AbstractBaseUser):
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField()
    nome = models.CharField(max_length=255)
    ...
    USERNAME_FIELD = "cpf"
```

```python
# settings.py
AUTH_USER_MODEL = "myapp.Usuario"

SABIA_USER_LOOKUP_FIELD = "cpf"
SABIA_USER_ATTR_MAP = {
    "cpf": "cpf",
    "email": "email",
    "nome": "name",          # store the full name in a single field
}
```

### Example: mapping fields from extended scopes

You can pull data from optional scopes (like `receita_federal`) directly into user model fields
using dotted Sabiá keys:

```python
# settings.py
SABIA_SCOPES = ["cpf", "email", "receita_federal"]

SABIA_USER_ATTR_MAP = {
    "username": "cpf",
    "email": "email",
    ("first_name", "last_name"): "name",
    # Pull birth date from the Receita Federal scope:
    "data_nascimento": "receita_federal.dtNascimento",
    "sexo": "receita_federal.sexo",
}
```

If the user's Receita Federal data is unavailable (not validated or an error response), those
fields are simply skipped — the user is still created with the remaining attributes.

### Example: saving the full Sabiá JSON response

Use the special `"fulljson"` value to store the entire raw payload returned by Sabiá into a
single field (e.g. a `JSONField`). This is the recommended approach for list-based scopes such
as `cnes`, `experiencia_profissional`, `formacao_academica`, and `cursos_cdp`, which do not
support dot-notation.

```python
# myapp/models.py
class Usuario(AbstractBaseUser):
    cpf = models.CharField(max_length=11, unique=True)
    email = models.EmailField()
    perfil_json = models.JSONField(default=dict, blank=True)
    ...
    USERNAME_FIELD = "cpf"
```

```python
# settings.py
SABIA_SCOPES = ["cpf", "email", "cnes", "experiencia_profissional"]

SABIA_USER_ATTR_MAP = {
    "cpf":        "cpf",
    "email":      "email",
    "perfil_json": "fulljson",   # entire Sabiá payload, including all requested scopes
}
```

### Example: minimal model (e-mail as identifier)

```python
SABIA_USER_LOOKUP_FIELD = "email"
SABIA_USER_ATTR_MAP = {
    "email": "email",
    "cpf": "cpf",
    ("first_name", "last_name"): "name",
}
```
