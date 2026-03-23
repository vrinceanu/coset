import os, json
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Initializes site with default data'

    def handle(self, *args, **options):
        fixtures_dir = os.path.join(settings.PROJECT_DIR, "base", "fixtures")
        menu_file = os.path.join(fixtures_dir, "menu.json")
        if os.path.exists(menu_file):
            self.stdout.write(self.style.SUCCESS('Loading menu structure from fixture...'))
            menu = json.load(open(menu_file))
        for top_nav in menu:
            for key, val in top_nav.items():
                print(key)
                for sub_nav in val:
                    for key, val in sub_nav.items():
                        print(f"  {key}")
                        for sub_sub_nav in val:
                            for key, val in sub_sub_nav.items():
                                print(f"    {key}")


        self.stdout.write(self.style.SUCCESS('Menu structure initialized successfully.'))
