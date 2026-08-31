
"""
Views de l'application users de MCWallet.

Ce fichier contient les endpoints API liés aux utilisateurs.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from .serializers import (
    LoginSerializer,
    UserRegistrationSerializer,
)


class UserRegistrationView(APIView):
    """
    Endpoint d'inscription d'un nouveau client.

    URL :
        POST /api/users/register/

    Le client peut fournir :
        - uniquement un email ;
        - uniquement un téléphone ;
        - ou les deux.

    Au moins l'un des deux est obligatoire.
    """

    def post(self, request):
        """
        Crée un nouveau compte client.
        """

        # ---------------------------------------------------------
        # VALIDATION DES DONNÉES
        # ---------------------------------------------------------

        serializer = UserRegistrationSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # CRÉATION DE L'UTILISATEUR
        # ---------------------------------------------------------

        user = serializer.save()

        # ---------------------------------------------------------
        # RÉPONSE
        # ---------------------------------------------------------

        return Response(
            {
                "success": True,
                "message": "Compte créé avec succès.",
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "telephone": (
                        str(user.telephone)
                        if user.telephone
                        else None
                    ),
                    "prenom": user.prenom,
                    "nom": user.nom,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    """
    Endpoint de connexion d'un utilisateur.

    URL :
        POST /api/users/login/

    L'utilisateur peut se connecter avec :
        - son adresse email ;
        - ou son numéro de téléphone.

    En cas de succès, l'API retourne :
        - un access token ;
        - un refresh token ;
        - les informations principales de l'utilisateur.
    """

    def post(self, request):
        """
        Vérifie les identifiants et génère les tokens JWT.
        """

        # ---------------------------------------------------------
        # VALIDATION DES IDENTIFIANTS
        # ---------------------------------------------------------

        serializer = LoginSerializer(
            data=request.data
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ---------------------------------------------------------
        # RÉCUPÉRATION DE L'UTILISATEUR
        # ---------------------------------------------------------

        user = serializer.validated_data["user"]

        # ---------------------------------------------------------
        # GÉNÉRATION DES TOKENS JWT
        # ---------------------------------------------------------

        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token

        # ---------------------------------------------------------
        # RÉPONSE
        # ---------------------------------------------------------

        return Response(
            {
                "success": True,
                "message": "Connexion réussie.",
                "tokens": {
                    "access": str(access_token),
                    "refresh": str(refresh),
                },
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "telephone": (
                        str(user.telephone)
                        if user.telephone
                        else None
                    ),
                    "prenom": user.prenom,
                    "nom": user.nom,
                    "role": user.role,
                },
            },
            status=status.HTTP_200_OK,
        )


class UserMeView(APIView):
    """
    Endpoint permettant de récupérer les informations
    de l'utilisateur actuellement connecté.

    URL :
        GET /api/users/me/

    Cet endpoint nécessite un JWT valide.
    """

    # ---------------------------------------------------------
    # AUTHENTIFICATION OBLIGATOIRE
    # ---------------------------------------------------------

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retourne les informations de l'utilisateur connecté.
        """

        # ---------------------------------------------------------
        # RÉCUPÉRATION DE L'UTILISATEUR CONNECTÉ
        # ---------------------------------------------------------

        user = request.user

        # ---------------------------------------------------------
        # RÉPONSE
        # ---------------------------------------------------------

        return Response(
            {
                "success": True,
                "user": {
                    "id": str(user.id),
                    "email": user.email,
                    "telephone": (
                        str(user.telephone)
                        if user.telephone
                        else None
                    ),
                    "prenom": user.prenom,
                    "nom": user.nom,
                    "role": user.role,
                    "actif": user.actif,
                    "email_verified": user.email_verified,
                    "phone_verified": user.phone_verified,
                },
            },
            status=status.HTTP_200_OK,
        )

