import os
from django.db import transaction
from django.core.files.images import ImageFile
from django.core.files import File
from wagtail.models import Page, Site
import wagtail.images 
from wagtail.images.models import Image
from wagtail.documents.models import Document
# Import specific models
from base.models import NewsEventIndexPage, PostPage, StandardPage, SectionPage, PostSectionPage, HomePage, PersonIndexPage, HeroPage

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

    posts = PostSectionPage(title="Posts", slug="posts")
    home.add_child(instance=posts)

 # people index page   
    people = PersonIndexPage(title="People", slug="people")
    home.add_child(instance=people)

# news and events index page
    news_events = NewsEventIndexPage(title="News and Events", slug="news-events")
    home.add_child(instance=news_events)

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

# Vision, Mission and Strategic Plan
    text_default = """<h3> Work in progress...</h3>
<p>We are currently working on developing the content for this page. Please check back soon for updates!</p>
"""
    vision_mission = StandardPage(title="Vision, Mission and Strategic Plan", slug="vision-mission-strategic-plan",
        body=[('paragraph', text_default),])
    about.add_child(instance=vision_mission)
    vision_mission.save_revision().publish()

# Administration

# College bylaws
    college_bylaws = StandardPage(title="College By-Laws", slug="college-by-laws",
        body=[('paragraph', text_default),])
    about.add_child(instance=college_bylaws)
    college_bylaws.save_revision().publish()

# Board of advisors
    board_of_advisors = StandardPage(title="Board of Advisors", slug="board-of-advisors",
        body=[('paragraph', text_default),])
    about.add_child(instance=board_of_advisors)
    board_of_advisors.save_revision().publish()

# Standing committees
    standing_committees = StandardPage(title="Standing Committees", slug="standing-committees",
        body=[('paragraph', text_default),])
    about.add_child(instance=standing_committees)
    standing_committees.save_revision().publish()

# News and Announcements
    news_and_announcements = StandardPage(title="News and Announcements", slug="news-announcements",
        body=[('paragraph', text_default),])
    about.add_child(instance=news_and_announcements)
    news_and_announcements.save_revision().publish()

# Work with us
    work_with_us = StandardPage(title="Work with us", slug="work-with-us",
        body=[('paragraph', text_default),])
    about.add_child(instance=work_with_us)
    work_with_us.save_revision().publish()

# Reports and Newsletters
    reports_and_newsletters = StandardPage(title="Reports and Newsletters", slug="reports-newsletters",
        body=[('paragraph', text_default),])
    about.add_child(instance=reports_and_newsletters)
    reports_and_newsletters.save_revision().publish()   

# Give to us!
    give_to_us = StandardPage(title="Give to us!", slug="give-to-us",
        body=[('paragraph', text_default),])
    about.add_child(instance=give_to_us)
    give_to_us.save_revision().publish()

# student services
    student_services = StandardPage(title="Student Services", slug="services",
            body=[('paragraph', text_default),])
    students.add_child(instance=student_services)
    student_services.save_revision().publish()

# advisors & support
    advisors_and_support = StandardPage(title="Advisors and Support", slug="advisors",
            body=[('paragraph', text_default),])
    students.add_child(instance=advisors_and_support)
    advisors_and_support.save_revision().publish()
# links for students
    student_links = StandardPage(title="Student Links", slug="links",
            body=[('paragraph', text_default),])
    students.add_child(instance=student_links)
    student_links.save_revision().publish()

# Summer Programs and Internships
    summer_programs = StandardPage(title="Summer Programs and Internships", slug="internships",
            body=[('paragraph', text_default),])
    students.add_child(instance=summer_programs)
    summer_programs.save_revision().publish()

# Scholarships & Fellowships
    scholarships = StandardPage(title="Scholarships & Fellowships", slug="scholarships",
            body=[('paragraph', text_default),])
    students.add_child(instance=scholarships)
    scholarships.save_revision().publish()

# Student Organizations
    student_organizations = StandardPage(title="Student Organizations", slug="organizations",
            body=[('paragraph', text_default),])
    students.add_child(instance=student_organizations)
    student_organizations.save_revision().publish()

# Accredited Programs
    accredited_programs = StandardPage(title="Accredited Programs", slug="accredited-programs",
            body=[('paragraph', text_default),])
    academics.add_child(instance=accredited_programs)
    accredited_programs.save_revision().publish()

