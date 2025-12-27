#!/bin/bash
set -e

echo "🚀 Starting ClarityAP Backend..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
while ! pg_isready -h db -U postgres; do
  sleep 1
done
echo "✅ PostgreSQL is ready!"

# Run database migrations
echo "📦 Running database migrations..."
alembic upgrade head
echo "✅ Migrations complete!"

# Create storage directory
mkdir -p ./storage/invoices
echo "✅ Storage directory ready!"

# Start the application
echo "🎉 Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
