"""
Mock Test Data Generator for Phase 4 End-to-End Testing

This script generates realistic test data including:
- Sample invoices (multiple formats)
- e-Invoice JSON payloads
- Test curl commands
- Expected responses

Usage:
    python scripts/generate_test_data.py
"""

import json
import os
from datetime import datetime, timedelta
from decimal import Decimal


# Mock vendor data
MOCK_VENDORS = [
    {
        "name": "Acme Construction Supplies",
        "gstin": "29ABCDE1234F1Z5",
        "legal_name": "Acme Construction Supplies Pvt Ltd",
        "trade_name": "Acme Supplies",
        "address": "123 Builder Street",
        "location": "Mumbai",
        "pincode": "400001",
        "state_code": "27"
    },
    {
        "name": "Global Tech Solutions",
        "gstin": "27XYZAB9876C2D4",
        "legal_name": "Global Tech Solutions Pvt Ltd",
        "trade_name": "Global Tech",
        "address": "45 IT Park Road",
        "location": "Bangalore",
        "pincode": "560100",
        "state_code": "29"
    },
    {
        "name": "Premier Office Furniture",
        "gstin": "06MNOPQ5432G3H6",
        "legal_name": "Premier Office Furniture Ltd",
        "trade_name": "Premier Furniture",
        "address": "78 Commerce Lane",
        "location": "Delhi",
        "pincode": "110001",
        "state_code": "07"
    },
    {
        "name": "Industrial Equipment Corp",
        "gstin": "33RSTPQ8765I4J7",
        "legal_name": "Industrial Equipment Corporation",
        "trade_name": "IndEquip",
        "address": "90 Factory Road",
        "location": "Chennai",
        "pincode": "600001",
        "state_code": "33"
    },
    {
        "name": "Metro Logistics Services",
        "gstin": "24GHIJK3456K5L8",
        "legal_name": "Metro Logistics Services Pvt Ltd",
        "trade_name": "Metro Logistics",
        "address": "12 Transport Hub",
        "location": "Pune",
        "pincode": "411001",
        "state_code": "27"
    }
]


def generate_einvoice_json(vendor_index=0, invoice_num=1):
    """Generate a valid India e-Invoice JSON payload"""
    vendor = MOCK_VENDORS[vendor_index % len(MOCK_VENDORS)]
    buyer = {
        "gstin": "27BUYER5678A1B2",
        "legal_name": "Test Buyer Corporation",
        "address": "456 Buyer Street",
        "location": "Mumbai",
        "pincode": "400002",
        "state_code": "27"
    }

    doc_date = datetime.now() - timedelta(days=invoice_num)
    doc_date_str = doc_date.strftime("%d/%m/%Y")

    # Generate IRN (64 char hash-like string)
    irn = f"{'a' * 32}{'b' * 32}"[:64]
    irn = f"{irn[:-10]}{invoice_num:010d}"

    taxable_value = 100000 + (invoice_num * 10000)
    cgst = taxable_value * 0.09  # 9% CGST
    sgst = taxable_value * 0.09  # 9% SGST
    total_value = taxable_value + cgst + sgst

    return {
        "irn": irn,
        "seller_gstin": vendor["gstin"],
        "buyer_gstin": buyer["gstin"],
        "doc_no": f"INV/{datetime.now().year}/{invoice_num:04d}",
        "doc_date": doc_date_str,
        "doc_type": "INV",

        "seller_legal_name": vendor["legal_name"],
        "seller_trade_name": vendor["trade_name"],
        "seller_address": vendor["address"],
        "seller_location": vendor["location"],
        "seller_pincode": vendor["pincode"],
        "seller_state_code": vendor["state_code"],

        "buyer_legal_name": buyer["legal_name"],
        "buyer_address": buyer["address"],
        "buyer_location": buyer["location"],
        "buyer_pincode": buyer["pincode"],
        "buyer_state_code": buyer["state_code"],

        "total_value": float(total_value),
        "taxable_value": float(taxable_value),
        "cgst_value": float(cgst),
        "sgst_value": float(sgst),
        "igst_value": 0.0,

        "supply_type": "B2B",
        "reverse_charge": False,
        "item_list": [
            {
                "item_no": 1,
                "description": "Construction Materials",
                "hsn_code": "6810",
                "quantity": 100,
                "unit": "KG",
                "unit_price": float(taxable_value * 0.6 / 100),
                "taxable_value": float(taxable_value * 0.6),
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "total_value": float(taxable_value * 0.6 * 1.18)
            },
            {
                "item_no": 2,
                "description": "Installation Services",
                "hsn_code": "9954",
                "quantity": 1,
                "unit": "LOT",
                "unit_price": float(taxable_value * 0.4),
                "taxable_value": float(taxable_value * 0.4),
                "cgst_rate": 9.0,
                "sgst_rate": 9.0,
                "total_value": float(taxable_value * 0.4 * 1.18)
            }
        ]
    }


