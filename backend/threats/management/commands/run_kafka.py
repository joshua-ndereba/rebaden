from django.core.management.base import BaseCommand
from threats.kafka_consumer import ThreatLogConsumer

class Command(BaseCommand):
    help = 'Runs the Kafka consumer for threat logs'

    def handle(self, *args, **options):
        self.stdout.write('Starting Kafka Consumer...')
        consumer = ThreatLogConsumer()
        try:
            consumer.start_listening()
        except KeyboardInterrupt:
            self.stdout.write('Stopping consumer...')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
