#!/usr/bin/env python3
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from policy_rules import validate_policy_rules

def test_validation_with_admission_date():
    """Test policy validation with the corrected admission date."""
    print("🧪 Testing Policy Validation with Admission Date")
    print("=" * 50)
    
    # Test data with corrected admission date
    policy_data = {
        "policy_start_date": "10/02/2025",  # 10th Feb 2025
        "policy_end_date": "09/02/2026",    # 9th Feb 2026
        "date_of_admission": "15/07/2025",  # 15th July 2025
        "base_sum_assured": "500000",
        "room_rent_capping": "100",
        "icu_capping": "100"
    }
    
    claim_data = {
        "admission_date": "15/07/2025",  # Use the corrected admission date
        "claim_amount": 50000,
        "condition": "cardiac",
        "hospital_bill": {
            "room_rent": 5000,
            "icu_charges": 15000,
            "procedure": "cardiac surgery",
            "procedure_cost": 30000
        }
    }
    
    print("📊 Test Data:")
    print(f"  Policy Start Date: {policy_data['policy_start_date']}")
    print(f"  Policy End Date: {policy_data['policy_end_date']}")
    print(f"  Admission Date: {claim_data['admission_date']}")
    
    # Run validation
    print("\n🔍 Running Policy Validation...")
    rule_report = validate_policy_rules(policy_data, claim_data)
    
    print(f"\n📋 Validation Results:")
    print(f"  Overall Valid: {rule_report.overall_valid}")
    print(f"  Risk Level: {rule_report.risk_level}")
    print(f"  Total Deductions: ₹{rule_report.total_deductions}")
    
    # Check inception date validation specifically
    inception_result = rule_report.rule_results.get('inception_date')
    if inception_result:
        print(f"\n📅 Inception Date Validation:")
        print(f"  Decision: {inception_result.decision}")
        print(f"  Criteria Met: {inception_result.criteria_met}")
        print(f"  Confidence: {inception_result.confidence_score}")
        print(f"  Details: {inception_result.details}")
        
        if inception_result.decision.value == "Pass":
            print("  ✅ SUCCESS: Policy validation now works correctly!")
        else:
            print("  ❌ FAILURE: Policy validation still has issues")
    else:
        print("  ❌ No inception date validation result found")
    
    print(f"\n📝 Recommendations:")
    for rec in rule_report.recommendations:
        print(f"  - {rec}")

if __name__ == "__main__":
    test_validation_with_admission_date() 