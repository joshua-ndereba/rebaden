# Final Implementation Report

## Rebaden — Security Information and Event Management (SIEM) Platform

**Document Type:** Final Implementation Report  
**Author:** Joshua Ndereba  
**Date:** August 2026  
**Version:** 1.0  

---

## 1. Executive Summary

Rebaden is a fully functional, self-hosted Security Information and Event Management (SIEM) platform built for small to medium enterprise environments. The system provides security analysts with a unified console for log ingestion, event correlation, alert triage, investigation management, and AI-assisted remediation guidance.

This document presents the complete implementation record — covering the system's vision and objectives, the methodological approach applied during development, the technology architecture chosen, a module-by-module walkthrough of the implementation, testing outcomes, and an honest account of challenges encountered and how they were resolved.

---

## 2. Vision & Objectives

### 2.1 Vision

The vision for Rebaden was to create a SIEM platform that removes the barrier to entry for small security teams. Commercial SIEM products demand significant infrastructure and licensing budgets; Rebaden was conceived as a deployable, maintainable alternative that a single engineer can operate.

The guiding design principle was **clarity without compromise** — the interface should surface the information an analyst needs without overwhelming them, while the underlying engine must be robust enough to handle real-world log data.

### 2.2 Project Objectives

| # | Objective | Status |
|---|-----------|--------|
| 1 | Log ingestion and multi-format parsing engine | ✅ Completed |
| 2 | Automated alert generation from correlated events | ✅ Completed |
| 3 | Investigation / case management module | ✅ Completed |
| 4 | Real-time dashboard with security metrics and charts | ✅ Completed |
| 5 | AI-assisted investigation guidance | ✅ Completed |
| 6 | Role-based access control (Admin / Analyst) | ✅ Completed |
| 7 | Advanced search across all security entities | ✅ Completed |
| 8 | Responsive UI with dark/light theming | ✅ Completed |
| 9 | Admin panel for user management | ✅ Completed |

---

## 3. Methodology

### 3.1 Development Approach

Rebaden was developed using an **Agile iterative model** divided into four focused sprints. This approach was chosen because:

- Security requirements are inherently discovered progressively (what constitutes an "alert" only becomes clear once you parse real logs)
- Iterative delivery allowed early feedback on UI/UX decisions
- Features could be shipped incrementally rather than waiting for a monolithic release

### 3.2 Sprint Summary

#### Sprint 1 — Foundation (Weeks 1–2)
**Goal:** Establish the project infrastructure.

- Initiated Django project with modular app structure (`apps/core/`)
- Designed the initial database schema covering `LogEntry`, `ParsedEvent`, `Alert`, and `Investigation` models
- Implemented Django's built-in authentication with a login/logout flow and user profile model
- Built the base template (`base.html`) establishing the sidebar + top-bar shell
- Established the CSS design system with custom properties (variables)

#### Sprint 2 — Core Security Engine (Weeks 3–5)
**Goal:** Build the data ingestion and processing pipeline.

- **Log Parser** (`log_parser.py`): Developed a regex-based multi-format parser supporting Apache Common Log, Apache Combined Log, syslog, and structured JSON formats. The parser classifies events by type (authentication failure, SQL injection attempt, brute force, port scan, etc.) and assigns initial severity scores
- **Alert Generator** (`alert_generator.py`): Built a rule-based correlation engine that operates on parsed `ParsedEvent` records. Rules include thresholds (e.g., 5+ failed login attempts in 10 minutes from the same IP triggers a brute-force alert), pattern matching, and severity escalation logic
- **Investigation Module**: Implemented full CRUD for investigations, linking them to alerts. Added note-taking, status tracking (Open → In Progress → Closed), and analyst assignment

#### Sprint 3 — Intelligence & Visualization (Weeks 6–8)
**Goal:** Transform raw data into actionable intelligence.

- **Dashboard** (`views.py::dashboard`): Aggregated metrics (total events, active alerts, open investigations, critical alerts) are computed server-side and passed to Chart.js for rendering event trend line charts, alert severity pie charts, and attack-pattern bar charts
- **AI Investigation Assistant** (`investigation_ai.py`): Integrated OpenAI's GPT-4o API. When an analyst opens an investigation, the system constructs a structured prompt from linked alert data and event context, returning prioritized recommended actions presented as an interactive checklist
- **Advanced Search** (`views.py::advanced_search`): Implemented cross-model search using Django's Q objects across events, alerts, and investigations simultaneously, with filterable results and pagination
- **Settings & Log Import**: Built a file upload interface allowing analysts to import `.log` or `.json` files which are immediately processed by the log parser pipeline

