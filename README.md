# Office IP Case Platform (Trademark)

A simple **office LAN** case database for managing **trademark applications** with:

- Case/Application master record
- Stage + sub-stage workflow
- Event timeline (legal actions)
- Assignments
- Strict audit log (append-only)
- Document links (shared drive / SharePoint links)

## Features

- Add Applications (Cases)
- Add Events (timeline)
- Track current stage/sub-stage and current status
- Assign cases to users
- Audit trail of changes

## Workflow / How it Works

1. Create an **Application** record (folder number, applicant, class, etc.)
2. Add **Events** as progress happens (filed, objection, reply filed, publication, etc.)
3. Each new Event updates the Application's current status/stage/sub-stage
4. Assign work using **Assignments**
5. Review accountability using **Audit Logs**

## Manual Usage Guide (Local)

1. Install dependencies

```bash
python -m pip install -r requirements.txt
```

1. Create database tables

```bash
python manage.py makemigrations
python manage.py migrate
```

1. Create admin user

```bash
python manage.py createsuperuser
```

1. Run server

```bash
python manage.py runserver
```

1. Open admin

- [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Input / Output

- **Input**: Application details, Events, Assignments, Document links
- **Output**: Searchable case database, timeline history, audit trail, due dates

## File Structure

- `ip_case_platform/` Django project settings
- `cases/` core app (models/admin)
- `Sample-Cases/` example PDFs/docs (your files)

## Example Output

- Application list filtered by stage
- Case detail with inline Events + Assignments
- Audit log entries showing who changed what and when

---

Author: 0utLawzz
Email: net2tara@gmail.com

For similar projects or ideas, feel free to contact
