# IP Case Platform — Workflow & Project Status

**Purpose:** Office LAN system for managing Trademark cases (Applications, Timeline, Assignments, Documents, Audit Log).

---

## 1. Quick Start (How to use day-to-day)

### 1.1 Login
- URL: `http://127.0.0.1:8000/accounts/login/`
- Enter username and password
- Click Login

### 1.2 Reset Password (Admin-only)
Since this is an office LAN tool, password reset is done by admin:

1. Admin goes to: `http://127.0.0.1:8000/admin/`
2. Navigate to **Users** (under Authentication and Authorization)
3. Click the user
4. Click “Change password” (top of user page)
5. Set new password and save

### 1.3 Create a New Application (Case)
1. From Applications list (`/`), click **+ New Application**
2. Fill:
   - Folder # (Case ID) — e.g. `X-454-004`
   - Client Type (N/X/A)
   - Application Type (Trademark / Copyright / NTN / Company)
   - Application Name
   - Trademark No
   - Applicant details + City
   - Agent details + Jurisdiction + Dispatch
   - Logo (optional image upload)
3. Click **Create Application**
4. You’re redirected to the case detail page.

### 1.4 Add Event (Timeline update)
On case detail page:

- **Quick buttons** (top right of Status Box):
  - ➕ Filing
  - ✅ Acknowledgement
  - ⚠️️ Objection
  - 🎗️ Publication
  - 💰 Demand Note
  - 🏆 Certificate

Click any button → modal opens → fill:
- Event Type (pre-selected by button)
- Sub-Status (optional)
- Deadline
- Document Upload or PDF
- Notes

Click **Save** → Event added and case status updates automatically (sub-status → stage).

### 1.5 Assignments
- On case detail page, under **Assignments** block:
- Fill:
  - Assigned To (user dropdown)
  - Due Date
  - Status (Pending/Completed/Overdue)
  - Notes
- Click **Add**

Assignments show as cards with color:
- Red left border = overdue
- Yellow left border = due soon
- Blue left border = normal

### 1.6 Documents
- Under **Documents** block:
- Fill:
  - File Type (Logo / Certificate / Notice / Other)
  - File Path (shared drive / SharePoint link)
  - Preview enabled checkbox
- Click **Add Document Link**

---

## 2. Project Status (What’s Built)

### 2.1 Backend (Django)
- **Project:** `ip_case_platform`
- **App:** `cases`
- **Database:** SQLite (default), PostgreSQL supported via env vars

### 2.2 Data Models
- **Application** (main case)
  - Folder #, Client Type, Application Type, Application Name
  - Trademark No, Application #, Class, Filing Date, Year
  - Applicant, Trading As, Applicant Type, Address, City
  - Agent, Agent Address, Jurisdiction, Dispatch Status
  - Logo upload (ImageField)
  - Current Stage, Sub-Status, Status
  - Audit log on changes

- **Event** (timeline)
  - Event Type (Filing / Objection / Publication / Demand / Certificate / Other)
  - Date/Time, Stage, Sub-Status, Deadline, Notes, Document Link
  - When saved, updates Application’s current stage/status

- **Assignment**
  - Assigned To (user), Due Date, Status, Notes

- **DocumentLink**
  - File Type, File Path (link only), Preview enabled

- **AuditLog** (append-only)
  - Action type, field changed, old/new value, changed by, timestamp

### 2.3 UI (Victorian Legal Theme)
- Victorian Legal Elegance style (premium, archival, authoritative)
- Colors: Deep Burgundy (#722F37), Forest Green (#2E5339), Antique Gold (#B8860B)
- Fonts: Syndra (headings), Mision (body)
- Small-caps utility class (.small-cap) for labels/headings only
- Border radius: 4px, hard shadows (0px 4px 0px rgba(0,0,0,0.15))
- Grid layout on detail page:
  - Case Info block
  - Status Box + Quick Event Buttons
  - Timeline (vertical)
  - Assignments (cards)
  - Documents
  - Audit Log

### 2.4 Admin (Django Admin)
- All models registered
- Inlines: Event, Assignment, Document
- AuditLog: read-only (no add/edit)

---

## 3. Tech Stack

- Django 6.0.4
- Pillow 11.3.0 (image uploads)
- Bootstrap 5.3.3 (CSS framework)
- Python 3.13

---

## 4. Dev Server

Run locally:

```bash
python manage.py runserver 127.0.0.1:8000
```

URLs:
- Main list: `http://127.0.0.1:8000/`
- Admin: `http://127.0.0.1:8000/admin/`
- Login: `http://127.0.0.1:8000/accounts/login/`

---

## 5. GitHub Repo

- Repo: `https://github.com/0utLawzz/DS-Brandex`
- Branch: `main`
- `.gitignore` excludes:
  - `Sample-Cases/`
  - `media/`
  - Python caches, logs, DB

---

## 6. Next Steps / TODO

1. ~~**Folder Number auto-generator** (`[ClientType]-[ClientID]-[Sequence]`) so IDs are auto-made.~~ ✅ COMPLETED
2. ~~**Dashboard** (deadlines + overdue summary).~~ ✅ COMPLETED
3. ~~**Assignment improvements** (agent list, overdue auto-status, “My Tasks” page).~~ ✅ COMPLETED
4. **Dispatch workflow** (Certificate Received → Print → Dispatch) with one-click actions.
5. (Optional) Email-based password reset if needed for remote users.

## 7. Recently Completed Features (April 2026)

### Folder Number Auto-Generator
- Automatic folder number generation in format: `[ClientType]-[ClientID]-[Sequence]`
- Example: `X-454-001`, `A-123-001`
- Folder number is optional in forms - auto-generated if client_id is provided
- Sequence auto-increments per client_type + client_id combination

### Dashboard
- Overview page with deadline summaries
- Shows overdue assignments, assignments due soon
- Shows overdue events and events with upcoming deadlines
- Stage summary (count of applications per stage)
- Recent applications list
- Accessible at `/` (root URL)

### Assignment Improvements
- **Agent Model**: Added Agent model for managing external agents
- **Auto-Status**: Assignments automatically marked as overdue when due date passes
- **My Tasks Page**: Personal task view for each user showing:
  - Overdue assignments
  - Pending assignments
  - Completed assignments
  - Upcoming events for assigned applications
- Accessible at `/my-tasks/`