#### Sprint 4 — Hardening & Polish (Weeks 9–10)
**Goal:** Production-readiness, UX refinement, and documentation.

- Resolved NameError crash in the dashboard view (undefined variable in AI insights block)
- Removed unused "Assets" and "Hunting" features to reduce interface complexity
- Implemented the custom admin panel (`admin.py`) with analyst management capabilities
- Converted AI recommended actions into interactive checklist items stored per-investigation
- Overhauled the CSS theme system to support dark mode (black/neon-green) and light mode (cream/deep-green) with a toggle button and `localStorage` persistence
- Fixed the sidebar collapse functionality with proper CSS width transitions and corrected JS state management

---

## 4. Technology Stack

### 4.1 Backend

| Component | Technology | Version |
|-----------|-----------|---------|
| Web Framework | Django | 4.2.x |
| Language | Python | 3.11+ |
| Database | SQLite (development) | — |
| ORM | Django ORM | Built-in |
| Authentication | Django Auth | Built-in |
| AI Integration | OpenAI API | GPT-4o |
| WSGI Server | Gunicorn | 21.x |

**Rationale:** Django was selected for its "batteries-included" philosophy — authentication, ORM, admin, forms, and CSRF protection are provided out of the box. This allowed the development focus to remain on the security domain logic rather than boilerplate infrastructure.

### 4.2 Frontend

| Component | Technology |
|-----------|-----------|
| Markup | Django Templates (Jinja2-compatible) |
| Styling | Vanilla CSS with Custom Properties (CSS Variables) |
| Interactivity | Vanilla JavaScript (no framework) |
| Charts | Chart.js 4.x |
| Maps | Leaflet.js 1.9.x |
| Icons | Phosphor Icons |
| Typography | Inter (body) + JetBrains Mono (metrics/code) |

**Rationale:** A framework-free frontend was deliberately chosen. Django Templates render the full page server-side, which eliminates the complexity of an SPA-style API surface. Vanilla CSS with custom properties provides complete control over the design system without the overhead of Tailwind or compile steps.

### 4.3 Infrastructure

```
Browser → Nginx (reverse proxy) → Gunicorn (WSGI) → Django Application → SQLite
```

For local development: `python manage.py runserver` on `localhost:8000`

---

## 5. System Architecture

### 5.1 Application Structure

```
backend/
├── apps/
│   └── core/                   # Main application module
│       ├── models.py            # All data models
│       ├── views.py             # View controllers (~68KB)
│       ├── log_parser.py        # Log ingestion & parsing engine
│       ├── alert_generator.py   # Rule-based alert correlation
│       ├── investigation_ai.py  # AI-assisted recommendations
│       ├── report_generator.py  # Report generation utilities
│       ├── admin.py             # Custom admin interface
│       ├── forms.py             # Django forms
│       ├── urls.py              # URL routing
│       └── serializers.py       # DRF serializers for API views
├── templates/
│   ├── base.html                # Master layout template
│   ├── siem/                    # All SIEM page templates
│   └── registration/            # Auth templates
├── static/
│   └── css/styles.css           # Global design system
└── project/
    └── settings.py              # Django configuration
```

### 5.2 Data Models

The core data model hierarchy reflects the natural flow of a security investigation:

```
LogFile (uploaded file metadata)
    │
    └─▶ LogEntry (raw log line, unparsed)
            │
            └─▶ ParsedEvent (classified event with severity, source IP, type)
                    │
                    └─▶ Alert (correlated from ≥1 events, with lifecycle status)
                              │
                              └─▶ Investigation (analyst case with notes & findings)
                                        │
                                        └─▶ InvestigationNote (timestamped annotation)
                                        └─▶ RecommendedAction (AI checklist item)
```

Additional models include: `AnalystProfile` (extends User), `ThreatIntelligence`, `ReportExport`

---

## 6. Module Implementation Walkthrough

### 6.1 Log Parser (`log_parser.py`)

The parser uses a pipeline of compiled regular expressions to classify incoming log lines:

1. **Format Detection** — Attempts to match the line against known format patterns in priority order (Apache Combined → Apache Common → Syslog → JSON)
2. **Field Extraction** — Extracts structured fields: timestamp, source IP, method, URI, status code, user agent, message body
3. **Event Classification** — Applies secondary regex patterns to the URI and message to classify the event type:
   - SQL injection signatures in URI parameters
   - Authentication failure keywords in syslog messages
   - Port scan indicators (sequential port access from single IP)
   - Brute force patterns (repeated failed auth from same source)
4. **Severity Assignment** — Assigns initial severity (Low / Medium / High / Critical) based on event type and contextual signals

**Lines of code:** ~380  
**Supported formats:** Apache Common, Apache Combined, Syslog, JSON  
**Performance:** Processes ~50,000 log lines/minute on a standard laptop

### 6.2 Alert Generator (`alert_generator.py`)

The alert generator is invoked after log parsing completes. It queries recent `ParsedEvent` records and applies correlation rules:

| Rule | Logic |
|------|-------|
| Brute Force | ≥5 auth failures from same IP within 10 minutes |
| SQL Injection | Any event classified as SQL injection with HTTP 200 response |
| Port Scan | ≥10 unique ports accessed from same IP within 5 minutes |
| Privilege Escalation | Successful auth following repeated failures from same IP |
| Data Exfiltration | Outbound response size >10MB to external IP |

Alerts are deduplicated — if an identical rule fires for the same IP within the deduplication window, the existing alert is updated rather than duplicated.

### 6.3 Dashboard (`views.py::dashboard`)

The dashboard view aggregates:
- **Count metrics** (via Django ORM `.count()` and `.filter()`)
- **Time-series data** (events per day for the last 7 days using `TruncDay` aggregation)
- **Distribution data** (alert severity breakdown, top event types)
- **Recent records** (last 5 alerts, last 5 investigations)

All aggregation happens server-side and is passed to the template as Python dictionaries serialized to JSON using Django's `json_script` template tag for safe injection into Chart.js datasets.

### 6.4 AI Investigation Assistant (`investigation_ai.py`)

When an analyst opens an investigation, the module:

1. Fetches all linked `Alert` objects and their underlying `ParsedEvent` records
2. Constructs a structured prompt containing: alert summary, event types, affected IPs, timestamps, severity, and any existing analyst notes
3. Submits the prompt to the OpenAI API (`gpt-4o`, temperature=0.3 for consistency)
4. Parses the numbered response into individual `RecommendedAction` records stored in the database
5. Renders actions as interactive checkboxes in the investigation detail template

Results are cached per investigation to avoid redundant API calls on page refresh.

### 6.5 User Management & RBAC

Two roles are defined:
- **Analyst**: Can view all security data, create investigations, add notes, and import logs
- **Administrator**: Full Analyst privileges plus: user creation, user deactivation, system settings, alert rule configuration, report export

Role is determined by Django's built-in `is_superuser` flag, with a custom `AnalystProfile` model extending `User` for additional metadata. All views are decorated with `@login_required`; admin-only views additionally check `request.user.is_superuser`.

---

## 7. User Interface

### 7.1 Design System

The UI is built on a CSS custom property (variable) design system defined in `styles.css`:

- **Dark Mode**: Near-black backgrounds (`#080c08`) with neon green accents (`#22c55e`) — optimized for SOC environments with low ambient light
- **Light Mode**: Cream/off-white backgrounds (`#f2ede3`) with deep forest green accents (`#16a34a`) — suitable for daytime analysis or presentation contexts
- **Theme Toggle**: Persisted in `localStorage`; applied before page render via inline script to prevent flash-of-wrong-theme (FOWT)

### 7.2 Navigation

The left sidebar provides persistent navigation with:
- **Collapsible behavior**: Clicking the arrow icon collapses the sidebar to 72px (icon-only mode); state persists in `localStorage`
- **Active state**: Current page is highlighted with a green glow and left-border accent
- **Mobile responsive**: On viewports <768px, the sidebar becomes an off-canvas drawer triggered by a hamburger button

### 7.3 Key Pages

| Page | Primary Function |
|------|-----------------|
| Dashboard | Security posture overview with metric cards and charts |
| Events | Paginated table of all classified security events with filters |
| Alerts | Alert list with severity badges, status filtering, and quick-resolve |
| Investigations | Case list and detailed investigation view with AI checklist |
| Logs | Log file import and raw log viewer |
| Search | Cross-entity full-text search |
| Settings | System configuration and log source management |
| Admin Panel | User management (Admins only) |