# biology
    biology = StandardPage(title="Biology", slug="biology",
            body=[('paragraph', text_default),])
    academics.add_child(instance=biology)
    biology.save_revision().publish()   

# chemistry
    chemistry = StandardPage(title="Chemistry", slug="chemistry",
            body=[('paragraph', text_default),])
    academics.add_child(instance=chemistry)
    chemistry.save_revision().publish()
# mathematics
    mathematics = StandardPage(title="Mathematics", slug="mathematics",
            body=[('paragraph', text_default),])
    academics.add_child(instance=mathematics)
    mathematics.save_revision().publish()
# physics
    physics = StandardPage(title="Physics", slug="physics",
            body=[('paragraph', text_default),] )
    academics.add_child(instance=physics)
    physics.save_revision().publish()

# Aerospace & Mechanical Engineering
    asme = StandardPage(title="Aerospace & Mechanical Engineering", slug="asme",
            body=[('paragraph', text_default),])
    academics.add_child(instance=asme)
    asme.save_revision().publish()

# Chemical Engineering & Environmental Toxicology
    ceet = StandardPage(title="Chemical Engineering & Environmental Toxicology", slug="ceet")
    academics.add_child(instance=ceet)
    ceet.save_revision().publish()  

# Civil Engineering & Transportation Studies
    cets = StandardPage(title="Civil Engineering & Transportation Studies", slug="cets",
            body=[('paragraph', text_default),])
    academics.add_child(instance=cets)
    cets.save_revision().publish()

# Electrical Engineering & Computer Science
    eecs = StandardPage(title="Electrical Engineering & Computer Science", slug="eecs",
            body=[('paragraph', text_default),])
    academics.add_child(instance=eecs)
    eecs.save_revision().publish() 

# highlights and strategic areas
    highlights = StandardPage(title="Highlights and Strategic Areas", slug="highlights-strategic-areas",
            body=[('paragraph', text_default),])
    research.add_child(instance=highlights)
    highlights.save_revision().publish()

# research committee
    committee = StandardPage(title="Research Committee", slug="committee",
            body=[('paragraph', text_default),])
    research.add_child(instance=committee)
    committee.save_revision().publish()

# student research opportunities
    student_research = StandardPage(title="Student Research Opportunities", slug="student-opportunities",
            body=[('paragraph', text_default),])
    research.add_child(instance=student_research)
    student_research.save_revision().publish()  

# core research resources
    core_resources = StandardPage(title="Core Research Resources", slug="core-resources",
            body=[('paragraph', text_default),])
    research.add_child(instance=core_resources)
    core_resources.save_revision().publish()

# high performance computing center
    hpcc = StandardPage(title="High Performance Computing Center", slug="hpcc",
            body=[('paragraph', text_default),])
    research.add_child(instance=hpcc)
    hpcc.save_revision().publish()

# Transportation Training and Research
    transportation_training = StandardPage(title="Transportation Training and Research", slug="ttr",
            body=[('paragraph', text_default),])
    research.add_child(instance=transportation_training)
    transportation_training.save_revision().publish()

# Innovative Transportation Research
    innovative_transportation = StandardPage(title="Innovative Transportation Research", slug="itr",
            body=[('paragraph', text_default),])
    research.add_child(instance=innovative_transportation)
    innovative_transportation.save_revision().publish() 

# Scientific Machine Learning
    scientific_ml = StandardPage(title="Scientific Machine Learning", slug="sciml-ms",
            body=[('paragraph', text_default),])
    research.add_child(instance=scientific_ml)
    scientific_ml.save_revision().publish()

# Microplastics Impacts Research
    microplastics = StandardPage(title="Microplastics Impacts Research", slug="microplastics",
            body=[('paragraph', text_default),])
    research.add_child(instance=microplastics)
    microplastics.save_revision().publish()

# Geostatistical Intelligence
    geostatistics = StandardPage(title="Geostatistical Intelligence", slug="geostats",
            body=[('paragraph', text_default),])
    research.add_child(instance=geostatistics)
    geostatistics.save_revision().publish()

