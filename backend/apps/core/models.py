from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import json


# ============================================================================
# ASSET MANAGEMENT
# ============================================================================

class Asset(models.Model):
    """Network assets/endpoints being monitored"""
    ASSET_TYPES = [
        ('server', 'Server'),
        ('workstation', 'Workstation'),
        ('network_device', 'Network Device'),
        ('mobile', 'Mobile Device'),
        ('iot', 'IoT Device'),
        ('cloud', 'Cloud Resource'),
    ]
    
    CRITICALITY_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    hostname = models.CharField(max_length=128)
    ip = models.GenericIPAddressField()
    mac_address = models.CharField(max_length=17, blank=True)
    asset_type = models.CharField(max_length=32, choices=ASSET_TYPES, default='server')
    os = models.CharField(max_length=64, blank=True)
    os_version = models.CharField(max_length=64, blank=True)
    owner = models.CharField(max_length=64, blank=True)
    department = models.CharField(max_length=64, blank=True)
    location = models.CharField(max_length=128, blank=True)
    criticality = models.CharField(max_length=16, choices=CRITICALITY_LEVELS, default='medium')
    risk_score = models.IntegerField(default=0)  # UEBA risk score
    last_seen = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    tags = models.TextField(blank=True)  # JSON array of tags
    metadata = models.TextField(blank=True)  # JSON for additional data
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-criticality', 'hostname']

    def __str__(self):
        return f"{self.hostname} ({self.ip})"


# ============================================================================
# EVENT & LOG MANAGEMENT
# ============================================================================

class LogSource(models.Model):
    """Log sources/collectors"""
    SOURCE_TYPES = [
        ('syslog', 'Syslog'),
        ('windows_event', 'Windows Event Log'),
        ('firewall', 'Firewall'),
        ('ids_ips', 'IDS/IPS'),
        ('web_server', 'Web Server'),
        ('database', 'Database'),
        ('cloud', 'Cloud Service'),
        ('edr', 'EDR/Endpoint'),
        ('application', 'Application'),
    ]
    
    name = models.CharField(max_length=128)
    source_type = models.CharField(max_length=32, choices=SOURCE_TYPES)
    host = models.CharField(max_length=128)
    port = models.IntegerField(null=True, blank=True)
    protocol = models.CharField(max_length=32, blank=True)
    is_active = models.BooleanField(default=True)
    events_received = models.BigIntegerField(default=0)
    last_event_time = models.DateTimeField(null=True, blank=True)
    parser_config = models.TextField(blank=True)  # JSON config for parsing
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.source_type})"


