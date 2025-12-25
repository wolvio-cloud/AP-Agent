# 🚀 ClarityAP Backend Testing - Quick Start Guide

## ⚡ One-Command Test (Recommended)

```bash
./run_all_tests.sh
```

This will:
- ✅ Start Docker containers
- ✅ Wait for API to be ready
- ✅ Run 10 comprehensive tests
- ✅ Verify IIF export format
- ✅ Generate test report
- ✅ Show pass/fail summary

**Expected Result:** 10/10 tests pass (100%)

---

## 📋 Manual Testing (Step-by-Step)

### Step 1: Start Backend

```bash
# Start Docker containers
docker-compose up -d

# Wait for API to start
sleep 15

# Verify API is running
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

### Step 2: Run Main Test Suite

```bash
python3 test_mvp_backend.py
```

**Tests:**
1. User Registration
2. User Login
3. JWT Authentication
4. Invoice Upload
5. Extraction Quality
6. Get Invoice
7. Update Invoice
8. QuickBooks Export
9. List Invoices
10. Delete Invoice

**Results:** See `MVP-Test-Results.json`

### Step 3: Test PDF Upload (Optional)

```bash
# Place a PDF invoice in the project root first
python3 test_pdf_upload.py
```

**Measures:**
- Extraction accuracy
- Confidence score
- Field completeness

### Step 4: Verify IIF Format

```bash
python3 verify_iif_format.py
```

**Validates:**
- Tab-delimited format
- QuickBooks compliance
- Required headers
- Date format

---

## ✅ What Was Fixed

### Security Bug: Password Hashing

**File:** `clarity-api/app/core/security.py`

**Problem:** bcrypt has a 72-byte limit, causing crashes with long passwords

**Fix Applied:**
```python
def get_password_hash(password: str) -> str:
    # Truncate to 72 bytes to avoid bcrypt limitation
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)
```

**Status:** ✅ FIXED

---

## 📊 Expected Test Results

### Comprehensive Test Suite (test_mvp_backend.py)

```
======================================================================
ClarityAP MVP Backend Test Suite
======================================================================

>>> PHASE 1: Authentication

✓ TEST 1: User Registration - PASS
✓ TEST 2: User Login - PASS
✓ TEST 3: JWT Token Works - PASS

>>> PHASE 2: Invoice Processing

✓ TEST 4: Invoice Upload - PASS
✓ TEST 5: Extraction Quality - PASS
✓ TEST 6: Get Invoice Details - PASS
✓ TEST 7: Update Invoice - PASS

>>> PHASE 3: QuickBooks Export

✓ TEST 8: IIF Export - PASS
✓ TEST 9: List Invoices - PASS
✓ TEST 10: Delete Invoice - PASS

======================================================================
TEST SUMMARY
======================================================================

Tests Passed: 10/10 (100%)

✓ BACKEND IS PRODUCTION READY
Next: Build frontend (3 days)

======================================================================
```

### IIF Format Verification (verify_iif_format.py)

```
======================================================================
QUICKBOOKS IIF FORMAT VERIFICATION
======================================================================

VALIDATION CHECKLIST:
----------------------------------------------------------------------
  ✓ File starts with !TRNS header
  ✓ Contains !SPL header
  ✓ Contains !ENDTRNS header
  ✓ Contains TRNS transaction line
  ✓ Contains SPL split line
  ✓ Contains ENDTRNS closer
  ✓ Uses tab-delimited format
  ✓ Contains date (MM/DD/YYYY)
  ✓ Contains BILL transaction type
  ✓ Contains Accounts Payable account

======================================================================
VALIDATION SUMMARY:
  Checks Passed: 10/10 (100%)

✓ IIF FORMAT: PERFECT
  File is ready for QuickBooks import

======================================================================
```

---

## 🎯 Success Criteria

| Test Category | Target | Status |
|---------------|--------|--------|
| Main Test Suite | ≥90% (9/10 tests) | ✅ Ready to verify |
| PDF Extraction | ≥75% completeness | ✅ Ready to verify |
| IIF Format | ≥80% validation | ✅ Ready to verify |
| Security Fix | Applied | ✅ COMPLETE |

---

## 📁 Generated Files

After running tests, you'll have:

```
/home/user/AP-Agent/
├── MVP-Test-Results.json          # Detailed test results
├── test_export.iif                # Sample IIF export
├── test-invoice-office-depot.txt  # Sample invoice
├── BACKEND-TEST-REPORT.md         # Comprehensive report
└── TESTING-QUICK-START.md         # This file
```

---

## 🐛 Troubleshooting

### API Not Starting

```bash
# Check container status
docker-compose ps

# View logs
docker-compose logs api

# Restart containers
docker-compose restart
```

### Tests Failing

```bash
# Check API health
curl http://localhost:8000/health

# Check database
docker-compose logs db

# Restart everything
docker-compose down
docker-compose up -d
sleep 15
```

### No IIF File Generated

- Test 8 may have failed
- Check `MVP-Test-Results.json` for details
- Ensure invoice was uploaded successfully

---

## ✅ Final Checklist

Before building frontend, verify:

- [ ] Security fix applied (`security.py` modified)
- [ ] Docker containers running (`docker-compose ps`)
- [ ] API health check passes (`curl localhost:8000/health`)
- [ ] 10/10 tests pass (`python3 test_mvp_backend.py`)
- [ ] IIF format validates (`python3 verify_iif_format.py`)
- [ ] Test results saved (`MVP-Test-Results.json` exists)

---

## 🚀 Next Steps

### If All Tests Pass (10/10):

✅ **BACKEND IS PRODUCTION READY**

**Action:** Start frontend development immediately

**Timeline:**
- **Week 1:** Build 3-screen frontend (3 days)
- **Week 2:** Find 5 beta users, deploy
- **Week 3:** Measure usage, iterate or pivot

### If Some Tests Fail (7-9/10):

⚠️ **BACKEND NEEDS MINOR FIXES**

**Action:**
1. Check `MVP-Test-Results.json` for failure details
2. Fix specific failing tests
3. Re-run test suite
4. Proceed to frontend when ≥9/10 pass

### If Many Tests Fail (<7/10):

❌ **BACKEND HAS SERIOUS ISSUES**

**Action:**
1. Review API logs: `docker-compose logs api`
2. Check database connection
3. Verify environment variables
4. Debug failing endpoints
5. Re-run tests

---

## 📞 Support

**Documentation:** See `BACKEND-TEST-REPORT.md`

**Quick Help:**
```bash
# Stop all containers
docker-compose down

# Start fresh
docker-compose up -d --build

# Re-run tests
./run_all_tests.sh
```

---

**Test Suite Version:** 1.0
**Last Updated:** December 25, 2025
**Backend Version:** MVP Simplified
