"""
COSET DataWarehouse – Admin Configuration
Provides a rich, searchable, filterable admin interface for all entities.
"""

from django.contrib import admin
from django.utils.html import format_html
from markdown import markdown
from .models import Room, Person, Unit, Course, Program, Grant, Research
import markdown
from django.utils.safestring import mark_safe

# ─────────────────────────────────────────────
# Room
# ─────────────────────────────────────────────

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ('__str__', 'purpose', 'unit', 'occupant', 'point_of_contact')
    list_filter   = ('purpose', 'unit')
    search_fields = ('room_number', 'occupant__last_first')
    autocomplete_fields = ('unit','occupant', 'point_of_contact')
    fieldsets = (
        ('Location', {
            'fields': ('room_number', 'purpose')
        }),
        ('Assignment', {
            'fields': ('unit', 'occupant', 'point_of_contact')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )


# ─────────────────────────────────────────────
# Person
# ─────────────────────────────────────────────

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display   = ('last_first', 'classification', 'rank', 'active', 'photo_badge')
    list_filter    = ('active', 'classification', 'department')
    search_fields  = ('last_first', 'name', 'email', 'admin_role')
    list_editable  = ('active',)
 #   autocomplete_fields = ('department',)
    readonly_fields = ('photo_preview','biography_preview',)

    fieldsets = (
        ('Identity', {
            'fields': ('last_first', 'name', 'active', 'classification', 'rank')
        }),
        ('Affiliation', {
            'fields': ('department', 'admin_role', 'room')
        }),
        ('Contact', {
            'fields': ('email', 'phone')
        }),
        ('Media & Biography', {
            'fields': ('cv_link', 'photo', 'photo_preview', 'biography','biography_preview'),
            'classes': ('collapse',),
        }),
    )

    def photo_badge(self, obj):
        if obj.photo:
            return format_html(
                '<img src="/media/{}" style="height:36px;width:36px;'
                'object-fit:cover;border-radius:50%;" />', obj.photo
            )
        return '—'
    photo_badge.short_description = 'Photo'

    def photo_preview(self, obj):
        if obj.photo:
            return format_html(
                '<img src="/media/{}" style="max-height:200px;" />', obj.photo
            )
        return '(no photo)'
    photo_preview.short_description = 'Photo Preview'

    def biography_preview(self, obj):
        if obj.biography:
            html = markdown.markdown(obj.biography)
            return mark_safe(html)
        return '(no biography)'
    biography_preview.short_description = 'Biography Preview'   

# ─────────────────────────────────────────────
# Unit
# ─────────────────────────────────────────────

@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_display  = ('name', 'unit_type', 'principal', 'interim',
                     'admin')
    list_filter   = ('unit_type', 'interim')
    search_fields = ('name', 'slug', 'principal__last_first', 'admin__last_first')
    prepopulated_fields = {'slug': ('name',)}
    autocomplete_fields = ('principal', 'admin')

    fieldsets = (
        ('Identity', {
            'fields': ('name', 'slug', 'unit_type', 'description', 'url')
        }),
        ('Location', {
            'fields': ('room',)
        }),
        ('Leadership', {
            'fields': ('principal', 'interim', 'principal_email', 'principal_phone')
        }),
        ('Administration', {
            'fields': ('admin', 'admin_email', 'admin_phone', 'admin_fax')
        }),
        ('Media', {
            'fields': ('logo', 'photo'),
            'classes': ('collapse',),
        }),
    )


# ─────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display  = ('code', 'name', 'department', 'lecture_credits',
                     'lab_credits', 'total_credits_display')
    list_filter   = ('department',)
    search_fields = ('code', 'name', 'description')
#    autocomplete_fields = ('department',)

    fieldsets = (
        ('Course Info', {
            'fields': ('code', 'name', 'department', 'description')
        }),
        ('Credits', {
            'fields': ('lecture_credits', 'lab_credits')
        }),
    )

    def total_credits_display(self, obj):
        return obj.total_credits
    total_credits_display.short_description = 'Total Credits'


# ─────────────────────────────────────────────
# Program
# ─────────────────────────────────────────────

class RequiredCoursesInline(admin.TabularInline):
    model  = Program.required_courses.through
    extra  = 1
    verbose_name = 'Required Course'
    verbose_name_plural = 'Required Courses'


class ElectiveCoursesInline(admin.TabularInline):
    model  = Program.elective_courses.through
    extra  = 1
    verbose_name = 'Elective Course'
    verbose_name_plural = 'Elective Courses'


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display  = ('name', 'degree_conferred', 'focus', 'level',
                     'department', 'credit_hours', 'active')
    list_filter   = ('active', 'level', 'degree_conferred', 'focus', 'department')
    search_fields = ('name', 'description', 'department__name')
    list_editable = ('active',)
#    autocomplete_fields = ('department',)
    filter_horizontal = ('required_courses', 'elective_courses')

    fieldsets = (
        ('Program Identity', {
            'fields': ('name', 'degree_conferred', 'focus', 'level',
                       'department', 'active')
        }),
        ('Description & Requirements', {
            'fields': ('description', 'admission_requirements', 'credit_hours')
        }),
        ('Curriculum', {
            'fields': ('major_requirements', 'other_requirements',
                       'electives', 'degree_plan'),
            'classes': ('collapse',),
        }),
        ('Linked Courses', {
            'fields': ('required_courses', 'elective_courses'),
            'classes': ('collapse',),
        }),
    )


# ─────────────────────────────────────────────
# Grant
# ─────────────────────────────────────────────

@admin.register(Grant)
class GrantAdmin(admin.ModelAdmin):
    list_display  = ('title', 'granting_agency', 'principal_investigator',
                     'dollar_amount', 'start_date', 'end_date', 'department')
    list_filter   = ('department', 'granting_agency', 'start_date')
    search_fields = ('title', 'granting_agency', 'program',
                     'principal_investigator__last_first')
    autocomplete_fields = ('principal_investigator',)
    date_hierarchy = 'start_date'

    fieldsets = (
        ('Grant Info', {
            'fields': ('title', 'granting_agency', 'program', 'department')
        }),
        ('Investigator & Funding', {
            'fields': ('principal_investigator', 'dollar_amount',
                       'start_date', 'end_date')
        }),
        ('Notes', {
            'fields': ('notes',),
            'classes': ('collapse',),
        }),
    )


# ─────────────────────────────────────────────
# Research
# ─────────────────────────────────────────────

@admin.register(Research)
class ResearchAdmin(admin.ModelAdmin):
    list_display  = ('name', 'principal_investigator')
    search_fields = ('name', 'principal_investigator__last_first',
                     'capabilities', 'equipment')
    autocomplete_fields = ('principal_investigator',)
    filter_horizontal = ('co_investigators', 'student_researchers', 'grants')

    fieldsets = (
        ('Research Group', {
            'fields': ('name', 'principal_investigator')
        }),
        ('Personnel', {
            'fields': ('co_investigators', 'student_researchers', 'personnel')
        }),
        ('Research Details', {
            'fields': ('capabilities', 'equipment', 'safety_requirements')
        }),
        ('Outputs & Funding', {
            'fields': ('publications', 'grants'),
            'classes': ('collapse',),
        }),
    )
