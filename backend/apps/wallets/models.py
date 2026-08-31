"""
Modèles de l'application wallets de MCWallet.

Cette application gère les comptes financiers multi-devises
de chaque utilisateur.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings


class WalletAccount(models.Model):
    """
    Compte financier d'un utilisateur pour une devise donnée.

    Un utilisateur peut posséder un compte pour chaque devise
    supportée par MCWallet.

    Exemple :

        Utilisateur
            ├── Compte XAF
            ├── Compte USD
            └── Compte EUR
    """

    class Currency(models.TextChoices):
        """
        Devises actuellement supportées par MCWallet.
        """

        XAF = "XAF", "Franc CFA"
        USD = "USD", "Dollar américain"
        EUR = "EUR", "Euro"

    # ------------------------------------------------------------------
    # IDENTIFIANT
    # ------------------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # PROPRIÉTAIRE
    # ------------------------------------------------------------------

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wallet_accounts",
        verbose_name="Utilisateur",
    )

    # ------------------------------------------------------------------
    # DEVISE
    # ------------------------------------------------------------------

    currency = models.CharField(
        max_length=3,
        choices=Currency.choices,
        verbose_name="Devise",
    )

    # ------------------------------------------------------------------
    # SOLDE
    # ------------------------------------------------------------------

    balance = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[
            MinValueValidator(Decimal("0.00")),
        ],
        verbose_name="Solde",
    )

    # ------------------------------------------------------------------
    # ÉTAT DU COMPTE
    # ------------------------------------------------------------------

    actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif",
    )

    # ------------------------------------------------------------------
    # DATES
    # ------------------------------------------------------------------

    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification",
    )

    # ------------------------------------------------------------------
    # MÉTADONNÉES
    # ------------------------------------------------------------------

    class Meta:
        db_table = "wallets_wallet_account"

        verbose_name = "Compte multi-devise"
        verbose_name_plural = "Comptes multi-devises"

        ordering = ["user", "currency"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "currency"],
                name="unique_user_currency_account",
            ),
        ]

        indexes = [
            models.Index(
                fields=["user", "currency"],
                name="wallet_user_currency_idx",
            ),
            models.Index(
                fields=["user", "actif"],
                name="wallet_user_active_idx",
            ),
        ]

    # ------------------------------------------------------------------
    # AFFICHAGE
    # ------------------------------------------------------------------

    def __str__(self):
        """
        Représentation lisible du compte.
        """

        return (
            f"{self.user} - "
            f"{self.currency} - "
            f"{self.balance}"
        )