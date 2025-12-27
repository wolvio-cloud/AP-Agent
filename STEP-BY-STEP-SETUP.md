# 🚀 ClarityAP - Complete Setup Guide

## What Was Fixed

### ✅ Critical Fixes Applied

1. **Backend Import Errors** - Fixed `ModuleNotFoundError` in 4 files
   - Changed `from app.core.auth` → `from app.core.deps`
   - Files: `invoices_simple.py`, `vendors.py`, `quickbooks.py`, `analytics.py`

2. **Missing Service Function** - Added `extract_invoice_data()` wrapper in `extraction_service.py`

3. **Docker Support** - Created Dockerfiles for both backend and frontend

4. **Environment Configuration** - Updated `.env` files for Docker and local development

5. **Frontend Cache** - Cleared Next.js build cache

## Prerequisites

- **Docker Desktop** (recommended) OR
- **Python 3.11+** and **Node.js 18+** (for local setup)
- **PostgreSQL 15** (if running locally without Docker)

---

## Option 1: Docker Setup (Recommended - Easiest)

### Windows

```cmd
cd C:\Users\YourName\path\to\AP-Agent

:: Pull latest changes
git pull

:: Stop any old containers
docker-compose down

:: Build and start services
docker-compose up --build -d

:: Check if services are running
docker-compose ps

:: View logs
docker-compose logs -f api
```

### Mac/Linux

```bash
cd ~/path/to/AP-Agent

# Pull latest changes
git pull

# Stop any old containers
docker-compose down

# Build and start services
docker-compose up --build -d

# Check if services are running
docker-compose ps

# View logs
docker-compose logs -f api
```

### ✅ Verify Backend is Working

Open http://localhost:8000/docs - you should see:
- Swagger API documentation
- Three sections: auth, invoices, quickbooks
- Green "Authorize" button

### Start Frontend

```bash
cd clarity-web

# Delete Next.js cache
rm -rf .next node_modules/.cache  # Mac/Linux
# OR
rmdir /s /q .next                 # Windows

# Install dependencies (if needed)
npm install

# Start dev server
npm run dev
```

Open http://localhost:3000

---

## Option 2: Local Development (Without Docker)

### Step 1: Database Setup

**Option A: PostgreSQL in Docker**
```bash
docker run -d \
  --name clarityap-postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=clarity \
  -p 5432:5432 \
  postgres:15-alpine
```

**Option B: Local PostgreSQL**
- Install PostgreSQL 15
- Create database: `CREATE DATABASE clarity;`

### Step 2: Backend Setup

```bash
cd clarity-api

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate     # Mac/Linux
# OR
venv\Scripts\activate        # Windows

# Copy environment file
cp .env.local .env

# Edit .env and set:
# DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clarity

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Create storage directory
mkdir -p storage/invoices

# Start server
uvicorn app.main:app --reload
```

Backend runs at http://localhost:8000

### Step 3: Frontend Setup

```bash
cd clarity-web

# Install dependencies
npm install

# Clear cache
rm -rf .next

# Start dev server
npm run dev
```

Frontend runs at http://localhost:3000

---

## Environment Variables

### Backend (.env)

```env
# For Docker
DATABASE_URL=postgresql://postgres:postgres@db:5432/clarity

# For Local
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/clarity

# Required
SECRET_KEY=dev-secret-key-change-in-production
ENVIRONMENT=development
BACKEND_CORS_ORIGINS=["http://localhost:3000"]

# Optional (uses fallbacks if not set)
GOOGLE_APPLICATION_CREDENTIALS=
GEMINI_API_KEY=
GCS_BUCKET_NAME=clarityap-invoices
```

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🧪 Testing the Application

### 1. Register an Account

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!",
    "first_name": "John",
    "last_name": "Doe",
    "company_name": "Acme Corp"
  }'
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "Test123!"
  }'
```

Save the `access_token` from the response.

### 3. Upload Invoice (Using UI)

1. Go to http://localhost:3000
2. Register/Login
3. Click "Upload Invoice"
4. Select a PDF/image file
5. Wait for AI extraction (uses mock data for demo)
6. Review extracted data
7. Click "Save"

### 4. Export to QuickBooks

1. Select an invoice
2. Click "Export" → "QuickBooks IIF"
3. Download the .iif file
4. Import into QuickBooks Desktop

---

## 🐛 Troubleshooting

### Backend won't start

**Error: `ModuleNotFoundError`**
```bash
# Make sure you pulled latest code
git pull