# Digital Twins and Robotics
    digital_twins = StandardPage(title="Digital Twins and Robotics", slug="digital-twins",
            body=[('paragraph', text_default),])
    research.add_child(instance=digital_twins)
    digital_twins.save_revision().publish()

# Testimonial post 1
img = add_image("media/sarah-johnson.jpg", "sarah-johnson")
text = "The research opportunities at COSET have been transformative. I've worked on cutting-edge AI projects that will shape my career."
testimonial= PostPage(
    category="testimonial",
    title="Sarah Johnson's Testimonial",
    slug="sarah-johnson-testimonial",
    summary=text,
    body =[('paragraph', text)],
    author="Sarah Johnson",
    unit = "Computer Science, Class of 2024",
    image = img,
)
posts.add_child(instance=testimonial)
testimonial.save_revision().publish()

# Testimonial post 2
img = add_image("media/michael-chen.jpg", "michael-chen")
text = "The faculty mentorship and hands-on engineering labs prepared me perfectly for my career at NASA."
testimonial= PostPage(
    category="testimonial",     
    title="Michael Chen's Testimonial",
    slug="michael-chen-testimonial",
    summary=text,
    body =[('paragraph', text)],
    author="Michael Chen",  
    unit = "Physics, Class of 2023",
    image = img,
)
posts.add_child(instance=testimonial)
testimonial.save_revision().publish()

# Testimonial post 3
img = add_image("media/aisha-patel.jpg", "aisha-patel")
text = "COSET's commitment to diversity and excellence created an environment where I could thrive both academically and personally."
testimonial= PostPage(
    category="testimonial",
    title="Aisha Patel's Testimonial",
    slug="aisha-patel-testimonial",
    summary=text,
    body =[('paragraph', text)],
    author="Aisha Patel",
    unit = "Biology, Class of 2027",
    image=img,
)
posts.add_child(instance=testimonial)
testimonial.save_revision().publish()

# Event post 
img = add_image("media/aviation.jpg", "aviation-hangar")
text = "The building will house the fleet of 12 new 2025 Cirrus SR20 aircraft and enable the TSU aviation program to operate at the airport independently in 7,200 square feet of classrooms and offices."
event = PostPage(
    category="event",
    title="New TSU Aviation Hangar Unveiled at Ellington Field Aviation Complex",
    slug="aviation-hangar-unveiled",
    summary=text,
    body ="<p>"+text+"</p>",
    unit = "Aviation Science and Technology",
    image=img,
    datetime="2026-04-25 16:00:00",
    location="Ellington Field Aviation Complex, Houston, TX"
)
posts.add_child(instance=event)
event.save_revision().publish()

# Announcement post
img = add_image("media/new-engineering.png", "new-engineering")
text = "The College of Science, Engineering, and Technology proudly announces that the Board of Regents has officially approved the creation of four new engineering departments and seven new engineering academic programs."
text2 = text+"This milestone marks a significant step forward in strengthening COSET’s commitment to innovation, workforce development, and excellence in engineering education. The new departments and programs will expand opportunities for students, support cutting-edge research, and address critical needs in high-demand engineering fields."

announcement = PostPage(
    category="announcement",
    title="COSET Announces Major Expansion in Engineering Education",
    slug="new-engineering",
    summary=text,
    body="<p>"+text2+"</p>",
    unit = "Dean's Office",
    image=img,
    datetime="2026-02-19 00:00:00"
)
posts.add_child(instance=announcement)
announcement.save_revision().publish()  

# Research post 
img = add_image("media/msipp-grant.png", "msipp-grant")
text = "Professors awarded a $4.7 million academic research grant from the U.S. Department of Energy’s National Nuclear Security Administration to lead the Consortium for Research and Education for Advanced Manufacturing of Alloys for Extreme Conditions (REAM)."
text2 = text+"Texas Southern will lead the research consortium that consists of two additional academic partners: Howard University and Texas A&M University. Together, the consortium institutions will investigate advanced manufacturing of alloys in extreme conditions."
research = PostPage(
    category="research",
    title="COSET Receives Major Research Grant",
    slug="msipp-grant",
    summary=text,
    body="<p>"+text2+"</p>",
    unit = "physics",
    image=img,
    datetime="2026-01-09 00:00:00"
)
posts.add_child(instance=research)
research.save_revision().publish()  