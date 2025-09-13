# api/admin.py
from django.contrib import admin
from .models import Employe

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'poste', 'user', 'email', 'telephone')
    list_filter = ('poste',)
    search_fields = ('nom', 'user__username', 'email')
    raw_id_fields = ('user',)  # ← Meilleur pour les ForeignKey

# api/admin.py (suite)
from .models import Presence

@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    list_display = ('employe', 'date', 'statut', 'heure_arrivee', 'heure_sortie')
    list_filter = ('statut', 'date')
    search_fields = ('employe__nom', 'employe__user__username')
    raw_id_fields = ('employe',)
    date_hierarchy = 'date'  # ← Navigation par date

# api/admin.py (suite)
from .models import Rapport

@admin.register(Rapport)
class RapportAdmin(admin.ModelAdmin):
    list_display = ('employe', 'get_type_display', 'date_debut', 'date_fin')
    list_filter = ('type', 'date_debut')
    search_fields = ('employe__nom', 'contenu')
    raw_id_fields = ('employe',)
    date_hierarchy = 'date_debut'