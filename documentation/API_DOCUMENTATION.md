# SIEM API Documentation

## Overview
This document describes the REST API endpoints available in the SIEM tool for programmatic access and integration.

---

## Authentication
All API endpoints require authentication. Use Django session authentication or implement token-based authentication.

### Session Authentication
```python
import requests

# Login first
session = requests.Session()
session.post('http://127.0.0.1:8000/login/', data={
    'username': 'admin',
    'password': 'admin123'
})

# Then make API calls
response = session.get('http://127.0.0.1:8000/api/events/')
```

---

## API Endpoints

### 1. Events API
**Endpoint**: `/api/events/`  
**Method**: `GET`  
**Description**: Retrieve security events data

#### Parameters
| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| range | string | Time range: `1h`, `24h`, `7d` | `24h` |

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/events/?range=24h" \
  -H "Cookie: sessionid=<your-session-id>"
```

#### Example Response
```json
[
  {
    "time": "2024-11-22T15:30:00Z",
    "severity": "high",
    "category": "authentication"
  },
  {
    "time": "2024-11-22T15:25:00Z",
    "severity": "critical",
    "category": "malware"
  }
]
```

#### Response Fields
- `time`: Event timestamp (ISO 8601)
- `severity`: Event severity (info, low, medium, high, critical)
- `category`: Event category (authentication, network, malware, etc.)

---

### 2. Alert Statistics API
**Endpoint**: `/api/alerts/stats/`  
**Method**: `GET`  
**Description**: Get alert statistics and aggregations

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/alerts/stats/" \
  -H "Cookie: sessionid=<your-session-id>"
```

#### Example Response
```json
{
  "by_severity": [
    {"severity": "critical", "count": 5},
    {"severity": "high", "count": 12},
    {"severity": "medium", "count": 23},
    {"severity": "low", "count": 8}
  ],
  "by_status": [
    {"status": "new", "count": 10},
    {"status": "open", "count": 15},
    {"status": "investigating", "count": 8},
    {"status": "resolved", "count": 15}
  ],
  "total": 48
}
```

#### Response Fields
- `by_severity`: Array of alert counts grouped by severity
- `by_status`: Array of alert counts grouped by status
- `total`: Total number of alerts

---

### 3. Threat Map API
**Endpoint**: `/api/threat-map/`  
**Method**: `GET`  
**Description**: Get geolocation data for threat visualization

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/threat-map/" \
  -H "Cookie: sessionid=<your-session-id>"
```

#### Example Response
```json
[
  {
    "source_geo_lat": 37.7749,
    "source_geo_lon": -122.4194,
    "severity": "high",
    "source_ip": "203.0.113.45"
  },
  {
    "source_geo_lat": 51.5074,
    "source_geo_lon": -0.1278,
    "severity": "critical",
    "source_ip": "198.51.100.23"
  }
]
```

#### Response Fields
- `source_geo_lat`: Latitude of source IP
- `source_geo_lon`: Longitude of source IP
- `severity`: Event severity
- `source_ip`: Source IP address

---

## Django REST Framework Integration (Future Enhancement)

### Recommended Setup
For a full-featured REST API, integrate Django REST Framework:

```bash
pip install djangorestframework
```

### Example Serializers

```python
# serializers.py
from rest_framework import serializers
from .models import Event, Alert, IOC, Investigation

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class AlertSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alert
        fields = '__all__'

class IOCSerializer(serializers.ModelSerializer):
    class Meta:
        model = IOC
        fields = '__all__'

class InvestigationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investigation
        fields = '__all__'
```

### Example ViewSets

```python
# api_views.py
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Event, Alert, IOC, Investigation
from .serializers import EventSerializer, AlertSerializer, IOCSerializer, InvestigationSerializer

class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    filterset_fields = ['severity', 'category', 'source_ip']
    search_fields = ['message', 'source']
    ordering_fields = ['time', 'severity']

class AlertViewSet(viewsets.ModelViewSet):
    queryset = Alert.objects.all()
    serializer_class = AlertSerializer
    filterset_fields = ['severity', 'status']
    
    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'investigating'
        alert.assigned_to = request.user
        alert.save()
        return Response({'status': 'acknowledged'})
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        alert = self.get_object()
        alert.status = 'resolved'
        alert.save()
        return Response({'status': 'resolved'})

