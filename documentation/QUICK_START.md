# REBADEN SIEM - Quick Start Reference

## 🚀 Start Development Server (30 seconds)

```bash
cd /home/josh/projects/rebaden/backend
source djangoback/bin/activate
python manage.py runserver 0.0.0.0:8000
```

**Access**:
- Admin: http://localhost:8000/admin/
- API: http://localhost:8000/api/v1/

---

## 📋 Available Features

### 1. Asset Management
Track network devices, servers, endpoints

```bash
# Create asset
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "prod-web-01",
    "ip": "10.0.1.5",
    "asset_type": "server",
    "criticality": "critical",
    "os": "Ubuntu 20.04"
  }'

# List assets
curl http://localhost:8000/api/v1/assets/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 2. Event Ingestion
Collect and normalize security logs

```bash
# Configure log source
curl -X POST http://localhost:8000/api/v1/log-sources/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Syslog Server",
    "source_type": "syslog",
    "hostname": "syslog.example.com",
    "port": 514,
    "protocol": "udp"
  }'

# Ingest events
curl -X POST http://localhost:8000/api/v1/events/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2026-07-13T10:30:00Z",
    "source_ip": "192.168.1.100",
    "destination_ip": "8.8.8.8",
    "event_type": "network",
    "severity": "medium",
    "action": "connection_attempt",
    "raw_log": "..."
  }'
```

### 3. Detection Rules
Define threat detection patterns

```bash
# Create rule
curl -X POST http://localhost:8000/api/v1/detection-rules/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rule_name": "Suspicious Login Activity",
    "description": "Alert on multiple failed logins",
    "rule_type": "threshold",
    "query": "event_type=authentication AND action=login_failed",
    "severity": "high",
    "enabled": true
  }'

# Test rule
curl -X POST http://localhost:8000/api/v1/detection-rules/1/test/ \
  -H "Authorization: Token YOUR_TOKEN"

# List active rules
curl http://localhost:8000/api/v1/detection-rules/enabled/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 4. Alerts
Automatic alert generation and management

```bash
# Get open alerts
curl http://localhost:8000/api/v1/alerts/open_alerts/ \
  -H "Authorization: Token YOUR_TOKEN"

# Get critical alerts
curl "http://localhost:8000/api/v1/alerts/?severity=critical" \
  -H "Authorization: Token YOUR_TOKEN"

# Acknowledge alert
curl -X POST http://localhost:8000/api/v1/alerts/1/take_action/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "acknowledge",
    "notes": "Investigating"
  }'

# Resolve alert
curl -X POST http://localhost:8000/api/v1/alerts/1/take_action/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "resolve",
    "notes": "False positive - test traffic"
  }'
```

### 5. Investigations
Correlate events into incident cases

```bash
# Create investigation
curl -X POST http://localhost:8000/api/v1/investigations/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Possible Brute Force Attack",
    "description": "Multiple failed logins from 192.168.1.100",
    "severity": "high",
    "lead_analyst": "security_team"
  }'

# Add note
curl -X POST http://localhost:8000/api/v1/investigations/1/add_note/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "note_text": "Confirmed 50+ failed attempts in 5 minutes",
    "note_type": "analyst_finding"
  }'

# Add evidence
curl -X POST http://localhost:8000/api/v1/investigations/1/add_evidence/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Failed Login Logs",
    "evidence_type": "log_file",
    "description": "Raw logs from failed attempt period"
  }'

# Close investigation
curl -X POST http://localhost:8000/api/v1/investigations/1/close/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 6. MITRE ATT&CK
Map attacks to MITRE techniques

```bash
# List tactics
curl http://localhost:8000/api/v1/mitre-tactics/ \
  -H "Authorization: Token YOUR_TOKEN"

# List techniques
curl http://localhost:8000/api/v1/mitre-techniques/ \
  -H "Authorization: Token YOUR_TOKEN"

# Create mapping
curl -X POST http://localhost:8000/api/v1/mitre-mappings/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "technique": 1,
    "alert": 5,
    "match_score": 0.95,
    "detection_method": "Signature: Brute Force Pattern"
  }'
```

### 7. Threat Intelligence (IOCs)
Manage indicators of compromise

```bash
# Add IOC
curl -X POST http://localhost:8000/api/v1/iocs/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "indicator_type": "ip",
    "indicator_value": "192.168.100.50",
    "threat_level": "critical",
    "source": "threat_feed",
    "context": "Known C2 server"
  }'

# Get critical IOCs
curl http://localhost:8000/api/v1/iocs/critical/ \
  -H "Authorization: Token YOUR_TOKEN"

# Mark resolved
curl -X POST http://localhost:8000/api/v1/iocs/1/mark_resolved/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 8. Compliance
Track compliance frameworks and checks

```bash
# List compliance frameworks
curl http://localhost:8000/api/v1/compliance-frameworks/ \
  -H "Authorization: Token YOUR_TOKEN"

# List compliance checks
curl http://localhost:8000/api/v1/compliance-checks/ \
  -H "Authorization: Token YOUR_TOKEN"
```

### 9. Reporting
Generate incident and compliance reports

