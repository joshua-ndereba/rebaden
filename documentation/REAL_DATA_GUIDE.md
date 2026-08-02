# REBADEN SIEM - Real Data Integration Guide

## Overview

This guide shows you how to use the REBADEN SIEM application with **real data** instead of dummy data. The system now includes:

- **Real asset management** - Add and manage actual network assets
- **Log file processing** - Upload and process real security logs
- **Event ingestion** - Automatic event extraction from log files
- **Alert generation** - Real-time alert generation from events
- **Investigation workflow** - Create and manage investigations
- **Settings synchronization** - User profile and settings persistence

## Quick Start

### 1. Clean Up Dummy Data

First, remove any existing dummy data:

```bash
cd backend
python manage.py cleanup_dummy_data --confirm
```

### 2. Initialize Real Data Structures

Set up detection rules and log sources:

```bash
python manage.py init_real_data
```

### 3. Add Real Assets

Create assets via the API:

```bash
curl -X POST http://localhost:8000/api/v1/assets/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN" \
  -d '{
    "hostname": "web-server-01",
    "ip": "192.168.1.10",
    "asset_type": "server",
    "criticality": "high",
    "os": "Ubuntu 20.04",
    "owner": "John Smith",
    "department": "Operations"
  }'
```

Or via the web interface:
- Navigate to `/api/v1/assets/` in your browser
- Use the form to create new assets

### 4. Upload Log Files

Two ways to upload log files:

**Option A: Via Settings Page**
1. Go to `/settings/`
2. Scroll to "Data Ingestion" section
3. Upload a log file
4. Select log type (auto-detect, syslog, apache, etc.)
5. Click "Upload & Process"

**Option B: Via API**

```bash
curl -X POST http://localhost:8000/api/v1/log-upload/upload/ \
  -F "file=@access.log" \
  -F "log_type=apache" \
  -F "source_name=web-server-01" \
  -H "X-CSRFToken: YOUR_CSRF_TOKEN"
```

## API Endpoints

### Assets Management

```
GET    /api/v1/assets/                    - List all assets
POST   /api/v1/assets/                    - Create new asset
GET    /api/v1/assets/{id}/               - Get asset details
PUT    /api/v1/assets/{id}/               - Update asset
DELETE /api/v1/assets/{id}/               - Delete asset
POST   /api/v1/assets/bulk_create/        - Bulk create assets
GET    /api/v1/assets/by_criticality/     - Filter by criticality
GET    /api/v1/assets/with_events/        - Assets with recent events
GET    /api/v1/assets/{id}/activity/      - Get asset activity
```

### Events

```
GET    /api/v1/events/                    - List all events
GET    /api/v1/events/{id}/               - Get event details
GET    /api/v1/events/by_severity/        - Filter by severity
GET    /api/v1/events/by_asset/           - Filter by asset
GET    /api/v1/events/timeline/           - Get timeline data
```

### Alerts

```
GET    /api/v1/alerts/                    - List all alerts
POST   /api/v1/alerts/                    - Create alert
GET    /api/v1/alerts/{id}/               - Get alert details
PUT    /api/v1/alerts/{id}/               - Update alert
DELETE /api/v1/alerts/{id}/               - Delete alert
GET    /api/v1/alerts/open_alerts/        - Get open alerts
GET    /api/v1/alerts/by_status/          - Filter by status
POST   /api/v1/alerts/{id}/take_action/   - Perform alert actions
```

### Investigations

```
GET    /api/v1/investigations/            - List all investigations
POST   /api/v1/investigations/            - Create investigation
GET    /api/v1/investigations/{id}/       - Get investigation details
PUT    /api/v1/investigations/{id}/       - Update investigation
DELETE /api/v1/investigations/{id}/       - Delete investigation
GET    /api/v1/investigations/open/       - Get open investigations
POST   /api/v1/investigations/{id}/assign/ - Assign investigation
```

### Log Upload

```
POST   /api/v1/log-upload/upload/         - Upload and process log file
GET    /api/v1/log-upload/history/        - Get upload history
GET    /api/v1/log-upload/stats/          - Get upload statistics
```

### User Profile

```
GET    /api/v1/profile/me/                - Get current user profile
POST   /api/v1/profile/update_profile/    - Update user profile
GET    /api/v1/profile/settings/          - Get user settings
```

## Log File Processing

### Supported Log Formats

The system automatically detects and parses:

1. **Syslog** - Standard syslog format (BSD/RFC 3164)
   ```
   Jan 15 14:30:22 hostname process[123]: message
   ```

2. **Apache** - Apache access/error logs
   ```
   192.168.1.1 - - [15/Jan/2023:14:30:22 +0000] "GET /index.html HTTP/1.1" 200 1234
   ```

3. **Nginx** - Nginx access/error logs
   ```
   192.168.1.1 - - [15/Jan/2023:14:30:22 +0000] "GET /index.html HTTP/1.1" 200 1234
   ```

4. **Windows Event Log** - Windows Event Log format
   ```
   2023-01-15 14:30:22 INFO SYSTEM 1000 User logged in
   ```

5. **Firewall** - Firewall rule logs
   ```
   2023-01-15 14:30:22 ACCEPT TCP 192.168.1.100:1234->8.8.8.8:443
   ```

6. **Authentication** - Auth/login logs
   ```
   Jan 15 14:30:22 hostname sshd[123]: Accepted password for user from 192.168.1.1
   ```

