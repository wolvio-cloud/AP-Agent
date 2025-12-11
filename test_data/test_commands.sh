#!/bin/bash

# Phase 4 Test Commands
# Set your token first: export TOKEN='your_access_token'

# Login and Get Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser@acme.com" \
  -d "password=yourpassword" \
  | jq -r '.access_token'

# Upload Invoice PDF
curl -X POST http://localhost:8000/api/v1/invoices/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test_invoice.pdf" \
  | jq

# Process Invoice with AI
curl -X POST http://localhost:8000/api/v1/invoices/$INVOICE_ID/extract \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Get Invoice Details
curl -X GET http://localhost:8000/api/v1/invoices/$INVOICE_ID \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Get Review Queue
curl -X GET http://localhost:8000/api/v1/invoices/queue/review \
  -H "Authorization: Bearer $TOKEN" \
  | jq

# Ingest e-Invoice JSON
curl -X POST http://localhost:8000/api/v1/invoices/ingest-json \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
  "einvoice_json": {
    "irn": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaabbbbbbbbbbbbbbbbbbbbbb0000000001",
    "seller_gstin": "29ABCDE1234F1Z5",
    "buyer_gstin": "27BUYER5678A1B2",
    "doc_no": "INV/2025/0001",
    "doc_date": "10/12/2025",
    "doc_type": "INV",
    "seller_legal_name": "Acme Construction Supplies Pvt Ltd",
    "seller_trade_name": "Acme Supplies",
    "seller_address": "123 Builder Street",
    "seller_location": "Mumbai",
    "seller_pincode": "400001",
    "seller_state_code": "27",
    "buyer_legal_name": "Test Buyer Corporation",
    "buyer_address": "456 Buyer Street",
    "buyer_location": "Mumbai",
    "buyer_pincode": "400002",
    "buyer_state_code": "27",
    "total_value": 129800.0,
    "taxable_value": 110000.0,
    "cgst_value": 9900.0,
    "sgst_value": 9900.0,
    "igst_value": 0.0,
    "supply_type": "B2B",
    "reverse_charge": false,
    "item_list": [
      {
        "item_no": 1,
        "description": "Construction Materials",
        "hsn_code": "6810",
        "quantity": 100,
        "unit": "KG",
        "unit_price": 660.0,
        "taxable_value": 66000.0,
        "cgst_rate": 9.0,
        "sgst_rate": 9.0,
        "total_value": 77880.0
      },
      {
        "item_no": 2,
        "description": "Installation Services",
        "hsn_code": "9954",
        "quantity": 1,
        "unit": "LOT",
        "unit_price": 44000.0,
        "taxable_value": 44000.0,
        "cgst_rate": 9.0,
        "sgst_rate": 9.0,
        "total_value": 51920.0
      }
    ]
  }
}' \
  | jq

