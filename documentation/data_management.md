# Rebaden SIEM Data Management Guide

This document outlines how data flows through the Rebaden SIEM platform, detailing the ingestion, storage, cleaning, and deletion processes. Understanding these mechanisms is essential for maintaining standard operating procedures and keeping the platform performant.

## 1. Data Ingestion
Rebaden SIEM ingests data directly via the backend endpoints or manual uploads.
- **API Ingestion (`/api/v1/logs/`)**: External systems and forwarders push JSON payloads containing structured event data straight into the SIEM.
- **Web UI Upload (`/logs/`)**: Analysts can manually ingest historical CSV or line-delimited log files using the web interface, which processes them and creates `Event` records directly.
- **Anomaly Signals**: The UEBA and ML systems continuously analyze user behavior, generating automated `AnomalyDetection` records directly when a baseline deviation is triggered.

## 2. Data Storage
Rebaden SIEM relies on Django's ORM linked to its primary database backend.
- **Local Environment:** When spinning up locally without specific environment variables, the system defaults to **SQLite (`db.sqlite3`)**. This is stored at the root of the `backend/` directory.
- **Production Environment:** Driven by the `DATABASE_URL` environment variable, production data is securely pooled in **Supabase (PostgreSQL)**, providing robust scalability for thousands of event rows.
- The bulk of data growth occurs in the `core_event` (raw logs) and `core_alert` (system detected threats) tables.

## 3. Data Cleaning
Keeping the SIEM fast requires regular data grooming to ensure old logs do not bottleneck the database.
- **Database Limits:** PostgreSQL is highly efficient, but older `Event` rows that are no longer needed (e.g., beyond organizational retention policy, such as 90 days) should be cleared. 
- **Admin Panel Cleaning:** Users with superuser privileges can utilize the built-in custom Admin Panel (`/admin-panel/`) or the default Django admin (`/admin/`) to bulk-select and delete old incidents or alerts.
- **Automated Retention (Future):** Current cleaning relies on manual curation or direct SQL queries. Best practice dictates implementing a scheduled Celery task to prune `Event` rows older than 90 days automatically.

## 4. Deleting Data
There are instances where specific data must be completely erased:
- **Individual Deletion:** Through the Django admin interface (`/admin/`), you can select specific `Event`, `Alert`, or `Investigation` records and execute the "Delete selected" action.
- **Complete Archival / Wipes:** If transitioning environments or clearing test data, the most thorough process is to wipe the database locally by deleting `db.sqlite3` and running `python manage.py migrate` to generate a fresh database. In production (Supabase), execute an SQL `TRUNCATE core_event CASCADE;` query through the Supabase console.
- **Caution:** Deleting an `Event` cascadingly drops associated context from its alerts or MITRE mappings. Always back up the database before doing mass deletions.
