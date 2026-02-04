from django.db import models

class ThreatLog(models.Model):
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]

    ACTION_CHOICES = [
        ('BLOCKED', 'Blocked'),
        ('FLAGGED', 'Flagged'),
        ('ALLOWED', 'Allowed'),
    ]

    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    url = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    headers = models.JSONField(default=dict)
    body = models.TextField(blank=True, null=True)
    threat_type = models.CharField(max_length=100) # e.g., SQL Injection, XSS
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES)
    ai_confidence = models.FloatField(help_text="Confidence score from AI (0.0 - 1.0)")
    action_taken = models.CharField(max_length=10, choices=ACTION_CHOICES)
    details = models.TextField(help_text="AI analysis details")

    def __str__(self):
        return f"{self.threat_type} from {self.ip_address} at {self.timestamp}"

class BlockedIP(models.Model):
    ip_address = models.GenericIPAddressField(unique=True)
    reason = models.CharField(max_length=255)
    blocked_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    is_permanent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.ip_address} - {self.reason}"
