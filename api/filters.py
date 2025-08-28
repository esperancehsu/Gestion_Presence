import django_filters

from .models import TonModele  # Remplace par le nom de ton modèle

class TonModeleFilter(django_filters.FilterSet):
    class Meta:
        model = TonModele
        fields = ['champ1', 'champ2']  # Remplace par les champs que tu veux filtrer