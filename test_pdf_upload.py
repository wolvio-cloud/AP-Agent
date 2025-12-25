#!/usr/bin/env python3
"""Test PDF invoice upload and extraction accuracy"""

import requests
from pathlib import Path
import sys

BASE_URL = "http://localhost:8000/api/v1"

def test_pdf_upload(pdf_path, token):
    """Upload PDF and check extraction quality"""

    print(f"\n{'='*70}")
    print(f"PDF INVOICE TEST")
    print(f"{'='*70}\n")
    print(f"File: {pdf_path}")
    print(f"Size: {pdf_path.stat().st_size / 1024:.1f} KB\n")

    headers = {"Authorization": f"Bearer {token}"}

    with open(pdf_path, 'rb') as f:
        files = {'file': (pdf_path.name, f, 'application/pdf')}

        print("Uploading PDF... ", end='', flush=True)
        response = requests.post(
            f"{BASE_URL}/invoices/upload",
            files=files,
            headers=headers
        )

    if response.status_code != 200:
        print(f"✗ FAILED")
        print(f"Status: {response.status_code}")
        print(f"Error: {response.text}")
        return False

    print("✓ SUCCESS\n")

    data = response.json()
    invoice_id = data.get("id")
    extracted = data.get("extracted_json", {})

    print(f"Invoice ID: {invoice_id}\n")
    print("EXTRACTED DATA:")
    print("-" * 70)

    # Display all extracted fields
    fields = [
        "vendor_name",
        "invoice_number",
        "invoice_date",
        "due_date",
        "total_amount",
        "subtotal",
        "tax_amount",
        "currency"
    ]

    for field in fields:
        value = extracted.get(field, "NOT FOUND")
        print(f"  {field:20s}: {value}")

    # Line items
    line_items = extracted.get("line_items", [])
    if line_items:
        print(f"\n  Line Items ({len(line_items)}):")
        for i, item in enumerate(line_items[:5], 1):  # Show first 5
            desc = item.get("description", "N/A")[:40]
            amt = item.get("amount", "N/A")
            print(f"    {i}. {desc}: {amt}")

    # Confidence score
    confidence = data.get("overall_confidence", 0)
    print(f"\n  Confidence Score: {confidence:.2%}")

    # Quality assessment
    print(f"\n{'='*70}")
    print("QUALITY ASSESSMENT:")
    print("-" * 70)

    has_vendor = extracted.get("vendor_name") is not None
    has_number = extracted.get("invoice_number") is not None
    has_amount = extracted.get("total_amount") is not None
    has_date = extracted.get("invoice_date") is not None

    required_fields = sum([has_vendor, has_number, has_amount, has_date])
    completeness = required_fields / 4 * 100

    print(f"  Vendor Name:      {'✓ Found' if has_vendor else '✗ Missing'}")
    print(f"  Invoice Number:   {'✓ Found' if has_number else '✗ Missing'}")
    print(f"  Total Amount:     {'✓ Found' if has_amount else '✗ Missing'}")
    print(f"  Invoice Date:     {'✓ Found' if has_date else '✗ Missing'}")
    print(f"\n  Completeness:     {completeness:.0f}%")
    print(f"  Confidence:       {confidence:.0f}%")

    # Overall pass/fail
    passed = completeness >= 75 and confidence >= 0.70

    print(f"\n{'='*70}")
    if passed:
        print("✓ PDF EXTRACTION: PASSED")
        print("Quality is acceptable for MVP beta testing")
    else:
        print("✗ PDF EXTRACTION: NEEDS IMPROVEMENT")
        print(f"Target: 75%+ completeness, 70%+ confidence")
        print(f"Actual: {completeness:.0f}% completeness, {confidence:.0f}% confidence")
    print(f"{'='*70}\n")

    return passed

if __name__ == "__main__":
    # Get token from previous test or login
    token_file = Path("test_token.txt")

    if not token_file.exists():
        print("Getting auth token...")
        # Login to get token
        login_data = {
            "email": "test@example.com",
            "password": "Test123456"
        }
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token = response.json()["access_token"]
            token_file.write_text(token)
        else:
            print("Failed to get token. Run main test suite first.")
            sys.exit(1)

    token = token_file.read_text().strip()

    # Find PDF file
    pdf_files = list(Path(".").glob("*.pdf"))

    if not pdf_files:
        print("No PDF files found. Please add a PDF invoice to test.")
        sys.exit(1)

    pdf_path = pdf_files[0]
    test_pdf_upload(pdf_path, token)
