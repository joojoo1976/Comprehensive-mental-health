#!/usr/bin/env bash
set -e

# Wait for the DB to be ready
host=$(echo "$DATABASE_URL" | sed -E 's|.*@([^:/]+).*|\1|')
port=$(echo "$DATABASE_URL" | sed -E 's|.*:([0-9]+)/.*|\1|')

# default ports
host=${host:-db}
port=${port:-5432}

until nc -z $host $port; do
  echo "Waiting for database at $host:$port..."
  sleep 1
done

# Run Alembic migrations
alembic upgrade head

# Continue with the main process (passed as arguments)
exec "$@"
