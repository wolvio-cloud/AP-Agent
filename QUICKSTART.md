# ClarityAP Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- PostgreSQL 15+
- Redis 7+

---

## 📦 Installation

### 1. Clone and Setup Environment

```bash
# Navigate to project
cd /path/to/AP-Agent

# Copy environment template
cp clarity-api/.env.example clarity-api/.env

# Edit .env with your settings
nano clarity-api/.env
```

### 2. Required Environment Variables

```bash
# Database
DATABASE_URL=postgresql://postgres:password@localhost:5432/clarityap

# JWT (Generate with: openssl rand -base64 32)
SECRET_KEY=your-generated-secret-key-here

# Redis
REDIS_URL=redis://localhost:6379/0

# Google Cloud (for production)
GCS_BUCKET_NAME=clarityap-invoices
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Optional: CMEK Encryption (SOC 2 Enhanced)
# GCS_KMS_KEY_NAME=projects/my-project/locations/us/keyRings/clarityap/cryptoKeys/invoice-encryption

# Gemini AI
GEMINI_API_KEY=your-gemini-api-key
```

---

## 🐳 Start with Docker Compose (Recommended)

### Start All Services
```bash
docker-compose up -d
```

This starts:
- PostgreSQL (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Celery worker
- Celery beat
- Flower monitoring (port 5555)

### Check Service Status
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f api
docker-compose logs -f worker
```

---

## 🗄️ Database Setup

### Run Migrations
```bash
# Inside API container
docker-compose exec api alembic upgrade head

# Or locally
cd clarity-api
alembic upgrade head
```

### Create First Organization & User
```bash
# Use the API or database directly
# Example SQL:
psql $DATABASE_URL

INSERT INTO organizations (id, name)
VALUES (gen_random_uuid(), 'My Company');

INSERT INTO users (id, organization_id, email, hashed_password, full_name, is_active)
VALUES (
  gen_random_uuid(),
  (SELECT id FROM organizations LIMIT 1),
  'admin@example.com',
  'hashed_password_here',  -- Use /api/v1/auth/register endpoint instead
  'Admin User',
  true
);
```

**Better:** Use the registration API:
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "full_name": "Admin User",
    "organization_name": "My Company"
  }'
```

---

## 🧪 Test the APIs

### 1. Login
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=SecurePass123!"

# Save the access_token from response
export TOKEN="your-access-token-here"
```

### 2. Upload Invoice
```bash
curl -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/invoice.pdf"

# Response includes task_id for background processing
{
  "id": "invoice-uuid",
  "task_id": "celery-task-uuid",
  "status": "processing"
}
```

### 3. Check Task Status
```bash
curl http://localhost:8000/api/v1/tasks/{task_id}/status \
  -H "Authorization: Bearer $TOKEN"

# Response shows progress
{
  "task_id": "abc123",
  "state": "PROCESSING",
  "status": "Extracting data...",
  "progress": 75
}
```

### 4. Get Dashboard Analytics
```bash
curl http://localhost:8000/api/v1/analytics/dashboard?days=30 \
  -H "Authorization: Bearer $TOKEN"
```

### 5. List Vendors
```bash
curl "http://localhost:8000/api/v1/vendors?search=acme" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🔍 Monitoring

### Flower UI (Task Monitoring)
```bash
# Open in browser
open http://localhost:5555

# Or
http://localhost:5555
```

View:
- Active tasks
- Worker status
- Task history
- Queue depths
- Success/failure rates

### API Documentation
```bash
# Swagger UI
open http://localhost:8000/docs

# ReDoc
open http://localhost:8000/redoc
```

---

## 🛠️ Development Mode

### Without Docker

```bash
# Terminal 1: Start PostgreSQL & Redis
brew services start postgresql
brew services start redis

# Terminal 2: Start FastAPI
cd clarity-api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Terminal 3: Start Celery Worker
cd clarity-api
celery -A app.celery_app worker --loglevel=info -Q extraction,validation,notifications,exports,analytics

# Terminal 4: Start Celery Beat
cd clarity-api
celery -A app.celery_app beat --loglevel=info

# Terminal 5: Start Flower
cd clarity-api
celery -A app.celery_app flower --port=5555
```

---

## 🔐 RBAC Setup

### Initialize System Roles
```python
from app.services.rbac_service import initialize_system_roles
from app.core.database import SessionLocal

db = SessionLocal()
org_id = "your-org-uuid"

# Creates Admin, Approver, Accountant, Viewer roles
initialize_system_roles(db, org_id)
```

### Assign Role to User
```bash
curl -X POST http://localhost:8000/api/v1/users/{user_id}/role \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "role_id": "role-uuid"
  }'
```

### Create Custom Role
```bash
curl -X POST http://localhost:8000/api/v1/roles \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Finance Manager",
    "description": "Can manage invoices up to $10K",
    "permissions": {
      "invoices.view": true,
      "invoices.create": true,
      "invoices.approve": true,
      "vendors.view": true,
      "reports.view": true
    }
  }'
```

---

## 📋 Approval Workflows

### Create Workflow
```bash
curl -X POST http://localhost:8000/api/v1/workflows \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Standard Approval ($1K-$10K)",
    "description": "Two-level approval for mid-range invoices",
    "conditions": {
      "min_amount": 1000,
      "max_amount": 10000
    },
    "steps": [
      {
        "approvers": ["manager-user-id"],
        "timeout_hours": 48,
        "escalate_to": ["director-user-id"]
      },
      {
        "approvers": ["finance-user-id"],
        "timeout_hours": 24
      }
    ],
    "priority": 10
  }'
```

### Approve/Reject Invoice
```bash
# Approve
curl -X POST http://localhost:8000/api/v1/approvals/{approval_id}/respond \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "notes": "Looks good, approved"
  }'

# Reject
curl -X POST http://localhost:8000/api/v1/approvals/{approval_id}/respond \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "rejected",
    "notes": "Missing required documentation"
  }'
```

---

## 🐛 Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
docker-compose ps db

# Check connection
docker-compose exec db psql -U postgres -c "SELECT version();"

# View logs
docker-compose logs db
```

### Redis Connection Issues
```bash
# Check Redis is running
docker-compose ps redis

# Test connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# View logs
docker-compose logs redis
```

### Celery Worker Not Processing
```bash
# Check worker status
docker-compose ps worker

# View worker logs
docker-compose logs -f worker

# Check Flower UI
open http://localhost:5555

# Restart worker
docker-compose restart worker
```

### Task Stuck in Queue
```bash
# Check task status in Flower
open http://localhost:5555/tasks

# Cancel task via API
curl -X POST http://localhost:8000/api/v1/tasks/{task_id}/cancel \
  -H "Authorization: Bearer $TOKEN"

# Or purge all tasks (DANGER - development only)
docker-compose exec worker celery -A app.celery_app purge
```

---

## 🧹 Cleanup

### Stop Services
```bash
docker-compose down
```

### Stop and Remove Volumes
```bash
docker-compose down -v
```

### Clean Everything
```bash
docker-compose down -v --remove-orphans
docker system prune -a
```

---

## 📚 Additional Resources

- **Full Documentation:** `SCALABILITY_SECURITY_IMPLEMENTATION.md`
- **API Docs:** http://localhost:8000/docs
- **Flower Monitoring:** http://localhost:5555
- **Alembic Migrations:** `clarity-api/alembic/versions/`
- **Service Code:** `clarity-api/app/services/`
- **API Routes:** `clarity-api/app/api/v1/`

---

## ✅ Production Deployment Checklist

Before going to production:

- [ ] Generate secure SECRET_KEY
- [ ] Configure production DATABASE_URL
- [ ] Set up managed Redis (AWS ElastiCache, GCP Memorystore)
- [ ] Configure GCS with CMEK encryption
- [ ] Set up email service (SendGrid, AWS SES)
- [ ] Configure domain and SSL certificates
- [ ] Set up monitoring (Datadog, New Relic, Sentry)
- [ ] Run security audit
- [ ] Load testing
- [ ] Database backups configured
- [ ] Set up CI/CD pipeline
- [ ] Configure CORS for production frontend
- [ ] Review and set appropriate rate limits
- [ ] Configure Flower authentication
- [ ] Set up log aggregation (ELK, CloudWatch)
- [ ] Document runbooks for common issues

---

## 🎉 You're Ready!

Your ClarityAP instance is now running with:
- ✅ Background processing (Celery + Redis)
- ✅ SOC 2 compliance features
- ✅ RBAC with granular permissions
- ✅ Approval workflows
- ✅ Analytics dashboard
- ✅ Vendor management
- ✅ Comprehensive audit logging
- ✅ Encryption at rest

**Next Steps:**
1. Register your first user
2. Upload a test invoice
3. Configure approval workflows
4. Assign roles to team members
5. Review analytics dashboard

Happy coding! 🚀