class Event(models.Model):
    """Security events/logs"""
    SEVERITY_CHOICES = [
        ('info', 'Info'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    EVENT_CATEGORIES = [
        ('authentication', 'Authentication'),
        ('network', 'Network'),
        ('malware', 'Malware'),
        ('data_access', 'Data Access'),
        ('system', 'System'),
        ('application', 'Application'),
        ('threat', 'Threat'),
    ]
    
    time = models.DateTimeField(db_index=True)
    source = models.CharField(max_length=128, db_index=True)
    log_source = models.ForeignKey(LogSource, null=True, blank=True, on_delete=models.SET_NULL)
    message = models.TextField()
    raw_log = models.TextField(blank=True)
    severity = models.CharField(max_length=16, choices=SEVERITY_CHOICES, default='info', db_index=True)
    category = models.CharField(max_length=32, choices=EVENT_CATEGORIES, default='system')
    asset = models.ForeignKey(Asset, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Normalized fields
    source_ip = models.GenericIPAddressField(null=True, blank=True, db_index=True)
    dest_ip = models.GenericIPAddressField(null=True, blank=True)
    source_port = models.IntegerField(null=True, blank=True)
    dest_port = models.IntegerField(null=True, blank=True)
    username = models.CharField(max_length=128, blank=True, db_index=True)
    process_name = models.CharField(max_length=256, blank=True)
    file_path = models.CharField(max_length=512, blank=True)
    protocol = models.CharField(max_length=32, blank=True)
    action = models.CharField(max_length=64, blank=True)
    result = models.CharField(max_length=64, blank=True)
    
    # Enrichment fields
    source_geo_country = models.CharField(max_length=64, blank=True)
    source_geo_city = models.CharField(max_length=128, blank=True)
    source_geo_lat = models.FloatField(null=True, blank=True)
    source_geo_lon = models.FloatField(null=True, blank=True)
    
    # Additional data
    tags = models.TextField(blank=True)  # JSON array
    custom_fields = models.TextField(blank=True)  # JSON object
    event_type = models.CharField(max_length=64, blank=True, db_index=True)  # sql_injection, brute_force, port_scan, etc.
    
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time']
        indexes = [
            models.Index(fields=['-time', 'severity']),
            models.Index(fields=['source_ip', '-time']),
        ]

    def __str__(self):
        return f"{self.time} - {self.source} - {self.severity}"


# ============================================================================
# THREAT INTELLIGENCE
# ============================================================================

class ThreatFeed(models.Model):
    """External threat intelligence feeds"""
    name = models.CharField(max_length=128)
    url = models.URLField(blank=True)
    feed_type = models.CharField(max_length=64)  # STIX, TAXII, CSV, JSON
    is_active = models.BooleanField(default=True)
    last_update = models.DateTimeField(null=True, blank=True)
    update_frequency = models.IntegerField(default=3600)  # seconds
    ioc_count = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class IOC(models.Model):
    """Indicators of Compromise"""
    IOC_TYPES = [
        ('ip', 'IP Address'),
        ('domain', 'Domain'),
        ('url', 'URL'),
        ('file_hash', 'File Hash'),
        ('email', 'Email Address'),
        ('registry', 'Registry Key'),
        ('mutex', 'Mutex'),
        ('user_agent', 'User Agent'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    
    ioc_type = models.CharField(max_length=32, choices=IOC_TYPES, db_index=True)
    value = models.CharField(max_length=512, db_index=True)
    description = models.TextField(blank=True)
    threat_type = models.CharField(max_length=128, blank=True)  # malware, phishing, c2, etc.
    confidence = models.CharField(max_length=16, choices=CONFIDENCE_LEVELS, default='medium')
    severity = models.CharField(max_length=16, choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], default='medium')
    
    # Attribution
    threat_actor = models.CharField(max_length=128, blank=True)
    campaign = models.CharField(max_length=128, blank=True)
    
    # Metadata
    source = models.ForeignKey(ThreatFeed, null=True, blank=True, on_delete=models.SET_NULL)
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    times_seen = models.IntegerField(default=1)
    is_active = models.BooleanField(default=True)
    tags = models.TextField(blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['ioc_type', 'value']
        ordering = ['-created']

    def __str__(self):
        return f"{self.ioc_type}: {self.value}"


class ThreatActor(models.Model):
    """Known threat actors and groups"""
    name = models.CharField(max_length=128, unique=True)
    aliases = models.TextField(blank=True)  # JSON array
    description = models.TextField(blank=True)
    motivation = models.CharField(max_length=128, blank=True)
    sophistication = models.CharField(max_length=32, choices=[('low','Low'),('medium','Medium'),('high','High'),('advanced','Advanced')], default='medium')
    country = models.CharField(max_length=64, blank=True)
    first_seen = models.DateField(null=True, blank=True)
    last_activity = models.DateField(null=True, blank=True)
    targets = models.TextField(blank=True)  # JSON array of target industries/regions
    ttps = models.TextField(blank=True)  # JSON array of MITRE ATT&CK techniques
    associated_malware = models.TextField(blank=True)
    references = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


# ============================================================================
# MITRE ATT&CK FRAMEWORK
# ============================================================================

class MitreTactic(models.Model):
    """MITRE ATT&CK Tactics"""
    tactic_id = models.CharField(max_length=16, unique=True)  # e.g., TA0001
    name = models.CharField(max_length=128)
    description = models.TextField()
    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.tactic_id} - {self.name}"


class MitreTechnique(models.Model):
    """MITRE ATT&CK Techniques"""
    technique_id = models.CharField(max_length=16, unique=True)  # e.g., T1078
    name = models.CharField(max_length=256)
    description = models.TextField()
    tactic = models.ForeignKey(MitreTactic, on_delete=models.CASCADE, related_name='techniques')
    parent_technique = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    is_subtechnique = models.BooleanField(default=False)
    platforms = models.TextField(blank=True)  # JSON array
    data_sources = models.TextField(blank=True)  # JSON array
    url = models.URLField(blank=True)

    def __str__(self):
        return f"{self.technique_id} - {self.name}"


class MITREMapping(models.Model):
    """Mapping of events/alerts/IOCs to MITRE ATT&CK techniques"""
    technique = models.ForeignKey(MitreTechnique, on_delete=models.CASCADE, related_name='mappings')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='mitre_mappings')
    alert = models.ForeignKey('Alert', on_delete=models.CASCADE, null=True, blank=True, related_name='mitre_mappings')
    ioc = models.ForeignKey(IOC, on_delete=models.CASCADE, null=True, blank=True, related_name='mitre_mappings')
    confidence = models.FloatField(default=0.5)  # Confidence score 0-1
    mapped_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    mapped_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "MITRE Mappings"
    
    def __str__(self):
        mapped_to = self.event or self.alert or self.ioc
        return f"{self.technique.technique_id} -> {mapped_to}"


# ============================================================================
# DETECTION & CORRELATION
# ============================================================================

class DetectionRule(models.Model):
    """Correlation and detection rules"""
    RULE_TYPES = [
        ('threshold', 'Threshold'),
        ('correlation', 'Correlation'),
        ('anomaly', 'Anomaly'),
        ('sigma', 'SIGMA Rule'),
        ('yara', 'YARA Rule'),
        ('custom', 'Custom Logic'),
    ]
    
    name = models.CharField(max_length=256)
    description = models.TextField()
    rule_type = models.CharField(max_length=32, choices=RULE_TYPES, default='threshold')
    severity = models.CharField(max_length=16, choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], default='medium')
    
    # Rule definition
    rule_logic = models.TextField()  # Query or logic definition
    threshold_value = models.IntegerField(null=True, blank=True)
    time_window = models.IntegerField(null=True, blank=True)  # seconds
    
    # MITRE ATT&CK mapping
    mitre_techniques = models.ManyToManyField(MitreTechnique, blank=True)
    
    # Metadata
    is_enabled = models.BooleanField(default=True)
    false_positive_rate = models.CharField(max_length=16, choices=[('low','Low'),('medium','Medium'),('high','High')], default='low')
    tags = models.TextField(blank=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    
    # Statistics
    times_triggered = models.IntegerField(default=0)
    last_triggered = models.DateTimeField(null=True, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Alert(models.Model):
    """Security alerts generated by detection rules"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('investigating', 'Investigating'),
        ('resolved', 'Resolved'),
        ('false_positive', 'False Positive'),
        ('closed', 'Closed'),
    ]
    
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    severity = models.CharField(max_length=16, choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], default='medium')
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='new', db_index=True)
    
    # Source
    detection_rule = models.ForeignKey(DetectionRule, null=True, blank=True, on_delete=models.SET_NULL)
    related_events = models.ManyToManyField(Event, blank=True)
    event_count = models.IntegerField(default=1)
    
    # Context
    source_ip = models.GenericIPAddressField(null=True, blank=True)
    dest_ip = models.GenericIPAddressField(null=True, blank=True)
    affected_assets = models.ManyToManyField(Asset, blank=True)
    affected_users = models.TextField(blank=True)  # JSON array
    
    # MITRE ATT&CK
    mitre_techniques = models.ManyToManyField(MitreTechnique, blank=True)
    
    # Assignment
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_alerts')
    
    # Timestamps
    first_seen = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Additional data
    tags = models.TextField(blank=True)
    metadata = models.TextField(blank=True)

    class Meta:
        ordering = ['-first_seen']

    def __str__(self):
        return f"{self.name} [{self.status}]"


# ============================================================================
# INCIDENT RESPONSE & CASE MANAGEMENT
# ============================================================================

class Investigation(models.Model):
    """Security investigations/cases"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('pending', 'Pending'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    case_id = models.CharField(max_length=64, unique=True)
    title = models.CharField(max_length=256)
    description = models.TextField()
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, default='new')
    priority = models.CharField(max_length=16, choices=PRIORITY_CHOICES, default='medium')
    severity = models.CharField(max_length=16, choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], default='medium')
    
    # Relationships
    alerts = models.ManyToManyField(Alert, blank=True)
    related_iocs = models.ManyToManyField(IOC, blank=True)
    affected_assets = models.ManyToManyField(Asset, blank=True)
    
    # MITRE ATT&CK
    mitre_techniques = models.ManyToManyField(MitreTechnique, blank=True)
    
    # Assignment
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_investigations')
    assigned_team = models.CharField(max_length=128, blank=True)
    
    # Timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(null=True, blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Outcome
    resolution = models.TextField(blank=True)
    root_cause = models.TextField(blank=True)
    lessons_learned = models.TextField(blank=True)
    
    # Metadata
    tags = models.TextField(blank=True)
    metadata = models.TextField(blank=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f"{self.case_id} - {self.title}"


class InvestigationNote(models.Model):
    """Notes/comments on investigations"""
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, related_name='notes')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    is_important = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return f"Note by {self.author} on {self.investigation.case_id}"


class InvestigationTimeline(models.Model):
    """Timeline events for investigations"""
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, related_name='timeline')
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=64)  # created, updated, note_added, etc.
    description = models.TextField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    metadata = models.TextField(blank=True)

    class Meta:
        ordering = ['timestamp']


