# 🔌 REBADEN SIEM - Complete API Guide & Fixes

## ✅ API Endpoints Status

All API endpoints are properly implemented and working. Here's the complete reference:

---

## 📋 API Endpoints by Category

### 1. **Assets API**
```
GET    /api/v1/assets/                    # List all assets
POST   /api/v1/assets/                    # Create new asset
GET    /api/v1/assets/{id}/               # Get asset details
PUT    /api/v1/assets/{id}/               # Update asset
DELETE /api/v1/assets/{id}/               # Delete asset
POST   /api/v1/assets/bulk_create/        # Bulk create assets
GET    /api/v1/assets/by_criticality/     # Filter by criticality
GET    /api/v1/assets/with_events/        # Assets with recent events
```

**Example Request:**
```bash
# Get all critical assets
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/assets/by_criticality/?level=critical"

# Response:
[
  {
    "id": 1,
    "hostname": "DC1.local",
    "ip": "192.168.1.10",
    "asset_type": "server",
    "criticality": "critical",
    "risk_score": 85,
    "is_active": true
  }
]
```

---

### 2. **Events API**
```
GET    /api/v1/events/                    # List all events
POST   /api/v1/events/                    # Create new event
GET    /api/v1/events/{id}/               # Get event details
PUT    /api/v1/events/{id}/               # Update event
DELETE /api/v1/events/{id}/               # Delete event
GET    /api/v1/events/by_severity/        # Filter by severity
GET    /api/v1/events/by_category/        # Filter by category
GET    /api/v1/events/time_series/        # Get time-series data
```

**Example Request:**
```bash
# Get critical events from last 24 hours
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/events/?severity=critical&hours=24"

# Response:
[
  {
    "id": 101,
    "event_type": "suspicious_login",
    "severity": "critical",
    "source_ip": "203.0.113.45",
    "asset": 5,
    "time": "2026-04-07T09:15:30Z"
  }
]
```

---

### 3. **Alerts API** ⭐ (Most Important)
```
GET    /api/v1/alerts/                    # List all alerts
POST   /api/v1/alerts/                    # Create new alert
GET    /api/v1/alerts/{id}/               # Get alert details
PUT    /api/v1/alerts/{id}/               # Update alert
DELETE /api/v1/alerts/{id}/               # Delete alert
GET    /api/v1/alerts/by_status/          # Filter by status
GET    /api/v1/alerts/open_alerts/        # Get open alerts only
POST   /api/v1/alerts/{id}/take_action/   # Perform action on alert
```

**Example Requests:**

**Get all open alerts:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/alerts/open_alerts/"

# Response:
[
  {
    "id": 1,
    "name": "Multiple Failed Logins",
    "severity": "high",
    "status": "open",
    "assigned_to": 5,
    "first_seen": "2026-04-07T08:30:00Z",
    "last_seen": "2026-04-07T09:45:00Z"
  }
]
```

**Create new alert:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Ransomware Detected",
    "severity": "critical",
    "status": "new",
    "description": "Encryption activity on file server detected",
    "source_ip": "192.168.1.100",
    "affected_users": ["admin@company.com"]
  }' \
  "http://localhost:8000/api/v1/alerts/"
```

**Take action on alert:**
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "assign",
    "assigned_to": 7,
    "notes": "Escalating to incident response team"
  }' \
  "http://localhost:8000/api/v1/alerts/1/take_action/"
```

---

### 4. **IOCs (Indicators of Compromise) API**
```
GET    /api/v1/iocs/                      # List all IOCs
POST   /api/v1/iocs/                      # Create new IOC
GET    /api/v1/iocs/{id}/                 # Get IOC details
PUT    /api/v1/iocs/{id}/                 # Update IOC
DELETE /api/v1/iocs/{id}/                 # Delete IOC
GET    /api/v1/iocs/by_type/              # Filter by type (IP, domain, hash)
GET    /api/v1/iocs/critical/             # Get critical IOCs only
```

**Example Request:**
```bash
# Get all malicious IPs
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/iocs/by_type/?ioc_type=ip"

