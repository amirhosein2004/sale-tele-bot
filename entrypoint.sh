#!/bin/bash
set -e

echo "================================"
echo "🤖 Telegram Bot Startup"
echo "================================"
echo ""

# بررسی environment variable
CREATE_MIGRATIONS="${CREATE_MIGRATIONS:-false}"

if [ "$CREATE_MIGRATIONS" = "true" ] || [ "$CREATE_MIGRATIONS" = "1" ]; then
    echo "🔄 Cleaning up old migration history..."
    # پاک کردن جدول alembic_version اگر وجود داشته باشد
    PGPASSWORD="$POSTGRES_PASSWORD" psql -h "$POSTGRES_HOST" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "DROP TABLE IF EXISTS alembic_version;" 2>/dev/null || true
    
    echo "🔄 Creating migration..."
    alembic revision --autogenerate -m "create_initial_tables" || true
    
    echo "📤 Applying migrations..."
    alembic upgrade head
    
    echo "✅ Migrations completed"
else
    echo "⏭️ Skipping migrations (set CREATE_MIGRATIONS=true to enable)"
fi

echo ""
echo "🚀 Starting bot..."
echo "================================"
python -m src.main
