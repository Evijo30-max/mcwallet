"""
Backend d'authentification de MCWallet.

Permet à un utilisateur de se connecter avec :

- son adresse email ;
- OU son numéro de téléphone.

Le mot de passe reste géré par le système sécurisé
d'authentification de Django.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend


class EmailOrPhoneBackend(BaseBackend):
    """
    Authentifie un utilisateur avec son email ou son téléphone.

    Un utilisateur peut donc avoir :
    - uniquement un email ;
    - uniquement un téléphone ;
    - les deux.

    Le compte doit également être actif.
    """

    def authenticate(
        self,
        request,
        username=None,
        password=None,
        **kwargs,
    ):
        """
        Recherche l'utilisateur avec l'identifiant fourni.

        L'identifiant peut être :
        - une adresse email ;
        - un numéro de téléphone.
        """

        User = get_user_model()

        # ---------------------------------------------------------
        # Vérification des données reçues
        # ---------------------------------------------------------

        if not username or not password:
            return None

        identifier = username.strip()

        user = None

        # ---------------------------------------------------------
        # Tentative de connexion avec l'email
        # ---------------------------------------------------------

        if "@" in identifier:
            try:
                user = User.objects.get(
                    email__iexact=identifier
                )
            except User.DoesNotExist:
                return None

        # ---------------------------------------------------------
        # Tentative de connexion avec le téléphone
        # ---------------------------------------------------------

        else:
            try:
                user = User.objects.get(
                    telephone=identifier
                )
            except User.DoesNotExist:
                return None

        # ---------------------------------------------------------
        # Vérification du mot de passe
        # ---------------------------------------------------------

        if not user.check_password(password):
            return None

        # ---------------------------------------------------------
        # Vérification que le compte peut s'authentifier
        # ---------------------------------------------------------

        if not self.user_can_authenticate(user):
            return None

        return user

    def user_can_authenticate(self, user):
        """
        Vérifie si l'utilisateur est autorisé à se connecter.

        MCWallet utilise le champ personnalisé `actif`.

        Un utilisateur inactif ne peut pas se connecter.
        """

        # Un compte désactivé ne peut pas se connecter.
        if not user.actif:
            return False

        # Si le modèle possède également is_active,
        # on respecte sa valeur.
        if hasattr(user, "is_active"):
            return user.is_active

        return True

    def get_user(self, user_id):
        """
        Retourne un utilisateur à partir de son identifiant primaire.
        """

        User = get_user_model()

        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

        # L'utilisateur doit toujours pouvoir s'authentifier.
        if not self.user_can_authenticate(user):
            return None

        return user