"""
Mock AI Extraction Service for Phase 4 Demonstration

This service simulates a 4-tier extraction pipeline without requiring
actual AI API credentials. Perfect for testing and demonstration.

In production, replace mock functions with real AI API calls.
"""

import random
from typing import Dict, Any, Tuple
from decimal import Decimal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

# Confidence score weights for overall calculation
CONFIDENCE_WEIGHTS = {
    "total_amount": 0.30,
    "vendor_name": 0.25,
    "invoice_date": 0.15,
    "invoice_number": 0.10,
    "line_items": 0.10,
    "due_date": 0.05,
    "tax_amount": 0.05,
}

# Mock vendors for realistic extraction
MOCK_VENDORS = [
    {"name": "Acme Construction Supplies", "gstin": "29ABCDE1234F1Z5", "address": "123 Builder St, Mumbai, MH 400001"},
    {"name": "Global Tech Solutions Pvt Ltd", "gstin": "27XYZAB9876C2D4", "address": "45 IT Park Road, Bangalore, KA 560100"},
    {"name": "Premier Office Furniture", "gstin": "06MNOPQ5432G3H6", "address": "78 Commerce Lane, Delhi, DL 110001"},
    {"name": "Industrial Equipment Corp", "gstin": "33RSTPQ8765I4J7", "address": "90 Factory Road, Chennai, TN 600001"},
    {"name": "Metro Logistics Services", "gstin": "24GHIJK3456K5L8", "address": "12 Transport Hub, Pune, MH 411001"},
]


def calculate_overall_confidence(field_confidences: Dict[str, float]) -> float:
    """
    Calculate weighted overall confidence score

    Args:
        field_confidences: Dictionary of field names and their confidence scores

    Returns:
        Weighted average confidence score (0.0 to 1.0)
    """
    total_weight = 0.0
    weighted_sum = 0.0

    for field, confidence in field_confidences.items():
        weight = CONFIDENCE_WEIGHTS.get(field, 0.0)
        weighted_sum += confidence * weight
        total_weight += weight

    # Add remaining fields with equal weight
    remaining_weight = 1.0 - total_weight
    if remaining_weight > 0:
        other_fields = {k: v for k, v in field_confidences.items() if k not in CONFIDENCE_WEIGHTS}
        if other_fields:
            equal_weight = remaining_weight / len(other_fields)
            weighted_sum += sum(other_fields.values()) * equal_weight

    return min(weighted_sum, 1.0)


