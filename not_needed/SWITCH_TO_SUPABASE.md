source# 🔄 How to Switch Your Database: SQLite → Supabase

## Current Status
- ✅ Your Django app currently uses **SQLite** (local file)
- ✅ Production-ready to switch to **Supabase (PostgreSQL)**
- ✅ All code changes already implemented!

---

## 📊 Comparison

| Aspect | SQLite (Current) | Supabase (Recommended) |
|--------|------------------|----------------------|
| **Storage** | Local file | Cloud (AWS) |
| **Cost** | Free | Free tier (500MB) |
| **Performance** | Good for dev | Great for production |
| **Scaling** | Limited | Unlimited |
| **Backup** | Manual | Automatic daily |
| **Concurrent Users** | 1-3 users | 100+ users |
| **Best For** | Local development | Production & teams |

---

## ⚡ 3-Minute Switch Process

### Step 1: Create Supabase Account (2 minutes)

```bash
# Go to https://supabase.com
# Click "Start your project"
# Sign in with GitHub or email
# Create new project:
#   - Name: rebaden-siem
#   - Password: Strong password (save it!)
#   - Region: closest to you

# Wait 2-3 minutes for provisioning...
```

### Step 2: Get Connection String (30 seconds)

```bash
# In Supabase Dashboard:
# 1. Click "Settings" (bottom left)
# 2. Click "Database"
# 3. Find "Connection String" section
# 4. Select "PostgreSQL" tab
# 5. Copy the full connection string

# It looks like:
# postgresql://postgres.XXXXX:your_password@aws-0-region.sql.supabase.co:5432/postgres?sslmode=require
```

### Step 3: Update Django (30 seconds)

```bash
cd /home/josh/projects/rebaden/backend

# Copy environment template
cp .env.example .env

# Edit .env
nano .env

# Add your connection string:
# DATABASE_URL=postgresql://postgres.XXXXX:password@aws-0-region.sql.supabase.co:5432/postgres?sslmode=require
```

### Step 4: Test & Migrate (1 minute)

```bash
# Activate virtual environment
source djangoback/bin/activate

# Test database connection
python manage.py dbshell
# You should see: psql (13.x, server 13.x)
# If yes, press: \q (to exit)

# Run migrations (creates tables)
python manage.py migrate

# Create admin user
python manage.py createsuperuser
# Username: admin
# Email: admin@example.com
# Password: (your password)

# Load sample data
python manage.py populate_sample_data

# Start server
python manage.py runserver
```

**Done! 🎉**

---

## 🔍 Verification Steps

### Check 1: Django Shell
```bash
python manage.py shell

# Inside shell:
from apps.core.models import Alert, Asset, Event
print(f"Alerts: {Alert.objects.count()}")
print(f"Assets: {Asset.objects.count()}")
print(f"Events: {Event.objects.count()}")
# Should show numbers > 0 if data loaded

exit()
```

### Check 2: Admin Panel
```bash
# Visit: http://localhost:8000/admin/
# Login with admin credentials
# You should see all the SIEM models
```

### Check 3: API Test
```bash
# Get auth token
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}' \
  "http://localhost:8000/api/v1/auth/"

# Response: {"token": "abc123..."}

# Test API (replace with your token)
curl -H "Authorization: Token abc123..." \
  "http://localhost:8000/api/v1/alerts/"

# Should return JSON list of alerts
```

### Check 4: Supabase Dashboard
```bash
# Visit: https://supabase.com
# Go to your project
# Click "SQL Editor"
# Run:
SELECT COUNT(*) FROM core_alert;

# Should show number > 0
```

---

## 📁 What Happens

When you migrate:

### ✅ Automatic (Django handles)
- Creates all PostgreSQL tables
- Migrates data structure
- Sets up indexes
- Configures relationships

### ✅ You need to do
- Copy environment template (`.env.example` → `.env`)
- Add database URL to `.env`
- Run `migrate` command
- Reload sample data (optional)

### ❓ What about current SQLite data?
- **Important**: SQLite data stays on your computer
- **New**: Supabase gets fresh schema (no data transfer)
- **Solution**: Re-run `populate_sample_data` or manually import if needed

---

## 🆘 Troubleshooting

### Issue: "psycopg2 import error"
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Or if in virtual env:
source djangoback/bin/activate
pip install psycopg2-binary
```

### Issue: "Connection refused"
```bash
# Check DATABASE_URL in .env
# Verify Supabase project is running
# Test manually:
psql postgresql://postgres:password@host:5432/postgres

# If that fails, recreate Supabase project
```

### Issue: "SSL error"
```bash
# Make sure connection string has ?sslmode=require
# Verify with:
grep DATABASE_URL .env

