"""
Configuration de l'application wallets de MCWallet.

Cette application gère les comptes multi-devises
des utilisateurs de la plateforme.
"""

from django.apps import AppConfig


class WalletsConfig(AppConfig):
    """
    Configuration de l'application wallets.
    """

    default_auto_field = "django.db.models.BigAutoField"

    # Chemin Python réel de l'application.
    name = "apps.wallets"

    # Label interne utilisé par Django.
    label = "wallets"

    # Nom affiché notamment dans Django Admin.
    verbose_name = "Portefeuilles"


    def ready(self):
        import apps.wallets.signals