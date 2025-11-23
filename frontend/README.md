SIEM Dashboard frontend

This is a small Create-React-App-style frontend skeleton for a SIEM dashboard. It uses mocked data in `src/services/api.js`.

Quick start (after creating a virtualenv / backend as you prefer):

1. Install Node dependencies

```bash
cd my-django-project/frontend
npm install
```

2. Start dev server

```bash
npm start
```

What to replace for production:
- Replace `src/services/api.js` with real API calls to your backend.
- Add authentication, role-based UI, and proper error handling.

Recommended backend alternatives (short rationale):

- Django (what you mentioned): full-featured, great admin, batteries-included. Good if you want a monolithic app with ORM and admin UI.
- FastAPI (Python): async-first, very fast, great for building APIs, automatic OpenAPI docs. Good if you need performant JSON APIs and async IO for log ingestion.
- Node.js + Express / NestJS: massive ecosystem, realtime-friendly (WebSockets). Use NestJS for structure and TypeScript.
- Go (Gin, Fiber): extremely performant, low memory footprint; great for high throughput ingestion and long-running processes.

For SIEM workloads you may want async ingestion pipelines (Kafka, NATS) and a time-series / search datastore (Elasticsearch, ClickHouse, TimescaleDB). For now, this frontend uses mocked data so you can iterate on UI.