class Evidence(models.Model):
    """Digital evidence attached to investigations"""
    EVIDENCE_TYPES = [
        ('file', 'File'),
        ('screenshot', 'Screenshot'),
        ('pcap', 'Network Capture'),
        ('memory_dump', 'Memory Dump'),
        ('log', 'Log File'),
        ('document', 'Document'),
        ('other', 'Other'),
    ]
    
    investigation = models.ForeignKey(Investigation, on_delete=models.CASCADE, related_name='evidence')
    evidence_type = models.CharField(max_length=32, choices=EVIDENCE_TYPES)
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    file_path = models.CharField(max_length=512, blank=True)
    file_hash = models.CharField(max_length=128, blank=True)
    file_size = models.BigIntegerField(null=True, blank=True)
    
    # Chain of custody
    collected_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    collected_at = models.DateTimeField(auto_now_add=True)
    chain_of_custody = models.TextField(blank=True)  # JSON log of access
    
    metadata = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name} ({self.evidence_type})"


class Playbook(models.Model):
    """Incident response playbooks/runbooks"""
    name = models.CharField(max_length=256)
    description = models.TextField()
    trigger_conditions = models.TextField(blank=True)
    steps = models.TextField()  # JSON array of steps
    is_automated = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    
    # MITRE ATT&CK mapping
    mitre_techniques = models.ManyToManyField(MitreTechnique, blank=True)
    
    # Usage stats
    times_executed = models.IntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class PlaybookExecution(models.Model):
    """Track playbook executions"""
    playbook = models.ForeignKey(Playbook, on_delete=models.CASCADE)
    investigation = models.ForeignKey(Investigation, null=True, blank=True, on_delete=models.CASCADE)
    started_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=32, choices=[('running','Running'),('completed','Completed'),('failed','Failed'),('cancelled','Cancelled')], default='running')
    execution_log = models.TextField(blank=True)  # JSON log of steps
    result = models.TextField(blank=True)

    def __str__(self):
        return f"{self.playbook.name} - {self.started_at}"


