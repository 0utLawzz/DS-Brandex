import os
import shutil
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup the database to a backup directory'

    def handle(self, *args, **options):
        # Get database path (SQLite)
        db_path = settings.DATABASES['default']['NAME']
        if isinstance(db_path, Path):
            db_path = str(db_path)

        # Create backup directory
        backup_dir = settings.BASE_DIR / 'backups'
        backup_dir.mkdir(exist_ok=True)

        # Create timestamped backup filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'db_backup_{timestamp}.sqlite3'
        backup_path = backup_dir / backup_filename

        # Copy database file
        try:
            shutil.copy2(db_path, backup_path)
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully backed up database to {backup_path}'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to backup database: {e}')
            )

        # Keep only last 7 backups (to save space)
        backups = sorted(backup_dir.glob('db_backup_*.sqlite3'), reverse=True)
        for old_backup in backups[7:]:
            try:
                old_backup.unlink()
                self.stdout.write(
                    self.style.WARNING(f'Deleted old backup: {old_backup.name}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to delete old backup {old_backup.name}: {e}')
                )
