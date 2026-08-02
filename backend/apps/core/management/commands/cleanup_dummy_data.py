"""
Management command to clean up dummy data and initialize real data structures
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import (
    Event, Alert, Asset, LogSource, Detection, Rule, Investigation
)


class Command(BaseCommand):
    help = 'Clean up dummy/sample data and prepare for real data ingestion'

    def add_arguments(self, parser):
        parser.add_argument(
            '--confirm',
            action='store_true',
            help='Confirm deletion of dummy data',
        )

    def handle(self, *args, **options):
        if not options['confirm']:
            self.stdout.write(
                self.style.WARNING(
                    'This command will delete dummy/sample data. '
                    'Use --confirm to proceed.'
                )
            )
            return

        self.stdout.write('Cleaning up dummy data...')

        # Count before deletion
        event_count = Event.objects.count()
        alert_count = Alert.objects.count()
        asset_count = Asset.objects.count()

        # Delete dummy data (events, alerts from sample log sources)
        sample_sources = LogSource.objects.filter(host='uploaded')
        Event.objects.filter(log_source__in=sample_sources).delete()
        Alert.objects.filter(event__isnull=True).delete()

        self.stdout.write(
            self.style.SUCCESS(
                f'Deleted {event_count} events and {alert_count} alerts'
            )
        )

        self.stdout.write(self.style.SUCCESS('Database cleaned and ready for real data!'))
        self.stdout.write(
            self.style.WARNING(
                '\nNext steps:\n'
                '1. Create real assets via /api/v1/assets/\n'
                '2. Configure log sources via /api/v1/log-sources/\n'
                '3. Upload log files via /api/v1/log-upload/upload/\n'
                '4. Alerts will be generated automatically from real events\n'
            )
        )
