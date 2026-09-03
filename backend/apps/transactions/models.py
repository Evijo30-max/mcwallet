"""
Modèles de l'application transactions de MCWallet.

Cette application enregistre tous les mouvements financiers
effectués sur les comptes multi-devises des utilisateurs.

IMPORTANT :
Une transaction représente un événement financier.
Le solde du wallet ne doit jamais être modifié sans qu'une
transaction correspondante puisse être retrouvée.
"""

from decimal import Decimal

from django.core.validators import MinValueValidator
from django.db import models
from django.conf import settings

from apps.wallets.models import WalletAccount


class Transaction(models.Model):
    """
    Représente une opération financière effectuée sur un wallet.

    Types actuellement prévus :
        - DEPOT
        - RETRAIT
        - CONVERSION

    Chaque transaction appartient à un utilisateur et concerne
    un compte wallet précis.
    """

    # ------------------------------------------------------------------
    # TYPES DE TRANSACTION
    # ------------------------------------------------------------------

    class TransactionType(models.TextChoices):
        DEPOT = "DEPOT", "Dépôt"
        RETRAIT = "RETRAIT", "Retrait"
        CONVERSION = "CONVERSION", "Conversion"

    # ------------------------------------------------------------------
    # STATUTS
    # ------------------------------------------------------------------

    class TransactionStatus(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        CONFIRMEE = "CONFIRMEE", "Confirmée"
        REFUSEE = "REFUSEE", "Refusée"
        ANNULEE = "ANNULEE", "Annulée"

    # ------------------------------------------------------------------
    # IDENTIFIANT
    # ------------------------------------------------------------------

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="Identifiant",
    )

    # ------------------------------------------------------------------
    # RÉFÉRENCE
    # ------------------------------------------------------------------

    reference = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Référence",
        help_text="Référence unique de la transaction.",
    )

    # ------------------------------------------------------------------
    # UTILISATEUR
    # ------------------------------------------------------------------

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Utilisateur",
    )

    # ------------------------------------------------------------------
    # WALLET CONCERNÉ
    # ------------------------------------------------------------------

    wallet = models.ForeignKey(
        WalletAccount,
        on_delete=models.PROTECT,
        related_name="transactions",
        verbose_name="Compte wallet",
    )

    # ------------------------------------------------------------------
    # TYPE
    # ------------------------------------------------------------------

    type = models.CharField(
        max_length=20,
        choices=TransactionType.choices,
        verbose_name="Type de transaction",
    )

    # ------------------------------------------------------------------
    # MONTANT
    # ------------------------------------------------------------------

    montant = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
        verbose_name="Montant",
    )

    # ------------------------------------------------------------------
    # DEVISE
    # ------------------------------------------------------------------

    currency = models.CharField(
        max_length=3,
        choices=WalletAccount.Currency.choices,
        verbose_name="Devise",
    )

    # ------------------------------------------------------------------
    # STATUT
    # ------------------------------------------------------------------

    statut = models.CharField(
        max_length=20,
        choices=TransactionStatus.choices,
        default=TransactionStatus.EN_ATTENTE,
        verbose_name="Statut",
    )

    # ------------------------------------------------------------------
    # DESCRIPTION
    # ------------------------------------------------------------------

    description = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Description",
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
        db_table = "transactions_transaction"

        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"

        ordering = ["-date_creation"]

        indexes = [
            models.Index(
                fields=["user", "date_creation"],
                name="transaction_user_date_idx",
            ),
            models.Index(
                fields=["wallet", "date_creation"],
                name="transaction_wallet_date_idx",
            ),
            models.Index(
                fields=["statut"],
                name="transaction_status_idx",
            ),
            models.Index(
                fields=["type"],
                name="transaction_type_idx",
            ),
        ]

    # ------------------------------------------------------------------
    # AFFICHAGE
    # ------------------------------------------------------------------

    def __str__(self):
        """
        Représentation lisible de la transaction.
        """

        return (
            f"{self.reference} - "
            f"{self.type} - "
            f"{self.montant} {self.currency}"
        )

class Deposit(models.Model):
    """
    Demande de dépôt effectuée par un utilisateur.

    Le dépôt n'est pas immédiatement crédité au wallet.
    Il reste en attente jusqu'à validation par l'administrateur.
    """

    class DepositStatus(models.TextChoices):
        EN_ATTENTE = "EN_ATTENTE", "En attente"
        CONFIRME = "CONFIRME", "Confirmé"
        REFUSE = "REFUSE", "Refusé"
        ANNULE = "ANNULE", "Annulé"

    id = models.BigAutoField(
        primary_key=True,
        verbose_name="Identifiant",
    )

    reference = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Référence",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="deposits",
        verbose_name="Utilisateur",
    )

    wallet = models.ForeignKey(
        WalletAccount,
        on_delete=models.PROTECT,
        related_name="deposits",
        verbose_name="Compte à créditer",
    )

    montant = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
        ],
        verbose_name="Montant",
    )

    currency = models.CharField(
        max_length=3,
        choices=WalletAccount.Currency.choices,
        verbose_name="Devise",
    )

    methode = models.CharField(
        max_length=100,
        verbose_name="Méthode de dépôt",
    )

    statut = models.CharField(
        max_length=20,
        choices=DepositStatus.choices,
        default=DepositStatus.EN_ATTENTE,
        verbose_name="Statut",
    )

    justificatif = models.FileField(
        upload_to="deposits/",
        blank=True,
        null=True,
        verbose_name="Justificatif",
    )

    commentaire = models.CharField(
        max_length=500,
        blank=True,
        default="",
        verbose_name="Commentaire",
    )

    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création",
    )

    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name="Date de modification",
    )

    class Meta:
        db_table = "transactions_deposit"
        verbose_name = "Dépôt"
        verbose_name_plural = "Dépôts"
        ordering = ["-date_creation"]
        indexes = [
            models.Index(
                fields=["user", "date_creation"],
                name="deposit_user_date_idx",
            ),
            models.Index(
                fields=["statut"],
                name="deposit_status_idx",
            ),
            models.Index(
                fields=["wallet", "date_creation"],
                name="deposit_wallet_date_idx",
            ),
        ]

    def __str__(self):
        return (
            f"{self.reference} - "
            f"{self.montant} {self.currency} - "
            f"{self.statut}"
        )