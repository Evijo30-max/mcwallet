from django.apps import AppConfig


class UsersConfig(AppConfig):
    """
    Configuration de l'application users de MCWallet.
    """

    default_auto_field = "django.db.models.BigAutoField"

    # Chemin Python réel de l'application.
    name = "apps.users"

    # Label interne utilisé par Django.
    label = "users"

    # Nom affiché notamment dans Django Admin.
    verbose_name = "Utilisateurs"