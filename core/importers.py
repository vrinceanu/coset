"""
COSET DataWarehouse – JSON Import Utilities

Handles importing data from JSON files into the database.
Each importer follows the same result structure:
    {'created': int, 'updated': int, 'errors': int, 'error_details': list}

Usage (management command or view):
    from core.importers import run_json_import
    result = run_json_import('person', data_list_or_dict)
"""

import logging
from decimal import Decimal, InvalidOperation
from datetime import date

logger = logging.getLogger(__name__)


def _parse_date(value):
    """Parse YYYY-MM-DD string to date. Returns None on failure."""
    if not value:
        return None
    try:
        return date.fromisoformat(str(value))
    except ValueError:
        return None


def _parse_decimal(value):
    if value is None or value == '':
        return None
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return None


def _result():
    return {'created': 0, 'updated': 0, 'errors': 0, 'error_details': []}


# ─────────────────────────────────────────────
# Room importer
# ─────────────────────────────────────────────

def import_rooms(data):
    """
    Expected JSON structure (list):
    [
      {
        "building": "Science Hall",
        "room_number": "101",
        "purpose": "office",
        "department": "Computer Science",
        "notes": ""
      }
    ]
    purpose choices: office, classroom, lab, conference, storage, server, other
    """
    from .models import Room
    result = _result()
    if not isinstance(data, list):
        data = [data]
    for item in data:
        try:
            obj, created = Room.objects.update_or_create(
                building=item['building'],
                room_number=item['room_number'],
                defaults={
                    'purpose': item.get('purpose', 'office'),
                    'department': dept,
                    'notes': item.get('notes', ''),
                }
            )
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append(
                f"Room '{item.get('building')} {item.get('room_number')}': {e}")
    return result


# ─────────────────────────────────────────────
# Person importer
# ─────────────────────────────────────────────
def import_persons(data):
    """
    Expected JSON structure (list):
    [
      {
        "last_first": "Smith, John A.",
        "name": "John A. Smith",
        "active": true,
        "classification": "faculty",
        "rank": "professor",
        "department": "PHYS",
        "admin_role": "Department Chair",
        "room_building": "Science Hall",
        "room_number": "205",
        "email": "jsmith@university.edu",
        "phone": "555-1234",
        "cv_link": "https://...",
        "photo": "media/person_photos/jsmith.jpg",
        "biography": "Dr. Smith is..."
      }
    ]
    classification choices: faculty, staff
    rank choices: professor, associate_professor, assistant_professor, lecturer,
                  instructor, adjunct, researcher, director, coordinator, specialist, other
    """
    from .models import Person, Room
    result = _result()
    if not isinstance(data, list):
        data = [data]
    for item in data:
        try:
            obj, created = Person.objects.update_or_create(
                last_first=item['last_first'],
                defaults={
                    'name': item.get('name', item['last_first']),
                    'slug': item.get('slug', ''),
                    'active': item.get('active', True),
                    'classification': item.get('classification', 'faculty'),
                    'rank': item.get('rank', ''),
                    'department': item.get('department', 'NA'),
                    'admin_role': item.get('admin_role', ''),
                    'room': item.get('room', ''),
                    'email': item.get('email', ''),
                    'phone': item.get('phone', ''),
                    'cv_link': item.get('cv_link', ''),
                    'photo': 'person_photos/' + item.get('photo', ''),
                    'biography': item.get('biography', ''),
                }
            )
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append(
                f"Person '{item.get('last_first')}': {e}")
    return result


# ─────────────────────────────────────────────
# Unit importer
# ─────────────────────────────────────────────