### Custom Log Parsing

To add custom log parsing, edit `apps/core/log_parser.py`:

```python
PATTERNS = {
    'your_format': r'your_regex_pattern_here',
}
```

## Alert Generation

Alerts are automatically generated from events based on:

### 1. Detection Rules
- Keyword matching in event messages
- Rule severity levels
- Configurable rule logic

### 2. IOC Matching
- IP address indicators
- User indicators
- Domain/URL indicators

### 3. Behavioral Analysis
- Brute force attempts (5+ failed logins in 5 minutes)
- Port scanning patterns
- Data exfiltration attempts
- Privilege escalation attempts

### 4. MITRE ATT&CK Mapping
- Events automatically mapped to MITRE techniques
- Confidence scoring
- Tactic association

## Settings & Profile Synchronization

The Settings page now syncs with user profile:

### User Profile Fields
- First Name & Last Name
- Email Address
- Department
- Role (Analyst, Investigator, Manager, Admin, Viewer)
- Timezone
- Alert preferences
- Notification settings

### Automatic Sync
When you save settings on `/settings/`, the API endpoint:
- Updates user profile data
- Persists preferences to database
- Reflects changes immediately

## Example Workflows

### Workflow 1: Upload Logs and Generate Alerts

1. **Upload log file** via `/settings/`
2. **System automatically**:
   - Parses the log file
   - Creates Event objects
   - Triggers alert generation
   - Maps to MITRE techniques
3. **View results**:
   - Check `/alerts/` for new alerts
   - View events at `/events/`
   - See dashboard statistics

### Workflow 2: Create Investigation from Alert

1. **Click on an alert** in `/alerts/`
2. **Review alert details** and related events
3. **Create investigation** via "Create Investigation" button
4. **Assign investigators**
5. **Add findings and recommendations**
6. **Resolve investigation**

### Workflow 3: Manage Assets and Track Activity

1. **Create assets** via `/api/v1/assets/`
2. **Upload logs** from those assets
3. **View asset activity** at `/assets/` -> click asset
4. **Track events and alerts** per asset
5. **Monitor risk scores** over time

## Dashboard Updates

The dashboard now shows:

- **Real-time metrics** from actual events
- **Event counts** by severity, type, category
- **Alert trends** over time
- **Top source IPs** with threat levels
- **Asset activity** visualization
- **MITRE ATT&CK coverage** mapping
- **Investigation status** summary

## Database Schema

### Key Models

**Event** - Security logs and events
- timestamp, source, message, severity, category
- source_ip, dest_ip, username, process_name
- file_path, protocol, action, result
- Relationships: asset, log_source

**Alert** - Generated security alerts
- title, description, severity, priority, status
- detection_rule, asset, related_events, ioc
- investigation_notes, resolution
- Relationships: investigation, detection_rule

**Asset** - Network endpoints
- hostname, ip, mac_address, os, owner
- criticality, risk_score, last_seen, is_active
- Relationships: events, alerts

**LogSource** - Event sources
- name, source_type, host, port
- is_active, events_received, last_event_time

## Troubleshooting

### Issue: Alerts not generating from events

**Solution:**
1. Check detection rules are active: `DetectionRule.objects.filter(is_active=True).count()`
2. Verify signals are loaded: Check console for signal registration
3. Manually trigger: `AlertGenerator.process_event(event_object)`

### Issue: Log files not parsing

**Solution:**
1. Check log format is supported
2. Verify regex pattern in PATTERNS dict
3. Test with smaller log file
4. Check for encoding issues (use UTF-8)

### Issue: API returns 403 Forbidden

**Solution:**
1. Ensure you're logged in
2. Include CSRF token in POST requests
3. Check user permissions

### Issue: Settings not saving

**Solution:**
1. Check browser console for errors
2. Verify API endpoint is accessible
3. Ensure CSRF token is correct
4. Check UserProfile exists: `UserProfile.objects.filter(user=user).exists()`

## Performance Optimization

For large-scale log ingestion:

### 1. Batch Event Creation
```python
from apps.core.models import Event

events = [Event(...) for i in range(1000)]
Event.objects.bulk_create(events, batch_size=500)
```

### 2. Disable Signals (if needed)
```python
from django.db.models.signals import post_save
from apps.core.models import Event

post_save.disconnect(generate_alerts_from_event, sender=Event)
# ... do bulk operations
post_save.connect(generate_alerts_from_event, sender=Event)
```

### 3. Database Indexing
```python
# Already configured in models:
Event._meta.indexes = [
    models.Index(fields=['-time', 'severity']),
    models.Index(fields=['source_ip', '-time']),
]
```

## Security Considerations

- API endpoints require authentication (`@login_required`)
- Use HTTPS in production
- Validate all file uploads
- Sanitize log input to prevent injection
- Implement rate limiting for API
- Use environment variables for sensitive config

## Next Steps

1. ✅ Clean up dummy data
2. ✅ Initialize real data structures
3. ✅ Add real assets
4. ✅ Upload real log files
5. ✅ Create investigations from alerts
6. ✅ Generate reports
7. ✅ Configure compliance checks
8. ✅ Set up threat intelligence feeds

For more information, see:
- API Documentation: `/api/v1/`
- Django Admin: `/admin/`
- Settings: `/settings/`
- Dashboard: `/dashboard/`
