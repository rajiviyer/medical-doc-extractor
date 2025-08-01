#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from validation import validate_extraction_result

def test_date_validation():
    """Test validation of the new date fields."""
    print("🧪 Testing Date Field Validation")
    
    # Load the updated extracted summary
    with open("output/extracted_summary_gemini.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    extraction_data = data["extraction"]
    
    print("📊 Extracted Date Fields:")
    date_fields = ['policy_start_date', 'policy_end_date', 'date_of_admission']
    
    for field in date_fields:
        value = extraction_data.get(field, "Not found")
        print(f"  {field}: {value}")
    
    # Test validation
    print("\n🔍 Running Validation...")
    validation_result = validate_extraction_result(extraction_data)
    
    print(f"Overall Valid: {validation_result.overall_valid}")
    print(f"Overall Confidence: {validation_result.overall_confidence:.3f}")
    
    # Check validation for date fields
    print("\n📅 Date Field Validation Results:")
    for field in date_fields:
        if field in validation_result.field_results:
            result = validation_result.field_results[field]
            print(f"  {field}:")
            print(f"    Valid: {result.is_valid}")
            print(f"    Confidence: {result.confidence_score:.3f}")
            print(f"    Value: {result.value}")
            if result.validation_messages:
                print(f"    Messages: {result.validation_messages}")
        else:
            print(f"  {field}: Not found in validation results")
    
    # Test with invalid date formats
    print("\n🧪 Testing Invalid Date Formats...")
    test_cases = [
        {"policy_start_date": "invalid-date", "policy_end_date": "2024-13-45", "date_of_admission": "not-a-date"},
        {"policy_start_date": "01/01/2024", "policy_end_date": "31/12/2024", "date_of_admission": "15/03/2024"},
        {"policy_start_date": "null", "policy_end_date": "", "date_of_admission": None}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        test_validation = validate_extraction_result(test_case)
        
        for field in date_fields:
            if field in test_validation.field_results:
                result = test_validation.field_results[field]
                print(f"  {field}: Valid={result.is_valid}, Confidence={result.confidence_score:.3f}")
    
    print("\n✅ Date field validation test completed!")

if __name__ == "__main__":
    test_date_validation() 