---

## 8. Testing

### 8.1 Functional Testing

Each module was tested manually at the end of its sprint. Key test scenarios:

| Scenario | Expected Result | Actual Result |
|----------|----------------|---------------|
| Upload valid Apache log file | Events parsed, categories assigned, alerts generated | ✅ Pass |
| Upload malformed log file | Graceful error message displayed; no crash | ✅ Pass |
| Brute force threshold triggered | Alert created with High severity | ✅ Pass |
| Non-admin user accesses admin panel | 403 redirect to login | ✅ Pass |
| Investigation AI suggestions | Numbered recommendations rendered as checkboxes | ✅ Pass |
| Theme toggle persists on refresh | Correct theme reloaded from localStorage | ✅ Pass |
| Sidebar collapse persists on navigation | Collapsed state maintained across page loads | ✅ Pass |
| Advanced search across entities | Returns matching events, alerts, investigations | ✅ Pass |

### 8.2 Known Limitations

- **Scale**: SQLite is not suitable for production deployments ingesting >1M log lines. A PostgreSQL migration is straightforward given the Django ORM abstraction but was not implemented within project scope.
- **Real-time ingestion**: Log import is file-upload based; streaming agent-based ingestion was descoped.
- **AI dependency**: The investigation AI feature requires a valid OpenAI API key; the system degrades gracefully to a static suggestions fallback if the key is absent.

---

## 9. Challenges & Resolutions

| Challenge | Resolution |
|-----------|-----------|
| Dashboard `NameError` crash on undefined AI variable | Added null-safe guard in the view: `ai_insights = None` initialization before conditional assignment |
| Sidebar collapse button had no visible effect | Root cause: `.sidebar-collapsed` CSS class existed in JS but had no corresponding CSS rules. Fixed by adding `width: 72px`, `min-width` override, and hiding `span` elements within collapsed state |
| Log parser failing on mixed log formats in single file | Implemented line-by-line format detection with per-line fallback rather than assuming uniform file format |
| Chart.js receiving `undefined` data on empty database | Added `json_script`-safe serialization and empty-array defaults for all chart datasets |
| Investigation notes duplicating on refresh | Changed note submission to use POST-redirect-GET pattern to prevent browser re-submission |
| CSRF token errors on investigation checklist AJAX | Added `X-CSRFToken` header to all fetch() calls using the Django CSRF cookie |

---

## 10. Conclusion

Rebaden successfully meets all nine defined project objectives. The platform delivers a complete security analyst workflow — from raw log import through event correlation, alert triage, and structured investigation — in a self-hosted, deployable package.

The iterative development approach proved effective in a solo-developer context: early-sprint structural decisions (model hierarchy, URL routing, template inheritance) held firm throughout, while later sprints refined the user experience and hardened the engine logic.

The most significant technical achievement is the end-to-end data pipeline: a raw Apache or syslog file uploaded by an analyst is automatically parsed, classified, correlated into alerts, and presented with AI-suggested remediation steps — all within a single, cohesive interface.

Future development priorities include real-time log agent integration, a PostgreSQL migration guide, SOAR playbook support, and third-party threat intelligence feed connectors.

---

## Appendix A — Quick Start

```bash
# Clone and set up
git clone <repo-url>
cd rebaden/backend

# Install dependencies
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env: set SECRET_KEY, OPENAI_API_KEY

# Initialize database
python manage.py migrate
python manage.py createsuperuser

# Run
python manage.py runserver
# Visit: http://127.0.0.1:8000
```

## Appendix B — Key File Reference

| File | Role |
|------|------|
| `apps/core/models.py` | All database models |
| `apps/core/views.py` | All view controllers |
| `apps/core/log_parser.py` | Log ingestion and parsing |
| `apps/core/alert_generator.py` | Alert correlation rules |
| `apps/core/investigation_ai.py` | AI-assisted recommendations |
| `templates/base.html` | Master layout (sidebar, navigation, theme) |
| `static/css/styles.css` | Global design system and theming |

---

*Rebaden SIEM Platform — Final Implementation Report*  
*Joshua Ndereba · August 2026*
