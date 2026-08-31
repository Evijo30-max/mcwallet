from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Configuration du modèle User de MCWallet
    dans l'interface Django Admin.
    """

    # Colonnes affichées dans la liste des utilisateurs.
    list_display = (
        "email",
        "telephone",
        "prenom",
        "nom",
        "role",
        "actif",
        "is_staff",
        "date_creation",
    )

    # Filtres disponibles dans la colonne de droite.
    list_filter = (
        "role",
        "actif",
        "is_staff",
        "is_superuser",
        "email_verified",
        "phone_verified",
    )

    # Recherche par ces champs.
    search_fields = (
        "email",
        "telephone",
        "prenom",
        "nom",
    )

    # Ordre d'affichage.
    ordering = ("-date_creation",)

    # Champs affichés lorsque l'on ouvre un utilisateur.
    fieldsets = (
        (
            "Informations de connexion",
            {
                "fields": (
                    "email",
                    "telephone",
                    "password",
                )
            },
        ),
        (
            "Identité",
            {
                "fields": (
                    "prenom",
                    "nom",
                )
            },
        ),
        (
            "MCWallet",
            {
                "fields": (
                    "role",
                    "actif",
                    "email_verified",
                    "phone_verified",
                )
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Dates",
            {
                "fields": (
                    "last_login",
                    "date_creation",
                    "date_modification",
                )
            },
        ),
    )

    # Champs utilisés lors de la création d'un utilisateur
    # depuis Django Admin.
    add_fieldsets = (
        (
            "Création de l'utilisateur",
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "telephone",
                    "prenom",
                    "nom",
                    "password1",
                    "password2",
                    "role",
                    "actif",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )

    # Évite d'afficher le mot de passe hashé comme un champ
    # modifiable directement.
    readonly_fields = (
        "last_login",
        "date_creation",
        "date_modification",
    )