def generate_mock_extraction(file_name: str, tier: int = 1) -> Tuple[Dict[str, Any], Dict[str, float], float]:
    """
    Generate mock extraction data for demonstration

    Args:
        file_name: Name of the invoice file
        tier: Processing tier (1-4), affects confidence

    Returns:
        Tuple of (extracted_data, field_confidences, overall_confidence)
    """
    # Select random vendor
    vendor = random.choice(MOCK_VENDORS)

    # Generate invoice data
    invoice_date = datetime.now() - timedelta(days=random.randint(1, 90))
    due_date = invoice_date + timedelta(days=30)

    subtotal = Decimal(random.randint(10000, 500000))
    tax_rate = Decimal("0.18")  # 18% GST
    tax_amount = subtotal * tax_rate
    total_amount = subtotal + tax_amount

    # Generate line items
    num_items = random.randint(2, 5)
    line_items = []
    for i in range(num_items):
        item_amount = subtotal / num_items
        line_items.append({
            "description": f"Item {i+1} - {random.choice(['Materials', 'Services', 'Equipment', 'Supplies'])}",
            "quantity": random.randint(1, 100),
            "unit_price": float(item_amount / random.randint(1, 100)),
            "amount": float(item_amount)
        })

    # Extract data
    extracted_data = {
        "vendor_name": vendor["name"],
        "vendor_address": vendor["address"],
        "vendor_tax_id": vendor["gstin"],
        "invoice_number": f"INV-{random.randint(1000, 9999)}",
        "invoice_date": invoice_date.isoformat(),
        "due_date": due_date.isoformat(),
        "currency": "INR",
        "payment_terms": "NET30",
        "subtotal": float(subtotal),
        "tax_amount": float(tax_amount),
        "tax_rate": float(tax_rate * 100),  # Convert to percentage
        "total_amount": float(total_amount),
        "line_items": line_items,
        "seller_gstin": vendor["gstin"],
    }

    # Generate confidence scores based on tier
    # Tier 1: 0.92-0.98
    # Tier 2 (after preprocessing): 0.88-0.95
    # Tier 3 (GPT-4V): 0.85-0.92
    # Tier 4 (human): 1.0

    base_ranges = {
        1: (0.92, 0.98),
        2: (0.88, 0.95),
        3: (0.85, 0.92),
        4: (1.0, 1.0),
    }

    min_conf, max_conf = base_ranges.get(tier, (0.85, 0.95))

    field_confidences = {
        "vendor_name": random.uniform(min_conf, max_conf),
        "vendor_address": random.uniform(min_conf - 0.05, max_conf - 0.02),
        "vendor_tax_id": random.uniform(min_conf, max_conf),
        "invoice_number": random.uniform(min_conf, max_conf),
        "invoice_date": random.uniform(min_conf, max_conf),
        "due_date": random.uniform(min_conf - 0.03, max_conf - 0.01),
        "currency": 0.99,  # Usually very confident
        "payment_terms": random.uniform(min_conf - 0.08, max_conf - 0.05),
        "subtotal": random.uniform(min_conf, max_conf),
        "tax_amount": random.uniform(min_conf, max_conf),
        "tax_rate": random.uniform(min_conf - 0.02, max_conf),
        "total_amount": random.uniform(min_conf + 0.02, max_conf),  # Critical field, slightly higher
        "line_items": random.uniform(min_conf - 0.05, max_conf - 0.03),
    }

    overall_confidence = calculate_overall_confidence(field_confidences)

    logger.info(f"Generated mock extraction for {file_name} (Tier {tier}): confidence={overall_confidence:.2f}")

    return extracted_data, field_confidences, overall_confidence


def determine_processing_tier(overall_confidence: float) -> Tuple[str, bool, str]:
    """
    Determine next processing tier based on confidence score

    Args:
        overall_confidence: Overall confidence score

    Returns:
        Tuple of (next_tier, requires_review, review_priority)
    """
    if overall_confidence >= 0.95:
        return "completed", False, None
    elif overall_confidence >= 0.90:
        return "tier2", False, None  # Try preprocessing
    elif overall_confidence >= 0.85:
        return "tier3", False, None  # Escalate to GPT-4V
    else:
        return "tier4", True, "high"  # Human review required


def mock_tier1_extraction(file_path: str, file_name: str) -> Dict[str, Any]:
    """
    Mock Tier 1: Gemini 1.5 Flash extraction

    In production, this would call the Gemini API.
    For demo, returns realistic mock data.

    Args:
        file_path: Path to invoice file
        file_name: Name of the file

    Returns:
        Extraction result with data, confidences, and processing info
    """
    extracted_data, field_confidences, overall_confidence = generate_mock_extraction(file_name, tier=1)

    next_tier, requires_review, review_priority = determine_processing_tier(overall_confidence)

    return {
        "extracted_data": extracted_data,
        "field_confidences": field_confidences,
        "overall_confidence": overall_confidence,
        "processing_tier": "tier1",
        "next_tier": next_tier,
        "requires_review": requires_review,
        "review_priority": review_priority,
        "processing_time_ms": random.randint(800, 1500),
        "cost_usd": 0.0015,  # Mock Gemini Flash cost
        "api_calls": {"gemini_flash": 1}
    }


