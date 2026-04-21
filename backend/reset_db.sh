#!/bin/bash
# Navigate to the script's directory (should be backend/)
cd "$(dirname "$0")"

echo "🧹 Cleaning up stale database and migrations..."
rm -f db.sqlite3
rm -rf requirements_app/migrations/
mkdir -p requirements_app/migrations
touch requirements_app/migrations/__init__.py

echo "📝 Generating fresh migrations..."
python manage.py makemigrations

echo "🚀 Applying migrations to database..."
python manage.py migrate

echo "✅ Database reset complete!"
echo "You can now create your superuser by running:"
echo "python manage.py createsuperuser"
