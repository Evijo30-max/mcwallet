
"""
Sérialiseurs de l'application transactions de MCWallet.
"""

from rest_framework import serializers

from .models import Transaction, Deposit
from apps.wallets.models import WalletAccount


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer principal des transactions.

    L'utilisateur connecté est automatiquement utilisé.
    Le client ne peut donc pas choisir un autre utilisateur.
    """

    class Meta:
        model = Transaction

        fields = [
            "id",
            "reference",
            "user",
            "wallet",
            "type",
            "montant",
            "currency",
            "statut",
            "description",
            "date_creation",
            "date_modification",
        ]

        read_only_fields = [
            "id",
            "reference",
            "user",
            "statut",
            "date_creation",
            "date_modification",
        ]

    def validate_wallet(self, wallet):
        """
        Vérifie que le wallet appartient bien à l'utilisateur connecté.
        """

        request = self.context.get("request")

        if request is None or not request.user.is_authenticated:
            raise serializers.ValidationError(
                "Utilisateur non authentifié."
            )

        if wallet.user_id != request.user.id:
            raise serializers.ValidationError(
                "Ce compte wallet ne vous appartient pas."
            )

        if not wallet.actif:
            raise serializers.ValidationError(
                "Ce compte wallet est actuellement désactivé."
            )

        return wallet

    def validate(self, attrs):
        """
        Vérifications supplémentaires sur la transaction.
        """

        wallet = attrs.get("wallet")
        currency = attrs.get("currency")

        if wallet and currency != wallet.currency:
            raise serializers.ValidationError(
                {
                    "currency": (
                        "La devise de la transaction doit correspondre "
                        "à la devise du compte wallet."
                    )
                }
            )

        return attrs


class DepositSerializer(serializers.ModelSerializer):
    """
    Serializer utilisé pour afficher une demande de dépôt.

    L'utilisateur ne peut pas choisir lui-même :
    - son utilisateur
    - son wallet
    - le statut
    - la référence

    Ces informations seront déterminées côté serveur.
    """

    class Meta:
        model = Deposit
        fields = [
            "id",
            "reference",
            "wallet",
            "montant",
            "currency",
            "methode",
            "statut",
            "justificatif",
            "commentaire",
            "date_creation",
            "date_modification",
        ]
        read_only_fields = [
            "id",
            "reference",
            "wallet",
            "statut",
            "commentaire",
            "date_creation",
            "date_modification",
        ]



