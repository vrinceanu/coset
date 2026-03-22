"""
COSET DataWarehouse – Core Models
College of Science, Engineering and Technology

Models represent the main data entities:
  Person, Unit, Course, Program, Grant, Room, Research
"""

from django.db import models
from django.utils.text import slugify


# ─────────────────────────────────────────────
# Choices
# ─────────────────────────────────────────────

class PersonClassification(models.TextChoices):
    FACULTY = 'faculty', 'Faculty'
    STAFF   = 'staff',   'Staff'


class PersonRank(models.TextChoices):
    PROFESSOR           = 'professor',           'Professor'
    ASSOCIATE_PROFESSOR = 'associate_professor', 'Associate Professor'
    ASSISTANT_PROFESSOR = 'assistant_professor', 'Assistant Professor'
    LECTURER            = 'visiting_professor',  'Visiting Professor'
    INSTRUCTOR          = 'instructor',          'Instructor'
    ADJUNCT             = 'adjunct_professor',   'Adjunct Professor'
    RESEARCHER          = 'research_professor',  'Research Professor'
    POSTDOC             = 'postdoctoral_researcher',  'Postdoctoral Researcher'
    OTHER               = 'other',               'Other'


class UnitType(models.TextChoices):
    ADMINISTRATIVE = 'administrative', 'Administrative'
    ACADEMIC       = 'academic',       'Academic'
    RESEARCH       = 'research',       'Research'


class DegreeLevel(models.TextChoices):
    UNDERGRADUATE = 'undergraduate', 'Undergraduate'
    GRADUATE      = 'graduate',      'Graduate'
    CERTIFICATE   = 'certificate',   'Certficate'


class ProgramFocus(models.TextChoices):
    MAJOR = 'major', 'Major'
    MINOR = 'minor', 'Minor'


class DegreeConferred(models.TextChoices):
    BS  = 'BS',  'Bachelor of Science'
    BA  = 'BA',  'Bachelor of Arts'
    MS  = 'MS',  'Master of Science'
    MA  = 'MA',  'Master of Arts'
    PHD = 'PhD', 'Doctor of Philosophy'
    OTHER = 'Other', 'Other'


class RoomPurpose(models.TextChoices):
    OFFICE      = 'office',      'Office'
    CLASSROOM   = 'classroom',   'Classroom'
    LAB         = 'lab',         'Laboratory'
    CONFERENCE  = 'conference',  'Conference Room'
    STORAGE     = 'storage',     'Storage'
    SERVER      = 'server',      'Server Room'
    OTHER       = 'other',       'Other'

# ─────────────────────────────────────────────
# Department (lookup table)
# ─────────────────────────────────────────────

departments = [
    {'name': 'Biology', 'abbreviation': 'BIOL', 'slug': 'biology'},
    {'name': 'Chemistry', 'abbreviation': 'CHEM', 'slug': 'chemistry'},
    {'name': 'Mathematical Sciences', 'abbreviation': 'MATH', 'slug': 'mathematics'},
    {'name': 'Physics', 'abbreviation': 'PHYS', 'slug': 'physics'},
    {'name': 'Aerospace & Mechanical Engineering', 'abbreviation': 'ASME', 'slug': 'asme'},
    {'name': 'Chemical Engineering & Environmental Toxicology', 'abbreviation': 'CEET', 'slug': 'ceet'},
    {'name': 'Civil Engineering & Transportation Studies', 'abbreviation': 'CETS', 'slug': 'cets'},
    {'name': 'Electrical Engineering & Computer Science', 'abbreviation': 'EECS', 'slug': 'eecs'},
    {'name': 'Dean\'s Office', 'abbreviation': 'ADMIN', 'slug': 'deans-office'},
]


# ─────────────────────────────────────────────
# Room
# ─────────────────────────────────────────────

class Room(models.Model):
    """Physical room / space record."""
    room_number     = models.CharField(max_length=10)
    purpose         = models.CharField(max_length=30, choices=RoomPurpose.choices,
                                       default=RoomPurpose.OFFICE)
    # Occupant and point-of-contact are resolved after Person  and Unit model is defined
    notes           = models.TextField(blank=True)

    class Meta:
        ordering = ['room_number']
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

    def __str__(self):
        return f'{self.room_number}'


# ─────────────────────────────────────────────
# Person
# ─────────────────────────────────────────────

