#!/bin/sh

# Configuration
BACKUP_DIR="/backups"
DB_NAME="${POSTGRES_DB:-bot_db}"
DB_USER="${POSTGRES_USER:-postgres}"
DB_HOST="postgres"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"
LATEST_BACKUP="$BACKUP_DIR/backup_latest.sql"
MAX_BACKUPS=10

# Create directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting database backup at $TIMESTAMP..."

# Take backup
PGPASSWORD="$POSTGRES_PASSWORD" pg_dump -h "$DB_HOST" -U "$DB_USER" -d "$DB_NAME" > "$BACKUP_FILE"

if [ $? -eq 0 ]; then
    echo "✅ Backup successful: $BACKUP_FILE"
    
    # Create link to latest backup
    ln -sf "$BACKUP_FILE" "$LATEST_BACKUP"
    
    # Remove older backups (keep only the last 10)
    ls -t "$BACKUP_DIR"/backup_*.sql 2>/dev/null | tail -n +$((MAX_BACKUPS + 1)) | xargs -r rm
    echo "🧹 Old backups removed (maximum $MAX_BACKUPS versions kept)"
else
    echo "❌ Error in backup"
    exit 1
fi
