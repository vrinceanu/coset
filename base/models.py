from multiprocessing import context
import os, csv
from django.db import models
from urllib3 import request
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel, PageChooserPanel
from core.models import Course, Person, Program, Unit
from core.departments import departments
from django.db.models import Q
from django.conf import settings 
from django.utils import timezone
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, route
from wagtail.images.models import Image
from wagtail.images import get_image_model_string
from wagtail import blocks
from wagtail.search import index
from wagtail.images.blocks import ImageChooserBlock
from wagtail.fields import StreamField
from wagtail.contrib.table_block.blocks import TableBlock
from modelcluster.fields import ParentalKey
from wagtailmarkdown.blocks import MarkdownBlock

class FloatingImageBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=True)
    caption = blocks.CharBlock(required=False, help_text="Optional image caption")
    
    alignment = blocks.ChoiceBlock(choices=[
        ('left', 'Float Left'),
        ('right', 'Float Right'),
    ], default='left')
    
    # Adjustable size (width in percentage or pixels)
    width_percent = blocks.IntegerBlock(
        default=50, 
        min_value=10, 
        max_value=100,
        help_text="Width of the image as a percentage of the container"
    )

    class Meta:
        icon = 'image'
        template = 'blocks/floating_image_block.html' # We will create this next

class StandardPage(Page):
    body = StreamField([
        ('paragraph', 
           blocks.RichTextBlock(features=['h2','h3','h4','bold','italic',
            'link','ul','ol','hr','document-link','image','blockquote','subscript','superscript'],
            default='Some')),
        ('floating_image', FloatingImageBlock()), 
        ('table', TableBlock()),
        ('markdown', MarkdownBlock(icon="code")),
    ], use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    page_description = "A standard content page with a rich text body field and a block with floating image"

class SectionPage(Page):
    """
    A page that serves as a section header, without body content.
    """

    page_description = "A section header page that organizes content without having its own body text."
    
    max_count = 4
    def serve(self, request, *args, **kwargs):
        return super().serve(request, *args, **kwargs)

class PostSectionPage(Page):
    page_description = "A section header page that organizes posts"
    max_count = 1
    subpage_types = ["PostPage"]
    def serve(self, request, *args, **kwargs):
        return super().serve(request, *args, **kwargs)

class HomePageFeaturedPost(Orderable):
    page = ParentalKey('HomePage', related_name='featured_posts')
    featured_post = models.ForeignKey(
        'PostPage', # Replace with your actual blog page model
        on_delete=models.CASCADE,
        related_name='+'
    )

    panels = [
        PageChooserPanel('featured_post'),
    ]

class HomePageTestimonialPost(Orderable):
    page = ParentalKey('HomePage', related_name='testimonial_posts')
    testimonial_post = models.ForeignKey(
        'PostPage', # Replace with your actual blog page model
        on_delete=models.CASCADE,
        related_name='+')
    
    panels = [
        PageChooserPanel('testimonial_post'),
    ]

class HomePage(Page):
    """
    The homepage of the site, which can have a custom template and content.
    """
    page_description = "The homepage of the site, which can have a custom template and content."

    hero_title = models.CharField(max_length=255, blank=True, default='Welcome to the COSET website!')
    hero_cta_text = models.CharField(max_length=255, blank=True, default='Explore our courses and people')
    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    content_panels = Page.content_panels + [
        FieldPanel('hero_title'),
        FieldPanel('hero_cta_text'),
        FieldPanel('hero_image'),
        InlinePanel('featured_posts',    label="Featured Posts", max_num=3, min_num=0),
        InlinePanel('testimonial_posts', label="Testimonial Posts", max_num=3, min_num=0),
    ]

class HeroPage(Page):
    # No extra fields defined here
    
    # We limit this so only one can exist (optional)
    max_count = 1 
    
    # This ensures the admin only sees the standard Title and Promote tabs
    content_panels = Page.content_panels

class CourseIndexPage(Page):
    """
    A page that lists all courses, with links to individual course pages.
    """

    page_description = "A page that lists all courses, with links to individual course pages."

    max_count = 1
    def get_context(self, request):
        context = super().get_context(request)
    # Get the 'query' parameter from the GET request
        search_query = request.GET.get('query', None)
        courses = Course.objects.all().order_by('code')

        if search_query:
            # Filter by name OR code (case-insensitive)
            courses = courses.filter(
                Q(name__icontains=search_query) | 
                Q(code__icontains=search_query)
            )

        context['courses'] = courses
        context['search_query'] = search_query
        return context

class UndergraduateProgramIndexPage(Page):
    intro = RichTextField(blank=True)

    page_description = "A page that lists all programs, grouped by level, each linking to its source URL."

    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        from core.models import Program
        context = super().get_context(request)
        programs = Program.objects.filter(active=True, degree_conferred='BS').order_by("department")
        context["programs"] = [p for p in programs if 'degree_conferred' == 'BS']
        context["programs"] = programs
        return context

class GraduateProgramIndexPage(Page):
    intro = RichTextField(blank=True)

    page_description = "A page that lists all programs, grouped by level, each linking to its source URL."

    max_count = 1

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
    ]

    def get_context(self, request):
        from core.models import Program
        context = super().get_context(request)
        programs = Program.objects.filter(active=True).filter(Q(degree_conferred='MS') | Q(degree_conferred='4+1') | Q(degree_conferred='PHD').order_by("department", "degree_conferred")
        context["programs"] = programs
        return context

class PersonIndexPage(RoutablePageMixin, Page):
    """
    A page that lists all people, with links to individual person pages.
    """

    page_description = "A page that lists all people, with links to individual person pages."

    def get_context(self, request):
        context = super().get_context(request)
        people = Person.objects.all().filter(active=True).values(
            'slug','name','classification','department','rank','admin_role','room','email','phone','cv_link','photo').order_by('name')
        context['people'] = people
        context['departments'] = departments[:-1]
        units = Unit.objects.all().values('slug','principal__slug','interim')
        chair = {u['slug']: u['principal__slug'] for u in units}
        context['chair'] = chair
        interim = {u['slug']: u['interim'] for u in units}
        context['interim'] = interim
        return context
    
    @path(r'')
    def index_view(self, request):
        return self.serve(request)
    
    @path(r'<slug:slug>/')
    def person_view(self, request, slug):
        print(f"Looking for person with slug: {slug}" )
        person = Person.objects.all().filter(slug=slug).first()
        if not person:
            return self.serve(request)  # Fallback to the index view if no person found
        
        return self.render(request,
                context_overrides = {'person': person}, template='person_page.html')

    subpage_types = []

class InterestFormPage(Page):
    subtitle = models.CharField(max_length=255, blank=True)
    
    content_panels = Page.content_panels + [
        FieldPanel('subtitle'),
    ]

    def serve(self, request):
        if request.method == 'POST':
            # Logic to save to CSV
            data = request.POST.dict()
            data.pop('csrfmiddlewaretoken', None)
            
            file_path = os.path.join(settings.MEDIA_ROOT, 'cset_submissions.csv')
            file_exists = os.path.isfile(file_path)

            with open(file_path, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=data.keys())
                if not file_exists:
                    writer.writeheader()
                writer.writerow(data)
                
        return super().serve(request)

## --- News and Events
class NewsEventIndexPage(Page):
    """
    A page that lists all news and events, with links to individual pages.
    """

    page_description = "A page that lists all news and events, with links to individual pages."

    max_count = 1
    
    hero_intro = models.CharField(
        max_length=300,
        blank=True,
        default="The latest news, announcements, and events from COSET",
    )

    content_panels = Page.content_panels + [
        FieldPanel("hero_intro"),
    ]

    subpage_types = ["PostPage"]
    class Meta:
        verbose_name = "News & Events Index Page"

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
 
        # ── collect    
        post_qs = PostPage.objects.live().public().filter(category__in=
            ["event","announcement","research","award","partnership","student","faculty"]
            )      
        items = []
        for page in post_qs:
            if page.category == "event":
                page.type = "event"
            else:
                page.type      = "news"
            items.append(page)
        
        # Sort newest-first
        items.sort(key=lambda p: p.datetime or timezone.now(), reverse=True)
 
        # ── filter by type if ?type= param supplied ───────────────────────────
        filter_type = request.GET.get("type", "all")
        if filter_type == "news":
            items = [i for i in items if i._type == "news"]
        elif filter_type == "event":
            items = [i for i in items if i._type == "event"]
 
        # ── paginate ──────────────────────────────────────────────────────────
        ITEMS_PER_PAGE = 10
        paginator = Paginator(items, ITEMS_PER_PAGE)
        page_num  = request.GET.get("page")
        try:
            page_obj = paginator.page(page_num)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)
 
        context["items"]       = page_obj
        context["paginator"]   = paginator
        context["filter_type"] = filter_type
        context["total_count"] = len(items)

        return context
    
