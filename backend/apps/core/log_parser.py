"""
Log Parser Utility for SIEM
Parses various log formats and extracts security events
"""

import re
import json
from datetime import datetime
from django.utils import timezone
import ipaddress


class LogParser:
    """Parse various log formats into structured events"""
    
    # Common log patterns
    PATTERNS = {
        'syslog': r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+)\s+(?P<hostname>\S+)\s+(?P<process>\S+?)(\[(?P<pid>\d+)\])?\:\s+(?P<message>.*)',
        'apache': r'(?P<ip>\S+)\s+\S+\s+\S+\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+\S+"\s+(?P<status>\d+)\s+(?P<size>\S+)',
        'nginx': r'(?P<ip>\S+)\s+-\s+-\s+\[(?P<timestamp>[^\]]+)\]\s+"(?P<method>\S+)\s+(?P<url>\S+)\s+\S+"\s+(?P<status>\d+)\s+(?P<size>\d+)',
        'windows_event': r'(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<source>\S+)\s+(?P<event_id>\d+)\s+(?P<message>.*)',
        'firewall': r'(?P<timestamp>\S+\s+\S+)\s+(?P<action>ACCEPT|DENY|DROP)\s+(?P<protocol>\S+)\s+(?P<src_ip>\S+):(?P<src_port>\d+)\s+->\s+(?P<dst_ip>\S+):(?P<dst_port>\d+)',
        'auth': r'(?P<timestamp>\w+\s+\d+\s+\d+:\d+:\d+).*?(?P<action>Failed|Accepted)\s+(?P<method>\w+)\s+for\s+(?P<user>\S+)\s+from\s+(?P<ip>\S+)',
    }
    
    @staticmethod
    def detect_log_type(line):
        """Detect the type of log from a sample line"""
        for log_type, pattern in LogParser.PATTERNS.items():
            if re.search(pattern, line):
                return log_type
        return 'generic'
    
    @staticmethod
    def parse_line(line, log_type=None):
        """Parse a single log line"""
        if not log_type:
            log_type = LogParser.detect_log_type(line)
        
        pattern = LogParser.PATTERNS.get(log_type)
        if not pattern:
            return LogParser.parse_generic(line)
        
        match = re.search(pattern, line)
        if not match:
            return LogParser.parse_generic(line)
        
        data = match.groupdict()
        
        # Parse timestamp
        timestamp = LogParser.parse_timestamp(data.get('timestamp', ''))
        
        # Extract IP addresses
        source_ip = data.get('ip') or data.get('src_ip')
        dest_ip = data.get('dst_ip')
        
        # Determine severity
        severity = LogParser.determine_severity(data, log_type)
        
        # Categorize event
        category = LogParser.categorize_event(data, log_type)
        
        return {
            'timestamp': timestamp,
            'source': data.get('hostname') or data.get('source') or 'unknown',
            'message': data.get('message') or line,
            'raw_log': line,
            'severity': severity,
            'category': category,
            'source_ip': source_ip,
            'dest_ip': dest_ip,
            'source_port': data.get('src_port'),
            'dest_port': data.get('dst_port'),
            'username': data.get('user'),
            'process_name': data.get('process'),
            'protocol': data.get('protocol'),
            'action': data.get('action') or data.get('method'),
            'result': data.get('status'),
            'log_type': log_type,
        }
    
    @staticmethod
    def parse_generic(line):
        """Parse generic log line"""
        return {
            'timestamp': timezone.now(),
            'source': 'generic',
            'message': line,
            'raw_log': line,
            'severity': 'info',
            'category': 'system',
            'log_type': 'generic',
        }
    
    @staticmethod
    def parse_timestamp(timestamp_str):
        """Parse various timestamp formats"""
        if not timestamp_str:
            return timezone.now()
        
        formats = [
            '%b %d %H:%M:%S',  # Syslog: Nov 22 10:30:45
            '%d/%b/%Y:%H:%M:%S',  # Apache: 22/Nov/2025:10:30:45
            '%Y-%m-%d %H:%M:%S',  # ISO: 2025-11-22 10:30:45
            '%Y-%m-%dT%H:%M:%S',  # ISO with T
        ]
        
        for fmt in formats:
            try:
                dt = datetime.strptime(timestamp_str.split()[0] + ' ' + timestamp_str.split()[1] if ' ' in timestamp_str else timestamp_str, fmt)
                # Add current year if not present
                if dt.year == 1900:
                    dt = dt.replace(year=datetime.now().year)
                return timezone.make_aware(dt)
            except (ValueError, IndexError):
                continue
        
        return timezone.now()
    
    @staticmethod
    def determine_severity(data, log_type):
        """Determine event severity based on content"""
        message = str(data.get('message', '')).lower()
        action = str(data.get('action', '')).lower()
        status = str(data.get('status', ''))
        
        # Critical indicators
        if any(word in message for word in ['critical', 'emergency', 'fatal', 'panic']):
            return 'critical'
        
        # High severity indicators
        if any(word in message for word in ['error', 'failed', 'failure', 'denied', 'unauthorized', 'breach', 'attack', 'malware', 'virus']):
            return 'high'
        
        if action in ['deny', 'drop', 'block', 'failed']:
            return 'high'
        
        if status and status.startswith('5'):  # 5xx errors
            return 'high'
        
        # Medium severity
        if any(word in message for word in ['warning', 'warn', 'suspicious', 'anomaly']):
            return 'medium'
        
        if status and status.startswith('4'):  # 4xx errors
            return 'medium'
        
        # Low severity
        if any(word in message for word in ['notice', 'info']):
            return 'low'
        
        return 'info'
    
    @staticmethod
    def categorize_event(data, log_type):
        """Categorize the event"""
        message = str(data.get('message', '')).lower()
        
        if log_type == 'auth' or 'login' in message or 'auth' in message:
            return 'authentication'
        
        if log_type == 'firewall' or 'firewall' in message:
            return 'network'
        
        if any(word in message for word in ['malware', 'virus', 'trojan', 'ransomware']):
            return 'malware'
        
        if any(word in message for word in ['access', 'read', 'write', 'file']):
            return 'data_access'
        
        if any(word in message for word in ['attack', 'exploit', 'intrusion', 'breach']):
            return 'threat'
        
        if log_type in ['apache', 'nginx']:
            return 'application'
        
        return 'system'
    
    @staticmethod
    def parse_file(file_content, log_type=None):
        """Parse entire log file"""
        lines = file_content.decode('utf-8', errors='ignore').split('\n')
        events = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            try:
                event = LogParser.parse_line(line, log_type)
                if event:
                    events.append(event)
            except Exception as e:
                # Log parsing error but continue
                continue
        
        return events
    
    @staticmethod
    def validate_ip(ip_str):
        """Validate IP address"""
        try:
            ipaddress.ip_address(ip_str)
            return True
        except ValueError:
            return False


