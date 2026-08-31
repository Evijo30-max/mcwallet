"""
Vues de l'application transactions de MCWallet.

Cette application permet aux utilisateurs authentifiés
de consulter leurs transactions financières.

Les opérations financières réelles (dépôt, retrait,
conversion) seront ajoutées progressivement.
"""

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Transaction
from .serializers import TransactionSerializer


class TransactionListView(APIView):
    """
    Endpoint permettant de consulter les transactions
    de l'utilisateur actuellement connecté.

    URL :
        GET /api/transactions/

    Seules les transactions appartenant à l'utilisateur
    connecté sont retournées.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retourne la liste des transactions de l'utilisateur connecté.
        """

        transactions = (
            Transaction.objects
            .filter(user=request.user)
            .select_related("wallet")
            .order_by("-date_creation")
        )

        serializer = TransactionSerializer(
            transactions,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "count": transactions.count(),
                "transactions": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TransactionDetailView(APIView):
    """
    Endpoint permettant de consulter une transaction précise.

    URL :
        GET /api/transactions/<id>/

    L'utilisateur ne peut consulter qu'une transaction
    qui lui appartient.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        """
        Retourne une transaction appartenant à l'utilisateur connecté.
        """

        try:
            transaction = (
                Transaction.objects
                .select_related("wallet")
                .get(
                    id=pk,
                    user=request.user,
                )
            )

        except Transaction.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Transaction introuvable.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TransactionSerializer(
            transaction,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "transaction": serializer.data,
            },
            status=status.HTTP_200_OK,
        )