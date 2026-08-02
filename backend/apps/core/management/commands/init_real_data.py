"""
Management command to initialize real data structures and processes
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.core.models import (
    LogSource, DetectionRule, UserProfile
)


class Command(BaseCommand):
    help = 'Initialize real data structures for production use'

    def handle(self, *args, **options):
        self.stdout.write('Initializing real data structures...')

        # Create default log sources
        log_sources = [
            {'name': 'API Upload', 'source_type': 'generic', 'host': 'api', 'port': None},
            {'name': 'Syslog', 'source_type': 'syslog', 'host': 'localhost', 'port': 514},
            {'name': 'Web Server', 'source_type': 'apache', 'host': 'localhost', 'port': 80},
            {'name': 'Firewall', 'source_type': 'firewall', 'host': 'localhost', 'port': 514},
        ]

        created_count = 0
        for source_data in log_sources:
            source, created = LogSource.objects.get_or_create(
                name=source_data['name'],
                defaults={
                    'source_type': source_data['source_type'],
                    'host': source_data['host'],
                    'port': source_data['port'],
                    'is_active': True,
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} log sources')
        )

        # Create default detection rules
        detection_rules = [
            {
                'name': 'Failed Login Attempts',
                'rule_type': 'custom',
                'severity': 'medium',
                'rule_content': 'action:failed OR result:failure',
            },
            {
                'name': 'Privilege Escalation',
                'rule_type': 'custom',
                'severity': 'critical',
                'rule_content': 'privilege OR sudoedit OR sudo',
            },
            {
                'name': 'Port Scanning',
                'rule_type': 'custom',
                'severity': 'high',
                'rule_content': 'port_scan OR nmap OR scanning',
            },
            {
                'name': 'Data Exfiltration',
                'rule_type': 'custom',
                'severity': 'critical',
                'rule_content': 'exfiltration OR data_transfer OR suspicious_upload',
            },
        ]

        admin_user = User.objects.filter(is_superuser=True).first()
        if admin_user:
            created_count = 0
            for rule_data in detection_rules:
                rule, created = DetectionRule.objects.get_or_create(
                    name=rule_data['name'],
                    defaults={
                        'rule_type': rule_data['rule_type'],
                        'severity': rule_data['severity'],
                        'rule_content': rule_data['rule_content'],
                        'is_active': True,
                        'created_by': admin_user,
                    }
                )
                if created:
                    created_count += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'Created {created_count} detection rules')
            )

        # Ensure all users have profiles
        for user in User.objects.all():
            profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'admin' if user.is_superuser else 'analyst',
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                'Real data structures initialized successfully!\n\n'
                'You can now:\n'
                '1. Upload real log files via /settings/\n'
                '2. Create real assets via /api/v1/assets/\n'
                '3. View generated alerts on the dashboard\n'
                '4. Create investigations from alerts\n'
            )
        )
