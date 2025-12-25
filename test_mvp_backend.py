#!/usr/bin/env python3
"""
ClarityAP MVP Backend Test Suite
Tests the 5 core modules: Auth, Invoice Upload, Extraction, Export, CRUD
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path

BASE_URL = "http://localhost:8000/api/v1"
RESULTS = []

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def log_test(test_num, name, passed, details=""):
    symbol = f"{Colors.GREEN}✓{Colors.END}" if passed else f"{Colors.RED}✗{Colors.END}"
    status = "PASS" if passed else "FAIL"
    result = f"{symbol} TEST {test_num}: {name} - {status}"
    if details:
        result += f"\n   {Colors.BLUE}→{Colors.END} {details}"
    print(result)
    RESULTS.append({
        "test": f"TEST {test_num}: {name}",
        "passed": passed,
        "details": details
    })

def print_summary():
    print("\n" + "="*70)
    print(f"{Colors.BLUE}TEST SUMMARY{Colors.END}")
    print("="*70)
    passed = sum(1 for r in RESULTS if r['passed'])
    total = len(RESULTS)
    percentage = (passed / total * 100) if total > 0 else 0

    print(f"\nTests Passed: {passed}/{total} ({percentage:.0f}%)")

    if percentage >= 90:
        print(f"\n{Colors.GREEN}✓ BACKEND IS PRODUCTION READY{Colors.END}")
        print("Next: Build frontend (3 days)")
    elif percentage >= 70:
        print(f"\n{Colors.YELLOW}⚠ BACKEND NEEDS MINOR FIXES{Colors.END}")
        print("Action: Fix failing tests, then build frontend")
    else:
        print(f"\n{Colors.RED}✗ BACKEND HAS SERIOUS ISSUES{Colors.END}")
        print("Action: Debug and fix before building frontend")

    print("\nFailed tests:")
    for r in RESULTS:
        if not r['passed']:
            print(f"  - {r['test']}")

    print("="*70 + "\n")

def main():
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}ClarityAP MVP Backend Test Suite{Colors.END}")
    print(f"{Colors.BLUE}Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")

    # Global variables for test data
    global token, invoice_id
    token = None
    invoice_id = None

    # TEST 1: User Registration
    print(f"\n{Colors.YELLOW}>>> PHASE 1: Authentication{Colors.END}\n")

    register_data = {
        "email": f"test_{int(time.time())}@example.com",
        "password": "Test123456",
        "first_name": "Test",
        "last_name": "User",
        "company_name": "Test Corp"
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        passed = response.status_code in [200, 201]
        details = f"Status: {response.status_code}"
        if passed:
            data = response.json()
            details += f", User ID: {data.get('id', 'N/A')[:8]}..."
        else:
            details += f", Error: {response.text[:100]}"
        log_test(1, "User Registration", passed, details)
    except Exception as e:
        log_test(1, "User Registration", False, f"Exception: {str(e)}")
        return

    # TEST 2: User Login
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"]
    }

    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        passed = response.status_code == 200
        if passed:
            data = response.json()
            token = data.get("access_token")
            details = f"Token received: {token[:20]}..."
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"
        log_test(2, "User Login", passed, details)

        if not token:
            print(f"{Colors.RED}Cannot continue without valid token{Colors.END}")
            return
    except Exception as e:
        log_test(2, "User Login", False, f"Exception: {str(e)}")
        return

    headers = {"Authorization": f"Bearer {token}"}

    # TEST 3: Protected Endpoint Access
    try:
        response = requests.get(f"{BASE_URL}/invoices", headers=headers)
        passed = response.status_code in [200, 404]  # 404 is ok if no invoices yet
        details = f"Status: {response.status_code}"
        log_test(3, "JWT Token Works", passed, details)
    except Exception as e:
        log_test(3, "JWT Token Works", False, f"Exception: {str(e)}")

    # TEST 4: Invoice Upload & Extraction
    print(f"\n{Colors.YELLOW}>>> PHASE 2: Invoice Processing{Colors.END}\n")

    # Check if test invoice exists
    test_file = Path("test-invoice-office-depot.txt")
    if not test_file.exists():
        # Create it
        invoice_content = """INVOICE

Vendor: Office Depot
Invoice Number: OD-2024-1234
Invoice Date: December 10, 2024
Due Date: January 9, 2025

ITEMS:
- Copy Paper (10 reams @ $45.00) .......... $450.00
- Pens (5 boxes @ $12.00) ................. $60.00
- Stapler ................................. $25.00

                              Subtotal: $535.00
                         Sales Tax 8.5%: $45.48
                                ---------------
                         TOTAL AMOUNT: $580.48

