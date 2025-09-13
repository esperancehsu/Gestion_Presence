from rest_framework import serializers
from api.models import Presence
from django.utils import timezone
from api.models import Employe


class PresenceSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source="employe.nom", read_only=True)
    employe_username = serializers.CharField(source="employe.user.username", read_only=True)

    class Meta:
        model = Presence
        fields = [
            "id", "employe", "employe_nom", "employe_username", "date",
            "heure_arrivee", "heure_sortie", "statut", "note",
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "employe_nom", "employe_username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        
        if request and request.user.is_authenticated:
            # Si pas admin/manager/rh, certains champs deviennent read-only
            if not (request.user.is_admin or request.user.is_manager or request.user.is_rh):
                # Staff ne peut pas modifier manuellement les heures et statut
                self.fields['heure_arrivee'].read_only = True
                self.fields['heure_sortie'].read_only = True
                self.fields['statut'].read_only = True
                
                # Staff ne peut créer que pour lui-même
                if not self.instance:  # Création
                    self.fields['employe'].read_only = True
                    self.fields['date'].read_only = True

    def validate(self, data):
        request = self.context.get("request")
        user = request.user if request else None
        
        # Déterminer l'employé
        employe = data.get("employe")
        if not employe and self.instance:
            employe = self.instance.employe
        elif not employe and user and not (user.is_admin or user.is_manager or user.is_rh):
            # Pour staff, utiliser son employé
            try:
                employe = user.employe
            except Employe.DoesNotExist:
                raise serializers.ValidationError("Votre compte n'est pas associé à un employé.")

        # Déterminer la date
        date = data.get("date", timezone.localdate())
        if self.instance:
            date = data.get("date", self.instance.date)

        # Vérification unicité en création
        if not self.instance and employe and date:
            if Presence.objects.filter(employe=employe, date=date).exists():
                raise serializers.ValidationError("Une présence existe déjà pour cet employé à cette date.")

        # Vérification cohérence des heures
        heure_arrivee = data.get("heure_arrivee")
        heure_sortie = data.get("heure_sortie")
        
        if self.instance:
            heure_arrivee = heure_arrivee or self.instance.heure_arrivee
            heure_sortie = heure_sortie or self.instance.heure_sortie

        if heure_arrivee and heure_sortie and heure_sortie <= heure_arrivee:
            raise serializers.ValidationError({
                "heure_sortie": "L'heure de sortie doit être après l'heure d'arrivée."
            })

        return data

    def create(self, validated_data):
        request = self.context.get("request")
        user = request.user if request else None
        
        # Pour staff, forcer son employé et la date du jour
        if user and not (user.is_admin or user.is_manager or user.is_rh):
            try:
                validated_data['employe'] = user.employe
                validated_data['date'] = timezone.localdate()
            except Employe.DoesNotExist:
                raise serializers.ValidationError("Votre compte n'est pas associé à un employé.")
        
        return super().create(validated_data)
