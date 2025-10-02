Alembic migrations

To generate a new migration after changing models:

1. Set `DATABASE_URL` in your environment or in `.env`.
2. Run:

   alembic revision --autogenerate -m "describe change"

3. Review and edit the generated migration file then apply it:

   alembic upgrade head

