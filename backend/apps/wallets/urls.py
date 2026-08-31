"""
URLs de l'application wallets de MCWallet.
"""

from django.urls import path

from .views import WalletDetailView, WalletListView


urlpatterns = [
    path(
        "",
        WalletListView.as_view(),
        name="wallet-list",
    ),
    path(
        "<str:currency>/",
        WalletDetailView.as_view(),
        name="wallet-detail",
    ),
]