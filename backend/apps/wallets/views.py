"""
Views de l'application wallets de MCWallet.

Ce fichier contient les endpoints API permettant à un
utilisateur authentifié de consulter ses comptes multi-devises.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import WalletAccount


class WalletListView(APIView):
    """
    Endpoint permettant de récupérer les comptes multi-devises
    de l'utilisateur actuellement connecté.

    URL :
        GET /api/wallets/

    L'utilisateur reçoit uniquement ses propres comptes.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retourne les comptes actifs de l'utilisateur connecté.
        """

        wallets = WalletAccount.objects.filter(
            user=request.user,
            actif=True,
        ).order_by("currency")

        return Response(
            {
                "success": True,
                "wallets": [
                    {
                        "id": wallet.id,
                        "currency": wallet.currency,
                        "balance": str(wallet.balance),
                        "actif": wallet.actif,
                        "date_creation": wallet.date_creation,
                        "date_modification": wallet.date_modification,
                    }
                    for wallet in wallets
                ],
            },
            status=status.HTTP_200_OK,
        )


class WalletDetailView(APIView):
    """
    Endpoint permettant de consulter un compte multi-devise précis.

    URL :
        GET /api/wallets/<currency>/

    Exemple :
        GET /api/wallets/XAF/
        GET /api/wallets/USD/
        GET /api/wallets/EUR/

    L'utilisateur ne peut consulter que son propre compte.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, currency):
        """
        Retourne les informations du compte correspondant
        à la devise demandée.
        """

        currency = currency.upper()

        if currency not in WalletAccount.Currency.values:
            return Response(
                {
                    "success": False,
                    "message": "Cette devise n'est pas supportée.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            wallet = WalletAccount.objects.get(
                user=request.user,
                currency=currency,
                actif=True,
            )
        except WalletAccount.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": (
                        "Aucun compte actif trouvé pour cette devise."
                    ),
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "success": True,
                "wallet": {
                    "id": wallet.id,
                    "currency": wallet.currency,
                    "balance": str(wallet.balance),
                    "actif": wallet.actif,
                    "date_creation": wallet.date_creation,
                    "date_modification": wallet.date_modification,
                },
            },
            status=status.HTTP_200_OK,
        )