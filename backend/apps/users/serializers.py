"""
Serializers de l'application users de MCWallet.

Ce fichier contient la logique de validation des données
échangées entre le frontend et l'API REST.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers


# Récupération du modèle User configuré dans AUTH_USER_MODEL.
User = get_user_model()


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer utilisé lors de la création d'un compte client.

    L'utilisateur peut fournir :
    - uniquement un email ;
    - uniquement un téléphone ;
    - ou les deux.

    Mais au moins l'un des deux doit être fourni.
    """

    # ---------------------------------------------------------
    # MOT DE PASSE
    # ---------------------------------------------------------

    password = serializers.CharField(
        write_only=True,
        required=True,
        min_length=8,
        style={"input_type": "password"},
    )

    password_confirmation = serializers.CharField(
        write_only=True,
        required=True,
        style={"input_type": "password"},
    )

    # ---------------------------------------------------------
    # CONFIGURATION DU SERIALIZER
    # ---------------------------------------------------------

    class Meta:
        model = User

        fields = (
            "id",
            "email",
            "telephone",
            "prenom",
            "nom",
            "password",
            "password_confirmation",
        )

        read_only_fields = (
            "id",
        )

        extra_kwargs = {
            "email": {
                "required": False,
                "allow_null": True,
                "allow_blank": True,
            },
            "telephone": {
                "required": False,
                "allow_null": True,
            },
        }

    # ---------------------------------------------------------
    # VALIDATION EMAIL
    # ---------------------------------------------------------

    def validate_email(self, value):
        """
        Vérifie que l'adresse email n'est pas déjà utilisée.
        """

        if not value:
            return None

        # Normalisation de l'adresse email.
        value = User.objects.normalize_email(value)

        # Vérification de l'unicité.
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError(
                "Cette adresse email est déjà utilisée."
            )

        return value

    # ---------------------------------------------------------
    # VALIDATION TÉLÉPHONE
    # ---------------------------------------------------------

    def validate_telephone(self, value):
        """
        Vérifie que le numéro de téléphone n'est pas déjà utilisé.

        django-phonenumber-field se charge déjà de valider
        le format du numéro.
        """

        if not value:
            return None

        if User.objects.filter(telephone=value).exists():
            raise serializers.ValidationError(
                "Ce numéro de téléphone est déjà utilisé."
            )

        return value

    # ---------------------------------------------------------
    # VALIDATION GLOBALE
    # ---------------------------------------------------------

    def validate(self, attrs):
        """
        Validation globale de l'inscription.

        Vérifie :

        1. qu'un email ou un téléphone est fourni ;
        2. que les deux mots de passe correspondent ;
        3. que le mot de passe respecte les validateurs Django.
        """

        email = attrs.get("email")
        telephone = attrs.get("telephone")

        password = attrs.get("password")
        password_confirmation = attrs.get("password_confirmation")

        # -----------------------------------------------------
        # EMAIL OU TÉLÉPHONE OBLIGATOIRE
        # -----------------------------------------------------

        if not email and not telephone:
            raise serializers.ValidationError(
                {
                    "non_field_errors": (
                        "Vous devez fournir une adresse email "
                        "ou un numéro de téléphone."
                    )
                }
            )

        # -----------------------------------------------------
        # CONFIRMATION DU MOT DE PASSE
        # -----------------------------------------------------

        if password != password_confirmation:
            raise serializers.ValidationError(
                {
                    "password_confirmation": (
                        "Les deux mots de passe ne correspondent pas."
                    )
                }
            )

        # -----------------------------------------------------
        # VALIDATION DU MOT DE PASSE PAR DJANGO
        # -----------------------------------------------------

        validate_password(
            password,
            user=None,
        )

        return attrs

    # ---------------------------------------------------------
    # CRÉATION DE L'UTILISATEUR
    # ---------------------------------------------------------

    def create(self, validated_data):
        """
        Crée réellement l'utilisateur.

        Le mot de passe est transmis au manager personnalisé
        UserManager.create_user(), qui utilise set_password().

        Le mot de passe en clair n'est donc jamais enregistré
        dans la base de données.
        """

        # Retrait de la confirmation car elle n'est pas
        # nécessaire dans le modèle User.
        validated_data.pop("password_confirmation")

        # Récupération du mot de passe.
        password = validated_data.pop("password")

        # Création via le manager personnalisé.
        user = User.objects.create_user(
            password=password,
            **validated_data,
        )

        return user


class LoginSerializer(serializers.Serializer):
    """
    Serializer utilisé pour la connexion d'un utilisateur.

    L'utilisateur peut se connecter avec :
    - son adresse email ;
    - ou son numéro de téléphone.

    En cas de succès, le serializer retourne :
    - un access token ;
    - un refresh token ;
    - les informations principales de l'utilisateur.
    """

    username = serializers.CharField(
        required=True,
        write_only=True,
        help_text="Adresse email ou numéro de téléphone.",
    )

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={"input_type": "password"},
    )

    def validate(self, attrs):
        """
        Vérifie les identifiants de connexion.
        """

        username = attrs.get("username")
        password = attrs.get("password")

        # ---------------------------------------------------------
        # Vérification des champs
        # ---------------------------------------------------------

        if not username or not password:
            raise serializers.ValidationError(
                "L'identifiant et le mot de passe sont obligatoires."
            )

        # ---------------------------------------------------------
        # Recherche de l'utilisateur
        # ---------------------------------------------------------

        identifier = username.strip()

        if "@" in identifier:
            try:
                user = User.objects.get(
                    email__iexact=identifier
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Identifiant ou mot de passe incorrect."
                )
        else:
            try:
                user = User.objects.get(
                    telephone=identifier
                )
            except User.DoesNotExist:
                raise serializers.ValidationError(
                    "Identifiant ou mot de passe incorrect."
                )

        # ---------------------------------------------------------
        # Vérification du mot de passe
        # ---------------------------------------------------------

        if not user.check_password(password):
            raise serializers.ValidationError(
                "Identifiant ou mot de passe incorrect."
            )

        # ---------------------------------------------------------
        # Vérification du compte
        # ---------------------------------------------------------

        if not user.actif:
            raise serializers.ValidationError(
                "Ce compte est désactivé."
            )

        # ---------------------------------------------------------
        # On conserve l'utilisateur validé
        # ---------------------------------------------------------

        attrs["user"] = user

        return attrs