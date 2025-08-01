#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from policy_rules import validate_policy_rules

def test_co_payment_fix():
    """Test the co-payment validation fix with null values."""
    print("🧪 Testing Co-payment Validation Fix")
    print("=" * 40)
    
    # Create test policy data with null co-payment
    policy_data = {
        "policy_start_date": "10/02/2025",
        "policy_end_date": "09/02/2026",
        "co_payment": "null",  # This was causing the error
        "room_rent_capping": 500000,
        "base_sum_assured": 500000
    }
    
    # Create claim data with valid admission date
    claim_data = {
        "admission_date": "15/07/2025",  # Valid date that should pass inception check
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
    print(f"  Policy Start: {policy_data['policy_start_date']}")
    print(f"  Policy End: {policy_data['policy_end_date']}")
    print(f"  Co-payment: {policy_data['co_payment']}")
    print(f"  Admission Date: {claim_data['admission_date']}")
    
    # Run validation
    print("\n🔍 Running Policy Validation...")
    rule_report = validate_policy_rules(policy_data, claim_data)
    
    print("✅ Validation completed!")
    print(f"📊 Overall Valid: {rule_report.overall_valid}")
    print(f"📊 Total Rules: {len(rule_report.rule_results)}")
    print(f"📊 Risk Level: {rule_report.risk_level}")
    
    # Check co-payment specifically
    co_payment_result = rule_report.rule_results.get('co_payment')
    if co_payment_result:
        print(f"\n📋 Co-payment Rule Result:")
        print(f"  Status: {co_payment_result.decision.value}")
        print(f"  Details: {co_payment_result.details}")
        if co_payment_result.decision.value == "Pass":
            print("✅ Co-payment fix working - null value handled correctly!")
        else:
            print("❌ Co-payment still has issues")
    else:
        print("⚠️  Co-payment rule not found in results")
    
    # Show all rules processed
    print(f"\n📋 All Rules Processed:")
    for rule_name, rule_result in rule_report.rule_results.items():
        print(f"  {rule_result.section} - {rule_result.rule_name}: {rule_result.decision.value}")

if __name__ == "__main__":
    test_co_payment_fix() 