Payment Terms: Net 30 Days
"""
        test_file.write_text(invoice_content)

    try:
        start_time = time.time()
        with open(test_file, 'rb') as f:
            files = {'file': ('test-invoice.txt', f, 'text/plain')}
            response = requests.post(
                f"{BASE_URL}/invoices/upload",
                files=files,
                headers=headers
            )
        elapsed = time.time() - start_time

        passed = response.status_code == 200
        if passed:
            data = response.json()
            invoice_id = data.get("id")
            status = data.get("status")
            details = f"Status: {status}, Time: {elapsed:.1f}s, ID: {invoice_id[:8]}..."
        else:
            details = f"Status: {response.status_code}, Error: {response.text[:100]}"
        log_test(4, "Invoice Upload", passed, details)
    except Exception as e:
        log_test(4, "Invoice Upload", False, f"Exception: {str(e)}")
        return

    # TEST 5: Extraction Quality
    if invoice_id:
        try:
            response = requests.get(
                f"{BASE_URL}/invoices/{invoice_id}",
                headers=headers
            )
            passed = response.status_code == 200
            if passed:
                data = response.json()
                extracted = data.get("extracted_json", {})

                # Check extraction accuracy
                vendor_correct = "Office Depot" in str(extracted.get("vendor_name", ""))
                invoice_num_correct = "OD-2024-1234" in str(extracted.get("invoice_number", ""))
                amount_correct = abs(float(extracted.get("total_amount", 0)) - 580.48) < 0.01

                accuracy = sum([vendor_correct, invoice_num_correct, amount_correct]) / 3
                confidence = extracted.get("confidence_score", 0)

                passed = accuracy >= 0.66  # At least 2/3 fields correct
                details = f"Accuracy: {accuracy*100:.0f}%, Confidence: {confidence:.2f}"
                details += f"\n     Vendor: {'✓' if vendor_correct else '✗'}"
                details += f" | Invoice#: {'✓' if invoice_num_correct else '✗'}"
                details += f" | Amount: {'✓' if amount_correct else '✗'}"
            else:
                details = f"Status: {response.status_code}"
            log_test(5, "Extraction Quality", passed, details)
        except Exception as e:
            log_test(5, "Extraction Quality", False, f"Exception: {str(e)}")

    # TEST 6: Get Invoice Details
    try:
        response = requests.get(
            f"{BASE_URL}/invoices/{invoice_id}",
            headers=headers
        )
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        log_test(6, "Get Invoice Details", passed, details)
    except Exception as e:
        log_test(6, "Get Invoice Details", False, f"Exception: {str(e)}")

    # TEST 7: Update Invoice
    try:
        update_data = {
            "extracted_json": {
                "vendor_name": "Office Depot Inc.",
                "notes": "Updated via API test"
            }
        }
        response = requests.put(
            f"{BASE_URL}/invoices/{invoice_id}",
            json=update_data,
            headers=headers
        )
        passed = response.status_code == 200
        details = f"Status: {response.status_code}"
        log_test(7, "Update Invoice", passed, details)
    except Exception as e:
        log_test(7, "Update Invoice", False, f"Exception: {str(e)}")

    # TEST 8: QuickBooks IIF Export
    print(f"\n{Colors.YELLOW}>>> PHASE 3: QuickBooks Export{Colors.END}\n")

    try:
        response = requests.get(
            f"{BASE_URL}/quickbooks/export/iif/{invoice_id}",
            headers=headers
        )
        passed = response.status_code == 200
        if passed:
            # Save IIF file
            iif_path = Path("test_export.iif")
            iif_path.write_bytes(response.content)

            # Validate IIF format
            content = response.content.decode('utf-8')
            has_header = "!TRNS" in content and "!SPL" in content
            has_data = "Office Depot" in content or "580.48" in content
            format_valid = has_header and has_data

            details = f"File size: {len(response.content)} bytes, Format: {'Valid' if format_valid else 'Invalid'}"
            passed = format_valid
        else:
            details = f"Status: {response.status_code}"
        log_test(8, "IIF Export", passed, details)
    except Exception as e:
        log_test(8, "IIF Export", False, f"Exception: {str(e)}")

    # TEST 9: List Invoices
    try:
        response = requests.get(f"{BASE_URL}/invoices", headers=headers)
        passed = response.status_code == 200
        if passed:
            data = response.json()
            count = len(data) if isinstance(data, list) else data.get("total", 0)
            details = f"Invoice count: {count}"
        else:
            details = f"Status: {response.status_code}"
        log_test(9, "List Invoices", passed, details)
    except Exception as e:
        log_test(9, "List Invoices", False, f"Exception: {str(e)}")

    # TEST 10: Delete Invoice
    try:
        response = requests.delete(
            f"{BASE_URL}/invoices/{invoice_id}",
            headers=headers
        )
        passed = response.status_code in [200, 204]
        details = f"Status: {response.status_code}"

        # Verify deleted
        response2 = requests.get(
            f"{BASE_URL}/invoices/{invoice_id}",
            headers=headers
        )
        deleted = response2.status_code == 404
        if not deleted:
            passed = False
            details += ", Still exists after delete!"

        log_test(10, "Delete Invoice", passed, details)
    except Exception as e:
        log_test(10, "Delete Invoice", False, f"Exception: {str(e)}")

    # Print summary
    print_summary()

    # Save results to file
    results_file = Path("MVP-Test-Results.json")
    results_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "tests": RESULTS,
        "summary": {
            "total": len(RESULTS),
            "passed": sum(1 for r in RESULTS if r['passed']),
            "failed": sum(1 for r in RESULTS if not r['passed']),
            "pass_rate": sum(1 for r in RESULTS if r['passed']) / len(RESULTS) * 100
        }
    }, indent=2))

    print(f"Results saved to: {results_file}")

if __name__ == "__main__":
    main()
