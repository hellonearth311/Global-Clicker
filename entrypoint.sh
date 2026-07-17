#!/bin/sh
set -e

echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
python <<'PY'
import os, time, socket

host = os.environ.get("DB_HOST", "localhost")
port = int(os.environ.get("DB_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        time.sleep(1)
else:
    raise SystemExit(f"Database at {host}:{port} not reachable")
PY

echo "Applying migrations..."
python <<'PY'
import os, subprocess
import psycopg2

conn = psycopg2.connect(
    dbname=os.environ["DB_NAME"],
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    host=os.environ["DB_HOST"],
    port=os.environ["DB_PORT"],
)
conn.autocommit = True
with conn.cursor() as cur:
    # Serializes `migrate` across the web and worker containers, which start
    # concurrently and would otherwise race to create the same tables.
    cur.execute("SELECT pg_advisory_lock(727272)")
    try:
        subprocess.run(["python", "manage.py", "migrate", "--noinput"], check=True)
        subprocess.run(["python", "manage.py", "createcachetable"], check=True)
    finally:
        cur.execute("SELECT pg_advisory_unlock(727272)")
conn.close()
PY

exec "$@"