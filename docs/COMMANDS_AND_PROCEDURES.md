# Commands and Procedures Guide

This guide provides comprehensive information about all commands, procedures, and best practices for the IP Case Platform.

## Table of Contents
- [Development Commands](#development-commands)
- [Database Commands](#database-commands)
- [Import/Export Commands](#importexport-commands)
- [When to Run Each Command](#when-to-run-each-command)
- [CSRF Token Issues](#csrf-token-issues)
- [Git Workflow](#git-workflow)
- [Backup Procedures](#backup-procedures)
- [Common Issues and Solutions](#common-issues-and-solutions)

---

## Development Commands

### Start Development Server
```bash
python manage.py runserver 127.0.0.1:8000
```
**When to use:** When you want to test the application locally.

**Note:** The development server automatically reloads when you save changes to Python files. You don't need to restart it for code changes, but you may need to refresh your browser.

### Create Database Migrations
```bash
python manage.py makemigrations
```
**When to use:** After modifying Django models (`cases/models.py`).

**What it does:** Detects changes in your models and creates migration files in `cases/migrations/`.

### Apply Database Migrations
```bash
python manage.py migrate
```
**When to use:** After creating migrations with `makemigrations`.

**What it does:** Applies the pending migrations to the database, updating the schema.

### Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
**When to use:** When you need to create an admin account to access the Django admin panel.

### Collect Static Files
```bash
python manage.py collectstatic
```
**When to use:** Before deploying to production or after adding new static files.

**What it does:** Copies all static files from apps into a single directory for serving.

### Backup Database
```bash
python manage.py backup_db
```
**When to use:** Before making significant changes or regularly to ensure data safety.

**What it does:** Creates a backup of the database in the `backups/` folder and syncs to Google Drive (if configured).

---

## Import/Export Commands

### Export Applications to CSV
**Via Web Interface:**
1. Go to Applications list page (`/`)
2. Click **Export CSV** button
3. CSV file downloads automatically

**Features:**
- Exports all application fields
- Includes timestamps (created_at, updated_at)
- Proper date formatting (YYYY-MM-DD)
- Ordered by creation date (newest first)

### Import Applications from CSV
**Via Web Interface:**
1. Go to Applications list page (`/`)
2. Click **Import CSV** button
3. Select a CSV file from your computer
4. Click **Import CSV**
5. Review import summary (success count + any errors)

**CSV Format Requirements:**
- Must have header row with these columns:
  - Case Number, Client Type, Client ID, Sequence, Folder Number, Application Name, Application Type, Trademark No, Case No, Class Numbers, Filing Date, Application Year, Applicant Name, Trading As, Applicant Type, Address, City, Agent Name, Agent Address, Jurisdiction, Dispatch Status, Demand Note Date, Current Stage, Current Sub Stage, Current Status, Created At, Updated At
- Dates must be in YYYY-MM-DD format
- Case Numbers are checked for duplicates (skipped if exists)
- Download sample CSV template from import page

**Import Behavior:**
- Skips duplicate case numbers
- Shows error messages for failed rows
- Continues processing even if some rows fail
- Creates audit logs for imported applications

**Best Practices:**
1. Export current data first as backup
2. Review CSV file before importing
3. Start with small batch to test
4. Check import summary for errors
5. Verify imported data in application list

---

## Database Commands

### View Database Shell
```bash
python manage.py dbshell
```
**When to use:** When you need to run SQL queries directly on the database.

### Reset Database (Warning: Deletes All Data)
```bash
# Delete the database file
rm db.sqlite3
# Or on Windows:
del db.sqlite3

# Then re-run migrations
python manage.py migrate
```
**When to use:** Only when you need to completely reset the database structure and data.

### Inspect Database Schema
```bash
python manage.py sqlmigrate cases <migration_number>
```
**When to use:** To see the SQL that will be executed by a migration before applying it.

---

## When to Run Each Command

### After Model Changes
1. Modify `cases/models.py`
2. Run: `python manage.py makemigrations`
3. Run: `python manage.py migrate`
4. **No server restart needed** (Django auto-reloads)

### After Template Changes
1. Modify HTML templates in `cases/templates/`
2. **No commands needed** - just refresh your browser
3. **No server restart needed**

### After Static File Changes (CSS/JS/Fonts)
1. Modify files in `cases/static/`
2. **No commands needed** for development - just refresh browser
3. For production: Run `python manage.py collectstatic`

### After Settings Changes
1. Modify `ip_case_platform/settings.py`
2. **Server restart required** - stop and start the server
3. If using background server, kill it and restart

### After View/URL Changes
1. Modify `cases/views.py` or `cases/urls.py`
2. **No commands needed** - just refresh browser
3. **No server restart needed** (Django auto-reloads)

### After Adding New Dependencies
1. Modify `requirements.txt`
2. Run: `pip install -r requirements.txt`
3. **No server restart needed** unless the dependency requires server config

---

## CSRF Token Issues

### What is CSRF Token?
CSRF (Cross-Site Request Forgery) protection is a security feature that ensures form submissions come from your site.

### Common Error Messages
```
Forbidden (403)
CSRF verification failed. Request aborted.
Origin checking failed - http://127.0.0.1:XXXX does not match any trusted origins.
```

### Solutions

#### 1. Add Browser Preview Port to Trusted Origins
If using browser preview (different port), add it to `ip_case_platform/settings.py`:

```python
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "http://127.0.0.1,http://localhost,http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:56317,http://localhost:56317"
    ).split(",")
    if o.strip()
]
```
Replace `56317` with your browser preview port.

#### 2. Ensure CSRF Token in Forms
All POST forms must include `{% csrf_token %}`:

```html
<form method="post" action="{% url 'some_url' %}">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

#### 3. File Upload Forms
For file uploads, add `enctype="multipart/form-data"`:

```html
<form method="post" action="{% url 'some_url' %}" enctype="multipart/form-data">
    {% csrf_token %}
    <input type="file" name="file" />
</form>
```

#### 4. Clear Browser Cookies
Sometimes old cookies can cause issues:
1. Open browser DevTools (F12)
2. Go to Application/Storage tab
3. Clear cookies for localhost
4. Refresh the page

#### 5. Login Again
After login, CSRF tokens are rotated. If you submitted a form before logging in:
1. Refresh the page
2. Submit the form again

---

## Git Workflow

### Basic Workflow
```bash
# Check status
git status

# Add all changes
git add -A

# Commit changes
git commit -m "Descriptive message"

# Push to GitHub
git push
```

### Before Making Changes
```bash
# Pull latest changes
git pull
```

### View Commit History
```bash
git log --oneline
```

### Undo Last Commit (if not pushed)
```bash
git reset --soft HEAD~1
```

### View Diff
```bash
git diff
```

---

## Backup Procedures

### Manual Backup
```bash
python manage.py backup_db
```
- Creates backup in `backups/` folder
- Filename format: `db_backup_YYYYMMDD_HHMMSS.sqlite3`
- Automatically syncs to Google Drive (if configured)

### Automatic Backup
Automatic backups are configured in settings:
- `BACKUP_ENABLED`: Enable/disable auto-backup
- `BACKUP_INTERVAL_HOURS`: Backup interval in hours (default: 6)
- `BACKUP_RETENTION_DAYS`: How long to keep backups (default: 7)

### Restore from Backup
```bash
# Stop server if running
# Copy backup file to db.sqlite3
cp backups/db_backup_YYYYMMDD_HHMMSS.sqlite3 db.sqlite3
```

---

## Common Issues and Solutions

### Import Errors
**Issue:** `ModuleNotFoundError: No module named 'package_name'`

**Solution:**
```bash
pip install package_name
# Or install all from requirements
pip install -r requirements.txt
```

### Port Already in Use
**Issue:** `Address already in use`

**Solution:**
1. Find process using port:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   # Kill the process
   taskkill /PID <PID> /F
   ```
2. Or use a different port:
   ```bash
   python manage.py runserver 127.0.0.1:8001
   ```

### Database Locked
**Issue:** `database is locked`

**Solution:**
1. Stop the Django server
2. Delete `.sqlite3-shm` and `.sqlite3-wal` files
3. Restart server

### Static Files Not Loading
**Issue:** CSS/JS files not loading

**Solution:**
1. Check `STATIC_URL` in settings
2. For development, ensure `DEBUG = True`
3. For production, run `python manage.py collectstatic`

### PDF Export Issues
**Issue:** PDF generation errors

**Solution:**
- Ensure reportlab is installed: `pip install reportlab`
- Check file paths for logo images
- Verify site settings are configured

---

## Development Best Practices

### 1. Always Backup Before Major Changes
```bash
python manage.py backup_db
```

### 2. Use Descriptive Commit Messages
```
Good: "Add file upload functionality to Events section"
Bad: "update stuff"
```

### 3. Test Changes Locally First
- Use the development server
- Test all related functionality
- Check for errors in the console

### 4. Keep Requirements Updated
After installing new packages:
```bash
pip freeze > requirements.txt
```

### 5. Review Migrations Before Applying
```bash
python manage.py sqlmigrate <app_name> <migration_number>
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Start Server | `python manage.py runserver` |
| Create Migrations | `python manage.py makemigrations` |
| Apply Migrations | `python manage.py migrate` |
| Backup DB | `python manage.py backup_db` |
| Create Admin | `python manage.py createsuperuser` |
| Collect Static | `python manage.py collectstatic` |
| Git Add All | `git add -A` |
| Git Commit | `git commit -m "message"` |
| Git Push | `git push` |

---

## Environment Variables

Configure these in your environment or `.env` file:
- `DJANGO_SECRET_KEY`: Django secret key
- `DJANGO_DEBUG`: Debug mode (ON for True, OFF for False, or 1/0)
- `DJANGO_ALLOWED_HOSTS`: Comma-separated allowed hosts
- `DJANGO_CSRF_TRUSTED_ORIGINS`: Comma-separated trusted origins
- `DB_ENGINE`: Database engine (sqlite/postgres)
- `BACKUP_ENABLED`: Enable auto-backup (true/false)
- `BACKUP_INTERVAL_HOURS`: Backup interval
- `BACKUP_RETENTION_DAYS`: Backup retention period

---

## Settings File Configuration

The main settings file is located at `ip_case_platform/settings.py`.

### Key Settings

#### DEBUG Mode
```python
DEBUG = os.environ.get("DJANGO_DEBUG", "ON") == "ON"
```
- **Development**: Set to "ON" or "1" for detailed error pages
- **Production**: Set to "OFF" or "0" for security
- **Default**: ON (for development)

#### Allowed Hosts
```python
ALLOWED_HOSTS = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(",") if h.strip()]
```
- Add your production domain here when deploying

#### CSRF Trusted Origins
```python
CSRF_TRUSTED_ORIGINS = [
    o.strip()
    for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS",
        "http://127.0.0.1,http://localhost,http://127.0.0.1:8000,http://localhost:8000,http://127.0.0.1:56317,http://localhost:56317"
    ).split(",")
    if o.strip()
]
```
- Add browser preview ports or production URLs here
- Format: `http://domain:port`

#### Database Configuration
```python
_db_engine = os.environ.get("DB_ENGINE", "sqlite").lower()

if _db_engine in {"postgres", "postgresql"}:
    # PostgreSQL configuration
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME", "ip_case_platform"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get("DB_PASSWORD", ""),
            "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
            "PORT": os.environ.get("DB_PORT", "5432"),
        }
    }
else:
    # SQLite configuration (default)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
```

#### Backup Configuration
```python
BACKUP_ENABLED = os.environ.get('BACKUP_ENABLED', 'true').lower() == 'true'
BACKUP_INTERVAL_HOURS = int(os.environ.get('BACKUP_INTERVAL_HOURS', '6'))
BACKUP_RETENTION_DAYS = int(os.environ.get('BACKUP_RETENTION_DAYS', '7'))
```

#### Media and Static Files
```python
STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

### When to Modify Settings

#### After Changing Settings
- **Server restart required** - stop and start the server
- If using background server, kill it and restart

#### Common Settings Changes

1. **Toggle DEBUG Mode**
   - Change `DJANGO_DEBUG` environment variable or default value
   - Restart server

2. **Add New Host/Domain**
   - Add to `ALLOWED_HOSTS`
   - Add to `CSRF_TRUSTED_ORIGINS`
   - Restart server

3. **Change Database**
   - Set `DB_ENGINE` environment variable
   - Configure database credentials
   - Run migrations: `python manage.py migrate`

4. **Change Time Zone**
   - Modify `TIME_ZONE` setting
   - No server restart needed

5. **Update Backup Settings**
   - Modify backup environment variables
   - No server restart needed

### Production Deployment Checklist

Before deploying to production:
- [ ] Set `DEBUG = False`
- [ ] Set strong `SECRET_KEY` via environment variable
- [ ] Add production domain to `ALLOWED_HOSTS`
- [ ] Add production URL to `CSRF_TRUSTED_ORIGINS`
- [ ] Configure production database (PostgreSQL recommended)
- [ ] Set up proper email backend (SMTP)
- [ ] Run `python manage.py collectstatic`
- [ ] Configure proper web server (nginx + gunicorn)
- [ ] Set up SSL/TLS certificates
- [ ] Configure backup to remote storage

---

For additional help, refer to:
- Django Documentation: https://docs.djangoproject.com/
- Project README.md
- docs/WORKFLOW.md
- docs/BACKUP_GUIDE.md
