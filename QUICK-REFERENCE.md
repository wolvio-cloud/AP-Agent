# ClarityAP - Quick Reference Card

## 🚀 Fastest Way to Get Started

### 1. Download
```bash
git clone https://github.com/YOUR-USERNAME/AP-Agent.git
cd AP-Agent
git checkout claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1
```

### 2. Setup (Choose ONE)

**A. With Docker (Easiest):**
```bash
docker-compose up -d
docker-compose exec backend alembic upgrade head
```

**B. With Local PostgreSQL:**
```bash
./QUICK-START.sh
# Select option [2]
```

**C. With Cloud Database:**
```bash
./QUICK-START.sh
# Select option [3]
# Paste Supabase/Railway URL
```

### 3. Test
```bash
./run_e2e_tests.sh
```

### 4. Access
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000/docs

---

## 📝 Testing Checklist

- [ ] Run automated tests: `./run_e2e_tests.sh`
- [ ] Register account at http://localhost:3000
- [ ] Upload: `test_data/invoice-india-gst.txt`
- [ ] Verify: ₹ symbol, GSTIN, PAN fields
- [ ] Upload: `test_data/invoice-us-sales-tax.txt`
- [ ] Verify: $ symbol, Sales Tax
- [ ] Test export to QuickBooks
- [ ] Test batch operations
- [ ] Test search & filter

---

## 🔧 Common Commands

**Start Backend:**
```bash
cd clarity-api
source venv/bin/activate
uvicorn app.main:app --reload
```

**Start Frontend:**
```bash
cd clarity-web
npm run dev
```

**Run Tests:**
```bash
./run_e2e_tests.sh
```

**View Logs:**
```bash
docker-compose logs -f  # Docker
tail -f clarity-api/app.log  # Local
```

**Reset Database:**
```bash
cd clarity-api
alembic downgrade base
alembic upgrade head
```

---

## 📊 Test Data

| File | Country | Currency | Tax | Special Fields |
|------|---------|----------|-----|----------------|
| `test_data/invoice-india-gst.txt` | 🇮🇳 India | ₹ INR | GST 18% | GSTIN, PAN |
| `test_data/invoice-us-sales-tax.txt` | 🇺🇸 USA | $ USD | Sales Tax 8.25% | - |
| `test_data/invoice-eu-vat.txt` | 🇪🇺 EU | € EUR | VAT 19% | VAT Number |
| `test_data/invoice-uk-vat.txt` | 🇬🇧 UK | £ GBP | VAT 20% | VAT Number |

---

## 🐛 Quick Troubleshooting

**Port in use:**
```bash
kill -9 $(lsof -ti:3000)  # Frontend
kill -9 $(lsof -ti:8000)  # Backend
```

**PostgreSQL not running:**
```bash
brew services start postgresql@15  # Mac
sudo service postgresql start  # Linux
```

**Dependencies issues:**
```bash
# Backend
cd clarity-api && pip install -r requirements.txt

# Frontend
cd clarity-web && npm install
```

---

## 📖 Full Documentation

- **Complete Setup:** `STEP-BY-STEP-SETUP.md`
- **Testing Guide:** `INTEGRATION-TESTING-GUIDE.md`
- **Project Overview:** `PROJECT-SUMMARY.md`
- **SaaS Roadmap:** `SAAS-ENHANCEMENT-PLAN.md`

---

## ✅ Success Criteria

All tests pass when you see:
- ✅ `[PASS]` for all 12 automated tests
- ✅ Can register and login
- ✅ Can upload invoices
- ✅ Currency symbols display correctly
- ✅ Can export to QuickBooks
- ✅ Batch operations work

**Next:** Start Phase 1 (Multi-Tenancy) → SaaS Launch → $165K ARR 🚀
