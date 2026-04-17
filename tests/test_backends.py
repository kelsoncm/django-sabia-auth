import pytest

from django_sabia_auth.backends import SabiaAuthBackend


@pytest.fixture
def backend():
    return SabiaAuthBackend()


@pytest.fixture
def sabia_user_info():
    return {
        "cpf": "98765432100",
        "name": "Maria Silva Santos",
        "email": "maria@example.com",
        "login": "mariasilva",
        "avatar": "https://example.com/avatar.png",
    }


@pytest.mark.django_db
def test_authenticate_creates_new_user(backend, sabia_user_info):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    assert not User.objects.filter(username="98765432100").exists()

    user = backend.authenticate(None, sabia_user_info=sabia_user_info)
    assert user is not None
    assert user.username == "98765432100"
    assert User.objects.filter(username="98765432100").exists()


@pytest.mark.django_db
def test_authenticate_returns_existing_user(backend, sabia_user_info):
    from django.contrib.auth import get_user_model
    User = get_user_model()
    existing = User.objects.create_user(username="98765432100", email="old@example.com")

    user = backend.authenticate(None, sabia_user_info=sabia_user_info)
    assert user is not None
    assert user.pk == existing.pk


@pytest.mark.django_db
def test_authenticate_returns_none_when_no_info(backend):
    user = backend.authenticate(None, sabia_user_info=None)
    assert user is None


@pytest.mark.django_db
def test_user_fields_mapped_correctly(backend, sabia_user_info):
    user = backend.authenticate(None, sabia_user_info=sabia_user_info)
    assert user.username == "98765432100"
    assert user.email == "maria@example.com"
    assert user.first_name == "Maria"
    assert user.last_name == "Silva Santos"
    assert user.is_active is True


@pytest.mark.django_db
def test_get_user_returns_user(backend, sabia_user_info):
    user = backend.authenticate(None, sabia_user_info=sabia_user_info)
    fetched = backend.get_user(user.pk)
    assert fetched.pk == user.pk


@pytest.mark.django_db
def test_get_user_returns_none_for_invalid_id(backend):
    result = backend.get_user(999999)
    assert result is None
