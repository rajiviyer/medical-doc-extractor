#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from validation import validate_extraction_result

def test_date_formats():
    """Test validation of various date formats including DD/MM/YY."""
    print("🧪 Testing Date Format Validation (DD/MM/YYYY and DD/MM/YY)")
    
    # Test cases with different date formats
    test_cases = [
        # Valid DD/MM/YYYY formats
        {
            "policy_start_date": "01/01/2024",
            "policy_end_date": "31/12/2024", 
            "date_of_admission": "15/03/2024"
        },
        # Valid DD/MM/YY formats
        {
            "policy_start_date": "01/01/24",
            "policy_end_date": "31/12/24",
            "date_of_admission": "15/03/24"
        },
        # Mixed formats
        {
            "policy_start_date": "01/01/2024",
            "policy_end_date": "31/12/24",
            "date_of_admission": "15/03/2024"
        },
        # Other valid formats
        {
            "policy_start_date": "01-01-2024",
            "policy_end_date": "31.12.24",
            "date_of_admission": "15/03/2024"
        },
        # Invalid formats
        {
            "policy_start_date": "invalid-date",
            "policy_end_date": "2024-13-45",
            "date_of_admission": "not-a-date"
        },
        # Null/empty values
        {
            "policy_start_date": "null",
            "policy_end_date": "",
            "date_of_admission": None
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📅 Test Case {i}:")
        print(f"  Input: {test_case}")
        
        validation_result = validate_extraction_result(test_case)
        
        date_fields = ['policy_start_date', 'policy_end_date', 'date_of_admission']
        for field in date_fields:
            if field in validation_result.field_results:
                result = validation_result.field_results[field]
                status = "✅ VALID" if result.is_valid else "❌ INVALID"
                print(f"  {field}: {status} (Confidence: {result.confidence_score:.3f})")
                if result.validation_messages:
                    print(f"    Messages: {result.validation_messages}")
            else:
                print(f"  {field}: Not found in validation results")
    
    print("\n📊 Summary:")
    print("✅ DD/MM/YYYY format should be valid with high confidence (0.9)")
    print("✅ DD/MM/YY format should be valid with high confidence (0.9)")
    print("❌ Invalid formats should be invalid with low confidence (0.3)")
    print("✅ Null/empty values should be valid with medium confidence (0.8)")
    
    print("\n✅ Date format validation test completed!")

if __name__ == "__main__":
    test_date_formats() 