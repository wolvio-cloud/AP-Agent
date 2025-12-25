# Global Invoice Testing Guide

## Overview

This guide provides instructions for testing the ClarityAP invoice processing system with international invoice samples from different countries.

## Test Invoice Samples

### 1. Indian GST Invoice (`invoice-india-gst.txt`)
**Region:** India
**Tax Type:** GST (Goods and Services Tax)
**Currency:** INR (₹)
**Tax Rate:** 18% (9% CGST + 9% SGST)

**Key Fields to Test:**
- GSTIN: 29AABCT1332L1Z5
- PAN: AABCT1332L
- Invoice Number: INV-2024-001
- Total Amount: ₹4,86,750
- Line Items: 5 items with HSN codes

**Expected Extraction:**
```json
{
  "vendor_name": "ABC Electronics Pvt Ltd",
  "invoice_number": "INV-2024-001",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-14",
  "subtotal": 412500,
  "tax_amount": 74250,
  "tax_type": "GST",
  "tax_percentage": 18,
  "total_amount": 486750,
  "currency": "INR",
  "gstin": "29AABCT1332L1Z5",
  "pan": "AABCT1332L",
  "line_items": [
    {
      "description": "Dell Laptop - Latitude 7420",
      "quantity": 5,
      "rate": 65000,
      "amount": 325000
    },
    // ... 4 more items
  ]
}
```

### 2. US Sales Tax Invoice (`invoice-us-sales-tax.txt`)
**Region:** United States
**Tax Type:** Sales Tax
**Currency:** USD ($)
**Tax Rate:** 8.25% (California)

**Key Fields to Test:**
- Tax ID: 94-1234567
- Invoice Number: US-2024-0045
- Total Amount: $15,125.77
- Line Items: 5 items

**Expected Extraction:**
```json
{
  "vendor_name": "TechSupply Inc.",
  "invoice_number": "US-2024-0045",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-14",
  "subtotal": 13973.00,
  "tax_amount": 1152.77,
  "tax_type": "Sales Tax",
  "tax_percentage": 8.25,
  "total_amount": 15125.77,
  "currency": "USD",
  "line_items": [
    {
      "description": "MacBook Pro 16\" M3 Max",
      "quantity": 3,
      "rate": 3499.00,
      "amount": 10497.00
    },
    // ... 4 more items
  ]
}
```

### 3. EU VAT Invoice (`invoice-eu-vat.txt`)
**Region:** European Union (Germany)
**Tax Type:** VAT (Value Added Tax)
**Currency:** EUR (€)
**Tax Rate:** 19%

**Key Fields to Test:**
- VAT Number: DE123456789
- Invoice Number: EU-2024-0123
- Total Amount: €22,729.00
- Line Items: 6 items

**Expected Extraction:**
```json
{
  "vendor_name": "EuroTech GmbH",
  "invoice_number": "EU-2024-0123",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-14",
  "subtotal": 19100.00,
  "tax_amount": 3629.00,
  "tax_type": "VAT",
  "tax_percentage": 19,
  "total_amount": 22729.00,
  "currency": "EUR",
  "vat_number": "DE123456789",
  "line_items": [
    {
      "description": "Server Dell PowerEdge R740",
      "quantity": 2,
      "rate": 4500.00,
      "amount": 9000.00
    },
    // ... 5 more items
  ]
}
```

### 4. UK VAT Invoice (`invoice-uk-vat.txt`)
**Region:** United Kingdom
**Tax Type:** VAT (Value Added Tax)
**Currency:** GBP (£)
**Tax Rate:** 20%

**Key Fields to Test:**
- VAT Number: GB 123 4567 89
- Invoice Number: UK-2024-0089
- Total Amount: £18,124.80
- Line Items: 7 items

**Expected Extraction:**
```json
{
  "vendor_name": "British IT Solutions Ltd",
  "invoice_number": "UK-2024-0089",
  "invoice_date": "2024-01-15",
  "due_date": "2024-02-14",
  "subtotal": 15104.00,
  "tax_amount": 3020.80,
  "tax_type": "VAT",
  "tax_percentage": 20,
  "total_amount": 18124.80,
  "currency": "GBP",
  "vat_number": "GB 123 4567 89",
  "line_items": [
    {
      "description": "HP EliteBook 850 G9",
      "quantity": 6,
      "rate": 1299.00,
      "amount": 7794.00
    },
    // ... 6 more items
  ]
}
```

## Testing Workflow

