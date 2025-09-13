import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings") 
django.setup()

from core.management.commands.setup_groups import Command

cmd = Command()
cmd.handle(dry_run=False, create_employees=True)

