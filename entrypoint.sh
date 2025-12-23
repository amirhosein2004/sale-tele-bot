#!/bin/bash
set -e

echo "Running Alembic migrations..."
alembic revision --autogenerate -m "create_initial_tables" || true
alembic upgrade head

echo "Migrations completed. Starting bot..."
python -m src.main
