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
python manage.py migrate --noinput

exec "$@"