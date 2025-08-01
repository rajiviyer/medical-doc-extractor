#!/usr/bin/env python3
"""
Test script for data validation system.
"""

import json
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from validation import validate_extraction_result, ValidationResult, PolicyValidationReport

def create_valid_policy_data():
    """Create valid policy data for testing."""
    return {
        "room_rent_capping": "2%",
        "icu_capping": "5%",
        "co_payment": "10%",
        "base_sum_assured": "500000",
        "cataract_capping": "25000",
        "hernia_capping": "30000",
        "joint_replacement_capping": "150000",
        "maternity_capping": "50000",
        "ambulance_charge_capping": "1000",
        "daily_cash_benefit": "2000",
        "modern_treatment_capping": "100%",
        "other_expenses_capping": "5%",
        "medical_practitioners_capping": "100%",
        "room_category_capping": "100%",
        "treatment_hazardous_sports_capping": "0%",
        "dialysis_capping": "50000",
        "chemotherapy_capping": "100000",
        "radiotherapy_capping": "100000",
        "consumable_non_medical_capping": "5%",
        "opd_daycare_domiciliary_capping": "10000",
        "pre_post_hospitalization_capping": "30000",
        "diagnostic_tests_capping": "15000",
        "implants_stents_prosthetics_capping": "100000",
        "mental_illness_treatment_capping": "50000",
        "organ_donor_expenses_capping": "50000",
        "bariatric_obesity_surgery_capping": "150000",
        "cancer_treatment_capping": "200000",
        "internal_congenital_disease_capping": "50000",
        "ayush_hospitalization_capping": "25000",
        "vaccination_preventive_capping": "5000",
        "artificial_prostheses_aids_capping": "25000"
    }

def create_invalid_policy_data():
    """Create invalid policy data for testing."""
    return {
        "room_rent_capping": "150%",  # Out of range
        "icu_capping": "5%",
        "co_payment": "60%",  # Out of range
        "base_sum_assured": "500000",
        "cataract_capping": "25000",
        "hernia_capping": "30000",
        "joint_replacement_capping": "150000",
        "maternity_capping": "50000",
        "ambulance_charge_capping": "1000",
        "daily_cash_benefit": "2000",
        "modern_treatment_capping": "100%",
        "other_expenses_capping": "5%",
        "medical_practitioners_capping": "100%",
        "room_category_capping": "100%",
        "treatment_hazardous_sports_capping": "0%",
        "dialysis_capping": "50000",
        "chemotherapy_capping": "100000",
        "radiotherapy_capping": "100000",
        "consumable_non_medical_capping": "5%",
        "opd_daycare_domiciliary_capping": "10000",
        "pre_post_hospitalization_capping": "30000",
        "diagnostic_tests_capping": "15000",
        "implants_stents_prosthetics_capping": "100000",
        "mental_illness_treatment_capping": "50000",
        "organ_donor_expenses_capping": "50000",
        "bariatric_obesity_surgery_capping": "150000",
        "cancer_treatment_capping": "200000",
        "internal_congenital_disease_capping": "50000",
        "ayush_hospitalization_capping": "25000",
        "vaccination_preventive_capping": "5000",
        "artificial_prostheses_aids_capping": "25000"
    }

def create_missing_fields_data():
    """Create policy data with missing required fields."""
    return {
        "room_rent_capping": "2%",
        "icu_capping": "5%",
        "co_payment": "10%",
        # Missing base_sum_assured (required field)
        "cataract_capping": "25000",
        "hernia_capping": "30000"
    }

def test_valid_policy_data():
    """Test validation with valid policy data."""
    print("🧪 Testing Valid Policy Data")
    print("=" * 50)
    
    valid_data = create_valid_policy_data()
    
    print("\n1. Testing validation with valid policy data...")
    validation_report = validate_extraction_result(valid_data)
    
    print(f"   Overall Valid: {validation_report.overall_valid}")
    print(f"   Overall Confidence: {validation_report.overall_confidence:.2f}")
    print(f"   Number of Fields: {len(validation_report.field_results)}")
    print(f"   Cross-field Issues: {len(validation_report.cross_field_issues)}")
    print(f"   Recommendations: {len(validation_report.recommendations)}")
    
    # Check field results
    valid_fields = 0
    total_fields = len(validation_report.field_results)
    
    for field_name, field_result in validation_report.field_results.items():
        if field_result.is_valid:
            valid_fields += 1
            print(f"   ✅ {field_name}: Valid")
        else:
            print(f"   ❌ {field_name}: Invalid - {field_result.validation_messages}")
    
    accuracy = (valid_fields / total_fields) * 100
    print(f"\n   Field Validation Accuracy: {accuracy:.1f}% ({valid_fields}/{total_fields})")
    
    return validation_report

