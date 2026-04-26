# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**COSET Data Warehouse** — A Django + Wagtail CMS for the College of Science, Engineering and Technology. It manages institutional data (people, units, courses, programs, grants, research groups) via a custom admin dashboard, and serves a public-facing website through Wagtail pages.

## Commands

### Development

```bash
# Set settings module (required before any manage.py command)
export DJANGO_SETTINGS_MODULE=coset.settings.dev

python manage.py runserver          # Start dev server
python manage.py migrate            # Apply migrations
python manage.py makemigrations     # Create new migrations
```

### CSS / Tailwind

Tailwind is configured in `tailwind.config.js` and targets `base/templates/` and `core/templates/`. The compiled output is `base/static/css/output.css`. Run Tailwind's CLI separately to rebuild CSS when templates change:

```bash
npx tailwindcss -i ./base/static/css/input.css -o ./base/static/css/output.css --watch
```

### Management Commands

```bash
python manage.py initialize   # Load menu structure from fixtures
python manage.py add_pages    # Add default Wagtail page tree
python manage.py import_json  # Bulk import JSON data
```

### Settings Modules

| Environment | Module |
|---|---|
| Development | `coset.settings.dev` |
| Production | `coset.settings.production` |

Dev uses SQLite + `django-browser-reload`; production enforces SSL, uses SMTP email, and reads `DJANGO_SECRET_KEY` from the environment.

## Architecture

### Apps

**`base/`** — Wagtail page models and public website.
- Page types: `HomePage`, `StandardPage`, `SectionPage`, `PostSectionPage`, `PostPage`, `CourseIndexPage`, `PersonIndexPage`, `NewsEventIndexPage`, `InterestFormPage`
- Custom Wagtail blocks: `FloatingImageBlock`, `RichTextBlock`, `TableBlock`, `MarkdownBlock`
- Custom template tags and Wagtail hooks for admin sidebar customization

**`core/`** — Data warehouse with Django admin-style custom views.
- Models: `Person`, `Unit`, `Course`, `Program`, `Grant`, `Research`, `Room`
- Views at `/manage/` require staff/superuser — not Wagtail CMS, not Django admin
- JSON import system at `/manage/import/`

**`search/`** — Thin Wagtail search wrapper.

### URL Routing

| Prefix | Purpose |
|---|---|
| `/admin/` | Django admin |
| `/cms/` | Wagtail CMS editor |
| `/manage/` | COSET data warehouse (core app) |
| `/documents/` | Wagtail document library |
| `/search/` | Site search |
| `/` | Wagtail page tree (public site) |

### Key Model Relationships

- `Person` ← FK from `Grant.principal_investigator`, `Room.occupant`, `Room.point_of_contact`
- `Research` → M2M to `Person` (co_investigators, student_researchers) and `Grant`
- `Program` → M2M to `Course` (required_courses, elective_courses)
- `Course` → M2M self (prerequisites)
- `Unit` → FK `Person` (principal, admin_contact)

Departments are hardcoded as choices on models (Biology, Chemistry, Mathematical Sciences, Physics, and the five engineering departments).

### Template Organization

- Public pages: `base/templates/base/`
- Data warehouse views: `core/templates/core/`
- Shared base: `base/templates/base/base.html`

### Data Import

JSON files are uploaded through `/manage/import/` and processed by `core/management/commands/import_json.py`. Supported entity types: `person`, `unit`, `course`, `program`, `grant`, `research`, `room`.
