# 🗄️ Supabase PostgreSQL Setup Guide for REBADEN SIEM

## Why Supabase?

For a SIEM application, **Supabase** (PostgreSQL) is the optimal choice because:

- ✅ **Relational Database**: Perfect for complex security queries and correlations
- ✅ **Always Free Tier**: 500MB storage, sufficient for development/testing
- ✅ **Built-in Authentication**: User management out of the box
- ✅ **Real-time Subscriptions**: Monitor alerts in real-time (WebSockets)
- ✅ **Row Level Security**: Database-level security policies
- ✅ **Easy Django Integration**: Works seamlessly with Django ORM
- ✅ **No Time Limits**: Not a trial—perpetually free for development

---

## 📋 Quick Setup (5-10 minutes)

### Step 1: Create Supabase Account & Project

1. Go to [supabase.com](https://supabase.com)
2. Click **"Start your project"**
3. Sign in with GitHub, Google, or email
4. Create a new organization (if needed)
5. Create a new project:
   - **Name**: `rebaden-siem` (or your choice)
   - **Database Password**: Create a strong password (save it!)
   - **Region**: Choose closest to you
   - Click **Create**

⏳ **Wait 2-3 minutes for provisioning...**

### Step 2: Get Your Connection String

1. In Supabase Dashboard, click **Settings** → **Database**
2. Under "Connection pooling" or "Connection string", find **PostgreSQL** section
3. Copy the **Connection String** (looks like):
   ```
   postgresql://postgres.XXXXXXXXXXXX:your_password@aws-0-us-east-1.sql.supabase.co:5432/postgres?sslmode=require
   ```

### Step 3: Configure Django

1. **Install dependencies:**
   ```bash
   cd /home/josh/projects/rebaden/backend
   source djangoback/bin/activate
   pip install -r requirements.txt
   ```

2. **Create `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

3. **Edit `.env` and add your Supabase connection:**
   ```env
   DATABASE_URL=postgresql://postgres.XXXXXXXXXXXX:your_password@aws-0-us-east-1.sql.supabase.co:5432/postgres?sslmode=require
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Test connection:**
   ```bash
   python manage.py dbshell
   # If it connects, you're good! Type: \q to exit
   ```

---

## 🚀 Run Django with Supabase

```bash
cd /home/josh/projects/rebaden/backend
source djangoback/bin/activate
python manage.py runserver 0.0.0.0:8000
```

Visit: `http://localhost:8000`

---

## 📊 Supabase Dashboard Features

Once set up, explore these features in the Supabase dashboard:

### 1. **SQL Editor** (Real-time SQL queries)
- Write raw SQL for complex SIEM queries
- Example: Find all critical alerts from last 24h
  ```sql
  SELECT * FROM core_alert 
  WHERE severity = 'critical' 
  AND first_seen > NOW() - INTERVAL '24 hours'
  ORDER BY first_seen DESC;
  ```

### 2. **Table Editor** (Browse/edit data visually)
- View your SIEM data in table format
- Insert/edit records manually
- Add filters and sorts

### 3. **Auth Tab** (User management)
- Add users directly (beyond Django admin)
- Configure email verification
- Set up passwordless login (optional)

### 4. **Realtime** (Enable real-time subscriptions)
- Enable for tables you want real-time updates
- Example: Get alert updates in real-time
- Requires frontend JavaScript integration

---

## 🔗 API Integration Examples

### Example 1: Fetch Alerts via REST API

```python
import requests

# Get all critical alerts
url = "http://localhost:8000/api/v1/alerts/"
params = {"severity": "critical", "status": "open"}
response = requests.get(url, params=params, headers={"Authorization": "Bearer YOUR_TOKEN"})

alerts = response.json()
print(f"Found {len(alerts)} critical alerts")
for alert in alerts:
    print(f"  - {alert['name']} ({alert['severity']})")
```

### Example 2: Create Alert Programmatically

```python
import requests

data = {
    "name": "Suspicious Login Activity",
    "description": "Multiple failed login attempts detected",
    "severity": "high",
    "status": "new",
    "source_ip": "192.168.1.100",
}

response = requests.post(
    "http://localhost:8000/api/v1/alerts/",
    json=data,
    headers={"Authorization": "Bearer YOUR_TOKEN"}
)

if response.status_code == 201:
    print(f"Alert created: {response.json()['id']}")
```

### Example 3: Query Events with Filters

```python
# Get events from specific asset in last 24h
from django.utils import timezone
from datetime import timedelta
from apps.core.models import Event

asset_id = 1
since = timezone.now() - timedelta(hours=24)

events = Event.objects.filter(
    asset=asset_id,
    time__gte=since
).order_by('-time')

print(f"Found {events.count()} recent events")
for event in events[:10]:
    print(f"  - [{event.severity}] {event.event_type} at {event.time}")
```

---

## 🔒 Security Best Practices

### 1. **Environment Variables**
- ✅ **DO**: Store `DATABASE_URL` in `.env`
- ❌ **DON'T**: Hardcode connection strings
- ❌ **DON'T**: Commit `.env` to Git

Add to `.gitignore`:
```
.env
.env.local
db.sqlite3
```

### 2. **Row Level Security (RLS)**
Enable RLS in Supabase for user isolation:

```sql
-- In Supabase SQL Editor:
ALTER TABLE core_alert ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users see their own alerts"
ON core_alert FOR SELECT
USING (assigned_to_id = auth.uid());
```

### 3. **Database Backups**
- Supabase auto-backs up daily
- Manual backups: Dashboard → Backups
- Retention: 7 days on free tier

---

## 📈 Monitoring & Limits

### Free Tier Limits
| Resource | Limit |
|----------|-------|
| Storage | 500MB |
| Bandwidth | 5GB/month |
| Real-time Connections | 200 |
| Database Rows | No limit |
| Concurrent Connections | 4 (shared) |

### Monitor Usage
1. Dashboard → **Database** → **Statistics**
2. Check storage usage monthly
3. Optimize if approaching limits

---

## 🆘 Troubleshooting

### Issue: "Connection refused"
```python
# Check DATABASE_URL in .env
# Verify Supabase project is active
# Ensure firewall allows connections
```

### Issue: "SSL error"
```python
# Make sure connection string has ?sslmode=require
# Install: pip install psycopg2-binary
```

### Issue: "Auth failed"
```python
# Check database password in Supabase Settings
# Reset password if needed
# Verify username is "postgres"
```

### Check Django Connection
```bash
python manage.py dbshell
# Should open PostgreSQL prompt
\dt  # List all tables
\q   # Exit
```

---

## 🚀 Advanced Features

### 1. **Real-time Alert Monitoring**

Enable real-time subscriptions for critical alerts:

```python
# In your view or service
from supabase import create_client

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_KEY')
)

# Subscribe to alert changes
def on_alert_change(payload):
    print(f"Alert updated: {payload['new']['name']}")

supabase.table('core_alert').on('*', on_alert_change).subscribe()
```

### 2. **Full-Text Search**

Use PostgreSQL's native full-text search:

```sql
-- Enable in Supabase
ALTER TABLE core_event ADD COLUMN search_vector tsvector;

CREATE TRIGGER event_search_update
BEFORE INSERT OR UPDATE ON core_event
FOR EACH ROW EXECUTE FUNCTION
tsvector_update_trigger(search_vector, 'pg_catalog.english', description, event_type);

CREATE INDEX search_idx ON core_event USING gin(search_vector);
```

### 3. **Query Performance**
Create indexes for frequently filtered columns:

```sql
CREATE INDEX idx_alert_severity ON core_alert(severity);
CREATE INDEX idx_alert_status ON core_alert(status);
CREATE INDEX idx_event_timestamp ON core_event(time);
```

---

## 📚 Useful Links

- 📖 [Supabase Docs](https://supabase.com/docs)
- 🐘 [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- 🎯 [Django PostgreSQL Setup](https://docs.djangoproject.com/en/4.2/ref/databases/#postgresql-notes)
- 🔐 [Supabase Auth Guide](https://supabase.com/docs/guides/auth)

---

## Next Steps

1. ✅ Set up Supabase project
2. ✅ Configure Django with `DATABASE_URL`
3. ✅ Run migrations: `python manage.py migrate`
4. ✅ Test with: `python manage.py dbshell`
5. ✅ Start server: `python manage.py runserver`
6. ✅ Populate sample data: `python manage.py populate_sample_data`

**Enjoy your cloud-powered SIEM! 🎉**