# Response:
[
  {
    "id": 1,
    "ioc_type": "ip",
    "value": "203.0.113.45",
    "severity": "critical",
    "source": "OSINT",
    "is_active": true
  }
]
```

---

### 5. **Investigations (Cases) API**
```
GET    /api/v1/investigations/             # List all investigations
POST   /api/v1/investigations/             # Create new investigation
GET    /api/v1/investigations/{id}/        # Get investigation details
PUT    /api/v1/investigations/{id}/        # Update investigation
PATCH  /api/v1/investigations/{id}/        # Partial update
DELETE /api/v1/investigations/{id}/        # Close investigation
GET    /api/v1/investigations/open/        # Get open investigations
POST   /api/v1/investigations/{id}/add_note/ # Add investigation note
```

**Example Request:**
```bash
# Create new investigation
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "APT28 Campaign - Wave 2",
    "severity": "critical",
    "description": "Multiple phishing emails detected",
    "status": "open",
    "owner": 3
  }' \
  "http://localhost:8000/api/v1/investigations/"
```

---

### 6. **Detection Rules API**
```
GET    /api/v1/detection-rules/            # List all rules
POST   /api/v1/detection-rules/            # Create new rule
GET    /api/v1/detection-rules/{id}/       # Get rule details
PUT    /api/v1/detection-rules/{id}/       # Update rule
DELETE /api/v1/detection-rules/{id}/       # Delete rule
GET    /api/v1/detection-rules/enabled/    # Get enabled rules only
GET    /api/v1/detection-rules/test/       # Test a rule
```

---

### 7. **MITRE ATT&CK API**
```
GET    /api/v1/mitre-tactics/              # List MITRE tactics
GET    /api/v1/mitre-techniques/           # List MITRE techniques
GET    /api/v1/mitre-techniques/{id}/      # Get technique details
GET    /api/v1/mitre-mappings/             # Get technique mappings
```

---

### 8. **Reports API**
```
GET    /api/v1/reports/                    # List all reports
POST   /api/v1/reports/                    # Generate new report
GET    /api/v1/reports/{id}/               # Get report details
DELETE /api/v1/reports/{id}/               # Delete report
POST   /api/v1/reports/{id}/download/      # Download report
```

---

### 9. **Compliance API**
```
GET    /api/v1/compliance-frameworks/      # List compliance frameworks
GET    /api/v1/compliance-checks/          # List compliance checks
GET    /api/v1/compliance-checks/{id}/     # Get check details
POST   /api/v1/compliance-checks/{id}/run/ # Run compliance check
```

---

## 🔐 Authentication

All API endpoints require authentication. Get your token:

**1. Obtain Token:**
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{
    "username": "your_username",
    "password": "your_password"
  }' \
  "http://localhost:8000/api-token-auth/"

# Response:
{ "token": "abc123def456..." }
```

**2. Use Token in Requests:**
```bash
curl -H "Authorization: Token abc123def456..." \
  "http://localhost:8000/api/v1/alerts/"
```

---

## 📊 Common Query Patterns

### Get Critical Alerts from Last 24 Hours
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/alerts/?severity=critical&status=open"
```

### Get Events for Specific Asset
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/events/?asset=5&hours=24"
```

### Get Active Investigations
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/investigations/open/"
```

### Bulk Create Assets
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "assets": [
      {"hostname": "web1.local", "ip": "192.168.1.20", "asset_type": "server"},
      {"hostname": "web2.local", "ip": "192.168.1.21", "asset_type": "server"}
    ]
  }' \
  "http://localhost:8000/api/v1/assets/bulk_create/"
```

---

## 🐍 Python Client Examples