CATEGORY_CHOICES = [
    ("event",         "Event"),
    ("announcement",  "Announcement"),
    ("research",      "Research"),
    ("award",         "Award & Recognition"),
    ("partnership",   "Partnership"),
    ("student",       "Student Achievement"),
    ("faculty",       "Faculty Spotlight"),
    ("general",       "General Post"),
    ("testimonial",    "Testimonial"),
    ("scholarship",    "Scholarship"),
    ("seminar",        "Seminar"),
    ("internship",     "Internship"),
]
class PostPage(Page):
    """
    Individual news article. Must live under Posts.
    """ 
    # ── metadata fields ───────────────────────────────────────────────────────────
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default="general")
    datetime = models.DateTimeField("Start Date & Time", default=timezone.now)    
    author   = models.CharField(max_length=200, blank=True, help_text="For News: the person(s) involved in the news item. For Events: the organizer or featured speaker.")
    location = models.CharField(max_length=300, blank=True, help_text="For Events: the event location. For News: optional location associated with the news item.")
    url      = models.URLField(blank=True, help_text="Link to RSVP / registration form/ Optional Google Maps or venue URL.")    
    unit     = models.CharField(max_length=100, blank=True, help_text="Optional unit/department associated with this news item.")
    # --- core fields 
    summary = models.TextField( max_length=400, help_text="Short summary shown on the index card (max 400 chars).")
    body    = RichTextField()
    image   = models.ForeignKey(
        "wagtailimages.Image",
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    # ── search ────────────────────────────────────────────────────────────────
    search_fields = Page.search_fields + [
        index.SearchField("summary"),
        index.SearchField("body"),
        index.SearchField("category"),
        index.FilterField("category"),
        index.FilterField("datetime"),
    ]
 
    # ── admin panels ──────────────────────────────────────────────────────────
    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldRowPanel([ FieldPanel("category"), FieldPanel("datetime"),]),
            FieldRowPanel([ FieldPanel("author"), FieldPanel("location"),]),
            FieldPanel("unit"),
            FieldPanel("url"),
        ], heading="Metadata"),
        FieldPanel("summary"),
        FieldPanel("image"),
        FieldPanel("body"),
    ]
 
    subpage_types     = []
    parent_page_types = ["NewsEventIndexPage",]
    class Meta:
        verbose_name = "Blog Post"

    @property
    def is_upcoming(self):
        return self.datetime >= timezone.now()

    @property
    def is_past(self):
        return self.datetime < timezone.now()

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Related news (same category, excluding self)
        context["related"] = (
            PostPage.objects.sibling_of(self)
            .live()
            .public()
            .filter(category=self.category)
            .exclude(pk=self.pk)
            .order_by("-datetime")[:3]
        )
        return context

