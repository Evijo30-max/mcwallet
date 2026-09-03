"""
Vues de l'application transactions de MCWallet.

Cette application permet aux utilisateurs authentifiés
de consulter leurs transactions et de créer des demandes
de dépôt.

Important :
Un dépôt créé par l'utilisateur reste EN_ATTENTE.
Le wallet n'est crédité qu'après validation administrative.
"""

import uuid

from django.db import transaction as db_transaction

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.wallets.models import WalletAccount

from .models import Deposit, Transaction
from .serializers import DepositSerializer, TransactionSerializer


class TransactionListView(APIView):
    """
    GET /api/transactions/

    Retourne uniquement les transactions
    appartenant à l'utilisateur connecté.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
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
    GET /api/transactions/<id>/

    Retourne une transaction appartenant
    à l'utilisateur connecté.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
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


class DepositListCreateView(APIView):
    """
    GET  /api/deposits/
    POST /api/deposits/

    GET :
        Retourne les demandes de dépôt de l'utilisateur connecté.

    POST :
        Crée une nouvelle demande de dépôt.

    Le wallet n'est PAS crédité lors de la création.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        deposits = (
            Deposit.objects
            .filter(user=request.user)
            .select_related("wallet")
            .order_by("-date_creation")
        )

        serializer = DepositSerializer(
            deposits,
            many=True,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "count": deposits.count(),
                "deposits": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        montant = request.data.get("montant")
        currency = request.data.get("currency")
        methode = request.data.get("methode")

        if not montant:
            return Response(
                {
                    "success": False,
                    "message": "Le montant est obligatoire.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not currency:
            return Response(
                {
                    "success": False,
                    "message": "La devise est obligatoire.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not methode:
            return Response(
                {
                    "success": False,
                    "message": "La méthode de dépôt est obligatoire.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_currencies = {
            WalletAccount.Currency.XAF,
            WalletAccount.Currency.USD,
            WalletAccount.Currency.EUR,
        }

        if currency not in valid_currencies:
            return Response(
                {
                    "success": False,
                    "message": "Devise non prise en charge.",
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
                    "message": "Compte wallet indisponible.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = DepositSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        reference = (
            f"DEP-{uuid.uuid4().hex[:12].upper()}"
        )

        deposit = serializer.save(
            user=request.user,
            wallet=wallet,
            reference=reference,
            statut=Deposit.DepositStatus.EN_ATTENTE,
        )

        return Response(
            {
                "success": True,
                "message": (
                    "Votre demande de dépôt a été créée "
                    "et est en attente de validation."
                ),
                "deposit": DepositSerializer(
                    deposit,
                    context={"request": request},
                ).data,
            },
            status=status.HTTP_201_CREATED,
        )


class DepositDetailView(APIView):
    """
    GET /api/deposits/<id>/

    Retourne une demande de dépôt appartenant
    à l'utilisateur connecté.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            deposit = (
                Deposit.objects
                .select_related("wallet")
                .get(
                    id=pk,
                    user=request.user,
                )
            )

        except Deposit.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Dépôt introuvable.",
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = DepositSerializer(
            deposit,
            context={"request": request},
        )

        return Response(
            {
                "success": True,
                "deposit": serializer.data,
            },
            status=status.HTTP_200_OK,
        )