from django.core.management.base import BaseCommand
from wagtail.models import Page
from coset.base.models import StandardPage, SectionPage

import re
import json

def parse_js_object(js_str):
    # Remove single-line comments
    js_str = re.sub(r'//.*', '', js_str)
    
    # Remove multi-line comments
    js_str = re.sub(r'/\*.*?\*/', '', js_str, flags=re.DOTALL)
    
    # Add quotes around unquoted keys
    js_str = re.sub(r'(\s*)(\w+)(\s*):', r'\1"\2"\3:', js_str)
    
    # Replace single quotes with double quotes
    js_str = re.sub(r"'(.*?)'", r'"\1"', js_str)
    
    # Remove trailing commas before } or ]
    js_str = re.sub(r',(\s*[}\]])', r'\1', js_str)

    return json.loads(js_str)



class Command(BaseCommand):
    help = 'Creates initial pages'

    def handle(self, *args, **kwargs):
        parent = Page.objects.get(slug='home')

        page = StandardPage(
            title="My New Page",
            slug="my-new-page",
            live=True,
        )

        parent.add_child(instance=page)

        self.stdout.write(self.style.SUCCESS('Page created!'))