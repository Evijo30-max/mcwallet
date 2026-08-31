"""
URLs de l'application users de MCWallet.
"""

from django.urls import path

from .views import (
    UserLoginView,
    UserMeView,
    UserRegistrationView,
)


urlpatterns = [
    # -------------------------------------------------------------
    # INSCRIPTION
    # -------------------------------------------------------------

    path(
        "register/",
        UserRegistrationView.as_view(),
        name="user-register",
    ),

    # -------------------------------------------------------------
    # CONNEXION
    # -------------------------------------------------------------

    path(
        "login/",
        UserLoginView.as_view(),
        name="user-login",
    ),

    # -------------------------------------------------------------
    # UTILISATEUR CONNECTÉ
    # -------------------------------------------------------------

    path(
        "me/",
        UserMeView.as_view(),
        name="user-me",
    ),
]