from rest_framework import serializers
from api.models import Presence
from django.utils import timezone
from api.models import Employe


# On crée un serializer pour la classe Presence,
# qui va permettre de transformer un objet Presence en JSON et vice versa.
class PresenceSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source="employe.nom", read_only=True)

    class Meta:
        model = Presence
        fields = [
            "id", "employe", "employe_nom", "date",
            "heure_arrivee", "heure_sortie", "statut", "note",
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "employe_nom", "statut"]

    def __init__(self, *args, **kwargs):
        # On peut régler les read_only_fields selon le user (admin ou staff)
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            # si pa admin, on rendre certains champs read-only (ne pas permettre d'écrire heure/ statut / employe / date)
            if not (hasattr(request.user, "groupe") and request.user.groupe == "admin") and not request.user.is_superuser:
                for f in ("heure_arrivee", "heure_sortie", "statut", "employe", "date"):
                    if f in self.fields:
                        self.fields[f].read_only = True

    def validate(self, data):
        """
        - Vérifie unicité (sur création)
        - Vérifie cohérence heures (si fournies)
        """
        request = self.context.get("request")
        is_admin = request and request.user.is_authenticated and ((hasattr(request.user, "groupe") and request.user.groupe == "admin") or request.user.is_superuser)

        # employe déterminé soit par le payload (admin) soit par le user (staff)
        employe = data.get("employe")
        if not employe and request and not is_admin:
            # staff : on forcera l'employe dans la vue, ici on récupère pour la validation si besoin
            try:
                employe = request.user.employe
            except Exception:
                raise serializers.ValidationError("Utilisateur non lié à un employé. Contactez l'administrateur.")

        # date
        date = data.get("date", timezone.localdate())

        # en création, vérifier qu'il n'existe pas déjà une présence pour cet employe/date
        if self.instance is None:
            if Presence.objects.filter(employe=employe, date=date).exists():
                raise serializers.ValidationError("Une présence pour cet employé à cette date existe déjà.")

        # if both heures provided, check ordre
        heure_arrivee = data.get("heure_arrivee") or (self.instance and getattr(self.instance, "heure_arrivee", None))
        heure_sortie = data.get("heure_sortie") or (self.instance and getattr(self.instance, "heure_sortie", None))
        if heure_arrivee and heure_sortie and heure_sortie <= heure_arrivee:
            raise serializers.ValidationError({"heure_sortie": "L'heure de sortie doit être strictement après l'heure d'arrivée."})

        return data




