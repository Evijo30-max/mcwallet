from django.urls import path

from .views import (
    DepositListCreateView,
    DepositDetailView,
)

urlpatterns = [
    path(
        "",
        DepositListCreateView.as_view(),
        name="deposit-list-create",
    ),

    path(
        "<int:pk>/",
        DepositDetailView.as_view(),
        name="deposit-detail",
    ),
]