class IOCViewSet(viewsets.ModelViewSet):
    queryset = IOC.objects.all()
    serializer_class = IOCSerializer
    filterset_fields = ['ioc_type', 'severity', 'is_active']
    search_fields = ['value', 'description']

class InvestigationViewSet(viewsets.ModelViewSet):
    queryset = Investigation.objects.all()
    serializer_class = InvestigationSerializer
    filterset_fields = ['status', 'priority', 'severity']
    search_fields = ['case_id', 'title', 'description']
```

### Example URLs

```python
# urls.py
from rest_framework.routers import DefaultRouter
from .api_views import EventViewSet, AlertViewSet, IOCViewSet, InvestigationViewSet

router = DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'alerts', AlertViewSet)
router.register(r'iocs', IOCViewSet)
router.register(r'investigations', InvestigationViewSet)

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
```

---

## API Usage Examples

### Python

#### Get Events
```python
import requests

session = requests.Session()
session.post('http://127.0.0.1:8000/login/', data={
    'username': 'admin',
    'password': 'admin123'
})

response = session.get('http://127.0.0.1:8000/api/events/?range=24h')
events = response.json()

for event in events:
    print(f"{event['time']} - {event['severity']} - {event['category']}")
```

#### Get Alert Statistics
```python
response = session.get('http://127.0.0.1:8000/api/alerts/stats/')
stats = response.json()

print(f"Total Alerts: {stats['total']}")
for item in stats['by_severity']:
    print(f"{item['severity']}: {item['count']}")
```

#### Get Threat Map Data
```python
response = session.get('http://127.0.0.1:8000/api/threat-map/')
threats = response.json()

for threat in threats:
    print(f"IP: {threat['source_ip']} at ({threat['source_geo_lat']}, {threat['source_geo_lon']})")
```

---

### JavaScript (Fetch API)

#### Get Events
```javascript
fetch('/api/events/?range=24h', {
    credentials: 'include'
})
.then(response => response.json())
.then(events => {
    events.forEach(event => {
        console.log(`${event.time} - ${event.severity} - ${event.category}`);
    });
});
```

#### Get Alert Statistics
```javascript
fetch('/api/alerts/stats/', {
    credentials: 'include'
})
.then(response => response.json())
.then(stats => {
    console.log(`Total Alerts: ${stats.total}`);
    stats.by_severity.forEach(item => {
        console.log(`${item.severity}: ${item.count}`);
    });
});
```

#### Get Threat Map Data
```javascript
fetch('/api/threat-map/', {
    credentials: 'include'
})
.then(response => response.json())
.then(threats => {
    threats.forEach(threat => {
        console.log(`IP: ${threat.source_ip} at (${threat.source_geo_lat}, ${threat.source_geo_lon})`);
    });
});
```

---

### cURL

#### Get Events
```bash
# Login first to get session cookie
curl -c cookies.txt -X POST http://127.0.0.1:8000/login/ \
  -d "username=admin&password=admin123"

# Use session cookie for API call
curl -b cookies.txt http://127.0.0.1:8000/api/events/?range=24h
```

#### Get Alert Statistics
```bash
curl -b cookies.txt http://127.0.0.1:8000/api/alerts/stats/
```

#### Get Threat Map Data
```bash
curl -b cookies.txt http://127.0.0.1:8000/api/threat-map/
```

---

## Integration Examples

### 1. SIEM to Slack Integration

```python
import requests
import json

def send_alert_to_slack(alert):
    webhook_url = "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    
    message = {
        "text": f"🚨 New Alert: {alert['name']}",
        "attachments": [{
            "color": "danger" if alert['severity'] == 'critical' else "warning",
            "fields": [
                {"title": "Severity", "value": alert['severity'], "short": True},
                {"title": "Status", "value": alert['status'], "short": True},
                {"title": "Description", "value": alert['description']}
            ]
        }]
    }
    
    requests.post(webhook_url, json=message)

# Get critical alerts
session = requests.Session()
session.post('http://127.0.0.1:8000/login/', data={
    'username': 'admin',
    'password': 'admin123'
})

response = session.get('http://127.0.0.1:8000/api/alerts/stats/')
stats = response.json()

# Send to Slack if critical alerts exist
for item in stats['by_severity']:
    if item['severity'] == 'critical' and item['count'] > 0:
        send_alert_to_slack({
            'name': 'Critical Alerts Detected',
            'severity': 'critical',
            'status': 'new',
            'description': f'{item["count"]} critical alerts detected'
        })
