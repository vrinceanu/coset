import os
from django.db import transaction
from django.core.files.images import ImageFile
from django.core.files import File
from wagtail.models import Page, Site
import wagtail.images 
from wagtail.images.models import Image
from wagtail.documents.models import Document
# Import specific models
from base.models import StandardPage, SectionPage, HomePage, PersonIndexPage, HeroPage

def add_image(path, title):
    with open(path, 'rb') as f:
        # Wrap the file in an ImageFile object
        image_file = ImageFile(f, name=os.path.basename(path))       
        # Create and save the Wagtail Image instance
        image = Image(title=title, file=image_file)
        image.save()
    return image

def add_document_programmatically(file_path, title):
    with open(file_path, 'rb') as f:
        # Wrap the file in a Django File object
        doc_file = File(f, name=os.path.basename(file_path))
        
        # Create and save the Wagtail Document instance
        doc = Document(title=title, file=doc_file)
        doc.save()
    return doc


root = Page.get_first_root_node()
with transaction.atomic():
    print("Cleaning existing content...")
    root.get_descendants().delete()
    root.refresh_from_db() 
    wagtail.images.get_image_model().objects.all().delete()

    home = HomePage(
        title="Home",
        slug="home"
        )
    root.add_child(instance=home)
    home.save_revision().publish()

    site, created = Site.objects.get_or_create(
        is_default_site=True,
        defaults={'root_page': home, 'hostname': 'localhost', 'port': 8000}
    )
    if not created:
        site.root_page = home
        site.save()  
    print(f"Site updated! '{home.title}' is now the live root.")
    
    img = add_image("media/coset_banner.jpg", "coset-banner")
    home.hero_title = "Science. Engineering. Technology."
    home.hero_image = img
    home.hero_cta_text= "Explore our new engineering programs"
    home.save_revision().publish()

with transaction.atomic():
#  adding section pages
    about = SectionPage(title="About", slug="about")
    home.add_child(instance=about)
    students = SectionPage(title="Students", slug="students")
    home.add_child(instance=students)
    academics = SectionPage(title="Academics", slug="academics")
    home.add_child(instance=academics)
    research = SectionPage(title="Research", slug="research")
    home.add_child(instance=research)
 # people index page   
    people = PersonIndexPage(title="People", slug="people")
    home.add_child(instance=people)
#  hero page
    hero = HeroPage(title="Engineering Initiative", slug="engineering-initiative")
    home.add_child(instance=hero)

#  dean's message page
    img = add_image("media/person_photos/mark-weatherspoon.jpg", "mark-weatherspoon")
    deans_welcome = StandardPage(title="Dean's Welcome", slug="deans-welcome",
        body=[('floating_image', {'image': img, 'caption': 'Mark Weatherspoon, Ph.D.\n Dean and Professor of Electrical Engineering', 'alignment': 'left', 'width_percent': 20}),
            ('paragraph', '<p>Welcome to the COSET website! We are excited to share our programs, research, and people with you. Explore our site to learn more about our innovative engineering programs, cutting-edge research, and vibrant community.</p>'),
            ('paragraph', '<br><br><br><br><br><br><br><br>')
              ]
    )
    about.add_child(instance=deans_welcome)
    deans_welcome.save_revision().publish()
# student services page
    student_services = StandardPage(title="Student Services", slug="services")
    students.add_child(instance=student_services)
    student_services.save_revision().publish()
# highlights and strategic areas page
    highlights = StandardPage(title="Highlights and Strategic Areas", slug="highlights-strategic-areas")
    research.add_child(instance=highlights)
    highlights.save_revision().publish()




