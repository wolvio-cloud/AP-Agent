# ClarityAP MVP - The Actually Minimal Version

## 🎯 What This Is

**A dead-simple invoice processing tool:**
1. Upload invoice PDF
2. AI extracts data (you wait 3-5 seconds)
3. Review/edit the extracted fields
4. Download file to import into QuickBooks

**That's it.** No fancy dashboards, no approvals, no roles, no enterprise bloat.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
- Python 3.11+
- PostgreSQL
- Gemini API key

### Setup
```bash
# 1. Install dependencies
cd clarity-api
pip install -r requirements.txt

# 2. Create database
psql -U postgres -c "CREATE DATABASE clarityap;"

# 3. Set environment variables
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 4. Create tables
python3 << 'EOF'
from app.core.database import Base, engine
from app.models import User, Organization, Invoice, Vendor
Base.metadata.create_all(bind=engine)
print("✅ Tables created")
EOF

# 5. Start server
uvicorn app.main:app --reload
```

Server runs on: http://localhost:8000

---

## 📋 API Endpoints

### Authentication
```bash
# Register (creates organization + user)
POST /api/v1/auth/register
{
  "email": "you@company.com",
  "password": "SecurePass123!",
  "first_name": "Your",
  "last_name": "Name",
  "company_name": "Your Company"
}

# Login
POST /api/v1/auth/login
{
  "email": "you@company.com",
  "password": "SecurePass123!"
}
# Returns: { "access_token": "..." }
```

### Core Flow

#### 1. Upload & Extract (Synchronous)
```bash
POST /api/v1/invoices/upload
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: invoice.pdf

# Response (after 3-5 seconds):
{
  "id": "uuid",
  "status": "extracted",
  "extracted_data": {
    "vendor_name": "Acme Corp",
    "invoice_number": "INV-001",
    "invoice_date": "2025-01-15",
    "total_amount": 1500.00,
    "subtotal": 1350.00,
    "tax_amount": 150.00,
    ...
  },
  "extraction_confidence": 0.95
}
```

#### 2. Review & Edit
```bash
# Get invoice
GET /api/v1/invoices/{invoice_id}

# Update after review
PUT /api/v1/invoices/{invoice_id}
{
  "data": {
    "vendor_name": "Acme Corp (corrected)",
    "invoice_number": "INV-001",
    "total_amount": 1500.00,
    ...
  }
}
```

#### 3. Export to QuickBooks
```bash
# Single invoice
GET /api/v1/quickbooks/export/iif/{invoice_id}
# Downloads: invoice_INV-001.iif

# Batch export
POST /api/v1/quickbooks/export/iif/batch
{
  "invoice_ids": ["uuid1", "uuid2", "uuid3"]
}
# Downloads: invoices_batch_3.iif

# CSV alternative
GET /api/v1/quickbooks/export/csv
# Downloads: invoices_export_10.csv
```

---

## 🧪 Testing the MVP

### End-to-End Test
```bash
# 1. Register user
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@test.com",
    "password": "Test123!",
    "first_name": "Test",
    "last_name": "User",
    "company_name": "Test Co"
  }' | jq -r '.data.access_token')

echo "Token: $TOKEN"

# 2. Upload invoice
INVOICE_ID=$(curl -s -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@/path/to/invoice.pdf" \
  | jq -r '.id')

echo "Invoice ID: $INVOICE_ID"

# 3. Get extracted data
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/invoices/$INVOICE_ID \
  | jq '.extracted_data'

# 4. Update (simulate user edits)
curl -s -X PUT http://localhost:8000/api/v1/invoices/$INVOICE_ID \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": {
      "vendor_name": "Updated Vendor",
      "invoice_number": "INV-001",
      "invoice_date": "2025-01-15",
      "total_amount": 1500.00,
      "subtotal": 1350.00,
      "tax_amount": 150.00,
      "currency": "USD"
    }
  }' | jq

# 5. Export to QuickBooks
curl -s -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/v1/quickbooks/export/iif/$INVOICE_ID \
  -o invoice.iif

echo "✅ Downloaded invoice.iif"
cat invoice.iif
```

