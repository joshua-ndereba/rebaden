from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.core.models import Asset, Event, Alert

class Command(BaseCommand):
    help = 'Seed the database with example SIEM data (assets, events, alerts)'

    def handle(self, *args, **options):
        # Create assets
        a1, _ = Asset.objects.get_or_create(hostname='host-1', ip='10.0.1.5', os='Linux', owner='team-a')
        a2, _ = Asset.objects.get_or_create(hostname='host-2', ip='172.16.0.3', os='Windows', owner='team-b')

        # Create events
        Event.objects.get_or_create(time=timezone.now(), source=a1.ip, message='Failed SSH login', severity='medium', asset=a1)
        Event.objects.get_or_create(time=timezone.now(), source=a2.ip, message='Malware signature match', severity='high', asset=a2)
        Event.objects.get_or_create(time=timezone.now(), source=a1.ip, message='Large file transfer', severity='low', asset=a1)

        # Create alerts
        Alert.objects.get_or_create(name='Suspicious Login', defaults={'count':5, 'status':'open'})
        Alert.objects.get_or_create(name='Malware Detected', defaults={'count':2, 'status':'investigating'})
        Alert.objects.get_or_create(name='Data Exfil', defaults={'count':1, 'status':'open'})

        self.stdout.write(self.style.SUCCESS('Seeded SIEM data'))
