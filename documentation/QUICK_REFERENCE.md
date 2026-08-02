# SIEM Tool - Quick Reference Guide

## 🚀 Getting Started

### Login Credentials
- **Username**: `admin`
- **Password**: `admin123`

### Access Points
- **Admin Interface**: http://127.0.0.1:8000/admin/
- **SIEM Dashboard**: http://127.0.0.1:8000/dashboard/
- **Login Page**: http://127.0.0.1:8000/login/

---

## 📍 URL Routes

### Core Navigation
| Feature | URL | Description |
|---------|-----|-------------|
| Dashboard | `/dashboard/` | Main SIEM dashboard with metrics |
| Events | `/events/` | Security events and logs |
| Alerts | `/alerts/` | Active security alerts |
| Assets | `/assets/` | Asset inventory |
| Investigations | `/investigations/` | Incident investigations |
| Threat Intel | `/threat-intel/` | IOCs and threat actors |
| Detection Rules | `/detection-rules/` | Correlation and detection rules |
| MITRE ATT&CK | `/mitre-attack/` | MITRE framework browser |
| Hunting | `/hunting/` | Threat hunting interface |
| UEBA | `/ueba/` | Behavior analytics and anomalies |
| Compliance | `/compliance/` | Compliance frameworks |
| Reports | `/reports/` | Generated reports |
| Playbooks | `/playbooks/` | Incident response playbooks |
| Settings | `/settings/` | System configuration |

### API Endpoints
| Endpoint | URL | Description |
|----------|-----|-------------|
| Events Data | `/api/events/` | JSON events data |
| Alert Stats | `/api/alerts/stats/` | Alert statistics |
| Threat Map | `/api/threat-map/` | Geolocation data |

---

## 🎯 Key Features by Use Case

### 1. Security Monitoring
**Start Here**: `/dashboard/`
- View real-time metrics
- Check critical alerts
- Monitor event rates
- Review top threats

**Then Go To**: `/events/`
- Filter by severity, category, time range
- Search for specific events
- Export event data

### 2. Alert Management
**Start Here**: `/alerts/`
- View all active alerts
- Filter by status and severity
- Assign alerts to analysts
- Acknowledge or resolve alerts

**Actions Available**:
- Acknowledge → Changes status to "Investigating"
- Resolve → Marks alert as resolved
- Close → Closes the alert
- Mark as False Positive → Removes from active alerts

### 3. Incident Investigation
**Start Here**: `/investigations/`
- View all cases
- Filter by status and priority
- Create new investigations

**Investigation Details**: `/investigations/<case_id>/`
- View timeline
- Add notes
- Link alerts and IOCs
- Track affected assets
- Map to MITRE ATT&CK
- Attach evidence

### 4. Threat Intelligence
**Start Here**: `/threat-intel/`
- Browse IOCs (IPs, domains, hashes, emails)
- View threat actors
- Check threat feeds

**IOC Details**: `/threat-intel/ioc/<id>/`
- View IOC details
- See related events
- Check threat actor attribution

### 5. Threat Hunting
**Start Here**: `/hunting/`
- Run custom queries
- Use saved searches
- Create new hunting queries
- Share queries with team

### 6. Behavior Analytics (UEBA)
**Start Here**: `/ueba/`
- View detected anomalies
- Check high-risk users
- Review behavior baselines

**Anomaly Actions**:
- Mark as reviewed
- Mark as false positive
- View related events

### 7. Compliance Monitoring
**Start Here**: `/compliance/`
- View compliance status for PCI-DSS, HIPAA, GDPR
- Check compliance rates
- Review failed checks

### 8. Detection Engineering
**Start Here**: `/detection-rules/`
- View all detection rules
- Check rule types (threshold, correlation, SIGMA, YARA)
- Review trigger statistics
- Map to MITRE ATT&CK

### 9. Incident Response
**Start Here**: `/playbooks/`
- View available playbooks
- Execute playbooks
- Track playbook runs

**Playbook Types**:
- Automated (run automatically)
- Manual (step-by-step guidance)

### 10. Reporting
**Start Here**: `/reports/`
- Generate new reports
- View historical reports
- Schedule recurring reports

**Report Types**:
- Security Summary
- Incident Response
- Compliance
- Threat Intelligence
- User Activity
- Asset Inventory

---

## 🔍 Search & Filter Tips

### Event Filtering
- **By Severity**: `?severity=critical`
- **By Category**: `?category=malware`
- **By Time**: `?time_range=24h` (options: 1h, 24h, 7d, 30d)
- **By Source IP**: `?source_ip=192.168.1.100`
- **By Username**: `?username=john.doe`
- **Search**: `?q=failed login`

### Alert Filtering
- **By Status**: `?status=open`
- **By Severity**: `?severity=high`

### Investigation Filtering
- **By Status**: `?status=in_progress`
- **By Priority**: `?priority=critical`

### Asset Filtering
- **By Type**: `?type=server`
- **By Criticality**: `?criticality=high`

---

## 📊 Dashboard Metrics Explained

| Metric | Description |
|--------|-------------|
| Events Per Minute | Average event ingestion rate (last 24h) |
| Critical Alerts | Number of critical severity alerts (open/new) |
| High Alerts | Number of high severity alerts (open/new) |
| Open Investigations | Active investigation cases |
| Top Alerts | Most frequent alert types |
| Recent Events | Latest critical/high severity events |
| Top Sources | IP addresses generating most events |
| MITRE Coverage | Number of ATT&CK techniques in database |
| Active IOCs | Number of active threat indicators |
| Threat Actors | Known threat groups in database |
| Unreviewed Anomalies | UEBA anomalies needing review |

---

## 🎨 MITRE ATT&CK Integration