```

### 2. SIEM to Ticketing System Integration

```python
import requests

def create_ticket(investigation):
    """Create ticket in external system (e.g., Jira, ServiceNow)"""
    ticket_api = "https://your-ticketing-system.com/api/tickets"
    
    ticket_data = {
        "title": investigation['title'],
        "description": investigation['description'],
        "priority": investigation['priority'],
        "severity": investigation['severity'],
        "assignee": investigation['owner']
    }
    
    response = requests.post(ticket_api, json=ticket_data, headers={
        'Authorization': 'Bearer YOUR_API_TOKEN'
    })
    
    return response.json()
```

### 3. External Log Shipper to SIEM

```python
import requests

def send_event_to_siem(event_data):
    """Send event from external source to SIEM"""
    siem_api = "http://127.0.0.1:8000/api/events/"
    
    session = requests.Session()
    session.post('http://127.0.0.1:8000/login/', data={
        'username': 'api_user',
        'password': 'api_password'
    })
    
    response = session.post(siem_api, json=event_data)
    return response.json()

# Example usage
event = {
    "time": "2024-11-22T15:30:00Z",
    "source": "firewall-01",
    "message": "Connection blocked from 203.0.113.45",
    "severity": "medium",
    "category": "network",
    "source_ip": "203.0.113.45"
}

send_event_to_siem(event)
```

---

## Webhook Support

### Outgoing Webhooks
Configure webhooks to send data to external systems when events occur.

```python
# Example webhook sender
import requests
import json

def send_webhook(url, data):
    """Send webhook to external system"""
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, json=data, headers=headers)
    return response.status_code

# Example: Send alert to webhook
alert_data = {
    "event_type": "alert.created",
    "alert": {
        "id": 123,
        "name": "Brute Force Detected",
        "severity": "high",
        "status": "new"
    },
    "timestamp": "2024-11-22T15:30:00Z"
}

send_webhook("https://your-system.com/webhook", alert_data)
```

---

## Rate Limiting (Future Enhancement)

Implement rate limiting to prevent API abuse:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## API Authentication Methods (Future Enhancement)

### 1. Token Authentication
```python
# Install
pip install djangorestframework-simplejwt

# settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

# Usage
import requests

# Get token
response = requests.post('http://127.0.0.1:8000/api/token/', data={
    'username': 'admin',
    'password': 'admin123'
})
token = response.json()['access']

# Use token
headers = {'Authorization': f'Bearer {token}'}
response = requests.get('http://127.0.0.1:8000/api/events/', headers=headers)
```

### 2. API Key Authentication
```python
# Custom API key authentication
class APIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        api_key = request.META.get('HTTP_X_API_KEY')
        if not api_key:
            return None
        
        try:
            user = User.objects.get(api_key=api_key)
            return (user, None)
        except User.DoesNotExist:
            raise AuthenticationFailed('Invalid API key')

# Usage
headers = {'X-API-Key': 'your-api-key-here'}
response = requests.get('http://127.0.0.1:8000/api/events/', headers=headers)
```

---

## Error Handling

### HTTP Status Codes
| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 500 | Internal Server Error |

### Error Response Format
```json
{
    "error": "Error message",
    "detail": "Detailed error description",
    "status_code": 400
}
```

---

## Best Practices

1. **Always Authenticate**: All API calls require authentication
2. **Use HTTPS**: In production, always use HTTPS
3. **Rate Limiting**: Implement rate limiting to prevent abuse
4. **Pagination**: Use pagination for large datasets
5. **Caching**: Cache frequently accessed data
6. **Versioning**: Use API versioning (e.g., `/api/v1/`)
7. **Error Handling**: Always handle errors gracefully
8. **Logging**: Log all API access for audit purposes

---

## Future API Enhancements

### Planned Features
1. ✅ Full REST API with Django REST Framework
2. ✅ JWT token authentication
3. ✅ API key management
4. ✅ Rate limiting
5. ✅ Pagination
6. ✅ Filtering and search
7. ✅ Bulk operations
8. ✅ Webhooks
9. ✅ GraphQL support
10. ✅ OpenAPI/Swagger documentation

---

## Support

For API support and questions:
- Check the main documentation: `SIEM_IMPLEMENTATION.md`
- Review the quick reference: `QUICK_REFERENCE.md`
- Contact the development team

---

**Happy Integrating!** 🚀