def import_units(data):
    """
    Expected JSON structure (list):
    [
      {
        "name": "Department of Computer Science",
        "slug": "computer-science",
        "description": "...",
        "url": "https://...",
        "unit_type": "academic",
        "room": "SB 101",
        "principal": "john-smith",
        "interim": false,
        "principal_email": "jsmith@university.edu",
        "head_phone": "555-1000",
        "admin_last_first": "Jones, Mary",
        "admin_email": "mjones@university.edu",
        "admin_phone": "555-1001",
        "admin_fax": "555-1002",
        "logo": "computer-logo.jpg",
        "photo": "computrt-logo.jpg"
      }
    ]
    unit_type choices: administrative, academic, research
    """
    from .models import Unit, Person, Room
    result = _result()
    if not isinstance(data, list):
        data = [data]
    for item in data:
        try:
            principal = None
            if item.get('principal'):
                principal = Person.objects.filter(
                    slug=item['principal']).first()

            admin = None
            if item.get('admin'):
                admin = Person.objects.filter(
                    slug=item['admin']).first()

            obj, created = Unit.objects.update_or_create(
                name=item['name'],
                defaults={
                    'slug': item.get('slug', ''),
                    'description': item.get('description', ''),
                    'url': item.get('url', ''),
                    'unit_type': item.get('unit_type', 'academic'),
                    'room': item.get('slug', ''),
                    'principal': principal,
                    'interim': item.get('interim', False),
                    'principal_email': item.get('principal_email', ''),
                    'principal_phone': item.get('principal_phone', ''),
                    'admin': admin,
                    'admin_email': item.get('admin_email', ''),
                    'admin_phone': item.get('admin_phone', ''),
                    'admin_fax': item.get('admin_fax', ''),
                    'logo': item.get('logo', ''),
                    'photo': item.get('photo', ''),
                }
            )
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append(f"Unit '{item.get('name')}': {e}")
    return result


# ─────────────────────────────────────────────
# Course importer
# ─────────────────────────────────────────────

def import_courses(data):
    """
    Expected JSON structure (list):
    [
      {
        "code": "CS 1301",
        "name": "Introduction to Computer Science",
        "description": "...",
        "department": "Computer Science",
        "lecture_credits": 3,
        "lab_credits": 1
      }
    ]
    """
    from .models import Course
    result = _result()
    if not isinstance(data, list):
        data = [data]
    for item in data:
        try:

            obj, created = Course.objects.update_or_create(
                code=item['code'],
                department=item.get('department', 'NA'),
                defaults={
                    'name': item['name'],
                    'description': item.get('description', ''),
                    'lecture_credits': _parse_decimal(item.get('lecture_credits', 3)) or 3,
                    'lab_credits': _parse_decimal(item.get('lab_credits', 0)) or 0,
                }
            )
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append(f"Course '{item.get('code')}': {e}")
    return result


# ─────────────────────────────────────────────
# Program importer
# ─────────────────────────────────────────────

def import_programs(data):
    """
    Expected JSON structure (list):
    [
      {
        "name": "Computer Science",
        "degree_conferred": "BS",
        "focus": "major",
        "department": "Computer Science",
        "active": true,
        "level": "undergraduate",
        "description": "...",
        "admission_requirements": "...",
        "credit_hours": 120,
        "major_requirements": "...",
        "other_requirements": "...",
        "electives": "...",
        "degree_plan": "..."
      }
    ]
    degree_conferred choices: BS, BA, MS, MA, PhD, EdD, Other
    focus choices: major, minor
    level choices: undergraduate, graduate
    """
    from .models import Program
    result = _result()
    if not isinstance(data, list):
        data = [data]
    for item in data:
        try:
            obj, created = Program.objects.update_or_create(
                name=item['name'],
                degree_conferred=item.get('degree_conferred', 'BS'),
                defaults={
                    'focus': item.get('focus', 'major'),
                    'department': item.get('department', 'NA'),
                    'active': item.get('active', True),
                    'level': item.get('level', 'undergraduate'),
                    'description': item.get('description', ''),
                    'admission_requirements': item.get('admission_requirements', ''),
                    'credit_hours': item.get('credit_hours', 120),
                    'major_requirements': item.get('major_requirements', ''),
                    'other_requirements': item.get('other_requirements', ''),
                    'electives': item.get('electives', ''),
                    'degree_plan': item.get('degree_plan', ''),
                }
            )
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append(f"Program '{item.get('name')}': {e}")
    return result


