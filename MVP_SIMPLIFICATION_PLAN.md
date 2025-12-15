# ClarityAP MVP Simplification Plan

## 🎯 Core MVP Features (What We're Keeping)

### 1. Upload Invoice (PDF/Image)
- Single file upload endpoint
- Store in GCS (or local for dev)
- Return invoice ID immediately

### 2. AI Extract to Editable Form
- **Synchronous** extraction (no Celery)
- Gemini API extraction
- Return JSON with extracted fields
- Frontend shows editable form
- Save edited data

### 3. Export to QuickBooks
- Mock integration for MVP
- Generate QBO IIF format file
- Download link for user to import manually
- (Real OAuth integration later)

---

## 🗑️ What We're REMOVING (For MVP v1)

### Removed: Background Processing
- ❌ Celery worker
- ❌ Redis
- ❌ Flower monitoring
- ❌ Task status API
- **Why:** <100 invoices/day works fine synchronously
- **When to add back:** When customers complain about speed

### Removed: Approval Workflows
- ❌ Multi-level approvals
- ❌ Workflow routing
- ❌ Approval notifications
- ❌ Timeout/escalation
- **Why:** Single-user MVP doesn't need approvals
- **When to add back:** When customer asks "can my manager approve?"

### Removed: RBAC & Permissions
- ❌ Roles table
- ❌ Permission checks
- ❌ 20+ granular permissions
- **Why:** Single user per org for MVP
- **When to add back:** When second user signs up

### Removed: SOC 2 Audit Logging
- ❌ Comprehensive audit trails
- ❌ IP address tracking
- ❌ User agent logging
- **Why:** Premature for MVP validation
- **When to add back:** When customer asks for compliance

### Removed: Analytics Dashboard
- ❌ Dashboard stats API
- ❌ Monthly trends
- ❌ Top vendors analysis
- ❌ Validation metrics
- **Why:** SQL queries work fine initially
- **When to add back:** When users ask "show me insights"

### Removed: Vendor Management
- ❌ Vendor CRUD API
- ❌ Vendor analytics
- ❌ Payment terms tracking
- **Why:** Can be CSV import or inline during invoice entry
- **When to add back:** When users have >20 vendors

### Removed: Advanced Validation
- ❌ 8 validation types
- ❌ Duplicate detection
- ❌ Anomaly detection
- ❌ Custom validation rules
- **Why:** Basic validation (required fields, math) is enough
- **When to add back:** When customers report duplicate payments

---

## ✅ What We're KEEPING (Minimal)

### Essential Infrastructure
- ✅ FastAPI backend
- ✅ PostgreSQL database
- ✅ SQLAlchemy ORM
- ✅ Pydantic schemas
- ✅ JWT authentication (simplified)
- ✅ Basic validation (required fields, math check)
- ✅ Invoice storage (GCS or local)
- ✅ Gemini AI extraction

### Simplified Database Schema
```sql
-- organizations (keep)
-- users (simplified - no roles)
-- invoices (simplified - no approval fields)
-- vendors (optional, can be inline)
```

---

## 🚀 MVP User Flow

```
1. User logs in
   ↓
2. Upload invoice PDF
   ↓
3. AI extracts data (sync, 3-5 seconds)
   ↓
4. Show editable form with extracted data
   ↓
5. User reviews/edits
   ↓
6. Click "Export to QuickBooks"
   ↓
7. Download IIF file
   ↓
8. User imports to QuickBooks manually
```

**Time to value:** < 2 minutes per invoice

---

## 📊 Metrics to Track (Minimal)

1. **Invoices processed** (count)
2. **Extraction accuracy** (user edit %)
3. **Time saved** (vs manual entry)
4. **QuickBooks exports** (completion rate)

Store in simple JSON column or Google Sheets API.

---

## 🔧 Implementation Steps

### Phase 1: Simplification (2-3 hours)
- [ ] Remove Celery/Redis/Flower from docker-compose
- [ ] Remove background task modules
- [ ] Remove RBAC service
- [ ] Remove approval service
- [ ] Remove analytics API
- [ ] Remove vendor management API
- [ ] Simplify database schema (drop unnecessary tables)

### Phase 2: Core Features (4-6 hours)
- [ ] Simplified invoice upload API (sync)
- [ ] Synchronous AI extraction
- [ ] Editable form API (PUT endpoint)
- [ ] QuickBooks IIF export generator
- [ ] Download endpoint

### Phase 3: Testing (2 hours)
- [ ] Manual end-to-end test
- [ ] 5 sample invoices
- [ ] Verify accuracy
- [ ] Time the flow

### Phase 4: Deploy & Validate (1 week)
- [ ] Deploy to Heroku/Railway/Fly.io
- [ ] 5 beta users
- [ ] Daily check-ins
- [ ] Iterate based on feedback

---

## 🎯 Success Criteria (MVP Validation)

**Ship within:** 1 week
**Beta users:** 5 companies
**Goal:** 3 out of 5 users process >10 invoices
**Pivot trigger:** <2 users find it useful

**If successful:**
- Then add approval workflows
- Then add QuickBooks OAuth
- Then add analytics

**If not:**
- Interview users: why didn't you use it?
- Pivot or kill

---

## 📝 File Changes Required

### Delete:
```
clarity-api/app/celery_app.py
clarity-api/app/tasks/
clarity-api/app/services/approval_service.py
clarity-api/app/services/rbac_service.py
clarity-api/app/services/audit_service.py
clarity-api/app/api/v1/analytics.py
clarity-api/app/api/v1/vendors.py
clarity-api/app/api/v1/tasks.py
clarity-api/alembic/versions/003_security_compliance.py
docker-compose.yml (simplify to just db + api)
```

### Modify:
```
clarity-api/app/api/v1/invoices.py (simplify to sync)
clarity-api/app/services/extraction_service.py (remove celery)
clarity-api/requirements.txt (remove celery, redis, flower)
```

### Create:
```
clarity-api/app/api/v1/quickbooks.py (export IIF)
clarity-api/app/services/quickbooks_export.py
```

---

## 🚨 Rollback Plan

If this simplification breaks things:
1. Current code is on branch: `claude/setup-backend-dev-01FwJmG2Rkv27vt6YY3mWUs1`
2. New simplified code will be on: `mvp-simplified`
3. Can always revert to enterprise version later

---

**Ready to implement?** Let's build the actual MVP. 🚀