def generate_test_curl_commands(base_url="http://localhost:8000"):
    """Generate curl commands for testing"""
    commands = []

    # 1. Login
    commands.append({
        "name": "Login and Get Token",
        "command": f"""curl -X POST {base_url}/api/v1/auth/login \\
  -H "Content-Type: application/x-www-form-urlencoded" \\
  -d "username=testuser@acme.com" \\
  -d "password=yourpassword" \\
  | jq -r '.access_token'"""
    })

    # 2. Upload Invoice
    commands.append({
        "name": "Upload Invoice PDF",
        "command": f"""curl -X POST {base_url}/api/v1/invoices/upload \\
  -H "Authorization: Bearer $TOKEN" \\
  -F "file=@test_invoice.pdf" \\
  | jq"""
    })

    # 3. Extract Invoice
    commands.append({
        "name": "Process Invoice with AI",
        "command": f"""curl -X POST {base_url}/api/v1/invoices/$INVOICE_ID/extract \\
  -H "Authorization: Bearer $TOKEN" \\
  | jq"""
    })

    # 4. Get Invoice Detail
    commands.append({
        "name": "Get Invoice Details",
        "command": f"""curl -X GET {base_url}/api/v1/invoices/$INVOICE_ID \\
  -H "Authorization: Bearer $TOKEN" \\
  | jq"""
    })

    # 5. Review Queue
    commands.append({
        "name": "Get Review Queue",
        "command": f"""curl -X GET {base_url}/api/v1/invoices/queue/review \\
  -H "Authorization: Bearer $TOKEN" \\
  | jq"""
    })

    # 6. Ingest e-Invoice JSON
    einvoice = generate_einvoice_json(0, 1)
    commands.append({
        "name": "Ingest e-Invoice JSON",
        "command": f"""curl -X POST {base_url}/api/v1/invoices/ingest-json \\
  -H "Authorization: Bearer $TOKEN" \\
  -H "Content-Type: application/json" \\
  -d '{json.dumps({"einvoice_json": einvoice}, indent=2)}' \\
  | jq"""
    })

    return commands