---

## 📊 Success Metrics (First Week)

Track these manually:

1. **User Sign-ups:** 5 beta users
2. **Invoices Processed:** >10 per user
3. **Extraction Accuracy:** >85% (measured by % of fields NOT edited)
4. **QuickBooks Exports:** >80% of invoices exported
5. **Time Saved:** User survey (vs manual entry)

**Pivot Trigger:** <2 users find it useful

---

## 🎨 Frontend (To Build)

Suggested tech stack:
- Next.js 14 (App Router)
- Tailwind CSS
- React Hook Form
- Zustand (state)

### Screens Needed (3 total):

1. **Login/Register** (`/auth`)
   - Email + password
   - Auto-redirects to dashboard

2. **Upload & Review** (`/dashboard`)
   - Drag-drop PDF upload
   - Shows loading spinner (3-5 sec)
   - Editable form with extracted data
   - Save button (PUT request)

3. **Export** (`/export`)
   - List of reviewed invoices
   - Checkboxes for batch selection
   - "Download IIF" button
   - "Download CSV" button

**Total build time:** 2-3 days for decent UI

---

## 🐛 Known Limitations (MVP Trade-offs)

### By Design:
- ✅ Synchronous processing (user waits) - **Good for <100 invoices/day**
- ✅ Single user per org - **Add multi-user when requested**
- ✅ Manual QuickBooks import - **OAuth later**
- ✅ No approval workflows - **Add when enterprise asks**
- ✅ No analytics dashboard - **SQL queries work fine**

### Tech Debt (Fix Later):
- ⚠️ No tests - **Add when feature set stabilizes**
- ⚠️ No rate limiting - **Add when we have traffic**
- ⚠️ Basic error handling - **Improve based on errors seen**

---

## 🔄 Rollback Plan

If this MVP fails validation:

```bash
# Switch back to enterprise version
git checkout claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1

# Or keep simplified but add features back
git cherry-pick <enterprise-commit>
```

**Enterprise features preserved on:**
`claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1`

---

## 📈 When to Add Features Back

### Approval Workflows
**Trigger:** Customer says "I need my manager to approve"
**Build time:** 1 day

### RBAC
**Trigger:** Customer says "I need to add another user"
**Build time:** 4 hours

### Background Processing
**Trigger:** User complains "extraction takes too long"
**Build time:** 2 hours (already built, just re-enable)

### Analytics
**Trigger:** Customer asks "show me insights"
**Build time:** 1 day

### QuickBooks OAuth
**Trigger:** Customer says "manual import is annoying"
**Build time:** 3 days

---

## 🎯 Next Steps

1. **Week 1:** Find 5 beta users
   - Reach out to your network
   - Offer free 3-month access
   - Daily check-ins

2. **Week 2:** Iterate based on feedback
   - Track what features they ask for
   - Measure: do they actually use it?

3. **Week 3:** Decision point
   - If >3/5 users active → keep building
   - If <2/5 users active → pivot or kill

---

## ❓ FAQ

**Q: Why remove all those features?**
A: They're not validated. Build them when customers ask.

**Q: Why synchronous processing?**
A: <100 invoices/day doesn't need async. Simpler is better.

**Q: Why manual QuickBooks import?**
A: OAuth integration is complex. Validate market fit first.

**Q: Where's the analytics?**
A: Run SQL queries. Dashboard is premature.

**Q: Can I add features back?**
A: Yes! Previous code is on `claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1`

---

## 🚀 Let's Ship It

The best code is code that ships to users.

**This MVP can be in front of customers in:**
- Backend: ✅ Done
- Frontend: 2-3 days
- Testing: 1 day
- Deploy: 1 hour

**Total: ~1 week to first user.**

Now go validate the market. 🎯
