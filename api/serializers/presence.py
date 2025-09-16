from rest_framework import serializers
from api.models import Presence
from django.utils import timezone
from api.models import Employe
from .employe import EmployeSerializer


class PresenceSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source="employe.nom", read_only=True)
    employe_username = serializers.CharField(source="employe.user.username", read_only=True)
    duree_travail = serializers.SerializerMethodField()
    peut_arriver = serializers.SerializerMethodField()
    peut_partir = serializers.SerializerMethodField()

    class Meta:
        model = Presence
        fields = [
            "id", "employe", "employe_nom", "employe_username", "date",
            "heure_arrivee", "heure_sortie", "statut", "note",
            "duree_travail", "peut_arriver", "peut_partir",
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "employe_nom", "employe_username"]

    def get_duree_travail(self, obj):
        return obj.get_duree_travail()

    def get_peut_arriver(self, obj):
        return obj.heure_arrivee is None

    def get_peut_partir(self, obj):
        return obj.heure_arrivee is not None and obj.heure_sortie is None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        
        if request and request.user.is_authenticated:
            if not (request.user.is_admin or request.user.is_manager or request.user.is_rh):
                self.fields['heure_arrivee'].read_only = True
                self.fields['heure_sortie'].read_only = True
                self.fields['statut'].read_only = True
                
                if not self.instance:
                    self.fields['employe'].read_only = True
                    self.fields['date'].read_only = True

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        
        if user and not (user.is_admin or user.is_manager or user.is_rh):
            try:
                validated_data['employe'] = user.employe
                validated_data['date'] = timezone.localdate()
            except Employe.DoesNotExist:
                raise serializers.ValidationError("Votre compte n'est pas associé à un employé.")
        
        return super().create(validated_data)