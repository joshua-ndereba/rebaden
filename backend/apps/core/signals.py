"""
Django Signals for automatic alert generation and event processing
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Event, LogSource
from .alert_generator import AlertGenerator


@receiver(post_save, sender=Event)
def generate_alerts_from_event(sender, instance, created, **kwargs):
    """
    Automatically generate alerts when new events are created
    """
    if created:
        try:
            # Process the event and generate alerts
            alerts = AlertGenerator.process_event(instance)
            
            # Log alert generation
            if alerts:
                print(f'Generated {len(alerts)} alert(s) from event {instance.id}')
        
        except Exception as e:
            print(f'Error generating alerts: {e}')


@receiver(post_save, sender=LogSource)
def initialize_log_source(sender, instance, created, **kwargs):
    """
    Initialize log source statistics when created
    """
    if created:
        try:
            # Initialize counters
            instance.events_received = 0
            instance.save(update_fields=['events_received'])
        
        except Exception as e:
            print(f'Error initializing log source: {e}')


# Import signals when app is ready
def ready():
    """Called when the app is ready"""
    pass
