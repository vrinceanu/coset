from multiprocessing import context
import os, csv
from django.db import models
from urllib3 import request
from wagtail.models import Page, Orderable
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, FieldRowPanel, PageChooserPanel
from core.models import Course, Person, Unit, departments
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
#        ('markdown', MarkdownBlock(icon="code")),
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
 