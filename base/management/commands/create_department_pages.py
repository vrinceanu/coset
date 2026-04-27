from django.core.management.base import BaseCommand
from wagtail.models import Page
from base.models import DepartmentFacultyPage, DepartmentIndexPage, DepartmentPage, DepartmentProgramsPage
from core.departments import departments


class Command(BaseCommand):
    help = 'Seeds DepartmentIndexPage and one DepartmentPage per academic department. Idempotent.'

    def handle(self, *args, **kwargs):
        try:
            home = Page.objects.get(slug='home')
        except Page.DoesNotExist:
            self.stderr.write('Home page (slug="home") not found. Run bootstrap first.')
            return

        if DepartmentIndexPage.objects.exists():
            dept_index = DepartmentIndexPage.objects.first()
            self.stdout.write('DepartmentIndexPage already exists — skipping creation.')
        else:
            dept_index = DepartmentIndexPage(title='Departments', slug='departments', live=True)
            home.add_child(instance=dept_index)
            dept_index.save_revision().publish()
            self.stdout.write(self.style.SUCCESS('Created DepartmentIndexPage at /departments/'))

        academic_depts = [d for d in departments if d['slug'] != 'deans-office']

        for dept in academic_depts:
            if DepartmentPage.objects.filter(department=dept['slug']).exists():
                self.stdout.write(f"  Skipping {dept['name']} (already exists)")
                continue

            dept_page = DepartmentPage(
                title=f"{dept['name']}",
                slug=dept['slug'],
                department=dept['slug'],
                live=True,
            )
            dept_index.add_child(instance=dept_page)
            dept_page.save_revision().publish()

            faculty_page = DepartmentFacultyPage(
                title='Faculty & Staff',
                slug=f"{dept['slug']}-faculty",
                live=True,
                show_in_menus=True,
            )
            dept_page.add_child(instance=faculty_page)
            faculty_page.save_revision().publish()

            programs_page = DepartmentProgramsPage(
                title='Academic Programs',
                slug=f"{dept['slug']}-programs",
                live=True,
                show_in_menus=True,
            )
            dept_page.add_child(instance=programs_page)
            programs_page.save_revision().publish()

            self.stdout.write(self.style.SUCCESS(f"  Created: {dept['name']}"))

        self.stdout.write(self.style.SUCCESS('Done.'))