### Using Requests Library
```python
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"
TOKEN = "your_auth_token"
HEADERS = {"Authorization": f"Token {TOKEN}"}

# Get all critical alerts
response = requests.get(
    f"{BASE_URL}/alerts/",
    params={"severity": "critical"},
    headers=HEADERS
)

alerts = response.json()
for alert in alerts:
    print(f"[{alert['severity']}] {alert['name']}")

# Create new alert
alert_data = {
    "name": "Suspicious Activity Detected",
    "severity": "high",
    "status": "new",
    "description": "Multiple port scans detected"
}

response = requests.post(
    f"{BASE_URL}/alerts/",
    json=alert_data,
    headers=HEADERS
)

new_alert = response.json()
print(f"Created alert: {new_alert['id']}")
```

### Using Django ORM (Server-side)
```python
from apps.core.models import Alert, Event, Asset
from django.utils import timezone
from datetime import timedelta

# Get critical alerts from last hour
recent_alerts = Alert.objects.filter(
    severity='critical',
    first_seen__gte=timezone.now() - timedelta(hours=1)
)

# Get events for specific asset
asset = Asset.objects.get(hostname='DC1.local')
events = asset.event_set.all().order_by('-time')[:100]

# Create alert programmatically
alert = Alert.objects.create(
    name="Ransomware Detected",
    severity="critical",
    status="new",
    source_ip="203.0.113.45"
)
print(f"Created alert: {alert.id}")
```

---

## 🧪 Testing Your API

### Using cURL
```bash
# Test API connectivity
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/alerts/ | python -m json.tool

# Test with specific filters
curl "http://localhost:8000/api/v1/alerts/?severity=critical&status=open" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Using Postman
1. Download [Postman](https://www.postman.com/downloads/)
2. Import the collection (see below)
3. Set `Authorization` header to `Bearer YOUR_TOKEN`
4. Send requests

### Using Python
```bash
python manage.py shell

# Inside Django shell:
from apps.core.models import Alert, Event
print(Alert.objects.count())  # Total alerts
print(Event.objects.count())  # Total events
```

---

## 🚨 API Error Handling

Common HTTP Status Codes:

| Code | Meaning | Solution |
|------|---------|----------|
| 200 | Success | ✅ Request successful |
| 201 | Created | ✅ Resource created |
| 400 | Bad Request | ❌ Check JSON formatting |
| 401 | Unauthorized | ❌ Invalid or missing token |
| 403 | Forbidden | ❌ Permission denied |
| 404 | Not Found | ❌ Resource doesn't exist |
| 500 | Server Error | ❌ Check server logs |

**Example Error Response:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

---

## 📈 Performance Tips

1. **Use pagination** (default: 20 items/page)
   ```bash
   curl "http://localhost:8000/api/v1/alerts/?page=2"
   ```

2. **Filter early** to reduce data transfer
   ```bash
   # Good: Filter on server
   curl "http://localhost:8000/api/v1/alerts/?severity=critical"
   
   # Bad: Get all, filter in client
   curl "http://localhost:8000/api/v1/alerts/" | filter locally
   ```

3. **Use bulk operations** for multiple creates
   ```bash
   POST /api/v1/assets/bulk_create/  # Better than creating one-by-one
   ```

4. **Cache results** where possible
   ```python
   from django.views.decorators.cache import cache_page
   
   @cache_page(60)  # Cache for 60 seconds
   def get_alerts(request):
       ...
   ```

---

## 🔗 Related Files

- API Views: [apps/core/api_views.py](backend/apps/core/api_views.py)
- Serializers: [apps/core/serializers.py](backend/apps/core/serializers.py)
- URLs: [apps/core/api_urls.py](backend/apps/core/api_urls.py)
- Models: [apps/core/models.py](backend/apps/core/models.py)

---

## 📚 Next Steps

1. ✅ Set up authentication token
2. ✅ Test endpoints with cURL
3. ✅ Build client application
4. ✅ Integrate with third-party tools
5. ✅ Set up monitoring/alerting

**All APIs are production-ready! 🎉**
