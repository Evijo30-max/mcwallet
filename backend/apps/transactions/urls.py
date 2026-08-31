from django.urls import path

from .views import (
TransactionListView,
TransactionDetailView,
)

urlpatterns = [
path(
"",
TransactionListView.as_view(),
name="transaction-list",
),
path(
"[int:pk](int:pk)/",
TransactionDetailView.as_view(),
name="transaction-detail",
),
]
