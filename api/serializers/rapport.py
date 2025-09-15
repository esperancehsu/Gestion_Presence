from rest_framework import serializers
from api.models import Rapport,Employe


class RapportSerializer(serializers.ModelSerializer):
    employe_nom = serializers.CharField(source="employe.nom", read_only=True)
    employe_poste = serializers.CharField(source="employe.poste", read_only=True)
    
  
    employe = serializers.PrimaryKeyRelatedField(
        queryset=Employe.objects.all(),
        required=False
    )

    class Meta:
        model = Rapport
        fields = [
            "id", "employe", "employe_nom", "employe_poste", "type", 
            "date_debut", "date_fin", "contenu", 
            "created_at", "updated_at"
        ]
        read_only_fields = ["created_at", "updated_at", "employe_nom", "employe_poste"]

    def validate(self, attrs):
        # PROBLÈME 5: Validation des dates ne vérifie pas si les champs existent
        date_debut = attrs.get("date_debut")
        date_fin = attrs.get("date_fin")
        
        if date_debut and date_fin and date_fin < date_debut:
            raise serializers.ValidationError({
                "date_fin": "La date de fin doit être après la date de début."
            })
        
        return attrs

    def validate_employe(self, value):
        """Validation spécifique pour le champ employe"""
        request = self.context.get('request')
        
        if request and request.user.is_authenticated:
            # Vérifier les permissions
            user_can_manage_all = (
                getattr(request.user, 'is_admin', False) or 
                getattr(request.user, 'is_rh', False) or
                getattr(request.user, 'is_manager', False) or
                request.user.has_perm('api.can_view_all_reports')
            )

            # Si l'utilisateur n'a pas les permissions étendues
            if not user_can_manage_all:
                # Il ne peut créer des rapports que pour lui-même
                try:
                    user_employe = request.user.employe
                    if value and value != user_employe:
                        raise serializers.ValidationError(
                            "Vous ne pouvez créer des rapports que pour vous-même."
                        )
                except AttributeError:
                    raise serializers.ValidationError(
                        "Votre compte n'est pas associé à un employé."
                    )
        
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        
        # Si pas d'employé spécifié, utiliser celui de l'utilisateur connecté
        if 'employe' not in validated_data or not validated_data['employe']:
            if request and request.user.is_authenticated:
                try:
                    validated_data['employe'] = request.user.employe
                except AttributeError:
                    raise serializers.ValidationError({
                        'employe': 'Votre compte n\'est pas associé à un employé.'
                    })
        
        return super().create(validated_data)