## ---- Departments 
class DepartmentIndexPage(Page):
    max_count = 1
    subpage_types = ['DepartmentPage']
    page_description = "Lists all department sub-sites."

    def get_context(self, request):
        context = super().get_context(request)
        context['departments'] = self.get_children().live().public().specific()
        return context


class DepartmentPage(Page):
    department = models.CharField(
        max_length=20,
        choices=[(x['slug'], x['name']) for x in departments],
    )
    intro = RichTextField(blank=True, features=['bold', 'italic', 'link'])
    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )

    content_panels = Page.content_panels + [
        FieldPanel('department'),
        FieldPanel('intro'),
        FieldPanel('hero_image'),
    ]

    parent_page_types = ['DepartmentIndexPage']
    subpage_types = ['DepartmentFacultyPage', 'DepartmentProgramsPage', 'DepartmentStandardPage']
    page_description = "A department sub-site hub page."

    @property
    def dept_info(self):
        return next((d for d in departments if d['slug'] == self.department), None)

    def get_context(self, request):
        context = super().get_context(request)
        context['dept_info'] = self.dept_info
        context.update(get_dept_sidebar_context(self))
        return context


def get_dept_sidebar_context(page):
    """Return sidebar nav + dept info card context for any page inside a DepartmentPage."""
    if isinstance(page, DepartmentPage):
        dept_page = page
    else:
        dept_page = (DepartmentPage.objects
            .ancestor_of(page)
            .order_by('-depth')
            .first())
    if not dept_page:
        return {}

    nav_items = []
    for child in dept_page.get_children().live().public().in_menu():
        grandchildren = list(child.get_children().live().public().in_menu())
        nav_items.append({
            'page': child,
            'children': grandchildren,
            'is_active': (child.pk == page.pk or page.is_descendant_of(child)),
        })

    unit = Unit.objects.filter(slug=dept_page.department).first()
    return {
        'dept_page': dept_page,
        'dept_nav_items': nav_items,
        'dept_unit': unit,
    }


