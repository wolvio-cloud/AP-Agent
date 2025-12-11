# Phase 4 Testing Guide: AI Extraction Pipeline

Complete guide for testing ClarityAP Phase 4 features including 4-tier AI extraction, confidence scoring, e-Invoice ingestion, and review queue.

## Table of Contents

1. [Setup](#setup)
2. [Testing Workflow](#testing-workflow)
3. [API Endpoints](#api-endpoints)
4. [Frontend UI Testing](#frontend-ui-testing)
5. [e-Invoice Ingestion](#e-invoice-ingestion)
6. [Review Queue](#review-queue)
7. [Troubleshooting](#troubleshooting)

---

## Setup

### Prerequisites

- Backend server running on `http://localhost:8000`
- Frontend server running on `http://localhost:3000`
- Valid authentication token
- Test invoice files (PDF, JPG, PNG)

### Get Authentication Token

```bash
# Login to get access token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@acme.com" \
  -d "password=yourpassword"

# Save the access_token from response
export TOKEN="your_access_token_here"
```

---

## Testing Workflow

### Full End-to-End Test

```bash
# 1. Upload an invoice
INVOICE_ID=$(curl -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@sample_invoice.pdf" \
  | jq -r '.data.id')

echo "Uploaded invoice ID: $INVOICE_ID"

# 2. Process with AI extraction
curl -X POST "http://localhost:8000/api/v1/invoices/$INVOICE_ID/extract" \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. View extraction results
curl -X GET "http://localhost:8000/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq

# 4. Check if it needs review
curl -X GET "http://localhost:8000/api/v1/invoices/queue/review" \
  -H "Authorization: Bearer $TOKEN" | jq
```

---

## API Endpoints

### 1. Upload Invoice

**Endpoint:** `POST /api/v1/invoices/upload`

**Description:** Upload PDF, JPG, or PNG invoice file

```bash
curl -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@invoice.pdf"
```

**Expected Response:**

```json
{
  "success": true,
  "message": "Invoice uploaded successfully",
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "file_name": "invoice.pdf",
    "status": "uploaded",
    "processing_tier": "uploaded",
    "created_at": "2024-01-15T10:30:00Z"
  }
}
```

---

### 2. Process Invoice with AI

**Endpoint:** `POST /api/v1/invoices/{invoice_id}/extract`

**Description:** Extract data using 4-tier AI pipeline

```bash
# Auto-tier selection (starts with Tier 1)
curl -X POST "http://localhost:8000/api/v1/invoices/$INVOICE_ID/extract" \
  -H "Authorization: Bearer $TOKEN" | jq

# Force specific tier for testing
curl -X POST "http://localhost:8000/api/v1/invoices/$INVOICE_ID/extract?force_tier=2" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Query Parameters:**
- `force_tier` (optional): Force specific tier (1, 2, or 3) for testing

**Expected Response:**

```json
{
  "success": true,
  "message": "Extraction completed",
  "data": {
    "invoice_id": "123e4567-e89b-12d3-a456-426614174000",
    "processing_tier": "tier1",
    "overall_confidence": 0.96,
    "requires_review": false,
    "review_priority": null,
    "extracted_data": {
      "vendor_name": "Acme Construction Supplies",
      "vendor_address": "123 Builder St, Mumbai, MH 400001",
      "vendor_tax_id": "29ABCDE1234F1Z5",
      "invoice_number": "INV-5678",
      "invoice_date": "2024-01-10T00:00:00Z",
      "due_date": "2024-02-09T00:00:00Z",
      "currency": "INR",
      "subtotal": 125000.00,
      "tax_amount": 22500.00,
      "tax_rate": 18.0,
      "total_amount": 147500.00,
      "line_items": [
        {
          "description": "Item 1 - Materials",
          "quantity": 50,
          "unit_price": 2500.00,
          "amount": 125000.00
        }
      ]
    },
    "field_confidences": {
      "vendor_name": 0.97,
      "invoice_number": 0.96,
      "invoice_date": 0.95,
      "total_amount": 0.98
    },
    "processing_time_ms": 1250
  }
}
```

**Confidence Thresholds:**
- **≥ 0.95**: Passes (status: `extracted`, tier: `completed`)
- **0.90 - 0.94**: Escalates to Tier 2 (preprocessing)
- **0.85 - 0.89**: Escalates to Tier 3 (GPT-4V)
- **< 0.85**: Requires human review (status: `requires_review`, tier: `tier4`)

---

### 3. Get Invoice Details

**Endpoint:** `GET /api/v1/invoices/{invoice_id}`

**Description:** Get full invoice details with extraction results

```bash
curl -X GET "http://localhost:8000/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Expected Response:**

```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "file_name": "invoice.pdf",
    "file_url": "https://storage.googleapis.com/...",
    "status": "extracted",
    "processing_tier": "completed",
    "overall_confidence": 0.96,
    "vendor_name": "Acme Construction Supplies",
    "invoice_number": "INV-5678",
    "total_amount": 147500.00,
    "per_field_confidence": {
      "vendor_name": 0.97,
      "total_amount": 0.98
    },
    "processing_history": [
      {
        "tier": "tier1",
        "confidence": 0.96,
        "timestamp": "2024-01-15T10:35:00Z",
        "processing_time_ms": 1250
      }
    ],
    "requires_review": false,
    "created_at": "2024-01-15T10:30:00Z",
    "extracted_at": "2024-01-15T10:35:00Z"
  }
}
```

---

### 4. List All Invoices

**Endpoint:** `GET /api/v1/invoices`

**Description:** List invoices with pagination and filtering

```bash
# List all invoices
curl -X GET "http://localhost:8000/api/v1/invoices" \
  -H "Authorization: Bearer $TOKEN" | jq

# Filter by status
curl -X GET "http://localhost:8000/api/v1/invoices?status=extracted" \
  -H "Authorization: Bearer $TOKEN" | jq

# Pagination
curl -X GET "http://localhost:8000/api/v1/invoices?page=2&limit=10" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Query Parameters:**
- `status` (optional): Filter by status (`uploaded`, `processing`, `extracted`, `requires_review`, `approved`, `rejected`, `error`)
- `page` (default: 1): Page number
- `limit` (default: 20, max: 100): Items per page

---

### 5. Review Queue

**Endpoint:** `GET /api/v1/invoices/queue/review`

**Description:** Get invoices requiring human review (confidence < 0.85)

```bash
# All invoices needing review
curl -X GET "http://localhost:8000/api/v1/invoices/queue/review" \
  -H "Authorization: Bearer $TOKEN" | jq

# Filter by priority
curl -X GET "http://localhost:8000/api/v1/invoices/queue/review?priority=high" \
  -H "Authorization: Bearer $TOKEN" | jq
```

**Query Parameters:**
- `priority` (optional): Filter by priority (`high`, `medium`, `low`)
- `page` (default: 1): Page number
- `limit` (default: 20): Items per page

**Expected Response:**

```json
{
  "success": true,
  "data": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174001",
      "file_name": "low_quality_invoice.jpg",
      "status": "requires_review",
      "processing_tier": "tier4",
      "overall_confidence": 0.78,
      "requires_review": true,
      "review_priority": "high",
      "vendor_name": "Unknown Vendor",
      "total_amount": 50000.00
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

**Priority Levels:**
- **High**: Confidence < 0.70 (critical fields unclear)
- **Medium**: Confidence 0.70 - 0.79
- **Low**: Confidence 0.80 - 0.84

---

### 6. Update Invoice

**Endpoint:** `PATCH /api/v1/invoices/{invoice_id}`

**Description:** Manually update/correct extracted data

```bash
curl -X PATCH "http://localhost:8000/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "vendor_name": "Corrected Vendor Name",
    "total_amount": 150000.00,
    "status": "approved"
  }' | jq
```

---

## e-Invoice Ingestion

### 7. Ingest e-Invoice JSON Only

**Endpoint:** `POST /api/v1/invoices/ingest-json`

**Description:** Ingest India e-Invoice JSON payload (IRN-based)

```bash
curl -X POST http://localhost:8000/api/v1/invoices/ingest-json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "einvoice_json": {
      "irn": "e8f4d2a1b5c6f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4",
      "seller_gstin": "29ABCDE1234F1Z5",
      "buyer_gstin": "27XYZAB9876C2D4",
      "doc_no": "INV/2024/001",
      "doc_date": "15/01/2024",
      "doc_type": "INV",
      "seller_legal_name": "ABC Corp Pvt Ltd",
      "seller_address": "123 Business St",
      "seller_location": "Mumbai",
      "seller_pincode": "400001",
      "buyer_legal_name": "XYZ Industries",
      "total_value": 147500.00,
      "taxable_value": 125000.00,
      "cgst_value": 11250.00,
      "sgst_value": 11250.00,
      "igst_value": 0.00
    }
  }' | jq
```

**Mandatory Fields:**
- `irn`: Invoice Reference Number (64 chars)
- `seller_gstin`: Seller GSTIN (15 chars)
- `buyer_gstin`: Buyer GSTIN (15 chars)
- `doc_no`: Invoice/Document number
- `doc_date`: Date in DD/MM/YYYY format
- `doc_type`: INV, CRN, or DBN

**Expected Response:**

```json
{
  "success": true,
  "message": "e-Invoice JSON ingested successfully",
  "data": {
    "id": "789e0123-e89b-12d3-a456-426614174002",
    "status": "extracted",
    "source_type": "einvoice_json",
    "processing_tier": "completed",
    "overall_confidence": 1.0,
    "irn": "e8f4d2a1b5c6f9e8d7c6b5a4f3e2d1c0...",
    "seller_gstin": "29ABCDE1234F1Z5",
    "buyer_gstin": "27XYZAB9876C2D4",
    "vendor_name": "ABC Corp Pvt Ltd",
    "invoice_number": "INV/2024/001",
    "total_amount": 147500.00
  }
}
```

---

### 8. Ingest PDF + e-Invoice JSON Pair

**Endpoint:** `POST /api/v1/invoices/ingest-pair`

**Description:** Upload PDF and e-Invoice JSON together

```bash
# Create JSON payload
cat > einvoice.json <<EOF
{
  "irn": "e8f4d2a1b5c6f9e8d7c6b5a4f3e2d1c0b9a8f7e6d5c4b3a2f1e0d9c8b7a6f5e4",
  "seller_gstin": "29ABCDE1234F1Z5",
  "buyer_gstin": "27XYZAB9876C2D4",
  "doc_no": "INV/2024/001",
  "doc_date": "15/01/2024",
  "doc_type": "INV",
  "seller_legal_name": "ABC Corp Pvt Ltd",
  "total_value": 147500.00
}
EOF

# Upload both PDF and JSON
curl -X POST http://localhost:8000/api/v1/invoices/ingest-pair \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@invoice.pdf" \
  -F "einvoice_json=$(cat einvoice.json)" | jq
```

---

## Frontend UI Testing

### Access the Application

1. **Login**: http://localhost:3000/login
2. **Dashboard**: http://localhost:3000/dashboard
3. **Upload Invoice**: http://localhost:3000/invoices/upload
4. **Invoice List**: http://localhost:3000/invoices
5. **Review Queue**: http://localhost:3000/invoices/review

### Test Invoice Detail Page

1. Upload an invoice via UI or API
2. Navigate to **Invoices** list
3. Click on any invoice to open detail page
4. Verify the following UI elements:
   - **Status badge** (uploaded, processing, extracted, etc.)
   - **Processing tier badge** (Tier 1, Tier 2, etc.)
   - **Overall confidence ring** (circular progress indicator)
   - **Process with AI button** (if status is `uploaded`)
   - **Extracted data sections**:
     - Vendor Information with per-field confidence
     - Invoice Details with dates and numbers
     - Financial Summary with amounts
     - Line Items table
   - **Processing history timeline**

### Test Process Button

1. Open an invoice with status `uploaded`
2. Click **"Process with AI"** button
3. Button should show loading state: **"Processing..."**
4. After extraction:
   - Status updates to `extracted` or `requires_review`
   - Confidence ring appears
   - Extracted data populates
   - Per-field confidence scores display

### Test Confidence Indicators

**Color Coding:**
- **Green (≥95%)**: High confidence, ready to approve
- **Yellow (85-94%)**: Medium confidence, may need verification
- **Red (<85%)**: Low confidence, requires review

**Components to verify:**
- Overall confidence ring (large, top right)
- Per-field confidence percentages (next to each field label)
- Processing history confidence badges

### Test Review Queue

1. Navigate to **Review Queue**: http://localhost:3000/invoices/review
2. Verify **statistics cards**:
   - Total Reviews
   - High Priority (red)
   - Medium Priority (yellow)
   - Low Priority (blue)
3. Test **priority filters**:
   - Click "High" → Shows only high-priority invoices
   - Click "Medium" → Shows only medium-priority invoices
   - Click "Low" → Shows only low-priority invoices
   - Click "All" → Shows all invoices requiring review
4. Verify **invoice cards** display:
   - File name and status badges
   - Vendor, invoice number, amount
   - Confidence ring
   - Time since extraction
   - Warning banner for high-priority items
5. Click on any invoice → Opens detail page for review

---

## Testing Scenarios

### Scenario 1: High Confidence Extraction

**Goal:** Invoice processes successfully with no review needed

```bash
# 1. Upload invoice
INVOICE_ID=$(curl -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@clear_invoice.pdf" | jq -r '.data.id')

# 2. Process (mock tier 1 returns 0.96 confidence)
curl -X POST "http://localhost:8000/api/v1/invoices/$INVOICE_ID/extract" \
  -H "Authorization: Bearer $TOKEN" | jq

# 3. Verify status is 'extracted', not 'requires_review'
curl -X GET "http://localhost:8000/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.status'
# Expected: "extracted"

# 4. Check review queue (should not appear)
curl -X GET "http://localhost:8000/api/v1/invoices/queue/review" \
  -H "Authorization: Bearer $TOKEN" | jq '.total'
# Expected: 0 (or doesn't include this invoice)
```

---

### Scenario 2: Low Confidence → Review Queue

**Goal:** Invoice with low confidence goes to review queue

```bash
# Force tier 3 (simulates lower confidence 0.85-0.92)
INVOICE_ID=$(curl -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@blurry_invoice.jpg" | jq -r '.data.id')

# Process with tier 3 to get lower confidence
curl -X POST "http://localhost:8000/api/v1/invoices/$INVOICE_ID/extract?force_tier=3" \
  -H "Authorization: Bearer $TOKEN" | jq

# Verify requires_review flag
curl -X GET "http://localhost:8000/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.data | {requires_review, review_priority, overall_confidence}'

# Check if it appears in review queue
curl -X GET "http://localhost:8000/api/v1/invoices/queue/review" \
  -H "Authorization: Bearer $TOKEN" | jq '.data[] | select(.id == "'$INVOICE_ID'")'
```

---

### Scenario 3: Tier Escalation

**Goal:** Verify automatic tier escalation

```bash
# Mock Tier 1 returns confidence 0.92 → escalates to Tier 2
# Mock Tier 2 returns confidence 0.87 → escalates to Tier 3
# Mock Tier 3 returns confidence 0.96 → completes successfully

INVOICE_ID=$(curl -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@moderate_invoice.pdf" | jq -r '.data.id')

# Process without forcing tier (auto-escalation)
curl -X POST "http://localhost:8000/api/v1/invoices/$INVOICE_ID/extract" \
  -H "Authorization: Bearer $TOKEN" | jq

# Check processing history for multiple tiers
curl -X GET "http://localhost:8000/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.processing_history'
# Expected: Array with tier1, tier2, tier3 attempts (in mock: only final tier shown)
```

---

### Scenario 4: e-Invoice JSON Ingestion

**Goal:** Ingest official e-Invoice with 100% confidence

```bash
# Ingest e-Invoice JSON
curl -X POST http://localhost:8000/api/v1/invoices/ingest-json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "einvoice_json": {
      "irn": "SAMPLE-IRN-12345678901234567890123456789012345678901234567890",
      "seller_gstin": "29ABCDE1234F1Z5",
      "buyer_gstin": "27XYZAB9876C2D4",
      "doc_no": "INV/2024/TEST001",
      "doc_date": "15/01/2024",
      "doc_type": "INV",
      "seller_legal_name": "Test Corp",
      "total_value": 100000.00
    }
  }' | jq

# Verify confidence is 1.0 and status is 'extracted'
EINVOICE_ID=$(curl -X POST http://localhost:8000/api/v1/invoices/ingest-json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"einvoice_json": {...}}' | jq -r '.data.id')

curl -X GET "http://localhost:8000/api/v1/invoices/$EINVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.data | {overall_confidence, source_type, irn}'
# Expected: {"overall_confidence": 1.0, "source_type": "einvoice_json", "irn": "..."}
```

---

## Troubleshooting

### Issue: "Failed to upload invoice"

**Possible causes:**
- File size > 10MB
- Invalid file type (must be PDF, JPG, PNG)
- GCS bucket not configured
- Missing authentication token

**Solution:**
```bash
# Check file size
ls -lh invoice.pdf

# Verify file type
file invoice.pdf

# Test authentication
curl -X GET http://localhost:8000/api/v1/users/me \
  -H "Authorization: Bearer $TOKEN"
```

---

### Issue: "Invoice not found"

**Cause:** Invalid invoice ID or not owned by your organization

**Solution:**
```bash
# List your invoices to get valid IDs
curl -X GET http://localhost:8000/api/v1/invoices \
  -H "Authorization: Bearer $TOKEN" | jq '.data[].id'
```

---

### Issue: Processing stuck in "processing" status

**Cause:** Mock service should complete instantly. Check logs for errors.

**Solution:**
```bash
# Check backend logs
docker logs clarity-api

# Manually check invoice status
curl -X GET "http://localhost:8000/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" | jq '.data.status'
```

---

### Issue: Review queue always empty

**Cause:** Mock service generates high confidence by default

**Solution:**
```bash
# Force tier 3 to get lower confidence (may still be > 0.85)
# Note: Mock service is designed for demo, adjust confidence ranges in
# clarity-api/app/services/extraction_service.py lines 127-132
```

---

### Issue: e-Invoice JSON validation fails

**Cause:** Missing mandatory fields or invalid GSTIN format

**Solution:**
```bash
# Verify all mandatory fields present:
# - irn (64 chars)
# - seller_gstin (15 chars)
# - buyer_gstin (15 chars)
# - doc_no
# - doc_date (DD/MM/YYYY format)
# - doc_type

# Example valid JSON:
{
  "irn": "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2",
  "seller_gstin": "29ABCDE1234F1Z5",
  "buyer_gstin": "27XYZAB9876C2D4",
  "doc_no": "INV-001",
  "doc_date": "15/01/2024",
  "doc_type": "INV"
}
```

---

## Performance Metrics

### Expected Processing Times (Mock)

- **Tier 1 (Gemini Flash)**: 800-1500ms
- **Tier 2 (Preprocessing)**: 2000-3500ms
- **Tier 3 (GPT-4V)**: 3000-5000ms

### Confidence Distribution (Mock)

- **Tier 1**: 92-98% confidence
- **Tier 2**: 88-95% confidence
- **Tier 3**: 85-92% confidence

### Cost Tracking (Mock)

- **Tier 1**: $0.0015 per invoice
- **Tier 2**: $0.0015 per invoice (Gemini retry)
- **Tier 3**: $0.0200 per invoice (GPT-4V)

View metrics in `extraction_metrics` table.

---

## Summary Checklist

- [ ] Upload invoice via API
- [ ] Upload invoice via UI
- [ ] Process invoice with AI
- [ ] View extraction results with confidence scores
- [ ] Test tier escalation (force_tier parameter)
- [ ] Verify review queue for low-confidence invoices
- [ ] Filter review queue by priority
- [ ] Update/correct extracted data
- [ ] Ingest e-Invoice JSON only
- [ ] Ingest PDF + e-Invoice JSON pair
- [ ] Test all UI components (badges, rings, buttons)
- [ ] Verify per-field confidence display
- [ ] Check processing history timeline

---

## Next Steps

**For Production:**

1. Replace mock extraction service with real AI APIs:
   - Integrate Google Gemini 1.5 Flash
   - Add OpenCV/PIL preprocessing
   - Connect GPT-4V API

2. Set up background task queue (Celery/Redis)

3. Implement QR code decoding for e-Invoices

4. Add anomaly detection (cross-validation between PDF and JSON)

5. Create admin dashboard for monitoring metrics

6. Set up cost alerts and optimization rules

**For Testing:**

- Prepare dataset of 100+ real invoices (varied quality)
- Run load tests (1000 concurrent extractions)
- Measure accuracy against ground truth
- Tune confidence thresholds based on real data

---

**Questions or Issues?**

Check logs:
```bash
# Backend
docker logs -f clarity-api

# Frontend
npm run dev # Check terminal output
```

Or open an issue on GitHub: https://github.com/wolvio-cloud/AP-Agent/issues