# ============================================================================
# USER & ENTITY BEHAVIOR ANALYTICS (UEBA)
# ============================================================================

class UserBehaviorBaseline(models.Model):
    """Baseline behavior patterns for users"""
    username = models.CharField(max_length=128, unique=True)
    typical_login_times = models.TextField(blank=True)  # JSON array of hour ranges
    typical_locations = models.TextField(blank=True)  # JSON array
    typical_systems = models.TextField(blank=True)  # JSON array
    average_data_access = models.FloatField(default=0.0)
    average_failed_logins = models.FloatField(default=0.0)
    peer_group = models.CharField(max_length=128, blank=True)
    risk_score = models.IntegerField(default=0)
    last_calculated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Baseline for {self.username}"


class AnomalyDetection(models.Model):
    """Detected anomalies in user/entity behavior"""
    ANOMALY_TYPES = [
        ('unusual_time', 'Unusual Login Time'),
        ('unusual_location', 'Unusual Location'),
        ('unusual_volume', 'Unusual Data Volume'),
        ('unusual_access', 'Unusual Access Pattern'),
        ('peer_deviation', 'Peer Group Deviation'),
        ('impossible_travel', 'Impossible Travel'),
    ]
    
    anomaly_type = models.CharField(max_length=64, choices=ANOMALY_TYPES)
    entity_type = models.CharField(max_length=32)  # user, asset, etc.
    entity_id = models.CharField(max_length=128)
    description = models.TextField()
    severity = models.CharField(max_length=16, choices=[('low','Low'),('medium','Medium'),('high','High')], default='medium')
    confidence_score = models.FloatField()  # 0.0 to 1.0
    baseline_value = models.FloatField(null=True, blank=True)
    observed_value = models.FloatField(null=True, blank=True)
    deviation_percentage = models.FloatField(null=True, blank=True)
    
    # Context
    related_events = models.ManyToManyField(Event, blank=True)
    created_alert = models.ForeignKey(Alert, null=True, blank=True, on_delete=models.SET_NULL)
    
    detected_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    is_false_positive = models.BooleanField(default=False)

    class Meta:
        ordering = ['-detected_at']

    def __str__(self):
        return f"{self.anomaly_type} - {self.entity_id}"


