#!/bin/bash

# ClarityAP - End-to-End Integration Tests
# Tests the complete API flow programmatically

set -e

echo "========================================="
echo "ClarityAP - E2E Integration Tests"
echo "========================================="
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

API_URL="http://localhost:8000"
TEST_EMAIL="test-$(date +%s)@example.com"
TEST_PASSWORD="TestPassword123!"
TOKEN=""
INVOICE_ID=""

print_test() {
    echo -e "${BLUE}[TEST]${NC} $1"
}

print_pass() {
    echo -e "${GREEN}[PASS]${NC} $1"
}

print_fail() {
    echo -e "${RED}[FAIL]${NC} $1"
    exit 1
}

# Check if server is running
print_test "Checking if API server is running..."
if curl -s "$API_URL/docs" > /dev/null; then
    print_pass "API server is running at $API_URL"
else
    print_fail "API server not running! Start it with: uvicorn app.main:app --reload"
fi

echo ""
echo "========================================="
echo "Test 1: User Registration"
echo "========================================="
print_test "Registering new user: $TEST_EMAIL"

REGISTER_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d "{
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"first_name\": \"Test\",
    \"last_name\": \"User\",
    \"company_name\": \"Test Company\"
  }")

if echo "$REGISTER_RESPONSE" | grep -q "email"; then
    print_pass "User registration successful"
else
    print_fail "User registration failed: $REGISTER_RESPONSE"
fi

echo ""
echo "========================================="
echo "Test 2: User Login"
echo "========================================="
print_test "Logging in user: $TEST_EMAIL"

LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=$TEST_EMAIL&password=$TEST_PASSWORD")

TOKEN=$(echo "$LOGIN_RESPONSE" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    print_pass "Login successful, token obtained"
else
    print_fail "Login failed: $LOGIN_RESPONSE"
fi

echo ""
echo "========================================="
echo "Test 3: Get Current User"
echo "========================================="
print_test "Fetching current user info..."

ME_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN")

if echo "$ME_RESPONSE" | grep -q "$TEST_EMAIL"; then
    print_pass "User info retrieved successfully"
else
    print_fail "Failed to get user info: $ME_RESPONSE"
fi

echo ""
echo "========================================="
echo "Test 4: Upload Invoice"
echo "========================================="
print_test "Uploading test invoice..."

# Create a test invoice file
TEST_INVOICE_FILE="/tmp/test_invoice.txt"
cat > "$TEST_INVOICE_FILE" << 'EOF'
INVOICE

Test Vendor Inc.
123 Test Street
Test City, TC 12345

Bill To:
Test Customer
456 Customer Ave
Customer City, CC 67890

Invoice Number: TEST-001
Invoice Date: January 15, 2024
Due Date: February 15, 2024

Description               Qty    Rate      Amount
-------------------------------------------------
Test Product A             2    $100.00    $200.00
Test Product B             1    $150.00    $150.00

                          Subtotal: $350.00
                         Sales Tax: $28.00
                             Total: $378.00
EOF

UPLOAD_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/invoices/upload" \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@$TEST_INVOICE_FILE")

