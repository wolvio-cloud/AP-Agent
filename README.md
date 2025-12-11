# ClarityAP - AI-Powered Invoice Processing

ClarityAP is an intelligent accounts payable automation system that uses AI to extract, validate, and process invoices with minimal manual intervention.

## 🚀 Features

- **AI-Powered Extraction**: Automatically extract invoice data using Google Gemini AI
- **Smart Validation**: Detect duplicates, math errors, and anomalies
- **GL Code Assignment**: Automatically assign GL codes based on vendor and line items
- **Multi-Tenancy**: Support multiple organizations with data isolation
- **Real-Time Dashboard**: Track processing metrics and invoice status
- **Cloud Storage**: Secure document storage using Google Cloud Storage

## 📁 Project Structure

```
AP-Agent/
├── clarity-api/        # FastAPI backend
│   ├── alembic/       # Database migrations
│   ├── app/
│   │   ├── api/v1/    # API endpoints
│   │   ├── core/      # Config & database
│   │   ├── models/    # SQLAlchemy models
│   │   ├── schemas/   # Pydantic schemas
│   │   └── services/  # Business logic
│   └── requirements.txt
│
└── clarity-web/       # Next.js frontend
    ├── app/           # App router pages
    ├── components/    # React components
    ├── lib/           # Utilities
    └── hooks/         # Custom hooks
```

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy
- **Migrations**: Alembic
- **AI**: Google Gemini AI
- **Storage**: Google Cloud Storage
- **Auth**: JWT (python-jose)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Forms**: React Hook Form + Zod
- **Data Fetching**: TanStack Query
- **Charts**: Recharts

## 🚦 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Google Cloud account (for storage & AI)

### Backend Setup

1. Navigate to backend:
```bash
cd clarity-api
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Create database:
```sql
CREATE DATABASE clarityap;
```

6. Run migrations:
```bash
alembic upgrade head
```

7. Start server:
```bash
uvicorn app.main:app --reload
```

8. Access API:
- Swagger UI: http://localhost:8000/docs
- Health check: http://localhost:8000/health

### Frontend Setup

1. Navigate to frontend:
```bash
cd clarity-web
```

2. Install dependencies:
```bash
npm install
```

3. Configure environment:
```bash
cp .env.example .env.local
# Edit .env.local with API URL
```

4. Start development server:
```bash
npm run dev
```

5. Open browser:
http://localhost:3000

## 📋 Development Phases

### ✅ Phase 1: Project Setup (Completed)
- Project structure created
- FastAPI backend with SQLAlchemy
- Next.js frontend with TypeScript
- Database models and migrations

### 🔄 Phase 2: Authentication + Multi-tenancy (Next)
- User registration and login
- JWT authentication
- Organization management
- Protected routes

### 📅 Upcoming Phases
- Phase 3: Document Upload + Storage
- Phase 4: AI Extraction Pipeline
- Phase 5: Validation + GL Coding
- Phase 6: Dashboard UI
- Phase 7: Invoice Detail + Edit

## 🔐 Environment Variables

### Backend (.env)
```env
DATABASE_URL=postgresql://user:password@localhost:5432/clarityap
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-key
GCS_BUCKET_NAME=your-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📖 API Documentation

Once the backend is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Testing

### Backend
```bash
cd clarity-api
pytest
```

### Frontend
```bash
cd clarity-web
npm test
```

## 📝 License

MIT License - see LICENSE file for details

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📧 Support

For questions or issues, please open an issue on GitHub.

---

Built with ❤️ using FastAPI, Next.js, and Google Gemini AI
