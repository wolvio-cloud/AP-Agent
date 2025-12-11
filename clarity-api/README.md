# ClarityAP Backend API

FastAPI backend for ClarityAP invoice processing system.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. Run migrations:
```bash
alembic upgrade head
```

5. Start server:
```bash
uvicorn app.main:app --reload
```

6. Access API:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Database

PostgreSQL is required. Create database:
```sql
CREATE DATABASE clarityap;
```

## Project Structure

```
clarity-api/
├── alembic/              # Database migrations
├── app/
│   ├── api/
│   │   └── v1/          # API endpoints
│   ├── core/            # Core config and database
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── main.py          # FastAPI app
├── requirements.txt
└── .env
```