def generate_test_scenarios():
    """Generate complete test scenarios"""
    scenarios = []

    # Scenario 1: High Confidence
    scenarios.append({
        "name": "Scenario 1: High Confidence Invoice (Auto-Approved)",
        "description": "Clear, well-formatted invoice that gets high confidence and auto-approval",
        "steps": [
            "Upload clear PDF invoice",
            "Process with tier 1 (Gemini Flash)",
            "Expect confidence >= 0.95",
            "Status should be 'extracted'",
            "Should NOT appear in review queue"
        ],
        "expected_result": {
            "status": "extracted",
            "processing_tier": "completed",
            "overall_confidence": ">= 0.95",
            "requires_review": False
        }
    })

    # Scenario 2: Medium Confidence
    scenarios.append({
        "name": "Scenario 2: Medium Confidence (Tier Escalation)",
        "description": "Invoice with some unclear elements that triggers tier escalation",
        "steps": [
            "Upload slightly blurry invoice",
            "Process with tier 1 (confidence 0.92)",
            "Auto-escalate to tier 2 (preprocessing)",
            "If still < 0.95, escalate to tier 3 (GPT-4V)",
            "Final confidence should be >= 0.85"
        ],
        "expected_result": {
            "status": "extracted",
            "processing_tier": "tier2 or tier3",
            "overall_confidence": "0.85 - 0.94",
            "requires_review": False,
            "processing_history": "Multiple tier attempts"
        }
    })

    # Scenario 3: Low Confidence
    scenarios.append({
        "name": "Scenario 3: Low Confidence (Human Review)",
        "description": "Poor quality invoice that requires human review",
        "steps": [
            "Upload very blurry or handwritten invoice",
            "Process through all tiers",
            "All tiers return confidence < 0.85",
            "Route to human review queue"
        ],
        "expected_result": {
            "status": "requires_review",
            "processing_tier": "tier4",
            "overall_confidence": "< 0.85",
            "requires_review": True,
            "review_priority": "high/medium/low"
        }
    })

    # Scenario 4: e-Invoice
    scenarios.append({
        "name": "Scenario 4: e-Invoice JSON Ingestion",
        "description": "Official e-Invoice JSON with 100% confidence",
        "steps": [
            "Submit e-Invoice JSON payload",
            "Validate IRN, GSTIN, mandatory fields",
            "Parse date (DD/MM/YYYY)",
            "Extract all fields from JSON",
            "Set confidence to 1.0 (100%)"
        ],
        "expected_result": {
            "status": "extracted",
            "source_type": "einvoice_json",
            "processing_tier": "completed",
            "overall_confidence": "1.0",
            "requires_review": False
        }
    })

    return scenarios


def main():
    """Generate all test data"""
    output_dir = "test_data"
    os.makedirs(output_dir, exist_ok=True)

    print("Generating mock test data for Phase 4...")

    # 1. Generate e-Invoice JSON samples
    print("\n1. Generating e-Invoice JSON samples...")
    for i in range(5):
        einvoice = generate_einvoice_json(i, i + 1)
        filename = f"{output_dir}/einvoice_sample_{i+1}.json"
        with open(filename, 'w') as f:
            json.dump(einvoice, f, indent=2)
        print(f"   Created: {filename}")

    # 2. Generate curl commands
    print("\n2. Generating test curl commands...")
    commands = generate_test_curl_commands()
    with open(f"{output_dir}/test_commands.sh", 'w') as f:
        f.write("#!/bin/bash\n\n")
        f.write("# Phase 4 Test Commands\n")
        f.write("# Set your token first: export TOKEN='your_access_token'\n\n")
        for cmd in commands:
            f.write(f"# {cmd['name']}\n")
            f.write(f"{cmd['command']}\n\n")
    print(f"   Created: {output_dir}/test_commands.sh")

    # 3. Generate test scenarios
    print("\n3. Generating test scenarios...")
    scenarios = generate_test_scenarios()
    with open(f"{output_dir}/test_scenarios.json", 'w') as f:
        json.dump(scenarios, f, indent=2)
    print(f"   Created: {output_dir}/test_scenarios.json")

    # 4. Generate README
    print("\n4. Generating test data README...")
    with open(f"{output_dir}/README.md", 'w') as f:
        f.write("# Phase 4 Test Data\n\n")
        f.write("This directory contains mock test data for end-to-end testing.\n\n")
        f.write("## Files\n\n")
        f.write("- `einvoice_sample_*.json` - Sample e-Invoice JSON payloads\n")
        f.write("- `test_commands.sh` - Curl commands for API testing\n")
        f.write("- `test_scenarios.json` - Complete test scenarios\n\n")
        f.write("## Usage\n\n")
        f.write("1. Start backend: `cd clarity-api && python -m uvicorn app.main:app --reload`\n")
        f.write("2. Get auth token: See test_commands.sh\n")
        f.write("3. Run test commands: `export TOKEN='...' && bash test_commands.sh`\n")
    print(f"   Created: {output_dir}/README.md")

    print(f"\n✅ All test data generated in '{output_dir}/' directory")
    print("\nNext steps:")
    print("1. Start the backend server")
    print("2. Run: export TOKEN=$(curl ... | jq -r '.access_token')")
    print("3. Execute test commands from test_commands.sh")


if __name__ == "__main__":
    main()