```bash
# Create report
curl -X POST http://localhost:8000/api/v1/reports/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Incident Report - 2026-07-13",
    "report_type": "incident",
    "format": "pdf"
  }'

# Generate report
curl -X POST http://localhost:8000/api/v1/reports/1/generate/ \
  -H "Authorization: Token YOUR_TOKEN"

# Download report
curl http://localhost:8000/api/v1/reports/1/download/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -o report.pdf
```

### 10. Playbooks
Automated incident response

```bash
# Create playbook
curl -X POST http://localhost:8000/api/v1/playbooks/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Disable Compromised Account",
    "description": "Lock account and notify admins",
    "trigger_type": "alert",
    "playbook_type": "containment",
    "actions": "lock_account, force_password_reset, notify_admin",
    "enabled": true
  }'

# Execute playbook
curl -X POST http://localhost:8000/api/v1/playbooks/1/execute/ \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## 🔧 Common Admin Tasks

### Create Superuser (First Time)
```bash
cd /home/josh/projects/rebaden/backend
source djangoback/bin/activate
python manage.py createsuperuser
# Enter username, email, password
```

### Load Sample Data
```bash
python manage.py populate_mitre  # Load MITRE ATT&CK framework
python manage.py populate_sample_data  # Load test data
```

### Check Database Status
```bash
python manage.py shell
>>> from apps.core.models import *
>>> Alert.objects.count()
>>> Event.objects.count()
>>> Investigation.objects.count()
```

### Migrations
```bash
python manage.py makemigrations  # Create migrations
python manage.py migrate  # Apply migrations
python manage.py showmigrations  # Show status
```

### Clear Old Data (if needed)
```bash
python manage.py shell
>>> from apps.core.models import Event
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> cutoff = timezone.now() - timedelta(days=30)
>>> Event.objects.filter(timestamp__lt=cutoff).delete()
```

---

## 📊 Data Models Summary

| Model | Purpose | Count |
|-------|---------|-------|
| Asset | Track devices/endpoints | ~10-100 |
| Event | Store security events | ~1000+ |
| Alert | Generated alerts | ~100-500 |
| Investigation | Incident cases | ~10-50 |
| DetectionRule | Threat patterns | ~20-100 |
| IOC | Threat indicators | ~100-1000 |
| MITRE Technique | Attack techniques | 200+ |
| Report | Generated reports | ~10-100 |
| User | System users | 1-20 |

---

## 🔑 API Authentication

### Get API Token (Django Shell)
```bash
python manage.py shell
>>> from rest_framework.authtoken.models import Token
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> token, created = Token.objects.get_or_create(user=user)
>>> print(token.key)
```

### Use Token in Requests
```bash
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
  http://localhost:8000/api/v1/alerts/
```

---

## 📖 Documentation Files

- **[doc1.md](doc1.md)** - Complete workability documentation (1,500+ lines)
  - Architecture diagrams
  - Complete API reference
  - Performance optimization
  - Deployment guide

- **[VERIFICATION_SUMMARY.md](VERIFICATION_SUMMARY.md)** - Verification checklist
  - All implemented features
  - Component status
  - Next steps

- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - This file
  - Quick API examples
  - Common tasks
  - Quick lookup

---

## 🚨 Troubleshooting

### Server Won't Start
```bash
# Check for port conflicts
lsof -i :8000

# Kill existing process
pkill -f runserver

# Restart
python manage.py runserver 0.0.0.0:8000
```

### Database Errors
```bash
# Fresh migrations
python manage.py migrate --fake-initial
python manage.py migrate

# Check migrations
python manage.py showmigrations
```

### Import Errors
```bash
# Reinstall requirements
pip install -r requirements.txt

# Check installation
python -c "import django; print(django.VERSION)"
```

### API Token Issues
```bash
# Generate new token
python manage.py shell
>>> from rest_framework.authtoken.models import Token
>>> from django.contrib.auth.models import User
>>> user = User.objects.get(username='admin')
>>> Token.objects.filter(user=user).delete()  # Delete old
>>> token = Token.objects.create(user=user)  # Create new
>>> print(token.key)
```

---

## 📞 Quick Help

| Question | Answer |
|----------|--------|
| How do I start the server? | `python manage.py runserver` |
| How do I create users? | Admin panel or `python manage.py createsuperuser` |
| How do I get API token? | Django shell: `Token.objects.get_or_create(user=user)` |
| How do I ingest events? | POST to `/api/v1/events/` with log data |
| How do I create alerts? | POST to `/api/v1/alerts/` or via detection rules |
| How do I investigate? | Create investigation → add notes → add evidence → close |
| How do I report? | Create report → generate → download |
| How do I add IOCs? | POST to `/api/v1/iocs/` with indicator data |

---

## 🎯 Typical Workflow

1. **Configure Assets** → Add servers/devices to monitor
2. **Set Log Sources** → Configure where logs come from
3. **Ingest Events** → Send logs to SIEM
4. **Create Rules** → Define threat detection patterns
5. **Generate Alerts** → Rules automatically create alerts
6. **Investigate** → Correlate events into incidents
7. **Respond** → Execute playbooks, gather evidence
8. **Report** → Generate incident report
9. **Comply** → Track compliance requirements

---

**REBADEN SIEM - Ready to Use**

Start server now and begin securing your infrastructure!

```bash
python manage.py runserver 0.0.0.0:8000
```
