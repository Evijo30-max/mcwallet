"""
Signaux de l'application wallets de MCWallet.

Ce fichier contient les automatismes liés aux comptes
multi-devises des utilisateurs.
"""

from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.users.models import User
from .models import WalletAccount


@receiver(post_save, sender=User)
def create_user_wallet_accounts(sender, instance, created, **kwargs):
    """
    Crée automatiquement les comptes XAF, USD et EUR
    lorsqu'un nouvel utilisateur est créé.
    """

    if not created:
        return

    currencies = ["XAF", "USD", "EUR"]

    for currency in currencies:
        WalletAccount.objects.create(
            user=instance,
            currency=currency,
            balance=0,
            actif=True,
        )