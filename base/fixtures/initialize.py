from django.db import transaction
from wagtail.models import Page, Site
# Import your specific models
from base.models import StandardPage, SectionPage, HomePage, PersonIndexPage  

site_data = {
    "title": "Home",
    "model": HomePage,
    "slug": "home",
    "children": [
        {
            "title": "About",
            "model": SectionPage,
            "slug": "about",
            "children": [
                {"title": "Dean's Welcome", "model": StandardPage, "slug": "deans-welcome"},
                {"title": "College By-Laws", "model": StandardPage, "slug": "bylaws"},
                {"title": "Vision, Mission and Strategic Plan", "model": StandardPage, "slug": "mission-vision-strategic-plan"},
            ]
        },
        {
            "title": "Students",
            "model": SectionPage,
            "slug": "students",
            "children": [
                {"title": "Student Services", "model": StandardPage, "slug": "student-services"},
            ]
        },
        {
            "title": "Academics",
            "model": SectionPage,
            "slug": "academics",
            "children": []
        },
        {
            "title": "Research",
            "model": SectionPage,
            "slug": "research",
            "children": [
                {"title": "Highlights and Strategic Areas", "model": StandardPage, "slug": "highlights"},
            ]
        },
        {
            "title": "People",
            "model": PersonIndexPage,
            "slug": "people"
        }
    ]
}

def add_pages(parent_node, data):
    new_page = data["model"](title=data["title"], slug=data["slug"])
    parent_node.add_child(instance=new_page)
    new_page.save_revision().publish()
    
    for child in data.get("children", []):
        add_pages(new_page, child)
    return new_page # Return the page object

root = Page.get_first_root_node()
with transaction.atomic():
    # 1. CLEANUP
    print("Cleaning existing content...")
    root.get_descendants().delete()
    root.refresh_from_db() 
 
    # 2. REBUILD (Recursive function)
    print("Building tree...")
    new_home_page = add_pages(root, site_data)
    # 3. UPDATE SITE SETTINGS
    # Get the default site (usually created by Wagtail by default)
    # or create one if it doesn't exist.
    site, created = Site.objects.get_or_create(
        is_default_site=True,
        defaults={'root_page': new_home_page, 'hostname': 'localhost', 'port': 8000}
    )
    
    if not created:
        site.root_page = new_home_page
        site.save()
        
    print(f"Site updated! '{new_home_page.title}' is now the live root.")

