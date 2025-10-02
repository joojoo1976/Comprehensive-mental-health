Development setup
=================

This project uses a FastAPI backend with SQLAlchemy and a Postgres database. The goal is to support multiple frontends (Android, iOS, web, desktop) all using a single shared database.

Quick start with Docker Compose
-------------------------------
1. Copy the example env file and edit values you need:

   - Copy `.env.example` to `.env` and set `SECRET_KEY` and any DB credentials you want.

2. Start services:

```bash
# from repository root (Windows PowerShell)
docker compose up --build
```

3. The backend will be available at http://localhost:8000 and the OpenAPI docs at http://localhost:8000{API_PREFIX}/openapi.json (for example http://localhost:8000/api/v1/openapi.json)

Notes and next steps
--------------------
- The backend config reads environment variables from `.env` via `pydantic_settings`. The `DATABASE_URL` env var should point to the Postgres service when running in Docker. Example: `postgresql://user:password@db/mental_health_db`.

- Single shared database: the backend already uses SQLAlchemy and Postgres by default (see `app/config.py`). All frontends (Android native, a new Flutter app, web frontend) should call the same REST API / websockets and therefore share the same DB.

- Frontend recommendation: use Flutter for a consolidated cross-platform client that targets Android, iOS, web, and desktop (Windows/macOS/Linux). This will avoid maintaining separate native codebases. Alternatively, you can keep the existing native Android app and build a Flutter/ReactNative iOS client or a web/desktop client separately.

- To add a Flutter frontend (high level):
  1. Install Flutter (https://flutter.dev/docs/get-started/install)
  2. Create a new Flutter project in `frontend/flutter_app`
  3. Implement an API client that authenticates against the FastAPI endpoints and stores tokens securely on the device
  4. Reuse the same backend API for all platforms

- I can scaffold a minimal Flutter project and a simple API client if you want. This is a larger change so I recommend doing it as a separate task.

Troubleshooting
---------------
- If you run into permission/volume issues on Windows with Docker, try running PowerShell as Administrator or use WSL2-based Docker engine.

Security
--------
- Do NOT use the example secrets/credentials in production. Use a secrets manager or environment-specific configs.

