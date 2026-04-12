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
#  Interests form page
    form = InterestFormPage(title="Engineering Initiative Interest Form", slug="engineering-initiative-interest-form")
    home.add_child(instance=form)

#  dean's message page
    img = add_image("media/person_photos/mark-weatherspoon.jpg", "mark-weatherspoon")
    text = """<p>We are very delighted that you have chosen to visit our College’s website to inquire about our many academic programs. 
Our College is a vibrant and creative place to pursue many fields of study in the following eight academic 
departments: Biology, Chemistry, Computer Science, Engineering, Environmental & Interdisciplinary Sciences, 
Mathematics, Physics, and Transportation Studies &Aviation Science and Technology.
COSET has 20 undergraduate and six graduate programs including a Ph.D. program in Environmental & Interdisciplinary Sciences.</p>
<p>Moreover, we have three college research centers in addition to the departmental research facilities: 
(1) Center for Transportation Training and Research (CTTR), (2) Center for Research on Complex Networks (CRCN), and
(3) Innovative Transportation Research Institute (ITRI). There are two new state-of-the art facilities where our faculty and
students participate in scholarly activities such as teaching, critical learning, and scientific research in an exemplary diverse
cultural environment.</p>
<p>Our College prepares our students to become successful graduates through the scholarly efforts of our accomplished and eminent faculty
and the effective student support of our enthusiastic and diligent staff. Our academic programs have well-prepared curricula, which is
supported by the latest practical and theoretical knowledge, equipment and software essential for the preparation of our students in the real world.</p>
<p>I would like to invite you to browse our website to explore and learn more about our departments, programs and facilities in more detail.
Also, with equal measure, I would like to invite you to visit our College in person to get a real experience of the unique and
vibrant atmosphere of COSET and TSU since, as the true expression goes, there is no substitute to real and active personal experience.
Moreover, I hope you would join us in the COSET in pursuit of academic excellence.<p><br>
<p>Mark H. Weatherspoon Ph.D.</p>
<p>Dean</p><p>College of Science, Engineering and Technology</p>"""

    deans_welcome = StandardPage(title="Dean's Welcome", slug="deans-welcome",
        body=[
            ('paragraph', '<br><h2>Welcome to our website!</h2>'),
            ('floating_image', {'image': img, 'caption': 'Mark Weatherspoon, Ph.D.\n Dean and Professor of Electrical Engineering', 'alignment': 'left', 'width_percent': 20}),
            ('paragraph', text),
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




