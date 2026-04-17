from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseBadRequest, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from urllib.parse import urlsplit

from .exceptions import SabiaStateMismatchError, SabiaTokenError, SabiaUserInfoError
from .utils import generate_state, get_oauth2_client


class SabiaLoginView(View):
    """Initiates the Sabiá OAuth2 authorization code flow."""

    def get(self, request):
        client = get_oauth2_client()
        state = generate_state()
        request.session["sabia_oauth2_state"] = state
        authorization_url = client.get_authorization_url(state)
        return redirect(authorization_url)


class SabiaCallbackView(View):
    """Handles the OAuth2 callback from Sabiá."""

    def get(self, request):
        from django.conf import settings

        error = request.GET.get("error")
        if error:
            messages.error(request, f"Sabiá login error: {error}")
            return redirect(settings.LOGIN_URL)

        try:
            received_state = request.GET.get("state", "")
            stored_state = request.session.pop("sabia_oauth2_state", None)
            if not stored_state or received_state != stored_state:
                raise SabiaStateMismatchError("OAuth2 state mismatch — possible CSRF attack.")

            code = request.GET.get("code")
            client = get_oauth2_client()
            token_data = client.exchange_code_for_token(code)
            access_token = token_data.get("access_token")
            user_info = client.get_user_info(access_token)

            user = authenticate(request, sabia_user_info=user_info)
            if user is not None:
                login(request, user, backend="django_sabia_auth.backends.SabiaAuthBackend")
                next_url = request.GET.get("next", "")
                safe_next_url = next_url.replace("\\", "")
                parsed_next = urlsplit(safe_next_url)
                if (
                    safe_next_url
                    and safe_next_url.startswith("/")
                    and not parsed_next.scheme
                    and not parsed_next.netloc
                    and url_has_allowed_host_and_scheme(
                        url=safe_next_url,
                        allowed_hosts={request.get_host()},
                        require_https=request.is_secure(),
                    )
                ):
                    return HttpResponseRedirect(safe_next_url)
                return redirect(settings.LOGIN_REDIRECT_URL)
            else:
                messages.error(request, "Authentication failed. Please try again.")
                return redirect(settings.LOGIN_URL)

        except SabiaStateMismatchError:
            messages.error(request, "Security check failed. Please try logging in again.")
            return redirect(settings.LOGIN_URL)
        except SabiaTokenError:
            messages.error(request, "Failed to complete login. Please try again.")
            return redirect(settings.LOGIN_URL)
        except SabiaUserInfoError:
            messages.error(request, "Failed to retrieve your profile. Please try again.")
            return redirect(settings.LOGIN_URL)
