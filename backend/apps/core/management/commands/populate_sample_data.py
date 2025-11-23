"""
Populate database with comprehensive sample data for SIEM testing
"""

import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
from apps.core.models import (
    Event, Alert, Asset, LogSource, IOC, ThreatActor, ThreatFeed,
    DetectionRule, Investigation, InvestigationNote, Playbook,
    MitreTactic, MitreTechnique, ComplianceFramework, ComplianceCheck,
    Report, AnomalyDetection, UserBehaviorBaseline
)


class Command(BaseCommand):
    help = 'Populate database with comprehensive sample SIEM data'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with sample data...')
        
        # Create sample users
        self.create_users()
        
        # Create log sources
        self.create_log_sources()
        
        # Create assets
        self.create_assets()
        
        # Create IOCs
        self.create_iocs()
        
        # Create threat actors
        self.create_threat_actors()
        
        # Create sample events with malicious activity
        self.create_sample_events()
        
        # Create sample alerts
        self.create_sample_alerts()
        
        # Create investigations
        self.create_investigations()
        
        # Create detection rules
        self.create_detection_rules()
        
        # Create playbooks
        self.create_playbooks()
        
        # Create anomalies
        self.create_anomalies()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
    
    def create_users(self):
        """Create sample users"""
        if not User.objects.filter(username='analyst').exists():
            User.objects.create_user('analyst', 'analyst@dere.com', 'password123')
            self.stdout.write('Created analyst user')
    
    def create_log_sources(self):
        """Create sample log sources"""
        sources = [
            {'name': 'Web Server 01', 'source_type': 'apache', 'host': '192.168.1.10'},
            {'name': 'Firewall Main', 'source_type': 'firewall', 'host': '192.168.1.1'},
            {'name': 'AD Controller', 'source_type': 'windows_event', 'host': '192.168.1.5'},
            {'name': 'Database Server', 'source_type': 'syslog', 'host': '192.168.1.20'},
            {'name': 'Email Gateway', 'source_type': 'generic', 'host': '192.168.1.30'},
        ]
        
        for source_data in sources:
            LogSource.objects.get_or_create(
                name=source_data['name'],
                defaults={
                    'source_type': source_data['source_type'],
                    'host': source_data['host'],
                    'is_active': True,
                }
            )
        self.stdout.write(f'Created {len(sources)} log sources')
    
    def create_assets(self):
        """Create sample assets"""
        assets = [
            {'hostname': 'WEB-SRV-01', 'asset_type': 'server', 'ip': '192.168.1.10', 'criticality': 'high'},
            {'hostname': 'DB-SRV-01', 'asset_type': 'server', 'ip': '192.168.1.20', 'criticality': 'critical'},
            {'hostname': 'FW-01', 'asset_type': 'network_device', 'ip': '192.168.1.1', 'criticality': 'critical'},
            {'hostname': 'LAPTOP-JOHN', 'asset_type': 'workstation', 'ip': '192.168.1.100', 'criticality': 'medium'},
            {'hostname': 'LAPTOP-JANE', 'asset_type': 'workstation', 'ip': '192.168.1.101', 'criticality': 'medium'},
        ]
        
        for asset_data in assets:
            Asset.objects.get_or_create(
                hostname=asset_data['hostname'],
                defaults=asset_data
            )
        self.stdout.write(f'Created {len(assets)} assets')
    
    def create_iocs(self):
        """Create sample IOCs"""
        iocs = [
            {'value': '185.220.101.45', 'ioc_type': 'ip', 'severity': 'critical', 'description': 'Known C2 server'},
            {'value': '198.51.100.23', 'ioc_type': 'ip', 'severity': 'high', 'description': 'Malware distribution'},
            {'value': 'malicious-domain.com', 'ioc_type': 'domain', 'severity': 'high', 'description': 'Phishing domain'},
            {'value': 'evil-site.net', 'ioc_type': 'domain', 'severity': 'critical', 'description': 'Ransomware C2'},
            {'value': 'a1b2c3d4e5f6', 'ioc_type': 'hash', 'severity': 'critical', 'description': 'Trojan hash'},
            {'value': 'http://malware-download.com/payload.exe', 'ioc_type': 'url', 'severity': 'critical', 'description': 'Malware download URL'},
        ]
        
        for ioc_data in iocs:
            IOC.objects.get_or_create(
                value=ioc_data['value'],
                defaults={
                    'ioc_type': ioc_data['ioc_type'],
                    'severity': ioc_data['severity'],
                    'description': ioc_data['description'],
                    'is_active': True,
                }
            )
        self.stdout.write(f'Created {len(iocs)} IOCs')
    
    def create_threat_actors(self):
        """Create sample threat actors"""
        actors = [
            {'name': 'APT28', 'description': 'Russian state-sponsored group', 'sophistication': 'high'},
            {'name': 'Lazarus Group', 'description': 'North Korean APT group', 'sophistication': 'high'},
            {'name': 'FIN7', 'description': 'Financial cybercrime group', 'sophistication': 'medium'},
        ]
        
        for actor_data in actors:
            ThreatActor.objects.get_or_create(
                name=actor_data['name'],
                defaults=actor_data
            )
        self.stdout.write(f'Created {len(actors)} threat actors')
    
    def create_sample_events(self):
        """Create sample events including malicious activity"""
        now = timezone.now()
        log_source = LogSource.objects.first()
        
        # Malicious events
        malicious_events = [
            # SQL Injection attempts
            {
                'message': "GET /login.php?user=admin' OR '1'='1 HTTP/1.1",
                'severity': 'critical',
                'category': 'threat',
                'source_ip': '203.0.113.50',
            },
            {
                'message': "POST /search?q='; DROP TABLE users; --",
                'severity': 'critical',
                'category': 'threat',
                'source_ip': '203.0.113.50',
            },
            # XSS attempts
            {
                'message': "GET /comment?text=<script>alert('XSS')</script>",
                'severity': 'high',
                'category': 'threat',
                'source_ip': '198.51.100.75',
            },
            # Command injection
            {
                'message': "Request: /api/exec?cmd=ls; cat /etc/passwd",
                'severity': 'critical',
                'category': 'threat',
                'source_ip': '198.51.100.75',
            },
            # Brute force attempts
            *[{
                'message': f"Failed password for admin from 185.220.101.45 port {5000+i}",
                'severity': 'high',
                'category': 'authentication',
                'source_ip': '185.220.101.45',
                'action': 'Failed',
            } for i in range(10)],
            # Port scanning
            *[{
                'message': f"Connection attempt to port {port}",
                'severity': 'medium',
                'category': 'network',
                'source_ip': '203.0.113.100',
                'dest_port': port,
            } for port in [21, 22, 23, 80, 443, 3306, 3389, 8080, 8443, 5432, 27017, 6379]],
            # Malware indicators
            {
                'message': "Detected: Trojan.Generic.12345 in file payload.exe",
                'severity': 'critical',
                'category': 'malware',
                'source_ip': '192.168.1.100',
            },
            {
                'message': "Suspicious process: mimikatz.exe started by user john",
                'severity': 'critical',
                'category': 'threat',
                'source_ip': '192.168.1.100',
            },
            # Data exfiltration
            {
                'message': "Large data transfer: 5GB uploaded to external IP 185.220.101.45",
                'severity': 'high',
                'category': 'data_access',
                'source_ip': '192.168.1.20',
                'dest_ip': '185.220.101.45',
            },
            # Lateral movement
            {
                'message': "psexec.exe executed targeting \\\\DB-SRV-01",
                'severity': 'high',
                'category': 'threat',
                'source_ip': '192.168.1.100',
            },
        ]
        
        created_count = 0
        for i, event_data in enumerate(malicious_events):
            Event.objects.create(
                time=now - timedelta(hours=random.randint(1, 48)),
                source=event_data.get('source', 'security-system'),
                log_source=log_source,
                message=event_data['message'],
                raw_log=event_data['message'],
                severity=event_data['severity'],
                category=event_data['category'],
                source_ip=event_data.get('source_ip'),
                dest_ip=event_data.get('dest_ip'),
                dest_port=event_data.get('dest_port'),
                action=event_data.get('action', ''),
            )
            created_count += 1
        
        # Normal events
        normal_events = [
            {'message': 'User login successful: john@company.com', 'severity': 'info', 'category': 'authentication'},
            {'message': 'Backup completed successfully', 'severity': 'info', 'category': 'system'},
            {'message': 'Database query executed: SELECT * FROM products', 'severity': 'info', 'category': 'data_access'},
            {'message': 'File uploaded: report.pdf', 'severity': 'info', 'category': 'data_access'},
            {'message': 'System update installed', 'severity': 'info', 'category': 'system'},
        ] * 10  # Create 50 normal events
        
        for event_data in normal_events:
            Event.objects.create(
                time=now - timedelta(hours=random.randint(1, 72)),
                source='system',
                log_source=log_source,
                message=event_data['message'],
                raw_log=event_data['message'],
                severity=event_data['severity'],
                category=event_data['category'],
                source_ip=f'192.168.1.{random.randint(10, 200)}',
                action='',
            )
            created_count += 1
        
        self.stdout.write(f'Created {created_count} events')
    
    def create_sample_alerts(self):
        """Create sample alerts"""
        alerts = [
            {
                'name': 'SQL Injection Attack',
                'description': 'Multiple SQL injection attempts detected from 203.0.113.50',
                'severity': 'critical',
                'status': 'new',
            },
            {
                'name': 'Brute Force Attack',
                'description': 'Brute force attack detected: 10 failed login attempts from 185.220.101.45',
                'severity': 'high',
                'status': 'open',
            },
            {
                'name': 'Port Scan Detected',
                'description': 'Port scanning detected: 12 different ports accessed from 203.0.113.100',
                'severity': 'medium',
                'status': 'investigating',
            },
            {
                'name': 'Malware Detected',
                'description': 'Trojan detected on LAPTOP-JOHN',
                'severity': 'critical',
                'status': 'new',
            },
            {
                'name': 'Suspicious Tool',
                'description': 'Mimikatz execution detected on LAPTOP-JOHN',
                'severity': 'critical',
                'status': 'new',
            },
        ]
        
        for alert_data in alerts:
            Alert.objects.get_or_create(
                name=alert_data['name'],
                defaults=alert_data
            )
        self.stdout.write(f'Created {len(alerts)} alerts')
    
    def create_investigations(self):
        """Create sample investigations"""
        user = User.objects.first()
        
        investigations = [
            {
                'case_id': 'INV-2025-001',
                'title': 'SQL Injection Investigation',
                'description': 'Investigating SQL injection attempts from external IP',
                'priority': 'critical',
                'status': 'in_progress',
            },
            {
                'case_id': 'INV-2025-002',
                'title': 'Malware Incident - LAPTOP-JOHN',
                'description': 'Trojan detected on user workstation',
                'priority': 'high',
                'status': 'open',
            },
        ]
        
        for inv_data in investigations:
            Investigation.objects.get_or_create(
                case_id=inv_data['case_id'],
                defaults={
                    **inv_data,
                    'owner': user,
                }
            )
        self.stdout.write(f'Created {len(investigations)} investigations')
    
    def create_detection_rules(self):
        """Create sample detection rules"""
        rules = [
            {
                'name': 'SQL Injection Detection',
                'description': 'Detects SQL injection patterns in web requests',
                'rule_type': 'signature',
                'severity': 'critical',
                'is_enabled': True,
            },
            {
                'name': 'Brute Force Detection',
                'description': 'Detects multiple failed login attempts',
                'rule_type': 'correlation',
                'severity': 'high',
                'is_enabled': True,
            },
            {
                'name': 'Malware Execution',
                'description': 'Detects known malware execution patterns',
                'rule_type': 'signature',
                'severity': 'critical',
                'is_enabled': True,
            },
        ]
        
        for rule_data in rules:
            DetectionRule.objects.get_or_create(
                name=rule_data['name'],
                defaults=rule_data
            )
        self.stdout.write(f'Created {len(rules)} detection rules')
    
    def create_playbooks(self):
        """Create sample playbooks"""
        playbooks = [
            {
                'name': 'SQL Injection Response',
                'description': 'Response procedures for SQL injection attacks',
            },
            {
                'name': 'Malware Containment',
                'description': 'Steps to contain and remediate malware infections',
            },
            {
                'name': 'Brute Force Mitigation',
                'description': 'Procedures to mitigate brute force attacks',
            },
        ]
        
        for pb_data in playbooks:
            Playbook.objects.get_or_create(
                name=pb_data['name'],
                defaults=pb_data
            )
        self.stdout.write(f'Created {len(playbooks)} playbooks')
    
    def create_anomalies(self):
        """Create sample anomalies"""
        anomalies = [
            {
                'anomaly_type': 'unusual_login_time',
                'description': 'User login at unusual time (3 AM)',
                'severity': 'medium',
                'confidence_score': 0.85,
            },
            {
                'anomaly_type': 'unusual_data_access',
                'description': 'Unusual volume of database queries',
                'severity': 'high',
                'confidence_score': 0.92,
            },
        ]
        
        for anomaly_data in anomalies:
            AnomalyDetection.objects.get_or_create(
                anomaly_type=anomaly_data['anomaly_type'],
                defaults=anomaly_data
            )
        self.stdout.write(f'Created {len(anomalies)} anomalies')
