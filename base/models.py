from django.db import models
from urllib3 import request
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, InlinePanel
from core.models import Course, Person, Unit, departments
from django.db.models import Q
from wagtail.contrib.routable_page.models import RoutablePageMixin, path, route
from wagtail.images.models import Image
from wagtail.images import get_image_model_string
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.fields import StreamField

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
        ('paragraph', blocks.RichTextBlock()),
        ('floating_image', FloatingImageBlock()), # Add the new block here
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
    



    




