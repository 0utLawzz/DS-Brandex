import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Backup the database to a backup directory and sync to Google Drive via rclone'

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
            return

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

        # Sync to Google Drive using rclone
        rclone_remote = os.environ.get('RCLONE_REMOTE', 'brandex-drive')
        rclone_destination = os.environ.get('RCLONE_DESTINATION', 'IP-Case-Backups')
        rclone_path = os.environ.get('RCLONE_PATH', r'C:\rclone\rclone.exe')
        
        # Check if rclone is available
        try:
            subprocess.run([rclone_path, 'version'], check=True, capture_output=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.stdout.write(
                self.style.WARNING('rclone not found. Skipping Google Drive sync. Install rclone and configure it following BACKUP_GUIDE.md')
            )
            return

        # Sync backups to Google Drive
        try:
            self.stdout.write(f'Syncing backups to Google Drive ({rclone_remote}:{rclone_destination})...')
            result = subprocess.run(
                [
                    rclone_path, 'sync',
                    str(backup_dir),
                    f'{rclone_remote}:{rclone_destination}',
                    '--progress'
                ],
                check=True,
                capture_output=True,
                text=True
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully synced backups to Google Drive')
            )
        except subprocess.CalledProcessError as e:
            self.stdout.write(
                self.style.ERROR(f'Failed to sync to Google Drive: {e}')
            )
            if e.stderr:
                self.stdout.write(self.style.ERROR(f'Error output: {e.stderr}'))