class Person(models.Model):
    """Faculty or staff member."""
    # Identity
    last_first      = models.CharField('Last, First', max_length=200,
                                        help_text='Sortable name: Last, First M.')
    name            = models.CharField('Display Name', max_length=200,
                                        help_text='Full display name: First M. Last')
    slug            = models.SlugField(max_length=200, unique=True, blank=True)
    # Status
    active          = models.BooleanField(default=True, db_index=True)
    classification  = models.CharField(max_length=10, choices=PersonClassification.choices,
                                        default=PersonClassification.FACULTY, db_index=True)
    rank            = models.CharField(max_length=350, # choices=PersonRank.choices,
                                        blank=True)
    # Affiliation
    department      = models.CharField('Department', max_length=20, null=True, blank=True,
                                        choices=[(x['slug'], x['name']) for x in departments],
                                        help_text='Primary department affiliation')
    admin_role      = models.CharField('Administrative Role', max_length=100, blank=True,
                                        help_text='e.g. Department Chair, Program Director')
    # Location / contact
    room            = models.CharField('Room', max_length=50, blank=True, null=True,
                                        help_text="e.g. TECH 206")
    email           = models.EmailField(blank=True)
    phone           = models.CharField(max_length=30, blank=True,
                                        help_text='(713) 313.4482')
    # External links
    cv_link         = models.URLField('CV Link', blank=True,
                                        help_text='e.g. https://live-tsu-hb2504.pantheonsite.io/wp-content/uploads/cv/harvey-mark-cv.pdf')

    photo           = models.ImageField('Photo', upload_to='person_photos/', blank=True, null=True)

    biography       = models.TextField(blank=True, verbose_name='Biography (plain text or markdown)')

    class Meta:
        ordering = ['last_first']
        verbose_name = 'Person'
        verbose_name_plural = 'People'

    def __str__(self):
        return self.last_first


# ─────────────────────────────────────────────
# Back-fill Room foreign keys to Person
# ─────────────────────────────────────────────

Room.add_to_class(
    'occupant',
    models.ForeignKey(Person, null=True, blank=True,
                      on_delete=models.SET_NULL,
                      related_name='occupied_rooms',
                      verbose_name='Primary Occupant')
)
Room.add_to_class(
    'point_of_contact',
    models.ForeignKey(Person, null=True, blank=True,
                      on_delete=models.SET_NULL,
                      related_name='rooms_as_contact',
                      verbose_name='Point of Contact')
)


# ─────────────────────────────────────────────
# Unit
# ─────────────────────────────────────────────