# Should end with: ?sslmode=require
```

### Issue: "Admin user not created"
```bash
python manage.py createsuperuser
```

---

## 💾 Keeping SQLite as Backup

### Option A: Keep SQLite file
```bash
# SQLite stays in local repo
# Good for offline development
cp db.sqlite3 db.sqlite3.backup
```

### Option B: Switch back temporarily
```bash
# Edit settings.py (comment out PostgreSQL, enable SQLite)
# Edit .env (comment out DATABASE_URL)
# Run: python manage.py runserver

# Django automatically detects SQLite
```

---

## 🔒 Security Best Practices

### ✅ DO
```bash
# Store in .env (gitignored)
DATABASE_URL=postgresql://...
SECRET_KEY=your-secret-key
OPENAI_API_KEY=sk-...

# Never commit .env
echo ".env" >> .gitignore
```

### ❌ DON'T
```bash
# ❌ Hardcode in settings.py
DATABASES = {'default': {'PASSWORD': 'exposed!'}}

# ❌ Commit to Git
git add .env  # DON'T DO THIS

# ❌ Share with others
# Never share DATABASE_URL or passwords
```

---

## 📈 Monitoring Your Database

### Check Storage Usage
```bash
# In Supabase Dashboard:
# Settings → Database → Statistics
# Shows: Storage used / Total available
```

### Check Connections
```bash
# In Supabase Dashboard:
# Settings → Database → Statistics
# Shows: Active connections
```

### Monitor Costs
```bash
# Supabase free tier:
# 500MB storage (usually enough for SIEM testing)
# 5GB bandwidth per month
# No costs unless you exceed free tier

# View usage:
# Billing → Usage
```

---

## 🚀 Advanced: Backup & Restore

### Automatic Backups
Supabase automatically backs up daily:
```bash
# In Supabase Dashboard:
# Settings → Backups
# View backup history
# Restore from backup (if needed)
```

### Manual Backup
```bash
# Export all data to SQL
pg_dump postgresql://user:pass@host:5432/db > backup.sql

# Or in Supabase:
# SQL Editor → "..." menu → Download backup
```

### Restore Backup
```bash
# Run SQL file
psql postgresql://user:pass@host:5432/db < backup.sql
```

---

## 🔄 Migration Checklist

- [ ] Create Supabase project
- [ ] Get connection string
- [ ] Create `.env` file from `.env.example`
- [ ] Add `DATABASE_URL` to `.env`
- [ ] Run `pip install -r requirements.txt`
- [ ] Run `python manage.py migrate`
- [ ] Run `python manage.py createsuperuser`
- [ ] Run `python manage.py populate_sample_data`
- [ ] Test with: `python manage.py dbshell`
- [ ] Start server: `python manage.py runserver`
- [ ] Access admin: `http://localhost:8000/admin/`
- [ ] Test API endpoints
- [ ] Verify data in Supabase dashboard

---

## 💡 Pro Tips

### Tip 1: Test Before Going Live
```bash
# Use free Supabase tier for testing
# No risk, just switch back to SQLite if needed
```

### Tip 2: Keep .env Secure
```bash
# In .gitignore:
.env
.env.local
.env.*.local

# Never commit secrets!
```

### Tip 3: Use Environment-Specific Config
```bash
# Development: DATABASE_URL points to Supabase dev project
# Staging: DATABASE_URL points to Supabase staging project
# Production: DATABASE_URL points to Supabase prod project
```

### Tip 4: Monitor Connection Limits
```bash
# Free tier: 4 concurrent connections
# For production, upgrade to higher tier
# Check current connections in Supabase dashboard
```

---

## 📞 Getting Help

If you get stuck:

1. **Check Django Logs**
   ```bash
   python manage.py runserver 2>&1 | tee server.log
   ```

2. **Check Database Connection**
   ```bash
   python manage.py dbshell
   # Should open psql prompt
   \dt  # List tables
   \q   # Exit
   ```

3. **Check Supabase Status**
   ```bash
   # Visit: https://status.supabase.com
   # Check if platform is operational
   ```

4. **Reset Everything**
   ```bash
   # If completely stuck:
   # 1. Delete all migrations (except 0001)
   # 2. Run: python manage.py migrate --fake
   # 3. Run: python manage.py migrate
   # 4. Create superuser again
   ```

---

## 🎯 Result

After migration, you have:

✅ **Cloud Database**
- PostgreSQL in the cloud
- Accessible from anywhere
- Automatic backups
- Easy scaling

✅ **Same Django App**
- No code changes needed
- Same models, views, APIs
- Drop-in replacement

✅ **Faster Performance**
- PostgreSQL is faster than SQLite for concurrent access
- Better for teams
- Production-ready

✅ **Better Collaboration**
- Multiple developers can access same database
- Real-time data sharing
- No file conflicts

---

## 🎉 You're Done!

Your SIEM is now running on Supabase! 

**Next steps:**
1. Load real security data
2. Configure detection rules
3. Set up monitoring
4. Integrate with tools like Slack, PagerDuty
5. Deploy to production

**Questions?** See: [SUPABASE_SETUP_GUIDE.md](SUPABASE_SETUP_GUIDE.md)
