"""
Management command to populate MITRE ATT&CK framework data
"""
from django.core.management.base import BaseCommand
from apps.core.models import MitreTactic, MitreTechnique


class Command(BaseCommand):
    help = 'Populate MITRE ATT&CK tactics and techniques'

    def handle(self, *args, **options):
        self.stdout.write('Populating MITRE ATT&CK data...')
        
        # Create Tactics
        tactics_data = [
            {
                'tactic_id': 'TA0001',
                'name': 'Initial Access',
                'description': 'The adversary is trying to get into your network.',
                'url': 'https://attack.mitre.org/tactics/TA0001/'
            },
            {
                'tactic_id': 'TA0002',
                'name': 'Execution',
                'description': 'The adversary is trying to run malicious code.',
                'url': 'https://attack.mitre.org/tactics/TA0002/'
            },
            {
                'tactic_id': 'TA0003',
                'name': 'Persistence',
                'description': 'The adversary is trying to maintain their foothold.',
                'url': 'https://attack.mitre.org/tactics/TA0003/'
            },
            {
                'tactic_id': 'TA0004',
                'name': 'Privilege Escalation',
                'description': 'The adversary is trying to gain higher-level permissions.',
                'url': 'https://attack.mitre.org/tactics/TA0004/'
            },
            {
                'tactic_id': 'TA0005',
                'name': 'Defense Evasion',
                'description': 'The adversary is trying to avoid being detected.',
                'url': 'https://attack.mitre.org/tactics/TA0005/'
            },
            {
                'tactic_id': 'TA0006',
                'name': 'Credential Access',
                'description': 'The adversary is trying to steal account names and passwords.',
                'url': 'https://attack.mitre.org/tactics/TA0006/'
            },
            {
                'tactic_id': 'TA0007',
                'name': 'Discovery',
                'description': 'The adversary is trying to figure out your environment.',
                'url': 'https://attack.mitre.org/tactics/TA0007/'
            },
            {
                'tactic_id': 'TA0008',
                'name': 'Lateral Movement',
                'description': 'The adversary is trying to move through your environment.',
                'url': 'https://attack.mitre.org/tactics/TA0008/'
            },
            {
                'tactic_id': 'TA0009',
                'name': 'Collection',
                'description': 'The adversary is trying to gather data of interest.',
                'url': 'https://attack.mitre.org/tactics/TA0009/'
            },
            {
                'tactic_id': 'TA0010',
                'name': 'Exfiltration',
                'description': 'The adversary is trying to steal data.',
                'url': 'https://attack.mitre.org/tactics/TA0010/'
            },
            {
                'tactic_id': 'TA0011',
                'name': 'Command and Control',
                'description': 'The adversary is trying to communicate with compromised systems.',
                'url': 'https://attack.mitre.org/tactics/TA0011/'
            },
            {
                'tactic_id': 'TA0040',
                'name': 'Impact',
                'description': 'The adversary is trying to manipulate, interrupt, or destroy your systems and data.',
                'url': 'https://attack.mitre.org/tactics/TA0040/'
            },
        ]
        
        tactics = {}
        for tactic_data in tactics_data:
            tactic, created = MitreTactic.objects.get_or_create(
                tactic_id=tactic_data['tactic_id'],
                defaults=tactic_data
            )
            tactics[tactic.tactic_id] = tactic
            if created:
                self.stdout.write(f'  Created tactic: {tactic.name}')
        
        # Create sample techniques
        techniques_data = [
            # Initial Access
            {
                'technique_id': 'T1078',
                'name': 'Valid Accounts',
                'description': 'Adversaries may obtain and abuse credentials of existing accounts.',
                'tactic_id': 'TA0001',
                'platforms': '["Windows", "Linux", "macOS", "Cloud"]',
                'data_sources': '["Authentication logs", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1078/'
            },
            {
                'technique_id': 'T1566',
                'name': 'Phishing',
                'description': 'Adversaries may send phishing messages to gain access to victim systems.',
                'tactic_id': 'TA0001',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Email gateway", "Network traffic"]',
                'url': 'https://attack.mitre.org/techniques/T1566/'
            },
            {
                'technique_id': 'T1190',
                'name': 'Exploit Public-Facing Application',
                'description': 'Adversaries may attempt to exploit a weakness in an Internet-facing host or system.',
                'tactic_id': 'TA0001',
                'platforms': '["Windows", "Linux", "Network"]',
                'data_sources': '["Application logs", "Network traffic"]',
                'url': 'https://attack.mitre.org/techniques/T1190/'
            },
            
            # Execution
            {
                'technique_id': 'T1059',
                'name': 'Command and Scripting Interpreter',
                'description': 'Adversaries may abuse command and script interpreters to execute commands.',
                'tactic_id': 'TA0002',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Process monitoring", "Command line"]',
                'url': 'https://attack.mitre.org/techniques/T1059/'
            },
            {
                'technique_id': 'T1203',
                'name': 'Exploitation for Client Execution',
                'description': 'Adversaries may exploit software vulnerabilities in client applications.',
                'tactic_id': 'TA0002',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Process monitoring", "Anti-virus"]',
                'url': 'https://attack.mitre.org/techniques/T1203/'
            },
            
            # Persistence
            {
                'technique_id': 'T1053',
                'name': 'Scheduled Task/Job',
                'description': 'Adversaries may abuse task scheduling functionality to facilitate persistence.',
                'tactic_id': 'TA0003',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["File monitoring", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1053/'
            },
            {
                'technique_id': 'T1136',
                'name': 'Create Account',
                'description': 'Adversaries may create an account to maintain access to victim systems.',
                'tactic_id': 'TA0003',
                'platforms': '["Windows", "Linux", "macOS", "Cloud"]',
                'data_sources': '["Process monitoring", "Authentication logs"]',
                'url': 'https://attack.mitre.org/techniques/T1136/'
            },
            
            # Privilege Escalation
            {
                'technique_id': 'T1068',
                'name': 'Exploitation for Privilege Escalation',
                'description': 'Adversaries may exploit software vulnerabilities to elevate privileges.',
                'tactic_id': 'TA0004',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Process monitoring", "Windows Error Reporting"]',
                'url': 'https://attack.mitre.org/techniques/T1068/'
            },
            {
                'technique_id': 'T1548',
                'name': 'Abuse Elevation Control Mechanism',
                'description': 'Adversaries may circumvent mechanisms designed to control elevate privileges.',
                'tactic_id': 'TA0004',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Process monitoring", "Command line"]',
                'url': 'https://attack.mitre.org/techniques/T1548/'
            },
            
            # Defense Evasion
            {
                'technique_id': 'T1070',
                'name': 'Indicator Removal',
                'description': 'Adversaries may delete or modify artifacts generated on a host system.',
                'tactic_id': 'TA0005',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["File monitoring", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1070/'
            },
            {
                'technique_id': 'T1027',
                'name': 'Obfuscated Files or Information',
                'description': 'Adversaries may attempt to make an executable or file difficult to discover.',
                'tactic_id': 'TA0005',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["File monitoring", "Network traffic"]',
                'url': 'https://attack.mitre.org/techniques/T1027/'
            },
            
            # Credential Access
            {
                'technique_id': 'T1110',
                'name': 'Brute Force',
                'description': 'Adversaries may use brute force techniques to gain access to accounts.',
                'tactic_id': 'TA0006',
                'platforms': '["Windows", "Linux", "macOS", "Cloud"]',
                'data_sources': '["Authentication logs"]',
                'url': 'https://attack.mitre.org/techniques/T1110/'
            },
            {
                'technique_id': 'T1003',
                'name': 'OS Credential Dumping',
                'description': 'Adversaries may attempt to dump credentials to obtain account login information.',
                'tactic_id': 'TA0006',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Process monitoring", "API monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1003/'
            },
            
            # Discovery
            {
                'technique_id': 'T1087',
                'name': 'Account Discovery',
                'description': 'Adversaries may attempt to get a listing of accounts on a system or domain.',
                'tactic_id': 'TA0007',
                'platforms': '["Windows", "Linux", "macOS", "Cloud"]',
                'data_sources': '["Process monitoring", "API monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1087/'
            },
            {
                'technique_id': 'T1018',
                'name': 'Remote System Discovery',
                'description': 'Adversaries may attempt to get a listing of other systems.',
                'tactic_id': 'TA0007',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Network protocol analysis", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1018/'
            },
            
            # Lateral Movement
            {
                'technique_id': 'T1021',
                'name': 'Remote Services',
                'description': 'Adversaries may use valid accounts to log into a service.',
                'tactic_id': 'TA0008',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Authentication logs", "Network traffic"]',
                'url': 'https://attack.mitre.org/techniques/T1021/'
            },
            {
                'technique_id': 'T1210',
                'name': 'Exploitation of Remote Services',
                'description': 'Adversaries may exploit remote services to gain unauthorized access.',
                'tactic_id': 'TA0008',
                'platforms': '["Windows", "Linux"]',
                'data_sources': '["Network traffic", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1210/'
            },
            
            # Collection
            {
                'technique_id': 'T1005',
                'name': 'Data from Local System',
                'description': 'Adversaries may search local system sources to find files of interest.',
                'tactic_id': 'TA0009',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["File monitoring", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1005/'
            },
            {
                'technique_id': 'T1056',
                'name': 'Input Capture',
                'description': 'Adversaries may use methods to capture user input.',
                'tactic_id': 'TA0009',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["API monitoring", "Kernel drivers"]',
                'url': 'https://attack.mitre.org/techniques/T1056/'
            },
            
            # Exfiltration
            {
                'technique_id': 'T1041',
                'name': 'Exfiltration Over C2 Channel',
                'description': 'Adversaries may steal data by exfiltrating it over an existing C2 channel.',
                'tactic_id': 'TA0010',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Network traffic", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1041/'
            },
            {
                'technique_id': 'T1567',
                'name': 'Exfiltration Over Web Service',
                'description': 'Adversaries may use an existing web service to exfiltrate data.',
                'tactic_id': 'TA0010',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Network traffic", "SSL/TLS inspection"]',
                'url': 'https://attack.mitre.org/techniques/T1567/'
            },
            
            # Command and Control
            {
                'technique_id': 'T1071',
                'name': 'Application Layer Protocol',
                'description': 'Adversaries may communicate using application layer protocols.',
                'tactic_id': 'TA0011',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Network traffic", "Packet capture"]',
                'url': 'https://attack.mitre.org/techniques/T1071/'
            },
            {
                'technique_id': 'T1573',
                'name': 'Encrypted Channel',
                'description': 'Adversaries may employ a known encryption algorithm to conceal C2 communications.',
                'tactic_id': 'TA0011',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Network traffic", "SSL/TLS inspection"]',
                'url': 'https://attack.mitre.org/techniques/T1573/'
            },
            
            # Impact
            {
                'technique_id': 'T1486',
                'name': 'Data Encrypted for Impact',
                'description': 'Adversaries may encrypt data on target systems to interrupt availability.',
                'tactic_id': 'TA0040',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["File monitoring", "Process monitoring"]',
                'url': 'https://attack.mitre.org/techniques/T1486/'
            },
            {
                'technique_id': 'T1490',
                'name': 'Inhibit System Recovery',
                'description': 'Adversaries may delete or remove built-in data and turn off services.',
                'tactic_id': 'TA0040',
                'platforms': '["Windows", "Linux", "macOS"]',
                'data_sources': '["Process monitoring", "Windows event logs"]',
                'url': 'https://attack.mitre.org/techniques/T1490/'
            },
        ]
        
        for tech_data in techniques_data:
            tactic_id = tech_data.pop('tactic_id')
            tactic = tactics[tactic_id]
            
            technique, created = MitreTechnique.objects.get_or_create(
                technique_id=tech_data['technique_id'],
                defaults={**tech_data, 'tactic': tactic}
            )
            if created:
                self.stdout.write(f'  Created technique: {technique.name}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully populated {len(tactics_data)} tactics and {len(techniques_data)} techniques'))
