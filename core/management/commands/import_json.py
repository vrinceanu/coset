"""
Management command: import_json

Usage:
    python manage.py import_json --type person --file /path/to/persons.json
    python manage.py import_json --type department --file /path/to/depts.json
    python manage.py import_json --type grant --file /path/to/grants.json

Supported types: department, room, person, unit, course, program, grant, research
"""

import json
import sys
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from core.importers import run_json_import, IMPORT_REGISTRY


class Command(BaseCommand):
    help = 'Import COSET data from a JSON file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--type', dest='import_type', required=True,
            choices=list(IMPORT_REGISTRY.keys()),
            help='Type of data to import'
        )
        parser.add_argument(
            '--file', dest='filepath', required=True,
            help='Path to the JSON file'
        )
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='Parse and validate without writing to database'
        )

    def handle(self, *args, **options):
        filepath = Path(options['filepath'])
        import_type = options['import_type']
        dry_run = options['dry_run']

        if not filepath.exists():
            raise CommandError(f'File not found: {filepath}')

        self.stdout.write(f'Reading {filepath} …')
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON: {e}')

        count = len(data) if isinstance(data, list) else 1
        self.stdout.write(f'Found {count} record(s) of type "{import_type}".')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN – no data will be written.'))
            return

        result = run_json_import(import_type, data)

        self.stdout.write(
            self.style.SUCCESS(
                f'Import complete: {result["created"]} created, '
                f'{result["updated"]} updated, {result["errors"]} errors.'
            )
        )
        if result.get('error_details'):
            self.stdout.write(self.style.WARNING('Errors:'))
            for err in result['error_details']:
                self.stdout.write(f'  • {err}')
