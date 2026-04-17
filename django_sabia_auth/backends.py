from django.contrib.auth import get_user_model


class SabiaAuthBackend:
    """
    Django authentication backend for Sabiá OAuth2.

    Looks up or creates a Django user based on the profile info returned by Sabiá.
    The CPF is used as the Django username.
    """

    def authenticate(self, request, sabia_user_info=None, **kwargs):
        if sabia_user_info is None:
            return None

        User = get_user_model()
        cpf = sabia_user_info.get("cpf")
        if not cpf:
            return None

        email = sabia_user_info.get("email", "")
        name = sabia_user_info.get("name", "")
        name_parts = name.split(" ", 1)
        first_name = name_parts[0] if name_parts else ""
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user, created = User.objects.get_or_create(
            username=cpf,
            defaults={
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "is_active": True,
            },
        )

        if not created:
            changed = False
            if user.email != email:
                user.email = email
                changed = True
            if user.first_name != first_name:
                user.first_name = first_name
                changed = True
            if user.last_name != last_name:
                user.last_name = last_name
                changed = True
            if not user.is_active:
                user.is_active = True
                changed = True
            if changed:
                user.save()

        return user

    def get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
