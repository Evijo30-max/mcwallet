"""
Modèles utilisateurs de MCWallet.

Cette application contient le modèle utilisateur principal
de la plateforme ainsi que son manager personnalisé.

IMPORTANT :
Le modèle User de MCWallet remplace le modèle User fourni
par défaut par Django.
"""

import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class UserManager(BaseUserManager):
    """
    Manager personnalisé pour le modèle User.

    Django utilise ce manager pour créer :
    - les utilisateurs normaux ;
    - les superutilisateurs.

    Nous n'utilisons pas le système username de Django.
    L'utilisateur MCWallet sera identifié par son email
    et/ou son numéro de téléphone.
    """

    def create_user(self, email=None, telephone=None, password=None, **extra_fields):
        """
        Crée un utilisateur normal.

        Au moins un moyen de connexion doit être fourni :
        - email
        OU
        - téléphone.
        """

        # Nettoyage de l'email s'il existe.
        if email:
            email = self.normalize_email(email)

        # Un utilisateur doit avoir au moins un identifiant.
        if not email and not telephone:
            raise ValueError(
                "Un utilisateur doit fournir un email ou un numéro de téléphone."
            )

        # Le mot de passe est obligatoire.
        if not password:
            raise ValueError(
                "Le mot de passe est obligatoire."
            )

        user = self.model(
            email=email,
            telephone=telephone,
            **extra_fields,
        )

        # IMPORTANT :
        # set_password() applique le système de hash sécurisé
        # de Django. Nous ne stockons jamais le mot de passe
        # en clair dans la base de données.
        user.set_password(password)

        user.save(using=self._db)

        return user

    def create_superuser(
        self,
        email=None,
        telephone=None,
        password=None,
        **extra_fields,
    ):
        """
        Crée un administrateur Django.

        Un superutilisateur doit obligatoirement :
        - être actif ;
        - avoir les permissions staff ;
        - avoir les permissions superuser ;
        - avoir le rôle ADMIN.
        """

        extra_fields.setdefault("role", User.Role.ADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("actif", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(
                "Un superutilisateur doit avoir is_staff=True."
            )

        if extra_fields.get("is_superuser") is not True:
            raise ValueError(
                "Un superutilisateur doit avoir is_superuser=True."
            )

        return self.create_user(
            email=email,
            telephone=telephone,
            password=password,
            **extra_fields,
        )


class User(AbstractBaseUser, PermissionsMixin):
    """
    Utilisateur principal de MCWallet.

    Ce modèle remplace le User standard de Django.

    L'utilisateur peut se connecter avec :
    - son email ;
    - ou son numéro de téléphone.

    Les deux peuvent également être renseignés.
    """

    class Role(models.TextChoices):
        """
        Rôles disponibles dans MCWallet.
        """

        CLIENT = "CLIENT", "Client"
        ADMIN = "ADMIN", "Administrateur"

    # ------------------------------------------------------------------
    # IDENTIFIANT PRINCIPAL
    # ------------------------------------------------------------------

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # IDENTIFIANTS DE CONNEXION
    # ------------------------------------------------------------------

    email = models.EmailField(
        max_length=254,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Adresse email",
    )

    telephone = PhoneNumberField(
        unique=True,
        null=True,
        blank=True,
        region="CM",
        verbose_name="Numéro de téléphone",
        help_text=(
            "Numéro enregistré au format international, "
            "par exemple +237XXXXXXXXX."
        ),
    )

    # ------------------------------------------------------------------
    # IDENTITÉ
    # ------------------------------------------------------------------

    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom",
    )

    nom = models.CharField(
        max_length=100,
        verbose_name="Nom",
    )

    # ------------------------------------------------------------------
    # RÔLE
    # ------------------------------------------------------------------

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.CLIENT,
        verbose_name="Rôle",
    )

    # ------------------------------------------------------------------
    # ÉTAT DU COMPTE
    # ------------------------------------------------------------------

    actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif",
    )

    # ------------------------------------------------------------------
    # VÉRIFICATION DES MOYENS DE CONTACT
    # ------------------------------------------------------------------

    email_verified = models.BooleanField(
        default=False,
        verbose_name="Email vérifié",
    )

    phone_verified = models.BooleanField(
        default=False,
        verbose_name="Téléphone vérifié",
    )

    # ------------------------------------------------------------------
    # PERMISSIONS DJANGO
    # ------------------------------------------------------------------

    is_staff = models.BooleanField(
        default=False,
        verbose_name="Accès administration",
    )

    # ------------------------------------------------------------------
    # DATES
    # ------------------------------------------------------------------

    date_creation = models.DateTimeField(
        default=timezone.now,
        editable=False,
        verbose_name="Date de création",
    )

    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification",
    )

    # ------------------------------------------------------------------
    # MANAGER
    # ------------------------------------------------------------------

    objects = UserManager()

    # ------------------------------------------------------------------
    # CONFIGURATION DE L'AUTHENTIFICATION DJANGO
    # ------------------------------------------------------------------

    # Nous n'avons volontairement PAS de username.
    #
    # Django utilisera notre système de connexion personnalisé
    # basé sur email/téléphone.

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "prenom",
        "nom",
    ]

    # ------------------------------------------------------------------
    # MÉTADONNÉES
    # ------------------------------------------------------------------

    class Meta:
        db_table = "users_user"
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ["-date_creation"]

        constraints = [
            models.CheckConstraint(
                condition=Q(email__isnull=False)
                | Q(telephone__isnull=False),
                name="user_email_or_phone_required",
            ),
        ]

    # ------------------------------------------------------------------
    # VALIDATION
    # ------------------------------------------------------------------

    def clean(self):
        """
        Validation métier du modèle.

        Cette méthode vérifie notamment qu'au moins un moyen
        de connexion est présent.
        """

        super().clean()

        if not self.email and not self.telephone:
            raise ValidationError(
                "L'utilisateur doit avoir un email ou un numéro de téléphone."
            )

        # Normalisation de l'email.
        if self.email:
            self.email = self.__class__.objects.normalize_email(
                self.email
            )

    # ------------------------------------------------------------------
    # AFFICHAGE
    # ------------------------------------------------------------------

    def __str__(self):
        """
        Représentation lisible de l'utilisateur.
        """

        if self.email:
            return self.email

        if self.telephone:
            return str(self.telephone)

        return f"{self.prenom} {self.nom}"