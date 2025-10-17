### Quick orientation

This repository is a bilingual (Arabic/English) FastAPI backend and Android frontend monorepo focused on a mental-health platform. The API server lives under `app/` and uses SQLAlchemy models in `app/models/`, Pydantic schemas in `app/schemas/`, and standard FastAPI routers under `app/api/`. The Android project and frontend assets are in `app/` (Android build files) and `frontend/`.

Keep answers concise and actionable. When proposing code changes reference the exact path (for example `app/models/user.py` or `app/schemas/user.py`).

### Architecture & important files

- Entry point: `app/main.py` — FastAPI app, middleware, templates, and mounts. Startup creates initial data (`app/core/initial_data.py`) and (in dev) database tables via `app/core/database.py`.
- Configuration: `app/config.py` and `app/config_new.py` — Pydantic settings load from `.env`. Use `settings` for runtime flags (e.g. `settings.auto_create_db`, `settings.api_prefix`).
- Database: `app/core/database.py` — SQLAlchemy engine, Base, `SessionLocal`. `create_tables()` is a dev helper.
- Cache & events: `app/core/events.py` — SQLAlchemy event listeners invalidate per-user cache when roles/permissions change. Cache service is in `app/core/cache.py` (used by listeners).
- API auth/deps: `app/api/deps.py` — `get_db`, `get_current_user`, `get_current_admin_user`. OAuth2 token flow expected under `api/v1/auth`.
- CRUD layer: `app/crud.py` — example CRUD helpers for users. Follow its patterns for DB access (use `db.commit()` then `db.refresh(obj)`).
- Models & Schemas: `app/models/*.py` and `app/schemas/*.py` — models use SQLAlchemy relationships; schemas use Pydantic with orm_mode enabled.

### Conventions and patterns to follow

- Database sessions: prefer `SessionLocal()` via dependency (`get_db`/`app/core/database.py`) and always close sessions. Use `db.add()`, `db.commit()`, `db.refresh()` pattern.
- Cache invalidation: changes to `User.role_id` or `Role.permissions` trigger cache invalidation via SQLAlchemy event listeners in `app/core/events.py`. If you add models that affect permissions, wire similar listeners.
- Config & secrets: runtime config comes from `app/config.py` (`settings`) which reads `.env`. Avoid hardcoding secrets; prefer env vars.
- Language: many files include Arabic comments and default values (e.g., `language = 'ar'`). Preserve or mirror i18n patterns when adding strings.
- File locations: static files and templates are mounted from `app/static` and `app/templates` in `app/main.py`. If adding assets, update the mounted dirs.

### Build, run, test & developer workflows

- Run the backend locally (dev): use the module entry in `app/main.py` (uvicorn is used). Typical run in dev uses:

  - `uvicorn app.main:app --reload --port 8000` (or run `app/main.py` directly as the repo demonstrates)

- DB setup: in development `settings.auto_create_db=True` will call `create_tables()` at startup. For production use Alembic under `alembic/` (migration scripts live in `alembic/versions/`).
- Android build: Android build helper in repository root uses `gradlew`/`gradlew.bat` (see `build.bat`). Use Android Studio/Gradle for app builds.
- Tests: project lists `pytest` and `httpx` in `requirements.txt`. Run tests with `pytest` — add `pytest-asyncio` for async tests.

### Integration points & external dependencies

- PostgreSQL (via `psycopg2-binary`) — configured with `settings.database_url`.
- Redis — `settings.redis_url` and `app/core/cache.py` for caching.
- Email (SMTP) — configured via settings (`smtp_server`, `smtp_port`, `smtp_username`, `smtp_password`).
- Machine learning / LLM integrations — `openai`, `langchain`, `transformers` present in `requirements.txt`. Example config keys: `OPENAI_API_KEY`, `MODEL_NAME`.
- WebRTC — `aiortc` listed and `webrtc_server_url` present in settings.

### Safety and guardrails for AI agents

- Always: reference and modify only files under `app/` unless the user explicitly asks to touch Android or `frontend/` code.
- Do not commit secrets. If adding samples, use placeholders and document required env vars in `.env.example` (create if missing).
- Prefer minimal, reversible changes. For DB-affecting code, add migrations under `alembic/` rather than calling `create_all` in production code.

### Examples for common edits

- Adding an endpoint that needs DB + auth: follow `app/api/deps.py` for `get_db` and `get_current_user`, add router under `app/api/api_v1/`, add Pydantic schema in `app/schemas/`, and a model in `app/models/` if needed. Mirror `app/crud.py` for DB operations.
- Adding cache-sensitive model fields: update `app/core/events.py` to include invalidation logic for the new field.

### Files to check when making changes

- app/main.py, app/config.py, app/core/database.py, app/core/events.py, app/core/cache.py, app/crud.py, app/models/, app/schemas/, alembic/

If anything above is unclear or you'd like me to expand any section with concrete code-edit examples, tell me which area to expand and I will iterate.

### Example: add an auth-protected endpoint (DB + cache invalidation)

Follow these concrete steps when adding a new endpoint that requires DB access and may affect cached permissions/data:

1. Add a Pydantic schema in `app/schemas/` (e.g., `app/schemas/new_feature.py`) with `orm_mode = True` when returning ORM models.
2. (Optional) Add or modify a SQLAlchemy model under `app/models/` if the endpoint requires a new table.
3. Add CRUD helpers in `app/crud.py` (follow existing patterns):
  - Use `db.add(obj)`, then `db.commit()` and `db.refresh(obj)` to persist and return objects.
4. Add a router under `app/api/api_v1/` (create a file and register it in `app/api/api_v1/api.py`):
  - Use dependencies from `app/api/deps.py` to get DB and current user: `db: Session = Depends(get_db)` and `current_user: User = Depends(get_current_user)`.
  - Example handler signature: `async def create_item(item_in: schemas.ItemCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_user)):`
5. If this endpoint changes role/permission-sensitive data (for example writes to `Role.permissions` or `User.role_id`), add/invoke cache invalidation:
  - Prefer making DB changes via CRUD helpers so `app/core/events.py` listeners pick up changes automatically. If you must bypass patterns, call `cache_service.invalidate_user(user_id)` from `app/core/cache.py` after commit.
6. Write tests under `tests/` using `pytest` and `httpx` to validate auth, happy-path, and one permission edge case.

### Suggested integrations to document (common for this repo)

- Sentry (optional): add `sentry-sdk` and initialize in `app/main.py` (early, before `setup_logging()`). Document `SENTRY_DSN` in `.env.example` when enabled.
- CI / CD: repository has GitHub Actions workflows in `.github/workflows/`. For deployment, prefer building backend Docker image and applying DB migrations via Alembic before traffic cutover. Add a workflow step that runs `alembic upgrade head` against the production DB (use secrets).
- Monitoring & feature flags: if used, add initialization in `app/main.py` and document required envs.

### .env example

See repository root file `.env.example` for the environment variables expected by the application. Keep secrets out of commits; use GitHub Secrets or your cloud provider's secret store for CI/CD.