# ============================================================================
# COMPLIANCE & REPORTING
# ============================================================================

class ComplianceFramework(models.Model):
    """Compliance frameworks (PCI-DSS, HIPAA, etc.)"""
    name = models.CharField(max_length=128, unique=True)
    description = models.TextField()
    version = models.CharField(max_length=32, blank=True)
    requirements = models.TextField()  # JSON array of requirements
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class ComplianceCheck(models.Model):
    """Individual compliance checks"""
    framework = models.ForeignKey(ComplianceFramework, on_delete=models.CASCADE, related_name='checks')
    requirement_id = models.CharField(max_length=64)
    name = models.CharField(max_length=256)
    description = models.TextField()
    check_query = models.TextField()  # Query to validate compliance
    is_automated = models.BooleanField(default=False)
    schedule = models.CharField(max_length=64, blank=True)  # cron-like schedule
    last_run = models.DateTimeField(null=True, blank=True)
    last_result = models.CharField(max_length=16, choices=[('pass','Pass'),('fail','Fail'),('warning','Warning')], null=True, blank=True)

    def __str__(self):
        return f"{self.framework.name} - {self.requirement_id}"


class Report(models.Model):
    """Generated reports"""
    REPORT_TYPES = [
        ('security_summary', 'Security Summary'),
        ('incident_response', 'Incident Response'),
        ('compliance', 'Compliance'),
        ('threat_intelligence', 'Threat Intelligence'),
        ('user_activity', 'User Activity'),
        ('asset_inventory', 'Asset Inventory'),
        ('custom', 'Custom'),
    ]
    
    FORMAT_CHOICES = [
        ('pdf', 'PDF'),
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('html', 'HTML'),
    ]
    
    name = models.CharField(max_length=256)
    report_type = models.CharField(max_length=64, choices=REPORT_TYPES)
    description = models.TextField(blank=True)
    format = models.CharField(max_length=16, choices=FORMAT_CHOICES, default='pdf')
    
    # Schedule
    is_scheduled = models.BooleanField(default=False)
    schedule = models.CharField(max_length=64, blank=True)
    
    # Content
    query_params = models.TextField(blank=True)  # JSON
    file_path = models.CharField(max_length=512, blank=True)
    
    # Metadata
    generated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    generated_at = models.DateTimeField(auto_now_add=True)
    time_range_start = models.DateTimeField(null=True, blank=True)
    time_range_end = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-generated_at']

    def __str__(self):
        return f"{self.name} - {self.generated_at.strftime('%Y-%m-%d')}"


# ============================================================================
# NOTIFICATIONS & ALERTING
# ============================================================================

class NotificationChannel(models.Model):
    """Notification delivery channels"""
    CHANNEL_TYPES = [
        ('email', 'Email'),
        ('slack', 'Slack'),
        ('webhook', 'Webhook'),
        ('sms', 'SMS'),
        ('pagerduty', 'PagerDuty'),
    ]
    
    name = models.CharField(max_length=128)
    channel_type = models.CharField(max_length=32, choices=CHANNEL_TYPES)
    config = models.TextField()  # JSON config (email addresses, webhook URLs, etc.)
    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.channel_type})"