INVOICE_ID=$(echo "$UPLOAD_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

if [ -n "$INVOICE_ID" ]; then
    print_pass "Invoice uploaded successfully, ID: $INVOICE_ID"
else
    print_fail "Invoice upload failed: $UPLOAD_RESPONSE"
fi

# Clean up test file
rm -f "$TEST_INVOICE_FILE"

echo ""
echo "========================================="
echo "Test 5: Get Invoice List"
echo "========================================="
print_test "Fetching all invoices..."

LIST_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/invoices" \
  -H "Authorization: Bearer $TOKEN")

if echo "$LIST_RESPONSE" | grep -q "$INVOICE_ID"; then
    print_pass "Invoice list retrieved successfully"
else
    print_fail "Failed to get invoice list: $LIST_RESPONSE"
fi

echo ""
echo "========================================="
echo "Test 6: Get Single Invoice"
echo "========================================="
print_test "Fetching invoice: $INVOICE_ID"

GET_RESPONSE=$(curl -s -X GET "$API_URL/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$GET_RESPONSE" | grep -q "TEST-001"; then
    print_pass "Single invoice retrieved successfully"
else
    print_fail "Failed to get invoice: $GET_RESPONSE"
fi

echo ""
echo "========================================="
echo "Test 7: Update Invoice"
echo "========================================="
print_test "Updating invoice..."

UPDATE_RESPONSE=$(curl -s -X PUT "$API_URL/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"vendor_name\": \"Updated Vendor Inc.\",
    \"invoice_number\": \"TEST-001-UPDATED\",
    \"invoice_date\": \"2024-01-15\",
    \"due_date\": \"2024-02-15\",
    \"subtotal\": 350.00,
    \"tax_amount\": 28.00,
    \"tax_type\": \"Sales Tax\",
    \"tax_percentage\": 8.0,
    \"total_amount\": 378.00,
    \"currency\": \"USD\",
    \"status\": \"reviewed\",
    \"line_items\": [
      {
        \"description\": \"Test Product A\",
        \"quantity\": 2,
        \"rate\": 100.00,
        \"amount\": 200.00
      }
    ]
  }")

if echo "$UPDATE_RESPONSE" | grep -q "Updated Vendor"; then
    print_pass "Invoice updated successfully"
else
    print_fail "Invoice update failed: $UPDATE_RESPONSE"
fi

echo ""
echo "========================================="
echo "Test 8: Export Invoice to IIF"
echo "========================================="
print_test "Exporting invoice to QuickBooks IIF format..."

IIF_FILE="/tmp/test_export_$INVOICE_ID.iif"
curl -s -X GET "$API_URL/api/v1/quickbooks/export/iif/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$IIF_FILE"

if [ -f "$IIF_FILE" ] && [ -s "$IIF_FILE" ]; then
    if grep -q "!TRNS" "$IIF_FILE"; then
        print_pass "IIF export successful, file created at $IIF_FILE"
        echo "First few lines of IIF file:"
        head -n 10 "$IIF_FILE"
    else
        print_fail "IIF file format invalid"
    fi
else
    print_fail "IIF export failed"
fi

echo ""
echo "========================================="
echo "Test 9: Export Batch IIF"
echo "========================================="
print_test "Exporting batch IIF..."

BATCH_FILE="/tmp/test_batch_export.iif"
curl -s -X POST "$API_URL/api/v1/quickbooks/export/iif/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"invoice_ids\": [\"$INVOICE_ID\"]}" \
  -o "$BATCH_FILE"

if [ -f "$BATCH_FILE" ] && [ -s "$BATCH_FILE" ]; then
    print_pass "Batch IIF export successful"
else
    print_fail "Batch IIF export failed"
fi

echo ""
echo "========================================="
echo "Test 10: Export CSV"
echo "========================================="
print_test "Exporting all invoices to CSV..."

CSV_FILE="/tmp/test_export.csv"
curl -s -X GET "$API_URL/api/v1/quickbooks/export/csv" \
  -H "Authorization: Bearer $TOKEN" \
  -o "$CSV_FILE"

if [ -f "$CSV_FILE" ] && [ -s "$CSV_FILE" ]; then
    print_pass "CSV export successful, file created at $CSV_FILE"
    echo "CSV headers:"
    head -n 1 "$CSV_FILE"
else
    print_fail "CSV export failed"
fi

echo ""
echo "========================================="
echo "Test 11: Delete Invoice"
echo "========================================="
print_test "Deleting invoice: $INVOICE_ID"

DELETE_RESPONSE=$(curl -s -X DELETE "$API_URL/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN")

# Verify deletion by trying to get the invoice
VERIFY_DELETE=$(curl -s -X GET "$API_URL/api/v1/invoices/$INVOICE_ID" \
  -H "Authorization: Bearer $TOKEN")

if echo "$VERIFY_DELETE" | grep -q "not found"; then
    print_pass "Invoice deleted successfully"
else
    print_fail "Invoice deletion failed"
fi

echo ""
echo "========================================="
echo "Test 12: International Invoice (India)"
echo "========================================="
print_test "Testing Indian GST invoice..."

INDIA_INVOICE_FILE="/home/user/AP-Agent/test_data/invoice-india-gst.txt"
if [ -f "$INDIA_INVOICE_FILE" ]; then
    INDIA_RESPONSE=$(curl -s -X POST "$API_URL/api/v1/invoices/upload" \
      -H "Authorization: Bearer $TOKEN" \
      -F "file=@$INDIA_INVOICE_FILE")

    INDIA_ID=$(echo "$INDIA_RESPONSE" | grep -o '"id":"[^"]*' | cut -d'"' -f4)

    if [ -n "$INDIA_ID" ]; then
        print_pass "Indian invoice uploaded successfully"

        # Get the invoice to verify GSTIN and PAN fields
        INDIA_GET=$(curl -s -X GET "$API_URL/api/v1/invoices/$INDIA_ID" \
          -H "Authorization: Bearer $TOKEN")

        if echo "$INDIA_GET" | grep -q "GSTIN\|gstin"; then
            print_pass "GSTIN field extracted"
        fi

        if echo "$INDIA_GET" | grep -q "PAN\|pan"; then
            print_pass "PAN field extracted"
        fi

        # Clean up
        curl -s -X DELETE "$API_URL/api/v1/invoices/$INDIA_ID" \
          -H "Authorization: Bearer $TOKEN" > /dev/null
    else
        print_fail "Indian invoice upload failed"
    fi
else
    print_fail "Indian test invoice not found at $INDIA_INVOICE_FILE"
fi

echo ""
echo "========================================="
echo "✅ All Integration Tests Complete!"
echo "========================================="
echo ""
echo "Summary:"
echo "  ✓ User Registration & Authentication"
echo "  ✓ Invoice Upload & Extraction"
echo "  ✓ Invoice CRUD Operations"
echo "  ✓ QuickBooks IIF Export (Single & Batch)"
echo "  ✓ CSV Export"
echo "  ✓ International Invoice Support"
echo ""
echo "Exported files:"
echo "  - IIF: $IIF_FILE"
echo "  - Batch IIF: $BATCH_FILE"
echo "  - CSV: $CSV_FILE"
echo ""
print_pass "Integration testing successful! Ready for SaaS deployment."