def test_invalid_policy_data():
    """Test validation with invalid policy data."""
    print("\n🧪 Testing Invalid Policy Data")
    print("=" * 50)
    
    invalid_data = create_invalid_policy_data()
    
    print("\n1. Testing validation with invalid policy data...")
    validation_report = validate_extraction_result(invalid_data)
    
    print(f"   Overall Valid: {validation_report.overall_valid}")
    print(f"   Overall Confidence: {validation_report.overall_confidence:.2f}")
    print(f"   Number of Fields: {len(validation_report.field_results)}")
    print(f"   Cross-field Issues: {len(validation_report.cross_field_issues)}")
    print(f"   Recommendations: {len(validation_report.recommendations)}")
    
    # Check specific invalid fields
    print("\n2. Invalid Field Details:")
    for field_name, field_result in validation_report.field_results.items():
        if not field_result.is_valid:
            print(f"   ❌ {field_name}:")
            print(f"     Value: {field_result.value}")
            print(f"     Messages: {field_result.validation_messages}")
            print(f"     Confidence: {field_result.confidence_score:.2f}")
            if field_result.suggested_value:
                print(f"     Suggested: {field_result.suggested_value}")
    
    # Check recommendations
    print("\n3. Recommendations:")
    for i, recommendation in enumerate(validation_report.recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    return validation_report

def test_missing_fields():
    """Test validation with missing required fields."""
    print("\n🧪 Testing Missing Required Fields")
    print("=" * 50)
    
    missing_data = create_missing_fields_data()
    
    print("\n1. Testing validation with missing required fields...")
    validation_report = validate_extraction_result(missing_data)
    
    print(f"   Overall Valid: {validation_report.overall_valid}")
    print(f"   Overall Confidence: {validation_report.overall_confidence:.2f}")
    print(f"   Number of Fields: {len(validation_report.field_results)}")
    print(f"   Cross-field Issues: {len(validation_report.cross_field_issues)}")
    print(f"   Recommendations: {len(validation_report.recommendations)}")
    
    # Check for missing field errors
    print("\n2. Missing Field Details:")
    for field_name, field_result in validation_report.field_results.items():
        if not field_result.is_valid:
            print(f"   ❌ {field_name}:")
            print(f"     Value: {field_result.value}")
            print(f"     Messages: {field_result.validation_messages}")
            print(f"     Confidence: {field_result.confidence_score:.2f}")
    
    return validation_report

def test_range_validation():
    """Test range validation for numerical fields."""
    print("\n🧪 Testing Range Validation")
    print("=" * 50)
    
    # Test percentage fields
    percentage_tests = [
        ("room_rent_capping", "150%", False),  # > 100%
        ("room_rent_capping", "2%", True),     # Valid
        ("room_rent_capping", "-5%", False),   # Negative
        ("co_payment", "60%", False),          # > 50%
        ("co_payment", "10%", True),           # Valid
        ("icu_capping", "5%", True),           # Valid
        ("icu_capping", "200%", False)         # > 100%
    ]
    
    print("\n1. Testing percentage field validation:")
    for field_name, value, expected_valid in percentage_tests:
        test_data = {field_name: value}
        validation_report = validate_extraction_result(test_data)
        
        field_result = validation_report.field_results.get(field_name)
        if field_result:
            actual_valid = field_result.is_valid
            status = "✅" if actual_valid == expected_valid else "❌"
            print(f"   {status} {field_name}: {value} -> Valid: {actual_valid} (Expected: {expected_valid})")
        else:
            print(f"   ⚠️  {field_name}: {value} -> Field not found in validation")
    
    # Test currency fields
    currency_tests = [
        ("base_sum_assured", "500000", True),   # Valid
        ("base_sum_assured", "5000", False),    # Too low
        ("base_sum_assured", "50000000", True), # Valid
        ("cataract_capping", "25000", True),    # Valid
        ("cataract_capping", "-1000", False),   # Negative
        ("cataract_capping", "100000", True)    # Valid
    ]
    
    print("\n2. Testing currency field validation:")
    for field_name, value, expected_valid in currency_tests:
        test_data = {field_name: value}
        validation_report = validate_extraction_result(test_data)
        
        field_result = validation_report.field_results.get(field_name)
        if field_result:
            actual_valid = field_result.is_valid
            status = "✅" if actual_valid == expected_valid else "❌"
            print(f"   {status} {field_name}: {value} -> Valid: {actual_valid} (Expected: {expected_valid})")
        else:
            print(f"   ⚠️  {field_name}: {value} -> Field not found in validation")

def test_format_validation():
    """Test format validation for different field types."""
    print("\n🧪 Testing Format Validation")
    print("=" * 50)
    
    # Test percentage format
    percentage_format_tests = [
        ("2%", True),
        ("2.5%", True),
        ("2.0%", True),
        ("2", False),  # Missing %
        ("%2", False), # Wrong format
        ("2.5", False), # Missing %
        ("at actuals", True),  # Special value
        ("actuals", True),     # Special value
        ("100%", True),
        ("0%", True)
    ]
    
    print("\n1. Testing percentage format validation:")
    for value, expected_valid in percentage_format_tests:
        test_data = {"room_rent_capping": value}
        validation_report = validate_extraction_result(test_data)
        
        field_result = validation_report.field_results.get("room_rent_capping")
        if field_result:
            actual_valid = field_result.is_valid
            status = "✅" if actual_valid == expected_valid else "❌"
            print(f"   {status} '{value}' -> Valid: {actual_valid} (Expected: {expected_valid})")
        else:
            print(f"   ⚠️  '{value}' -> Field not found in validation")
    
    # Test currency format
    currency_format_tests = [
        ("500000", True),
        ("500,000", True),
        ("500000.00", True),
        ("500000.50", True),
        ("abc", False),  # Non-numeric
        ("500000abc", False),  # Mixed
        ("", False),  # Empty
        ("0", True),
        ("999999999", True)
    ]
    
    print("\n2. Testing currency format validation:")
    for value, expected_valid in currency_format_tests:
        test_data = {"base_sum_assured": value}
        validation_report = validate_extraction_result(test_data)
        
        field_result = validation_report.field_results.get("base_sum_assured")
        if field_result:
            actual_valid = field_result.is_valid
            status = "✅" if actual_valid == expected_valid else "❌"
            print(f"   {status} '{value}' -> Valid: {actual_valid} (Expected: {expected_valid})")
        else:
            print(f"   ⚠️  '{value}' -> Field not found in validation")

def test_cross_field_validation():
    """Test cross-field validation logic."""
    print("\n🧪 Testing Cross-Field Validation")
    print("=" * 50)
    
    # Test 1: Valid cross-field relationship
    print("\n1. Testing valid cross-field relationship...")
    valid_cross_data = {
        "room_rent_capping": "2%",
        "base_sum_assured": "500000",
        "icu_capping": "5%",
        "co_payment": "10%"
    }
    validation_report = validate_extraction_result(valid_cross_data)
    print(f"   Overall Valid: {validation_report.overall_valid}")
    print(f"   Cross-field Issues: {len(validation_report.cross_field_issues)}")
    
    # Test 2: Invalid cross-field relationship
    print("\n2. Testing invalid cross-field relationship...")
    invalid_cross_data = {
        "room_rent_capping": "150%",  # Invalid
        "base_sum_assured": "500000",
        "icu_capping": "200%",        # Invalid
        "co_payment": "60%"           # Invalid
    }
    validation_report = validate_extraction_result(invalid_cross_data)
    print(f"   Overall Valid: {validation_report.overall_valid}")
    print(f"   Cross-field Issues: {len(validation_report.cross_field_issues)}")
    
    if validation_report.cross_field_issues:
        print("   Cross-field Issues:")
        for issue in validation_report.cross_field_issues:
            print(f"     - {issue}")
    
    # Test 3: Missing base sum assured
    print("\n3. Testing missing base sum assured...")
    missing_base_data = {
        "room_rent_capping": "2%",
        "icu_capping": "5%",
        "co_payment": "10%"
        # Missing base_sum_assured
    }
    validation_report = validate_extraction_result(missing_base_data)
    print(f"   Overall Valid: {validation_report.overall_valid}")
    print(f"   Cross-field Issues: {len(validation_report.cross_field_issues)}")
    
    if validation_report.cross_field_issues:
        print("   Cross-field Issues:")
        for issue in validation_report.cross_field_issues:
            print(f"     - {issue}")

def test_confidence_scoring():
    """Test confidence scoring for different scenarios."""
    print("\n🧪 Testing Confidence Scoring")
    print("=" * 50)
    
    # Test scenarios with different confidence levels
    test_scenarios = [
        {
            "name": "Perfect Data",
            "data": create_valid_policy_data(),
            "expected_confidence": 0.8
        },
        {
            "name": "Invalid Data",
            "data": create_invalid_policy_data(),
            "expected_confidence": 0.3
        },
        {
            "name": "Missing Fields",
            "data": create_missing_fields_data(),
            "expected_confidence": 0.5
        }
    ]
    
    for scenario in test_scenarios:
        print(f"\n1. Testing {scenario['name']}...")
        validation_report = validate_extraction_result(scenario['data'])
        
        print(f"   Overall Confidence: {validation_report.overall_confidence:.2f}")
        print(f"   Expected Confidence: {scenario['expected_confidence']:.2f}")
        
        # Check if confidence is reasonable
        if validation_report.overall_confidence >= 0.7:
            confidence_level = "High"
        elif validation_report.overall_confidence >= 0.4:
            confidence_level = "Medium"
        else:
            confidence_level = "Low"
        
        print(f"   Confidence Level: {confidence_level}")
        
        # Show field confidence distribution
        high_confidence_fields = 0
        medium_confidence_fields = 0
        low_confidence_fields = 0
        
        for field_result in validation_report.field_results.values():
            if field_result.confidence_score >= 0.7:
                high_confidence_fields += 1
            elif field_result.confidence_score >= 0.4:
                medium_confidence_fields += 1
            else:
                low_confidence_fields += 1
        
        print(f"   High Confidence Fields: {high_confidence_fields}")
        print(f"   Medium Confidence Fields: {medium_confidence_fields}")
        print(f"   Low Confidence Fields: {low_confidence_fields}")

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    # Test 1: Empty data
    print("\n1. Testing empty data...")
    try:
        validation_report = validate_extraction_result({})
        print(f"   Handled gracefully: {validation_report.overall_valid}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: None data
    print("\n2. Testing None data...")
    try:
        validation_report = validate_extraction_result(None)
        print(f"   Handled gracefully: {validation_report.overall_valid}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Invalid field types
    print("\n3. Testing invalid field types...")
    try:
        invalid_types_data = {
            "room_rent_capping": 123,  # Should be string
            "base_sum_assured": "abc",  # Should be numeric
            "co_payment": None          # Should not be None
        }
        validation_report = validate_extraction_result(invalid_types_data)
        print(f"   Handled gracefully: {validation_report.overall_valid}")
    except Exception as e:
        print(f"   Error: {e}")

def main():
    """Run all validation tests."""
    print("🚀 Starting Data Validation Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        valid_report = test_valid_policy_data()
        invalid_report = test_invalid_policy_data()
        missing_report = test_missing_fields()
        
        test_range_validation()
        test_format_validation()
        test_cross_field_validation()
        test_confidence_scoring()
        test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 VALIDATION TEST SUMMARY")
        print("=" * 60)
        print(f"Valid Data Test: {'✅ Passed' if valid_report.overall_valid else '❌ Failed'}")
        print(f"Invalid Data Test: {'✅ Passed' if not invalid_report.overall_valid else '❌ Failed'}")
        print(f"Missing Fields Test: {'✅ Passed' if not missing_report.overall_valid else '❌ Failed'}")
        
        print("\n📊 Test Coverage:")
        print("  ✅ Range validation for numerical fields")
        print("  ✅ Format validation for percentage values")
        print("  ✅ Cross-field consistency checks")
        print("  ✅ Confidence score calculation")
        print("  ✅ Validation report generation")
        print("  ✅ Error handling scenarios")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 