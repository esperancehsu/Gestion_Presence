# users/management/commands/setup_groups.py

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from api.models import Employe, Presence

User = get_user_model()

class Command(BaseCommand):
    help = 'Assigne automatiquement tous les utilisateurs aux groupes selon leurs rôles'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-employees',
            action='store_true',
            help='Créer les employés manquants pour les utilisateurs'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Afficher ce qui sera fait sans l\'exécuter'
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        create_employees = options['create_employees']

        if dry_run:
            self.stdout.write(self.style.WARNING('🧪 MODE DRY-RUN: Aucune modification ne sera effectuée'))

        self.stdout.write("🚀 Attribution automatique des groupes selon les rôles")
        self.stdout.write("="*60)

        # 1. Créer les permissions
        self.create_permissions(dry_run)

        # 2. Créer les groupes avec permissions
        self.create_groups_with_permissions(dry_run)

        # 3. Assigner les utilisateurs
        stats = self.assign_users_to_groups(dry_run)

        # 4. Créer les employés si demandé
        employees_created = 0
        if create_employees:
            employees_created = self.create_missing_employees(dry_run)

        # 5. Vérification finale
        self.verify_setup()

        # Résumé
        self.stdout.write("\n" + "="*60)
        self.stdout.write(self.style.SUCCESS("🎉 TRAITEMENT TERMINÉ!"))
        self.stdout.write("="*60)
        self.stdout.write("📊 STATISTIQUES:")
        for group, count in stats.items():
            self.stdout.write(f"  • {group}: {count} utilisateurs")
        if create_employees:
            self.stdout.write(f"  • Employés créés: {employees_created}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\n✅ Tous les utilisateurs sont maintenant correctement configurés!"))

    def create_permissions(self, dry_run=False):
        """Créer les permissions manquantes"""
        self.stdout.write("\n📋 Vérification des permissions...")

        employe_ct = ContentType.objects.get_for_model(Employe)
        presence_ct = ContentType.objects.get_for_model(Presence)

        permissions_to_create = [
            ('can_view_all_employees', 'Peut voir tous les employés', employe_ct),
            ('can_manage_employee', 'Peut gérer les employés', employe_ct),
            ('can_manage_presence', 'Peut gérer les présences', presence_ct),
            ('can_view_all_reports', 'Peut voir tous les rapports', presence_ct),
            ('can_generate_reports', 'Peut générer des rapports', presence_ct),
        ]

        for codename, name, content_type in permissions_to_create:
            perm = Permission.objects.filter(codename=codename, content_type=content_type).first()
            if perm:
                self.stdout.write(f"  ⚠️ La permission existe déjà: {name}")
                continue

            if dry_run:
                self.stdout.write(f"  🔍 {name}: sera créée")
            else:
                perm = Permission.objects.create(
                    codename=codename,
                    name=name,
                    content_type=content_type
                )
                self.stdout.write(f"  ✅ Créée: {name}")

    def create_groups_with_permissions(self, dry_run=False):
        """Créer les groupes avec leurs permissions"""
        self.stdout.write("\n👥 Configuration des groupes...")

        if dry_run:
            self.stdout.write("  🔍 Groupes qui seront créés/mis à jour: Admin, Managers, RH, Staff")
            return

        permissions = {
            'can_view_all_employees': Permission.objects.get(codename='can_view_all_employees'),
            'can_manage_employee': Permission.objects.get(codename='can_manage_employee'),
            'can_manage_presence': Permission.objects.get(codename='can_manage_presence'),
            'can_view_all_reports': Permission.objects.get(codename='can_view_all_reports'),
            'can_generate_reports': Permission.objects.get(codename='can_generate_reports'),
        }

        groups_config = {
            'Admin': list(permissions.values()),
            'Managers': [
                permissions['can_view_all_employees'],
                permissions['can_manage_presence'],
                permissions['can_view_all_reports'],
                permissions['can_generate_reports']
            ],
            'RH': [
                permissions['can_view_all_employees'],
                permissions['can_manage_employee'],
                permissions['can_manage_presence'],
                permissions['can_view_all_reports'],
                permissions['can_generate_reports']
            ],
            'Staff': [permissions['can_manage_presence']]
        }

        for group_name, group_permissions in groups_config.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.set(group_permissions)
            status = "✅ Créé" if created else "🔄 Mis à jour"
            self.stdout.write(f"  {status}: {group_name} ({len(group_permissions)} permissions)")

    def assign_users_to_groups(self, dry_run=False):
        """Assigner les utilisateurs aux groupes selon leur rôle"""
        self.stdout.write("\n🎯 Attribution des utilisateurs...")

        if not dry_run:
            groups = {
                'Admin': Group.objects.get(name='Admin'),
                'Managers': Group.objects.get(name='Managers'),
                'RH': Group.objects.get(name='RH'),
                'Staff': Group.objects.get(name='Staff')
            }

        users = User.objects.all()
        stats = {'Admin': 0, 'Managers': 0, 'RH': 0, 'Staff': 0}

        for user in users:
            target_group = None

            if getattr(user, 'is_superuser', False) or getattr(user, 'is_admin', False):
                target_group = 'Admin'
            elif getattr(user, 'is_manager', False):
                target_group = 'Managers'
            elif getattr(user, 'is_rh', False):
                target_group = 'RH'
            elif hasattr(user, 'role'):
                role = getattr(user, 'role', '').lower()
                if role == 'admin':
                    target_group = 'Admin'
                elif role == 'manager':
                    target_group = 'Managers'
                elif role == 'rh':
                    target_group = 'RH'
                else:
                    target_group = 'Staff'
            else:
                target_group = 'Staff'

            if target_group:
                stats[target_group] += 1
                
                if dry_run:
                    current_groups = [g.name for g in user.groups.all()]
                    self.stdout.write(f"  🔍 {user.username}: {current_groups} → {target_group}")
                else:
                    user.groups.clear()
                    user.groups.add(groups[target_group])
                    self.stdout.write(f"  👤 {user.username} → {target_group}")

        return stats

    def create_missing_employees(self, dry_run=False):
        """Créer les employés manquants"""
        self.stdout.write("\n👷 Vérification des employés...")

        users_without_employee = []
        for user in User.objects.all():
            try:
                user.employe
            except Employe.DoesNotExist:
                users_without_employee.append(user)

        if not users_without_employee:
            self.stdout.write("  ✅ Tous les utilisateurs ont déjà un employé associé")
            return 0

        if dry_run:
            self.stdout.write(f"  🔍 {len(users_without_employee)} employés seront créés")
            for user in users_without_employee:
                self.stdout.write(f"    - {user.username}")
            return len(users_without_employee)

        created_count = 0
        for user in users_without_employee:
            employe = Employe.objects.create(
                user=user,
                nom=user.last_name or user.username,
                prenom=user.first_name or "Prénom",
                email=user.email or f"{user.username}@example.com",
                poste="Employé",
            )
            created_count += 1
            self.stdout.write(f"  ✅ Employé créé pour {user.username}: {employe}")

        return created_count

    def verify_setup(self):
        """Vérification finale de la configuration"""
        self.stdout.write("\n🔍 VÉRIFICATION...")

        problematic_users = []
        for user in User.objects.all():
            groups = [g.name for g in user.groups.all()]
            has_presence_perm = user.has_perm('api.can_manage_presence')
            
            try:
                user.employe
                has_employee = True
            except Employe.DoesNotExist:
                has_employee = False

            if not groups or not has_presence_perm:
                problematic_users.append(user.username)

            self.stdout.write(
                f"  👤 {user.username}: "
                f"Groupes={groups} "
                f"Presence={'✅' if has_presence_perm else '❌'} "
                f"Employé={'✅' if has_employee else '❌'}"
            )

        if problematic_users:
            self.stdout.write(
                self.style.WARNING(f"⚠️ Utilisateurs avec problèmes: {', '.join(problematic_users)}")
            )
