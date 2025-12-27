# 🚀 ClarityAP - Quick Reference

## One-Line Setup (Docker)

```bash
git pull && docker-compose down && docker-compose up --build -d
```

## Check Status

```bash
# All services
docker-compose ps

# Backend logs
docker-compose logs -f api

# Database
docker exec -it ap-agent-db-1 psql -U postgres -d clarity -c "\dt"
```

## URLs

- **Backend API**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **Health Check**: http://localhost:8000/health

## Common Commands

### Docker

```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Rebuild and restart
docker-compose up --build -d

# View logs
docker-compose logs -f

# Shell into backend container
docker exec -it ap-agent-api-1 bash

# Database shell
docker exec -it ap-agent-db-1 psql -U postgres -d clarity
```

### Backend (Local)

```bash
cd clarity-api

# Activate venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Run migrations
alembic upgrade head

# Start server
uvicorn app.main:app --reload

# Create migration
alembic revision --autogenerate -m "description"
```

### Frontend

```bash
cd clarity-web

# Clear cache and start
rm -rf .next && npm run dev

# Build for production
npm run build && npm start
```

## Quick Test

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!","first_name":"John","last_name":"Doe","company_name":"Test Co"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test123!"}'

# Health
curl http://localhost:8000/health
```

## Environment Files

### Backend `.env` (Docker)
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/clarity
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Backend `.env.local` (Local)
```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clarity
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
BACKEND_CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend `.env.local`
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting One-Liners

```bash
# Full Docker reset
docker-compose down -v && docker system prune -f && docker-compose up --build -d

# Reset database
docker exec -it ap-agent-db-1 psql -U postgres -d clarity -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Clear frontend cache
rm -rf clarity-web/.next clarity-web/node_modules/.cache

# Rebuild backend
docker-compose build --no-cache api && docker-compose up -d api

# Check disk space
docker system df
```

## Database Quick Queries

```sql
-- List all tables
\dt

-- Count users
SELECT COUNT(*) FROM users;

-- Count invoices
SELECT COUNT(*) FROM invoices;

-- View organizations
SELECT id, name, slug FROM organizations;

-- Delete test data
DELETE FROM invoices WHERE created_at < NOW() - INTERVAL '1 day';
```

## Files Modified in Latest Update

```
✅ clarity-api/app/api/v1/invoices_simple.py  (line 19)
✅ clarity-api/app/api/v1/vendors.py           (line 16)
✅ clarity-api/app/api/v1/quickbooks.py        (line 18)
✅ clarity-api/app/api/v1/analytics.py         (line 16)
✅ clarity-api/app/services/extraction_service.py (added extract_invoice_data)
✅ clarity-api/Dockerfile                      (new)
✅ clarity-web/Dockerfile                      (new)
✅ clarity-api/.env                            (updated)
✅ clarity-api/.env.local                      (new)
✅ clarity-api/.env.example                    (updated)
```

## Git Workflow

```bash
# Pull latest
git pull

# Check status
git status

# View recent commits
git log --oneline -5

# Reset to specific commit
git reset --hard <commit-hash>

# Discard local changes
git reset --hard HEAD
```

## Production Checklist

- [ ] Change `SECRET_KEY` to random 32+ char string
- [ ] Set `ENVIRONMENT=production`
- [ ] Configure HTTPS/TLS
- [ ] Set real `GEMINI_API_KEY`
- [ ] Configure GCS with proper credentials
- [ ] Enable GCS CMEK encryption
- [ ] Set up proper backup strategy
- [ ] Configure monitoring/alerting
- [ ] Review CORS origins
- [ ] Set up rate limiting
- [ ] Enable API authentication
- [ ] Configure logging to external service
