# 🚀 SIEM Application - Quick Start Guide

## Immediate Actions You Can Take

### 1. Upload a Log File (2 minutes)

```bash
# The test file is ready at:
/home/josh/mine/hackathon/web-app/my-django-project/backend/test_sample.log
```

**Steps**:
1. Go to: http://localhost:8000/logs/
2. Click "Choose File" and select `test_sample.log`
3. Select log type: "Auto-detect"
4. Click "Upload"
5. **Watch the magic happen!**
   - 12 events parsed
   - 3 threats detected (Brute Force, SQL Injection, XSS)
   - 3 alerts created automatically
   - Statistics displayed

---

### 2. View Generated Alerts (30 seconds)

1. Go to: http://localhost:8000/alerts/
2. See alerts created from log upload:
   - "Brute Force Detected" (High severity)
   - "Malicious Pattern Detected" (Critical - SQL Injection)
   - "Malicious Pattern Detected" (Critical - XSS)
3. Click on any alert to see details

---

### 3. Create an Investigation (1 minute)

1. Go to: http://localhost:8000/investigations/create/
2. Fill in:
   - **Title**: "Brute Force Attack Investigation"
   - **Description**: "Investigating multiple failed login attempts from 192.168.1.100"
   - **Priority**: High
   - **Severity**: High
3. Click "Create"
4. Get auto-generated case ID (e.g., `INV-20251122-1234`)

---

### 4. Generate a Security Report (1 minute)

1. Go to: http://localhost:8000/reports/generate/
2. Select:
   - **Report Type**: Security Summary
   - **Format**: HTML (to view in browser)
3. Click "Generate"
4. Report downloads with:
   - Event statistics
   - Alert breakdown
   - Top source IPs
   - Threat summary

---

### 5. Search for Specific Data (30 seconds)

1. Go to: http://localhost:8000/search/
2. Search for: `192.168.1.100`
3. See results across:
   - Events from this IP
   - Related alerts
   - Associated investigations

---

### 6. Update Your Profile (1 minute)

1. Go to: http://localhost:8000/profile/
2. Update:
   - First Name
   - Last Name
   - Email
3. Change password if needed
4. View your activity statistics

---

### 7. Export Data (30 seconds)

1. Go to: http://localhost:8000/events/
2. Apply filters (optional):
   - Severity: High
   - Time Range: Last 24 Hours
