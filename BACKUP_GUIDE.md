# Backup Guide

## Manual Backup

Run the backup command manually:

```bash
python manage.py backup_db
```

This will create a timestamped backup in the `backups/` directory and keep only the last 7 backups.

## Automated Backup (Every 6 Hours)

### Windows Task Scheduler

1. Open Task Scheduler
2. Create a new task:
   - Name: `IP Case Platform Backup`
   - Trigger: Daily, repeat every 6 hours for 24 hours
   - Action: Start a program
     - Program: `python`
     - Arguments: `manage.py backup_db`
     - Start in: `g:\DS-Brandex` (your project directory)

### Linux/Mac Cron Job

Add to crontab:

```bash
crontab -e
```

Add this line (runs every 6 hours):

```
0 */6 * * * cd /path/to/DS-Brandex && python manage.py backup_db
```

## Backup to Google Drive

### Option 1: Google Drive Desktop (Recommended)

1. Install Google Drive for Desktop from https://www.google.com/drive/download/
2. Sign in with brandex004@gmail.com
3. Sync the `g:\DS-Brandex\backups\` folder to Google Drive

### Option 2: rclone

Install rclone and configure it with Google Drive:

```bash
rclone config
# Select "Google Drive" and authenticate with brandex004@gmail.com
```

Then add a scheduled task to sync after backup:

```bash
rclone sync g:\DS-Brandex\backups\ brandex-drive:IP-Case-Backups
```

## Environment Variables

Configure backup behavior via environment variables:

- `BACKUP_ENABLED`: Enable/disable backup (default: `true`)
- `BACKUP_INTERVAL_HOURS`: Backup interval in hours (default: `6`)
- `BACKUP_RETENTION_DAYS`: Number of days to keep backups (default: `7`)

Example:

```bash
set BACKUP_ENABLED=true
set BACKUP_INTERVAL_HOURS=6
set BACKUP_RETENTION_DAYS=7
```