# Reinstall dependencies
pip install -r requirements.txt
```

**Error: `Can't connect to database`**
```bash
# Check if PostgreSQL is running
docker ps  # If using Docker
# OR
pg_isready  # If local PostgreSQL

# Verify DATABASE_URL in .env
cat .env | grep DATABASE_URL
```

**Error: `Alembic migration failed`**
```bash
# Reset migrations (WARNING: deletes data)
docker exec -it ap-agent-db-1 psql -U postgres -d clarity -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Re-run migrations
alembic upgrade head
```

### Frontend won't build

**Error: `Expected '>', got 'value'`**
```bash
# Clear all caches
rm -rf .next node_modules/.cache
npm cache clean --force
npm install
npm run dev
```

**Error: `Can't connect to API`**
```bash
# Check if backend is running
curl http://localhost:8000/health

# Verify .env.local
cat .env.local
# Should have: NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Docker issues

**Error: `port already in use`**
```bash
# Stop conflicting services
docker-compose down
lsof -ti:8000 | xargs kill  # Mac/Linux
# OR find and kill process on Windows

# Start again
docker-compose up -d
```

**Error: `build failed`**
```bash
# Clean Docker cache
docker system prune -a
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 Feature Testing Checklist

- [ ] Register new account
- [ ] Login with credentials
- [ ] Upload PDF invoice
- [ ] Upload image invoice (JPG/PNG)
- [ ] View extracted data with confidence scores
- [ ] Edit extracted data
- [ ] Save invoice
- [ ] List all invoices
- [ ] Search/filter invoices
- [ ] Export single invoice to IIF
- [ ] Export multiple invoices to IIF
- [ ] Export to CSV
- [ ] View invoice details
- [ ] Delete invoice
- [ ] Logout

---

## 🎯 What Works Out of the Box

### ✅ Working Features

1. **Authentication**
   - User registration
   - Login/logout
   - JWT tokens
   - Password hashing with bcrypt

2. **Invoice Upload**
   - PDF support
   - Image support (JPG, PNG)
   - Local storage fallback (no GCS needed)
   - File validation

3. **AI Extraction** (Mock Mode)
   - Realistic mock data generation
   - Confidence scores
   - Multi-tier processing simulation
   - International support (INR, USD, EUR, GBP)

4. **Data Management**
   - View invoices
   - Edit extracted data
   - Delete invoices
   - Vendor auto-creation

5. **QuickBooks Export**
   - IIF format
   - CSV format
   - Multi-currency support

### ⚠️ Requires Configuration

1. **Real AI Extraction**
   - Set `GEMINI_API_KEY` in `.env`
   - Currently uses mock service

2. **Cloud Storage**
   - Set `GOOGLE_APPLICATION_CREDENTIALS` in `.env`
   - Currently uses local `./storage/invoices` directory

3. **Background Tasks**
   - Requires Redis (optional for MVP)
   - Docker Compose includes Redis by default

---

## 📦 What's Included

### Backend Services
- ✅ FastAPI REST API
- ✅ PostgreSQL database with migrations
- ✅ Mock AI extraction (works without API keys)
- ✅ Local file storage (works without GCS)
- ✅ JWT authentication
- ✅ QuickBooks IIF export

### Frontend
- ✅ Next.js 14 with TypeScript
- ✅ React 18
- ✅ Tailwind CSS
- ✅ Form validation with React Hook Form
- ✅ API client with Axios
- ✅ Authentication context

### Docker
- ✅ PostgreSQL 15
- ✅ Redis (optional)
- ✅ Backend container
- ✅ Frontend container (optional)
- ✅ Health checks
- ✅ Volume persistence

---

## 🔐 Security Notes

- Change `SECRET_KEY` in production
- Use strong passwords (8+ chars, letters + numbers)
- Set `ENVIRONMENT=production` in production
- Configure HTTPS/TLS for production
- Use proper GCS credentials for production
- Enable CMEK encryption for SOC 2 compliance

---

## 📞 Need Help?

1. Check logs: `docker-compose logs -f api`
2. Check database: `docker exec -it ap-agent-db-1 psql -U postgres -d clarity`
3. Restart services: `docker-compose restart`
4. Full reset: `docker-compose down -v && docker-compose up --build -d`

---

**Status**: ✅ All critical issues fixed and tested  
**Setup Time**: ~5 minutes with Docker  
**Difficulty**: Easy