3. Click "Export" (you'll need to add this button to the template)
4. Or go directly to: http://localhost:8000/export/events/
5. CSV file downloads with all events

---

## All Available URLs

### Main Features
- **Dashboard**: http://localhost:8000/dashboard/
- **Events**: http://localhost:8000/events/
- **Alerts**: http://localhost:8000/alerts/
- **Logs**: http://localhost:8000/logs/
- **Investigations**: http://localhost:8000/investigations/
- **Assets**: http://localhost:8000/assets/
- **Threat Intel**: http://localhost:8000/threat-intel/
- **Hunting**: http://localhost:8000/hunting/
- **Reports**: http://localhost:8000/reports/
- **Settings**: http://localhost:8000/settings/

### New Interactive Features
- **User Profile**: http://localhost:8000/profile/
- **Advanced Search**: http://localhost:8000/search/
- **Create Investigation**: http://localhost:8000/investigations/create/
- **Generate Report**: http://localhost:8000/reports/generate/
- **Export Events**: http://localhost:8000/export/events/

### Authentication
- **Login**: http://localhost:8000/accounts/login/
- **Register**: http://localhost:8000/register/
- **Logout**: http://localhost:8000/accounts/logout/

### Admin
- **Django Admin**: http://localhost:8000/admin/

---

## Key Capabilities

### ✅ What Users Can Do

1. **Upload & Analyze Logs**
   - Drag & drop log files
   - Auto-detect format
   - Parse thousands of events
   - Detect threats automatically

2. **Manage Alerts**
   - View all alerts
   - Acknowledge alerts
   - Assign to team members
   - Mark as resolved/false positive
   - Add notes

3. **Investigate Incidents**
   - Create investigations
   - Add notes and evidence
   - Track timeline
   - Assign to teams
   - Close with resolution

4. **Generate Reports**
   - 6 report types
   - 3 export formats (JSON/CSV/HTML)
   - Custom date ranges
   - Automatic statistics

5. **Search Everything**
   - Search across all data
   - Filter by type
   - Quick navigation
   - Real-time results

6. **Export Data**
   - Export events to CSV
   - Filter before export
   - Audit logging
   - Download instantly

7. **Manage Profile**
   - Update information
   - Change password
   - View activity
   - See statistics

---

## Threat Detection

### Automatically Detected Threats

1. **SQL Injection**
   - `UNION SELECT`
   - `DROP TABLE`
   - `INSERT INTO`
   - `OR 1=1`

2. **Cross-Site Scripting (XSS)**
   - `<script>`
   - `javascript:`
   - `onerror=`
   - `onload=`

3. **Path Traversal**
   - `../`
   - `..\\`

4. **Command Injection**
   - `cmd.exe`
   - `/bin/bash`
   - `/bin/sh`

5. **Code Execution**
   - `eval(`
   - `exec(`
   - `system(`

6. **Brute Force**
   - 5+ failed logins from same IP

---

## File Formats Supported

### Log Upload
- `.log` - Standard log files
- `.txt` - Text files
- `.csv` - CSV format logs
- Max size: 10MB

### Report Export
- `.json` - Machine-readable
- `.csv` - Spreadsheet
- `.html` - Web page

### Data Export
- `.csv` - Event data

---

## Quick Commands

### Create Sample Log File
```bash
cat > sample.log << 'EOF'
Nov 22 10:30:45 server sshd[1234]: Failed password for admin from 192.168.1.100
Nov 22 10:30:47 server sshd[1235]: Failed password for admin from 192.168.1.100
Nov 22 10:30:49 server sshd[1236]: Failed password for admin from 192.168.1.100
Nov 22 10:30:51 server sshd[1237]: Failed password for admin from 192.168.1.100
Nov 22 10:30:53 server sshd[1238]: Failed password for admin from 192.168.1.100
Nov 22 10:30:55 server sshd[1239]: Failed password for admin from 192.168.1.100
EOF
```

### Access Django Shell
```bash
cd /home/josh/mine/hackathon/web-app/my-django-project/backend
python manage.py shell
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### View Logs
```bash
# In Django shell
from apps.core.models import Event
Event.objects.all().count()  # Total events
Event.objects.filter(severity='critical').count()  # Critical events
```

---

## Testing Checklist

- [ ] Upload test_sample.log file
- [ ] View generated alerts
- [ ] Create an investigation
- [ ] Add notes to investigation
- [ ] Generate a security report
- [ ] Search for an IP address
- [ ] Export events to CSV
- [ ] Update user profile
- [ ] Change password
- [ ] View audit logs

---

## Troubleshooting

### Log Upload Not Working
- Check file size (max 10MB)
- Ensure file format is .log, .txt, or .csv
- Check Django logs for errors

### No Alerts Generated
- Check if threats were detected in logs
- Verify log format is recognized
- Check Event table for parsed events

### Report Not Downloading
- Check browser download settings
- Verify report type is selected
- Check Django logs for errors

### Search Not Working
- Ensure you're logged in
- Check if data exists to search
- Try different search terms

---

## Next Steps

1. **Upload Real Logs** - Try with your actual log files
2. **Create Workflows** - Set up investigation processes
3. **Configure Alerts** - Set up notification rules
4. **Train Team** - Share this guide with team members
5. **Customize** - Modify detection rules for your needs

---

## Support Files

- **Full Guide**: `INTERACTIVE_FEATURES_GUIDE.md`
- **Sample Logs**: `SAMPLE_LOGS.md`
- **Test File**: `test_sample.log`
- **Registration Guide**: `REGISTRATION_GUIDE.md`

---

## 🎉 You're Ready!

Everything is set up and ready to use. Start by uploading the test log file and explore all the features!

**Have fun securing your systems!** 🔒🚀