class NotificationRule(models.Model):
    """Rules for when to send notifications"""
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    trigger_conditions = models.TextField()  # JSON conditions
    channels = models.ManyToManyField(NotificationChannel)
    severity_threshold = models.CharField(max_length=16, choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')], default='high')
    is_enabled = models.BooleanField(default=True)
    
    # Throttling
    max_notifications_per_hour = models.IntegerField(default=10)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


# ============================================================================
# AUDIT & SYSTEM LOGS
# ============================================================================

class AuditLog(models.Model):
    """Audit trail of all user actions in the SIEM"""
    ACTION_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('view', 'View'),
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('export', 'Export'),
        ('search', 'Search'),
    ]
    
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action_type = models.CharField(max_length=32, choices=ACTION_TYPES)
    resource_type = models.CharField(max_length=64)  # alert, investigation, etc.
    resource_id = models.CharField(max_length=128, blank=True)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=256, blank=True)
    metadata = models.TextField(blank=True)  # JSON

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.user} - {self.action_type} - {self.resource_type}"


# ============================================================================
# SAVED QUERIES & SEARCHES
# ============================================================================

class SavedSearch(models.Model):
    """Saved search queries for hunting"""
    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    query = models.TextField()
    query_type = models.CharField(max_length=32, default='event')  # event, alert, etc.
    
    # Sharing
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_searches')
    is_public = models.BooleanField(default=False)
    
    # Usage stats
    times_executed = models.IntegerField(default=0)
    last_executed = models.DateTimeField(null=True, blank=True)
    
    # Schedule
    is_scheduled = models.BooleanField(default=False)
    schedule = models.CharField(max_length=64, blank=True)
    
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    tags = models.TextField(blank=True)

    class Meta:
        ordering = ['-updated']

    def __str__(self):
        return self.name


# ============================================================================
# USER & SYSTEM CONFIGURATION
# ============================================================================

class UserProfile(models.Model):
    """Extended user profile information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=32, choices=[
        ('analyst', 'Security Analyst'),
        ('investigator', 'Investigator'),
        ('admin', 'Administrator'),
        ('viewer', 'Viewer'),
    ], default='analyst')
    department = models.CharField(max_length=128, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    timezone = models.CharField(max_length=64, default='UTC')
    
    # Preferences
    theme = models.CharField(max_length=32, choices=[('light', 'Light'), ('dark', 'Dark')], default='dark')
    notifications_enabled = models.BooleanField(default=True)
    email_alerts = models.BooleanField(default=True)
    
    # Metadata
    last_login = models.DateTimeField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class SystemSettings(models.Model):
    """System-wide configuration settings"""
    setting_key = models.CharField(max_length=128, unique=True)
    setting_value = models.TextField()
    setting_type = models.CharField(max_length=32, choices=[
        ('string', 'String'),
        ('boolean', 'Boolean'),
        ('integer', 'Integer'),
        ('json', 'JSON'),
    ], default='string')
    description = models.TextField(blank=True)
    
    # Access control
    is_sensitive = models.BooleanField(default=False)  # Hide in UI if True
    updated_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "System Settings"

    def __str__(self):
        return self.setting_key


class Anomaly(models.Model):
    """Behavioral anomalies detected for users/assets"""
    ANOMALY_TYPES = [
        ('login_anomaly', 'Login Anomaly'),
        ('data_exfiltration', 'Data Exfiltration'),
        ('lateral_movement', 'Lateral Movement'),
        ('privilege_escalation', 'Privilege Escalation'),
        ('unusual_activity', 'Unusual Activity'),
        ('high_risk_command', 'High Risk Command'),
        ('resource_abuse', 'Resource Abuse'),
    ]
    
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='anomalies')
    anomaly_type = models.CharField(max_length=64, choices=ANOMALY_TYPES)
    description = models.TextField()
    severity = models.CharField(max_length=16, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ], default='medium')
    
    # Detection details
    detected_at = models.DateTimeField(auto_now_add=True)
    detection_method = models.CharField(max_length=128)  # UEBA, ML model, etc.
    confidence_score = models.FloatField(default=0.5)
    
    # Response
    is_acknowledged = models.BooleanField(default=False)
    acknowledged_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    # Metadata
    related_events = models.ManyToManyField(Event, blank=True)
    related_alerts = models.ManyToManyField(Alert, blank=True)

    class Meta:
        ordering = ['-detected_at']
        verbose_name_plural = "Anomalies"

    def __str__(self):
        return f"{self.anomaly_type} on {self.asset.hostname}"