# Backup Guide

## Manual Backup

Run the backup command manually:

```bash
python manage.py backup_db
```

This will create a timestamped backup in the `backups/` directory and keep only the last 7 backups.

## Install rclone (Windows)

1. Download rclone from https://rclone.org/downloads/
2. Extract to a folder (e.g., `C:\rclone`)
3. Add `C:\rclone` to your system PATH
4. Verify installation:
   ```bash
   rclone version
   ```

## Configure rclone with Google Drive

1. Run rclone config:
   ```bash
   rclone config
   ```

2. Follow the prompts:
   - Type `n` for new remote
   - Name: `brandex-drive` (or your preferred name)
   - Type: `drive` (Google Drive)
   - Scope: `1` (Full access all files)
   - Root folder ID: Leave blank
   - Service Account Credentials: Leave blank
   - Advanced config: `n`
   - Auto config: `y` (this will open a browser window)
   - Sign in with brandex004@gmail.com
   - Grant permissions
   - Configure as team drive: `n`
   - Confirm: `y`

3. Verify connection:
   ```bash
   rclone ls brandex-drive:
   ```

## Create Google Drive Folder

1. Go to https://drive.google.com
2. Sign in with brandex004@gmail.com
3. Create a folder named `IP-Case-Backups`

## Update Backup Management Command

The backup command has been updated to automatically sync to Google Drive using rclone after each backup. You just need to ensure rclone is configured.

## Automated Backup (Every 6 Hours)

### Windows Task Scheduler

1. Open Task Scheduler
2. Create a new task:
   - Name: `IP Case Platform Backup with Sync`
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

## Manual Sync to Google Drive

If you need to manually sync backups to Google Drive:

```bash
rclone sync g:\DS-Brandex\backups\ brandex-drive:IP-Case-Backups
```

## Environment Variables

Configure backup behavior via environment variables:

- `BACKUP_ENABLED`: Enable/disable backup (default: `true`)
- `BACKUP_INTERVAL_HOURS`: Backup interval in hours (default: `6`)
- `BACKUP_RETENTION_DAYS`: Number of days to keep backups (default: `7`)
- `RCLONE_REMOTE`: rclone remote name (default: `brandex-drive`)
- `RCLONE_DESTINATION`: Google Drive folder (default: `IP-Case-Backups`)

Example:

```bash
set BACKUP_ENABLED=true
set BACKUP_INTERVAL_HOURS=6
set BACKUP_RETENTION_DAYS=7
```
