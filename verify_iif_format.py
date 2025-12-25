#!/usr/bin/env python3
"""
Verify QuickBooks IIF Export Format
Validates that exported IIF files meet QuickBooks standards
"""

from pathlib import Path
import sys

def verify_iif_format(iif_path):
    """Verify IIF file format compliance"""

    print(f"\n{'='*70}")
    print(f"QUICKBOOKS IIF FORMAT VERIFICATION")
    print(f"{'='*70}\n")
    print(f"File: {iif_path}\n")

    if not iif_path.exists():
        print("✗ FAILED: File not found")
        return False

    content = iif_path.read_text()
    lines = content.split('\n')

    print("FILE CONTENTS:")
    print("-" * 70)
    for i, line in enumerate(lines[:20], 1):  # Show first 20 lines
        print(f"{i:3d}: {line}")
    if len(lines) > 20:
        print(f"... ({len(lines) - 20} more lines)")

    print(f"\n{'='*70}")
    print("VALIDATION CHECKLIST:")
    print("-" * 70)

    # Validation checks
    checks = []

    # Check 1: File starts with !TRNS header
    has_trns_header = content.startswith("!TRNS")
    checks.append(("File starts with !TRNS header", has_trns_header))

    # Check 2: Contains !SPL header
    has_spl_header = "!SPL" in content
    checks.append(("Contains !SPL header", has_spl_header))

    # Check 3: Contains !ENDTRNS header
    has_endtrns_header = "!ENDTRNS" in content
    checks.append(("Contains !ENDTRNS header", has_endtrns_header))

    # Check 4: Contains TRNS transaction line
    has_trns_line = any(line.startswith("TRNS\t") for line in lines)
    checks.append(("Contains TRNS transaction line", has_trns_line))

    # Check 5: Contains SPL split line
    has_spl_line = any(line.startswith("SPL\t") for line in lines)
    checks.append(("Contains SPL split line", has_spl_line))

    # Check 6: Contains ENDTRNS closer
    has_endtrns_line = "ENDTRNS" in content
    checks.append(("Contains ENDTRNS closer", has_endtrns_line))

    # Check 7: Tab-delimited format
    has_tabs = '\t' in content
    checks.append(("Uses tab-delimited format", has_tabs))

    # Check 8: Contains date in MM/DD/YYYY format
    import re
    has_date = bool(re.search(r'\d{1,2}/\d{1,2}/\d{4}', content))
    checks.append(("Contains date (MM/DD/YYYY)", has_date))

    # Check 9: Contains BILL transaction type
    has_bill = "BILL" in content
    checks.append(("Contains BILL transaction type", has_bill))

    # Check 10: Contains Accounts Payable account
    has_ap = "Accounts Payable" in content
    checks.append(("Contains Accounts Payable account", has_ap))

    # Print results
    for check_name, passed in checks:
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {check_name}")

    # Calculate pass rate
    passed_count = sum(1 for _, passed in checks if passed)
    total_count = len(checks)
    pass_rate = (passed_count / total_count) * 100

    print(f"\n{'='*70}")
    print(f"VALIDATION SUMMARY:")
    print(f"  Checks Passed: {passed_count}/{total_count} ({pass_rate:.0f}%)")

    # Final verdict
    if pass_rate == 100:
        print(f"\n✓ IIF FORMAT: PERFECT")
        print("  File is ready for QuickBooks import")
    elif pass_rate >= 80:
        print(f"\n⚠ IIF FORMAT: ACCEPTABLE")
        print("  File should work but may need minor adjustments")
    else:
        print(f"\n✗ IIF FORMAT: INVALID")
        print("  File needs significant fixes before import")

    print(f"{'='*70}\n")

    return pass_rate >= 80

if __name__ == "__main__":
    # Check for IIF file
    iif_files = list(Path(".").glob("*.iif"))

    if not iif_files:
        print("No IIF files found. Run the main test suite first.")
        sys.exit(1)

    # Verify each IIF file found
    all_passed = True
    for iif_file in iif_files:
        passed = verify_iif_format(iif_file)
        if not passed:
            all_passed = False

    sys.exit(0 if all_passed else 1)