class ThreatDetector:
    """Detect threats in parsed events with comprehensive pattern matching"""
    
    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(?i)(union.*select|select.*from.*where)',
        r'(?i)(insert.*into|update.*set)',
        r'(?i)(drop.*table|delete.*from)',
        r'(?i)(exec.*xp_|exec.*sp_)',
        r'(?i)(\'.*or.*\'.*=.*\')',
        r'(?i)(--|\#|\/\*)',  # SQL comments
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r'(?i)(<script[^>]*>)',
        r'(?i)(javascript:)',
        r'(?i)(onerror\s*=|onload\s*=|onclick\s*=)',
        r'(?i)(<iframe|<object|<embed)',
        r'(?i)(alert\(|confirm\(|prompt\()',
    ]
    
    # Command Injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r'(?i)(cmd\.exe|powershell\.exe)',
        r'(?i)(/bin/bash|/bin/sh|/bin/zsh)',
        r'(?i)(;.*ls|;.*cat|;.*wget|;.*curl)',
        r'(?i)(\|.*whoami|\|.*id|\|.*uname)',
        r'(?i)(&&.*rm|&&.*chmod)',
    ]
    
    # Path Traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r'(\.\.\/|\.\.\\){2,}',
        r'(?i)(\/etc\/passwd|\/etc\/shadow)',
        r'(?i)(c:\\windows\\system32)',
        r'(?i)(%2e%2e%2f|%2e%2e%5c)',  # URL encoded
    ]
    
    # Malware indicators
    MALWARE_PATTERNS = [
        r'(?i)(ransomware|cryptolocker|wannacry)',
        r'(?i)(trojan|backdoor|rootkit)',
        r'(?i)(mimikatz|metasploit|cobalt)',
        r'(?i)(reverse.*shell|bind.*shell)',
        r'(?i)(payload|exploit|shellcode)',
    ]
    
    # Data exfiltration patterns
    DATA_EXFIL_PATTERNS = [
        r'(?i)(base64.*decode|base64.*encode)',
        r'(?i)(wget.*http|curl.*http)',
        r'(?i)(scp.*@|rsync.*@)',
        r'(?i)(ftp.*put|tftp.*put)',
    ]
    
    # Privilege escalation patterns
    PRIVILEGE_ESC_PATTERNS = [
        r'(?i)(sudo.*su|sudo.*-i)',
        r'(?i)(chmod.*777|chmod.*\+s)',
        r'(?i)(setuid|setgid)',
        r'(?i)(runas|psexec)',
    ]
    
    # Port scanning patterns
    PORT_SCAN_THRESHOLD = 10  # Connections to different ports from same IP
    
    # Brute force detection
    FAILED_LOGIN_THRESHOLD = 5
    
    # DDoS detection
    REQUEST_RATE_THRESHOLD = 100  # Requests per IP
    
    @staticmethod
    def detect_threats(events):
        """Detect threats in a list of events with comprehensive analysis"""
        threats = []
        
        # Pattern-based detection
        pattern_categories = {
            'sql_injection': (ThreatDetector.SQL_INJECTION_PATTERNS, 'critical'),
            'xss_attack': (ThreatDetector.XSS_PATTERNS, 'high'),
            'command_injection': (ThreatDetector.COMMAND_INJECTION_PATTERNS, 'critical'),
            'path_traversal': (ThreatDetector.PATH_TRAVERSAL_PATTERNS, 'high'),
            'malware_detected': (ThreatDetector.MALWARE_PATTERNS, 'critical'),
            'data_exfiltration': (ThreatDetector.DATA_EXFIL_PATTERNS, 'critical'),
            'privilege_escalation': (ThreatDetector.PRIVILEGE_ESC_PATTERNS, 'critical'),
        }
        
        for event in events:
            message = event.get('message', '')
            raw_log = event.get('raw_log', '')
            combined = f"{message} {raw_log}"
            
            for threat_type, (patterns, severity) in pattern_categories.items():
                for pattern in patterns:
                    if re.search(pattern, combined):
                        threats.append({
                            'type': threat_type,
                            'event': event,
                            'pattern': pattern,
                            'severity': severity,
                            'description': f'{threat_type.replace("_", " ").title()} detected in log'
                        })
                        break  # Only report once per threat type per event
        
        # Behavioral analysis
        
        # 1. Brute force detection
        failed_logins = {}
        for event in events:
            if event.get('category') == 'authentication' and 'failed' in str(event.get('action', '')).lower():
                ip = event.get('source_ip')
                if ip:
                    failed_logins[ip] = failed_logins.get(ip, 0) + 1
        
        for ip, count in failed_logins.items():
            if count >= ThreatDetector.FAILED_LOGIN_THRESHOLD:
                threats.append({
                    'type': 'brute_force_attack',
                    'source_ip': ip,
                    'failed_attempts': count,
                    'severity': 'high',
                    'description': f'Brute force attack detected: {count} failed login attempts from {ip}'
                })
        
        # 2. Port scanning detection
        port_connections = {}
        for event in events:
            if event.get('dest_port'):
                ip = event.get('source_ip')
                if ip:
                    if ip not in port_connections:
                        port_connections[ip] = set()
                    port_connections[ip].add(event.get('dest_port'))
        
        for ip, ports in port_connections.items():
            if len(ports) >= ThreatDetector.PORT_SCAN_THRESHOLD:
                threats.append({
                    'type': 'port_scan',
                    'source_ip': ip,
                    'ports_scanned': len(ports),
                    'severity': 'medium',
                    'description': f'Port scanning detected: {len(ports)} different ports accessed from {ip}'
                })
        
        # 3. DDoS/High request rate detection
        request_counts = {}
        for event in events:
            ip = event.get('source_ip')
            if ip:
                request_counts[ip] = request_counts.get(ip, 0) + 1
        
        for ip, count in request_counts.items():
            if count >= ThreatDetector.REQUEST_RATE_THRESHOLD:
                threats.append({
                    'type': 'ddos_attempt',
                    'source_ip': ip,
                    'request_count': count,
                    'severity': 'high',
                    'description': f'Potential DDoS attack: {count} requests from {ip}'
                })
        
        # 4. Suspicious user agent detection
        suspicious_agents = ['nikto', 'sqlmap', 'nmap', 'masscan', 'burp', 'metasploit']
        for event in events:
            message = event.get('message', '').lower()
            for agent in suspicious_agents:
                if agent in message:
                    threats.append({
                        'type': 'suspicious_tool',
                        'event': event,
                        'tool': agent,
                        'severity': 'high',
                        'description': f'Suspicious security tool detected: {agent}'
                    })
                    break
        
        # 5. Lateral movement detection
        lateral_movement_patterns = [
            r'(?i)(psexec|wmic|winrm)',
            r'(?i)(net.*use|net.*share)',
            r'(?i)(rdp.*connection|remote.*desktop)',
        ]
        
        for event in events:
            combined = f"{event.get('message', '')} {event.get('raw_log', '')}"
            for pattern in lateral_movement_patterns:
                if re.search(pattern, combined):
                    threats.append({
                        'type': 'lateral_movement',
                        'event': event,
                        'pattern': pattern,
                        'severity': 'high',
                        'description': 'Potential lateral movement detected'
                    })
                    break
        
        return threats
