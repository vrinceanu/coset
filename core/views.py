"""
COSET DataWarehouse – Views
All views are restricted to authenticated staff users (administrators).
"""

import json
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum, Q
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import (
    Room, Person, Unit, Course, Program, Grant, Research
)
from .models import departments

from .importers import run_json_import, IMPORT_REGISTRY


def is_admin(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)


admin_required = user_passes_test(is_admin, login_url='/admin/login/')


def redirect_to_dashboard(request):
    return redirect('core:dashboard')


# ─────────────────────────────────────────────
# Dashboard
# ─────────────────────────────────────────────

@admin_required
def dashboard(request):
    stats = {
        'people_active': Person.objects.filter(active=True).count(),
        'people_inactive': Person.objects.filter(active=False).count(),
        'faculty': Person.objects.filter(classification='faculty', active=True).count(),
        'staff': Person.objects.filter(classification='staff', active=True).count(),
        'units': Unit.objects.count(),
        'courses': Course.objects.count(),
        'programs_active': Program.objects.filter(active=True).count(),
        'grants': Grant.objects.count(),
        'grant_total': Grant.objects.aggregate(t=Sum('dollar_amount'))['t'] or 0,
        'research_groups': Research.objects.count(),
        'rooms': Room.objects.count(),
        'departments': len(departments),
    }
    recent_people = Person.objects.order_by('-id')[:5]
    recent_grants = Grant.objects.select_related('principal_investigator').order_by('-id')[:5]
    context = {
        'stats': stats,
        'recent_people': recent_people,
        'recent_grants': recent_grants,
        'title': 'Dashboard',
    }
    return render(request, 'core/dashboard.html', context)


# ─────────────────────────────────────────────
# People
# ─────────────────────────────────────────────

@admin_required
def people_list(request):
    qs = Person.objects.order_by('last_first')
    classification = request.GET.get('classification', '')
    department = request.GET.get('department', '')
    active = request.GET.get('active', '')
    q = request.GET.get('q', '')

    if classification:
        qs = qs.filter(classification=classification)
    if department:
        qs = qs.filter(department=department)
    if active == '1':
        qs = qs.filter(active=True)
    elif active == '0':
        qs = qs.filter(active=False)
    if q:
        qs = qs.filter(
            Q(last_first__icontains=q) | Q(name__icontains=q) |
            Q(email__icontains=q) | Q(admin_role__icontains=q)
        )

    context = {
        'people': qs,
        'title': 'People',
        'departments': departments,
        'filters': {'classification': classification, 'department': department,
                    'active': active, 'q': q},
    }
    return render(request, 'core/people_list.html', context)


# ─────────────────────────────────────────────
# Units
# ─────────────────────────────────────────────

@admin_required
def units_list(request):
    qs = Unit.objects.select_related('principal', 'admin').order_by('name')
    unit_type = request.GET.get('type', '')
    if unit_type:
        qs = qs.filter(unit_type=unit_type)
    context = {
        'units': qs,
        'title': 'Units',
        'filters': {'type': unit_type},
    }
    return render(request, 'core/units_list.html', context)


# ─────────────────────────────────────────────
# Courses
# ─────────────────────────────────────────────

@admin_required
def courses_list(request):
    qs = Course.objects.order_by('department', 'code')
    department = request.GET.get('department', '')
    q = request.GET.get('q', '')
    if department:
        qs = qs.filter(department__id=department)
    if q:
        qs = qs.filter(Q(code__icontains=q) | Q(name__icontains=q))
    context = {
        'courses': qs,
        'title': 'Courses',
        'filters': {'department': department, 'q': q},
    }
    return render(request, 'core/courses_list.html', context)


# ─────────────────────────────────────────────
# Programs
# ─────────────────────────────────────────────

@admin_required
def programs_list(request):
    qs = Program.objects.order_by('name')
    level = request.GET.get('level', '')
    active = request.GET.get('active', '')
    if level:
        qs = qs.filter(level=level)
    if active == '1':
        qs = qs.filter(active=True)
    elif active == '0':
        qs = qs.filter(active=False)
    context = {
        'programs': qs,
        'title': 'Programs',
        'filters': {'level': level, 'active': active},
    }
    return render(request, 'core/programs_list.html', context)


# ─────────────────────────────────────────────
# Grants
# ─────────────────────────────────────────────

@admin_required
def grants_list(request):
    qs = Grant.objects.select_related('principal_investigator').order_by('-start_date')
    department = request.GET.get('department', '')
    q = request.GET.get('q', '')
    if department:
        qs = qs.filter(department__id=department)
    if q:
        qs = qs.filter(
            Q(title__icontains=q) | Q(granting_agency__icontains=q) |
            Q(principal_investigator__last_first__icontains=q)
        )
    total = qs.aggregate(t=Sum('dollar_amount'))['t'] or 0
    context = {
        'grants': qs,
        'total': total,
        'title': 'Grants',
        'filters': {'department': department, 'q': q},
    }
    return render(request, 'core/grants_list.html', context)


# ─────────────────────────────────────────────
# Research
# ─────────────────────────────────────────────

@admin_required
def research_list(request):
    qs = Research.objects.select_related('principal_investigator').prefetch_related(
        'co_investigators', 'grants'
    ).order_by('name')
    context = {
        'research_groups': qs,
        'title': 'Research Groups',
    }
    return render(request, 'core/research_list.html', context)


# ─────────────────────────────────────────────
# Data Import
# ─────────────────────────────────────────────

@admin_required
def import_data(request):
    context = {
        'title': 'Import Data',
        'import_types': list(IMPORT_REGISTRY.keys()),
    }
    return render(request, 'core/import_data.html', context)


@admin_required
@require_POST
def run_import(request):
    import_type = request.POST.get('import_type', '')
    json_text   = request.POST.get('json_data', '')

    if not import_type or not json_text:
        messages.error(request, 'Import type and JSON data are required.')
        return redirect('core:import_data')

    try:
        data = json.loads(json_text)
    except json.JSONDecodeError as e:
        messages.error(request, f'Invalid JSON: {e}')
        return redirect('core:import_data')

    try:
        result = run_json_import(import_type, data)
        messages.success(request,
            f'Import complete: {result["created"]} created, '
            f'{result["updated"]} updated, {result["errors"]} errors.')
        if result.get('error_details'):
            for err in result['error_details'][:10]:
                messages.warning(request, err)
    except ValueError as e:
        messages.error(request, str(e))

    return redirect('core:import_data')