class DepartmentFacultyPage(Page):
    intro = RichTextField(blank=True, features=['bold', 'italic', 'link'])
    content_panels = Page.content_panels + [FieldPanel('intro')]

    parent_page_types = ['DepartmentPage']
    subpage_types = []
    max_count_per_parent = 1
    page_description = "Auto-generated faculty listing for a department."

    def get_context(self, request):
        context = super().get_context(request)
        dept_slug = self.get_parent().specific.department
        dept_info = next((d for d in departments if d['slug'] == dept_slug), None)
        dept_abbrev = dept_info['abbreviation']

        unit = Unit.objects.filter(slug=dept_slug).first()
        chair_slug = unit.principal.slug if (unit and unit.principal) else None

        context['people'] = (Person.objects
            .filter(active=True, department=dept_abbrev).order_by('last_first'))
        
        context.update(get_dept_sidebar_context(self))
        return context


class DepartmentProgramsPage(Page):
    intro = RichTextField(blank=True, features=['bold', 'italic', 'link'])
    content_panels = Page.content_panels + [FieldPanel('intro')]

    parent_page_types = ['DepartmentPage']
    subpage_types = []
    max_count_per_parent = 1
    page_description = "Auto-generated academic programs listing for a department."

    def get_context(self, request):
        context = super().get_context(request)
        dept_slug = self.get_parent().specific.department
        dept_info = next((d for d in departments if d['slug'] == dept_slug), None)
        dept_abbrev = dept_info['abbreviation'] if dept_info else dept_slug
        programs = (Program.objects
            .filter(active=True, department=dept_abbrev)
            .order_by('degree_conferred', 'name'))
        context['programs'] = programs
        context.update(get_dept_sidebar_context(self))
        return context

class DepartmentStandardPage(Page):
    body = StreamField([
        ('paragraph',
           blocks.RichTextBlock(features=['h2','h3','h4','bold','italic',
            'link','ul','ol','hr','document-link','image','blockquote','subscript','superscript'])),
        ('floating_image', FloatingImageBlock()),
        ('table', TableBlock()),
        ('markdown', MarkdownBlock(icon="code")),
    ], use_json_field=True)

    content_panels = Page.content_panels + [FieldPanel('body')]

    parent_page_types = ['DepartmentPage', 'DepartmentStandardPage']
    subpage_types = ['DepartmentStandardPage']
    page_description = "A standard content page within a department sub-site (shows dept sidebar)."

    def get_context(self, request):
        context = super().get_context(request)
        context.update(get_dept_sidebar_context(self))
        return context
