#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from validation import validate_extraction_result

def test_single_digit_dates():
    """Test validation of single-digit day and month date formats."""
    print("🧪 Testing Single-Digit Date Format Validation")
    print("=" * 60)
    
    # Test cases with single-digit day and month formats
    test_cases = [
        # User's specific examples
        {
            "name": "User Example 1: 7/5/25 (7th May 2025)",
            "policy_start_date": "7/5/25",
            "policy_end_date": "6/5/26",
            "date_of_admission": "15/3/25"
        },
        {
            "name": "User Example 2: 17/2/25 (17th Feb 2025)",
            "policy_start_date": "17/2/25",
            "policy_end_date": "16/2/26",
            "date_of_admission": "20/2/25"
        },
        # Additional single-digit combinations
        {
            "name": "D/M/YY format variations",
            "policy_start_date": "1/1/25",
            "policy_end_date": "31/12/25",
            "date_of_admission": "15/3/25"
        },
        {
            "name": "DD/M/YY format variations",
            "policy_start_date": "01/1/25",
            "policy_end_date": "31/1/25",
            "date_of_admission": "15/3/25"
        },
        {
            "name": "D/MM/YY format variations",
            "policy_start_date": "1/01/25",
            "policy_end_date": "31/12/25",
            "date_of_admission": "15/03/25"
        },
        # Mixed formats
        {
            "name": "Mixed single and double digit formats",
            "policy_start_date": "7/05/25",
            "policy_end_date": "06/5/26",
            "date_of_admission": "15/3/25"
        },
        # Standard formats (for comparison)
        {
            "name": "Standard DD/MM/YY format",
            "policy_start_date": "07/05/25",
            "policy_end_date": "06/05/26",
            "date_of_admission": "15/03/25"
        },
        # Invalid formats
        {
            "name": "Invalid formats",
            "policy_start_date": "32/13/25",
            "policy_end_date": "0/0/25",
            "date_of_admission": "invalid-date"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📅 Test Case {i}: {test_case['name']}")
        print("-" * 50)
        
        # Remove the 'name' key for validation
        validation_data = {k: v for k, v in test_case.items() if k != 'name'}
        
        validation_result = validate_extraction_result(validation_data)
        
        date_fields = ['policy_start_date', 'policy_end_date', 'date_of_admission']
        for field in date_fields:
            if field in validation_result.field_results:
                result = validation_result.field_results[field]
                status = "✅ VALID" if result.is_valid else "❌ INVALID"
                print(f"  {field}: {status} (Confidence: {result.confidence_score:.3f})")
                print(f"    Value: {result.value}")
                if result.validation_messages:
                    print(f"    Messages: {result.validation_messages}")
            else:
                print(f"  {field}: Not found in validation results")
    
    print("\n📊 Summary:")
    print("✅ D/M/YY format (e.g., 7/5/25) should be valid")
    print("✅ DD/M/YY format (e.g., 17/2/25) should be valid")
    print("✅ D/MM/YY format (e.g., 7/12/25) should be valid")
    print("✅ DD/M/YY format (e.g., 17/2/25) should be valid")
    print("❌ Invalid formats should be rejected")
    print("✅ Mixed formats should be handled correctly")
    
    print("\n✅ Single-digit date format validation test completed!")

if __name__ == "__main__":
    test_single_digit_dates() 