def mock_tier2_extraction(file_path: str, file_name: str) -> Dict[str, Any]:
    """
    Mock Tier 2: Preprocessing + Gemini retry

    In production, would preprocess image and retry Gemini.
    For demo, simulates improved extraction.
    """
    extracted_data, field_confidences, overall_confidence = generate_mock_extraction(file_name, tier=2)

    # Boost confidence slightly from preprocessing
    overall_confidence = min(overall_confidence + 0.03, 0.98)

    next_tier, requires_review, review_priority = determine_processing_tier(overall_confidence)

    return {
        "extracted_data": extracted_data,
        "field_confidences": field_confidences,
        "overall_confidence": overall_confidence,
        "processing_tier": "tier2",
        "next_tier": next_tier,
        "requires_review": requires_review,
        "review_priority": review_priority,
        "processing_time_ms": random.randint(2000, 3500),
        "cost_usd": 0.0015,  # Gemini retry
        "api_calls": {"gemini_flash": 1, "preprocessing": 1}
    }


def mock_tier3_extraction(file_path: str, file_name: str) -> Dict[str, Any]:
    """
    Mock Tier 3: GPT-4 Vision fallback

    In production, would call GPT-4V API.
    For demo, simulates high-quality extraction.
    """
    extracted_data, field_confidences, overall_confidence = generate_mock_extraction(file_name, tier=3)

    # GPT-4V is usually pretty good
    overall_confidence = min(overall_confidence + 0.05, 0.96)

    next_tier, requires_review, review_priority = determine_processing_tier(overall_confidence)

    return {
        "extracted_data": extracted_data,
        "field_confidences": field_confidences,
        "overall_confidence": overall_confidence,
        "processing_tier": "tier3",
        "next_tier": next_tier,
        "requires_review": requires_review,
        "review_priority": review_priority,
        "processing_time_ms": random.randint(3000, 5000),
        "cost_usd": 0.0200,  # GPT-4V is more expensive
        "api_calls": {"gpt4v": 1}
    }


def process_invoice_extraction(file_path: str, file_name: str, force_tier: int = None) -> Dict[str, Any]:
    """
    Process invoice through extraction pipeline

    Args:
        file_path: Path to invoice file
        file_name: Name of the file
        force_tier: Force specific tier for testing (1-3)

    Returns:
        Final extraction result
    """
    if force_tier == 2:
        return mock_tier2_extraction(file_path, file_name)
    elif force_tier == 3:
        return mock_tier3_extraction(file_path, file_name)
    else:
        # Start with Tier 1
        result = mock_tier1_extraction(file_path, file_name)

        # If confidence too low, try next tier
        if result["next_tier"] == "tier2":
            logger.info(f"Tier 1 confidence {result['overall_confidence']:.2f} < 0.95, trying Tier 2")
            result = mock_tier2_extraction(file_path, file_name)

        if result["next_tier"] == "tier3":
            logger.info(f"Tier 2 confidence {result['overall_confidence']:.2f} < 0.90, trying Tier 3")
            result = mock_tier3_extraction(file_path, file_name)

        return result


def extract_invoice_data(file_path: str, file_type: str) -> Dict[str, Any]:
    """
    Extract data from invoice - wrapper for invoices_simple.py compatibility

    Args:
        file_path: Path to the invoice file
        file_type: Type of file (pdf, jpg, png, etc)

    Returns:
        Dictionary with extracted data, confidence scores, and metadata
    """
    # Extract filename from path for logging
    import os
    file_name = os.path.basename(file_path) if '/' in file_path or '\\' in file_path else file_path

    # Process the extraction
    result = process_invoice_extraction(file_path, file_name)

    # Return in the format expected by invoices_simple.py
    return {
        "data": result.get("extracted_data", {}),
        "confidence": result.get("field_confidences", {}),
        "overall_confidence": result.get("overall_confidence", 0.0),
        "processing_tier": result.get("processing_tier", "tier1"),
        "processing_time_ms": result.get("processing_time_ms", 0),
    }
