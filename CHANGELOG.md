# Changelog

## v1.0.0.3 - 24/Apr/26

- add: HOME button to header
- add: charts (bar charts) to dashboard and application detail pages for visual status tracking
- add: search page for Trademark Number (TM No) with clickable results
- change: links from folder number to trademark number (TM No is now the primary key for display)
- change: client type text to X (CLIENTS) and N (NOOR BAAF)
- remove: bold/strong formatting from templates (fw-bold class and strong tags)
- add: assignment status chart on application detail page
- add: stage summary bar chart on dashboard

## v1.0.0.2 - 24/Apr/26

- add: Victorian Legal UI theme (replaces De Stijl)
- add: custom self-hosted fonts (Syndra for headings, Mision for body)
- add: small-caps utility class (.small-cap) for labels/headings only
- fix: typography - normal weights (no bold), 11pt body, 12pt headings
- fix: unbold stat boxes, buttons, and event list items
- fix: CSRF trusted origins for preview port (54691) and standard dev ports
- update: VICTORIAN_THEME_GUIDE.md with implementation instructions
- update: table font size reduced by ~1-2pt for denser dashboard tables

## v1.0.0.1 - 23/Apr/26

- add: initial Django project scaffold
- add: core models (Application, Event, Assignment, AuditLog, DocumentLink)
- add: Django Admin configuration for quick internal usage