### Step 1: Start the Backend Server
```bash
cd /home/user/AP-Agent
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

### Step 2: Start the Frontend Development Server
```bash
cd /home/user/AP-Agent/clarity-web
npm run dev
```

### Step 3: Test Invoice Upload & Extraction

1. **Navigate to Dashboard**
   - Open browser: http://localhost:3000
   - Login with test credentials
   - Go to Dashboard page

2. **Upload Invoice**
   - Drag and drop one of the test invoice files OR
   - Click to browse and select a test invoice
   - Wait 3-5 seconds for AI extraction

3. **Verify Extracted Data**
   - Check all fields are populated correctly
   - Verify currency matches the invoice
   - Verify tax type is correct
   - Check line items are extracted
   - Verify calculations (subtotal + tax = total)

4. **Test Region-Specific Fields**
   - **India**: Check GSTIN and PAN fields are filled
   - **EU/UK**: Check VAT number field is filled
   - **US**: Verify no region-specific fields required

### Step 4: Test Manual Editing

1. **Edit Invoice Fields**
   - Change vendor name
   - Modify amounts
   - Add/remove line items
   - Change tax percentage
   - Switch currency

2. **Verify Auto-Calculations**
   - Line item amount = quantity × rate
   - Subtotal = sum of all line items
   - Total = subtotal + tax amount

3. **Save Changes**
   - Click "Save Changes" button
   - Verify success message appears
   - Refresh page and confirm data persists

### Step 5: Test QuickBooks Export

1. **Export Single Invoice**
   - Click "Export to QuickBooks" button
   - Verify IIF file downloads
   - Open IIF file in text editor
   - Check format is correct

2. **Verify IIF Content**
   - Header section with company info
   - Transaction date and number
   - Line items with descriptions and amounts
   - Tax calculations
   - Total amount

### Step 6: Test Different Currencies

Test each currency to ensure:
- Symbol displays correctly (₹, $, €, £)
- Decimal places are correct (2 for most currencies)
- Formatting matches regional standards
- Export maintains currency information

### Step 7: Test Error Handling

1. **Invalid File Upload**
   - Try uploading non-invoice files
   - Try uploading files > 10MB
   - Verify error messages appear

2. **Required Fields**
   - Try saving without vendor name
   - Try saving without invoice number
   - Verify validation messages

3. **Network Errors**
   - Stop backend server
   - Try uploading invoice
   - Verify error handling

## Expected Results

### ✅ Pass Criteria

- All 4 test invoices upload successfully
- AI extraction completes in 3-5 seconds
- All fields populate with correct data
- Region-specific fields (GSTIN, PAN, VAT) extract correctly
- Currency symbols display properly
- Tax calculations are accurate
- Line items extract completely
- Manual edits save successfully
- QuickBooks IIF export downloads
- IIF file format is valid
- Error messages are clear and helpful

### ❌ Fail Criteria

- Extraction takes > 10 seconds
- Critical fields missing (vendor, amount, date)
- Incorrect tax calculations
- Currency symbols wrong or missing
- Line items incomplete
- Save fails silently
- Export file is corrupted
- No error handling for invalid inputs

## Test Data Summary

| Country | Invoice # | Currency | Tax Type | Tax % | Total Amount | Line Items | Special Fields |
|---------|-----------|----------|----------|-------|--------------|------------|----------------|
| 🇮🇳 India | INV-2024-001 | INR (₹) | GST | 18% | ₹4,86,750 | 5 | GSTIN, PAN |
| 🇺🇸 USA | US-2024-0045 | USD ($) | Sales Tax | 8.25% | $15,125.77 | 5 | Tax ID |
| 🇪🇺 EU | EU-2024-0123 | EUR (€) | VAT | 19% | €22,729.00 | 6 | VAT Number |
| 🇬🇧 UK | UK-2024-0089 | GBP (£) | VAT | 20% | £18,124.80 | 7 | VAT Number |

## Common Issues & Solutions

### Issue 1: AI Extraction Not Working
**Solution:** Ensure the backend AI service is running and configured with valid API keys.

### Issue 2: Currency Symbols Not Displaying
**Solution:** Check that your browser supports UTF-8 encoding and proper font rendering.

### Issue 3: Tax Calculations Incorrect
**Solution:** Verify the tax percentage field is set correctly before saving.

### Issue 4: IIF Export Empty
**Solution:** Ensure the invoice has all required fields (vendor, amount, date, number).

### Issue 5: Region-Specific Fields Not Showing
**Solution:** Select the correct tax type (GST for India, VAT for EU/UK) to reveal conditional fields.

## Performance Benchmarks

- **Upload Time:** < 2 seconds
- **AI Extraction:** 3-5 seconds
- **Save Operation:** < 1 second
- **Export Generation:** < 2 seconds
- **Page Load:** < 3 seconds

## Browser Compatibility

Test on the following browsers:
- ✅ Chrome/Edge (Chromium) - Latest
- ✅ Firefox - Latest
- ✅ Safari - Latest (macOS/iOS)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## Reporting Issues

When reporting issues, include:
1. Test invoice used
2. Browser and OS
3. Steps to reproduce
4. Expected vs actual behavior
5. Console errors (F12 Developer Tools)
6. Network request details

---

**Last Updated:** December 25, 2025
**Test Data Version:** 1.0
**Supported Regions:** India, USA, EU, UK
**Supported Currencies:** INR, USD, EUR, GBP, AUD, CAD, SGD, AED