class Unit(models.Model):
    """Organizational unit: department, center, institute, office, etc."""
    name            = models.CharField(max_length=200, unique=True)
    slug            = models.SlugField(max_length=220, unique=True, blank=True)
    description     = models.TextField(blank=True)
    url             = models.URLField('Website URL', blank=True)
    unit_type       = models.CharField('Type', max_length=20, choices=UnitType.choices,
                                        default=UnitType.ACADEMIC, db_index=True)
    room            = models.CharField('Room', max_length=50, blank=True, null=True,
                                        help_text="e.g. TECH 201")
    # Leadership
    principal       = models.ForeignKey(Person, null=True, blank=True,
                                        on_delete=models.SET_NULL,
                                        related_name='led_units',
                                        verbose_name='Principal / Head')
    interim         = models.BooleanField('Principal is Interim', default=False)
    principal_email = models.EmailField(blank=True)
    principal_phone = models.CharField(max_length=30, blank=True)
    # Administration
    admin           = models.ForeignKey(Person, null=True, blank=True,
                                        on_delete=models.SET_NULL,
                                        related_name='admin_units',
                                        verbose_name='Administrative Contact')
    admin_email     = models.EmailField(blank=True)
    admin_phone     = models.CharField(max_length=30, blank=True)
    admin_fax       = models.CharField(max_length=30, blank=True)
    # Media
    logo            = models.URLField('Logo URL', blank=True)
    photo           = models.URLField('Photo URL', blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Unit'
        verbose_name_plural = 'Units'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

#--- Back-fill Room foreign keys to Unit

Room.add_to_class(
    'unit',
    models.ForeignKey(Unit, null=True, blank=True,
                      on_delete=models.SET_NULL,
                      related_name='rooms',
                      verbose_name='Unit Affiliation')
)

# ─────────────────────────────────────────────
# Course
# ─────────────────────────────────────────────

class Course(models.Model):
    """Individual course offering."""
    code            = models.CharField(max_length=6, db_index=True)
    name            = models.CharField(max_length=100)
    description     = models.TextField(blank=True)
    department      = models.CharField('Department', max_length=20, null=True, blank=True,
                                        choices=[(x['slug'], x['name']) for x in departments],
                                        help_text='Primary department affiliation')
    lecture_credits = models.DecimalField(max_digits=4, decimal_places=1, default=3)
    lab_credits     = models.DecimalField(max_digits=4, decimal_places=1, default=0)

    prerequisites = models.ManyToManyField(
        'self',
        symmetrical=False,
        related_name='required_for',
        blank=True
    )
    
    class Meta:
        ordering = ['department', 'code']
        unique_together = [['department', 'code']]
        verbose_name = 'Course'
        verbose_name_plural = 'Courses'

    def __str__(self):
        return f'{self.code} – {self.name}'

    @property
    def total_credits(self):
        return self.lecture_credits + self.lab_credits


# ─────────────────────────────────────────────
# Program
# ─────────────────────────────────────────────

class Program(models.Model):
    """Degree or certificate program."""
    degree_conferred    = models.CharField(max_length=10, choices=DegreeConferred.choices)
    focus               = models.CharField(max_length=10, choices=ProgramFocus.choices,
                                            default=ProgramFocus.MAJOR)
    name                = models.CharField(max_length=300)
    department          = models.CharField('Department', max_length=20, null=True, blank=True,
                                        choices=[(x['slug'], x['name']) for x in departments],
                                        help_text='Primary department affiliation')
    active              = models.BooleanField(default=True, db_index=True)
    level               = models.CharField('Graduate / Undergraduate', max_length=15,
                                            choices=DegreeLevel.choices,
                                            default=DegreeLevel.UNDERGRADUATE, db_index=True)
    description         = models.TextField(blank=True)
    admission_requirements = models.TextField(blank=True)
    credit_hours        = models.PositiveSmallIntegerField(default=120)
    major_requirements  = models.TextField(blank=True,
                                            help_text='Narrative or course list for required courses')
    other_requirements  = models.TextField(blank=True)
    electives           = models.TextField(blank=True)
    degree_plan         = models.TextField(blank=True,
                                            help_text='Semester-by-semester degree plan narrative or link')
    # Courses (M2M for structured relationship)
    required_courses    = models.ManyToManyField(Course, blank=True,
                                                  related_name='required_by_programs',
                                                  verbose_name='Required Courses')
    elective_courses    = models.ManyToManyField(Course, blank=True,
                                                  related_name='elective_in_programs',
                                                  verbose_name='Elective Courses')

    class Meta:
        ordering = ['name']
        verbose_name = 'Program'
        verbose_name_plural = 'Programs'

    def __str__(self):
        return f'{self.degree_conferred} – {self.name}'


# ─────────────────────────────────────────────
# Grant
# ─────────────────────────────────────────────

class Grant(models.Model):
    """External funding grant."""
    title               = models.CharField(max_length=500)
    department          = models.CharField('Department', max_length=20, null=True, blank=True,
                                        choices=[(x['slug'], x['name']) for x in departments],
                                        help_text='Primary department affiliation')
    granting_agency     = models.CharField(max_length=300)
    program             = models.CharField(max_length=300, blank=True,
                                            help_text='Funding program within the agency')
    principal_investigator = models.ForeignKey(Person, null=True, blank=True,
                                               on_delete=models.SET_NULL,
                                               related_name='pi_grants',
                                               verbose_name='Principal Investigator')
    dollar_amount       = models.DecimalField(max_digits=14, decimal_places=2,
                                              null=True, blank=True)
    start_date          = models.DateField(null=True, blank=True)
    end_date            = models.DateField(null=True, blank=True)
    notes               = models.TextField(blank=True)

    class Meta:
        ordering = ['start_date', 'title']
        verbose_name = 'Grant'
        verbose_name_plural = 'Grants'

    def __str__(self):
        return self.title


# ─────────────────────────────────────────────
# Research
# ─────────────────────────────────────────────

class Research(models.Model):
    """Research group, center, or initiative."""
    name                    = models.CharField(max_length=300, unique=True)
    principal_investigator  = models.ForeignKey(Person, null=True, blank=True,
                                                on_delete=models.SET_NULL,
                                                related_name='pi_research',
                                                verbose_name='Principal Investigator')
    co_investigators        = models.ManyToManyField(Person, blank=True,
                                                      related_name='co_i_research',
                                                      verbose_name='Co-Investigators')
    student_researchers     = models.ManyToManyField(Person, blank=True,
                                                      related_name='student_research',
                                                      verbose_name='Student Researchers')
    publications            = models.TextField(blank=True,
                                               help_text='List or description of publications; '
                                                         'structured DOIs, or link to external source')
    grants                  = models.ManyToManyField(Grant, blank=True,
                                                      related_name='research_projects')
    capabilities            = models.TextField(blank=True,
                                               help_text='Research capabilities and expertise')
    equipment               = models.TextField('Equipment & Instrumentation', blank=True)
    personnel               = models.TextField(blank=True,
                                               help_text='Additional personnel not captured as Persons')
    safety_requirements     = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Research Group'
        verbose_name_plural = 'Research Groups'

    def __str__(self):
        return self.name