# ─────────────────────────────────────────────
# Grant importer
# ─────────────────────────────────────────────

def import_grants(data):
    """
    Expected JSON structure (list):
    [
      {
        "title": "AI Research Initiative",
        "department": "Computer Science",
        "granting_agency": "National Science Foundation",
        "program": "CISE",
        "principal_investigator": "Smith, John A.",
        "dollar_amount": 500000.00,
        "start_date": "2023-09-01",
        "end_date": "2026-08-31",
        "notes": ""
      }
    ]
    """
    from .models import Grant, Person
    result = _result()
    if not isinstance(data, list):
        data = [data]
    for item in data:
        try:
            pi = None
            if item.get('principal_investigator'):
                pi = Person.objects.filter(
                    last_first=item['principal_investigator']).first()

            obj, created = Grant.objects.update_or_create(
                title=item['title'],
                defaults={
                    'department': item.get('department', 'NA'),
                    'granting_agency': item.get('granting_agency', ''),
                    'program': item.get('program', ''),
                    'principal_investigator': pi,
                    'dollar_amount': _parse_decimal(item.get('dollar_amount')),
                    'start_date': _parse_date(item.get('start_date')),
                    'end_date': _parse_date(item.get('end_date')),
                    'notes': item.get('notes', ''),
                }
            )
            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append(f"Grant '{item.get('title')}': {e}")
    return result


# ─────────────────────────────────────────────
# Research importer
# ─────────────────────────────────────────────

def import_research(data):
    """
    Expected JSON structure (list):
    [
      {
        "name": "Autonomous Systems Lab",
        "principal_investigator": "Smith, John A.",
        "co_investigators": ["Jones, Mary B.", "Lee, Robert C."],
        "student_researchers": [],
        "publications": "Smith et al. (2023)...",
        "grants": ["AI Research Initiative"],
        "capabilities": "...",
        "equipment": "...",
        "personnel": "...",
        "safety_requirements": "..."
      }
    ]
    """
    from .models import Research, Person, Grant
    result = _result()
    if not isinstance(data, list):
        data = [data]
    for item in data:
        try:
            pi = None
            if item.get('principal_investigator'):
                pi = Person.objects.filter(
                    last_first=item['principal_investigator']).first()

            obj, created = Research.objects.update_or_create(
                name=item['name'],
                defaults={
                    'principal_investigator': pi,
                    'publications': item.get('publications', ''),
                    'capabilities': item.get('capabilities', ''),
                    'equipment': item.get('equipment', ''),
                    'personnel': item.get('personnel', ''),
                    'safety_requirements': item.get('safety_requirements', ''),
                }
            )
            # Set M2M relationships
            if item.get('co_investigators'):
                co_is = Person.objects.filter(
                    last_first__in=item['co_investigators'])
                obj.co_investigators.set(co_is)

            if item.get('student_researchers'):
                students = Person.objects.filter(
                    last_first__in=item['student_researchers'])
                obj.student_researchers.set(students)

            if item.get('grants'):
                grants = Grant.objects.filter(title__in=item['grants'])
                obj.grants.set(grants)

            if created:
                result['created'] += 1
            else:
                result['updated'] += 1
        except Exception as e:
            result['errors'] += 1
            result['error_details'].append(f"Research '{item.get('name')}': {e}")
    return result


# ─────────────────────────────────────────────
# Registry
# ─────────────────────────────────────────────

IMPORT_REGISTRY = {
    'room':       import_rooms,
    'person':     import_persons,
    'unit':       import_units,
    'course':     import_courses,
    'program':    import_programs,
    'grant':      import_grants,
    'research':   import_research,
}


def run_json_import(import_type, data):
    """Dispatch to the correct importer."""
    if import_type not in IMPORT_REGISTRY:
        raise ValueError(
            f"Unknown import type '{import_type}'. "
            f"Valid types: {', '.join(IMPORT_REGISTRY.keys())}"
        )
    return IMPORT_REGISTRY[import_type](data)