### Tactics (12 Total)
1. **TA0001** - Initial Access
2. **TA0002** - Execution
3. **TA0003** - Persistence
4. **TA0004** - Privilege Escalation
5. **TA0005** - Defense Evasion
6. **TA0006** - Credential Access
7. **TA0007** - Discovery
8. **TA0008** - Lateral Movement
9. **TA0009** - Collection
10. **TA0010** - Exfiltration
11. **TA0011** - Command and Control
12. **TA0040** - Impact

### Techniques (25+ Populated)
Examples:
- **T1078** - Valid Accounts
- **T1566** - Phishing
- **T1110** - Brute Force
- **T1486** - Data Encrypted for Impact (Ransomware)

### Usage
- Map alerts to techniques
- Map detection rules to techniques
- Map investigations to techniques
- Track technique coverage

---

## 🔐 User Roles & Permissions

### Admin
- Full access to all features
- Can manage users
- Can configure system settings

### Analyst (Staff)
- View and manage alerts
- Create and manage investigations
- Run queries and hunts
- Generate reports

### Viewer (Regular User)
- Read-only access to dashboards
- View events and alerts
- Cannot modify data

---

## 📝 Common Workflows

### Workflow 1: Responding to an Alert
1. Go to `/alerts/`
2. Click on alert to view details
3. Click "Acknowledge" to assign to yourself
4. Review related events
5. Check MITRE ATT&CK techniques
6. Create investigation if needed
7. Mark as "Resolved" or "False Positive"

### Workflow 2: Creating an Investigation
1. Go to `/investigations/`
2. Click "Create New Investigation"
3. Fill in case details
4. Link related alerts
5. Add affected assets
6. Map to MITRE techniques
7. Add notes as you investigate
8. Attach evidence
9. Execute playbook if available
10. Close when resolved

### Workflow 3: Threat Hunting
1. Go to `/hunting/`
2. Enter search query
3. Review results
4. Save query for future use
5. Create alert if threat found
6. Create investigation if needed

### Workflow 4: Reviewing Anomalies
1. Go to `/ueba/`
2. Review unreviewed anomalies
3. Click on anomaly for details
4. Check related events
5. Mark as reviewed or false positive
6. Create alert if legitimate threat

---

## 🛠️ Admin Tasks

### Managing Users
1. Go to `/admin/auth/user/`
2. Add new users
3. Assign permissions
4. Set staff status

### Managing Detection Rules
1. Go to `/admin/core/detectionrule/`
2. Create new rules
3. Set thresholds and time windows
4. Map to MITRE techniques
5. Enable/disable rules

### Managing IOCs
1. Go to `/admin/core/ioc/`
2. Add new IOCs
3. Set confidence and severity
4. Link to threat feeds
5. Attribute to threat actors

### Managing Compliance
1. Go to `/admin/core/complianceframework/`
2. Add frameworks
3. Create compliance checks
4. Set automated check schedules

---

## 📈 Sample Data Included

### Assets (8)
- 2 web servers
- 1 database server
- 1 file server
- 2 workstations
- 1 firewall
- 1 core switch

### Events (100)
- Various severities and categories
- Last 72 hours
- Multiple source IPs

### Alerts (3)
- Brute force detection
- SQL injection
- Malware detection

### IOCs (6)
- Malicious IPs
- Phishing domains
- Ransomware hash
- C2 domains

### Threat Actors (3)
- APT28 (Fancy Bear)
- Lazarus Group
- FIN7

### Detection Rules (4)
- Brute force detection
- SQL injection attempt
- Malware execution
- Unusual data transfer

### Investigations (2)
- Brute force attack
- Ransomware incident

### Playbooks (2)
- Brute force response
- Malware containment

### Compliance Frameworks (3)
- PCI-DSS
- HIPAA
- GDPR

---

## 🎓 Tips & Best Practices

### 1. Alert Management
- Acknowledge alerts promptly
- Don't ignore false positives - mark them properly
- Create investigations for complex incidents
- Use MITRE mapping to understand attack patterns

### 2. Threat Hunting
- Save useful queries for reuse
- Share public queries with team
- Schedule important queries
- Document findings in investigations

### 3. UEBA
- Review anomalies daily
- Update baselines periodically
- Don't dismiss unusual behavior without investigation
- Track high-risk users

### 4. Compliance
- Run compliance checks regularly
- Document remediation for failed checks
- Keep frameworks up to date
- Generate compliance reports for audits

### 5. Incident Response
- Use playbooks for consistency
- Document everything in investigation notes
- Maintain chain of custody for evidence
- Map incidents to MITRE ATT&CK
- Capture lessons learned

---

## 🔧 Troubleshooting

### Can't Login
- Check username/password: admin/admin123
- Ensure you're using `/login/` or `/admin/`

### No Data Showing
- Run: `python manage.py populate_sample_data`
- Check database connection

### Missing MITRE Techniques
- Run: `python manage.py populate_mitre`

### Permission Denied
- Ensure user has staff status
- Check user permissions in admin

---

## 📚 Additional Resources

### Django Admin
- Full CRUD operations for all models
- Advanced filtering and search
- Bulk operations
- Data export

### API Integration
- Use `/api/events/` for event data
- Use `/api/alerts/stats/` for metrics
- Use `/api/threat-map/` for geolocation

### Customization
- All templates in `backend/templates/siem/`
- All static files in `backend/static/`
- All models in `backend/apps/core/models.py`
- All views in `backend/apps/core/views.py`

---

## 🎉 You're Ready!

This SIEM tool now has all the features of enterprise solutions like:
- ✅ Splunk Enterprise Security
- ✅ IBM QRadar
- ✅ ArcSight
- ✅ LogRhythm
- ✅ AlienVault USM

**Start exploring and happy hunting!** 🚀
