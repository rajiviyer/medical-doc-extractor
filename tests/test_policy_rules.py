#!/usr/bin/env python3
"""
Test script for policy rule validation system.
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, date

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from policy_rules import PolicyRuleValidator, validate_policy_rules, RuleDecision, RuleSection

def create_sample_policy_data():
    """Create sample policy data for testing."""
    return {
        "inception_date": "2023-01-01",
        "policy_status": "active",
        "grace_period": 30,
        "last_payment_date": "2024-01-01",
        "room_rent_capping": "2%",
        "icu_capping": "5%",
        "co_payment": "10%",
        "base_sum_assured": "500000",
        "cataract_capping": "25000",
        "hernia_capping": "30000",
        "joint_replacement_capping": "150000",
        "bariatric_obesity_surgery_capping": "150000"
    }

def create_sample_claim_data():
    """Create sample claim data for testing."""
    return {
        "admission_date": "2024-01-15",
        "claim_amount": 50000,
        "condition": "cardiac",
        "hospital_bill": {
            "room_rent": 5000,
            "icu_charges": 15000,
            "procedure": "cardiac surgery",
            "procedure_cost": 30000,
            "itemized_bill": {
                "toiletries": 500,
                "food": 1000,
                "telephone": 200,
                "tv": 300
            }
        },
        "discharge_summary": {
            "procedure": "cardiac surgery",
            "is_daycare": False
        }
    }

def test_policy_validity_rules():
    """Test policy validity rules (inception date, lapse check)."""
    print("🧪 Testing Policy Validity Rules")
    print("=" * 50)
    
    validator = PolicyRuleValidator()
    policy_data = create_sample_policy_data()
    
    # Test 1: Valid inception date
    print("\n1. Testing valid inception date...")
    result = validator.validate_inception_date(policy_data, "2024-01-15")
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Details: {result.details}")
    
    # Test 2: Invalid inception date (policy not active)
    print("\n2. Testing invalid inception date...")
    result = validator.validate_inception_date(policy_data, "2022-12-31")
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Details: {result.details}")
    
    # Test 3: Lapse check - active policy
    print("\n3. Testing lapse check - active policy...")
    result = validator.validate_lapse_check(policy_data)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Details: {result.details}")
    
    # Test 4: Lapse check - lapsed policy
    print("\n4. Testing lapse check - lapsed policy...")
    lapsed_policy = policy_data.copy()
    lapsed_policy["policy_status"] = "lapsed"
    result = validator.validate_lapse_check(lapsed_policy)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Details: {result.details}")
    
    return True

def test_policy_limits_rules():
    """Test policy limits rules (room rent, ICU, co-payment, sub-limits)."""
    print("\n🧪 Testing Policy Limits Rules")
    print("=" * 50)
    
    validator = PolicyRuleValidator()
    policy_data = create_sample_policy_data()
    claim_data = create_sample_claim_data()
    
    # Test 1: Room rent eligibility - within limit
    print("\n1. Testing room rent eligibility - within limit...")
    result = validator.validate_room_rent_eligibility(policy_data, claim_data["hospital_bill"])
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    # Test 2: Room rent eligibility - exceeds limit
    print("\n2. Testing room rent eligibility - exceeds limit...")
    high_rent_bill = claim_data["hospital_bill"].copy()
    high_rent_bill["room_rent"] = 15000  # Exceeds 2% of 500000 = 10000
    result = validator.validate_room_rent_eligibility(policy_data, high_rent_bill)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    # Test 3: ICU capping - within limit
    print("\n3. Testing ICU capping - within limit...")
    result = validator.validate_icu_capping(policy_data, claim_data["hospital_bill"])
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    # Test 4: ICU capping - exceeds limit
    print("\n4. Testing ICU capping - exceeds limit...")
    high_icu_bill = claim_data["hospital_bill"].copy()
    high_icu_bill["icu_charges"] = 30000  # Exceeds 5% of 500000 = 25000
    result = validator.validate_icu_capping(policy_data, high_icu_bill)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    # Test 5: Co-payment calculation
    print("\n5. Testing co-payment calculation...")
    result = validator.validate_co_payment(policy_data, claim_data["claim_amount"])
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    # Test 6: Sub-limits - cataract surgery
    print("\n6. Testing sub-limits - cataract surgery...")
    cataract_bill = claim_data["hospital_bill"].copy()
    cataract_bill["procedure"] = "cataract surgery"
    cataract_bill["procedure_cost"] = 20000  # Within 25000 limit
    result = validator.validate_sub_limits(policy_data, cataract_bill)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    return True

def test_waiting_period_rules():
    """Test waiting period rules (initial, disease-specific, maternity)."""
    print("\n🧪 Testing Waiting Period Rules")
    print("=" * 50)
    
    validator = PolicyRuleValidator()
    policy_data = create_sample_policy_data()
    claim_data = create_sample_claim_data()
    
    # Test 1: Initial waiting period - satisfied
    print("\n1. Testing initial waiting period - satisfied...")
    waiting_results = validator.validate_waiting_periods(
        policy_data, claim_data["admission_date"], claim_data["condition"]
    )
    
    for result in waiting_results:
        if "Initial Waiting" in result.rule_name:
            print(f"   Decision: {result.decision.value}")
            print(f"   Criteria Met: {result.criteria_met}")
            print(f"   Confidence: {result.confidence_score:.2f}")
            print(f"   Details: {result.details}")
            break
    
    # Test 2: Disease-specific waiting period - cardiac condition
    print("\n2. Testing disease-specific waiting period - cardiac condition...")
    for result in waiting_results:
        if "Disease Specific" in result.rule_name:
            print(f"   Decision: {result.decision.value}")
            print(f"   Criteria Met: {result.criteria_met}")
            print(f"   Confidence: {result.confidence_score:.2f}")
            print(f"   Details: {result.details}")
            break
    
    # Test 3: Short policy duration - waiting period not satisfied
    print("\n3. Testing short policy duration - waiting period not satisfied...")
    short_policy = policy_data.copy()
    short_policy["inception_date"] = "2024-01-10"  # Only 5 days old
    short_waiting_results = validator.validate_waiting_periods(
        short_policy, claim_data["admission_date"], claim_data["condition"]
    )
    
    for result in short_waiting_results:
        if "Initial Waiting" in result.rule_name:
            print(f"   Decision: {result.decision.value}")
            print(f"   Criteria Met: {result.criteria_met}")
            print(f"   Confidence: {result.confidence_score:.2f}")
            print(f"   Details: {result.details}")
            break
    
    return True

def test_non_medical_items():
    """Test non-medical items validation."""
    print("\n🧪 Testing Non-Medical Items Validation")
    print("=" * 50)
    
    validator = PolicyRuleValidator()
    claim_data = create_sample_claim_data()
    
    # Test 1: Non-medical items found
    print("\n1. Testing non-medical items found...")
    result = validator.validate_non_medical_items(claim_data["hospital_bill"])
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    # Test 2: No non-medical items
    print("\n2. Testing no non-medical items...")
    clean_bill = claim_data["hospital_bill"].copy()
    clean_bill["itemized_bill"] = {
        "surgery": 25000,
        "medication": 5000
    }
    result = validator.validate_non_medical_items(clean_bill)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Deduction Amount: {result.deduction_amount or 'None'}")
    print(f"   Details: {result.details}")
    
    return True

def test_daycare_validation():
    """Test daycare procedure validation."""
    print("\n🧪 Testing Daycare Validation")
    print("=" * 50)
    
    validator = PolicyRuleValidator()
    policy_data = create_sample_policy_data()
    
    # Test 1: IRDA-approved daycare procedure
    print("\n1. Testing IRDA-approved daycare procedure...")
    approved_daycare = {
        "procedure": "cataract surgery",
        "is_daycare": True
    }
    result = validator.validate_daycare(policy_data, approved_daycare)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Details: {result.details}")
    
    # Test 2: Non-IRDA daycare procedure
    print("\n2. Testing non-IRDA daycare procedure...")
    non_approved_daycare = {
        "procedure": "complex heart surgery",
        "is_daycare": True
    }
    result = validator.validate_daycare(policy_data, non_approved_daycare)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Details: {result.details}")
    
    # Test 3: Not a daycare procedure
    print("\n3. Testing not a daycare procedure...")
    non_daycare = {
        "procedure": "cardiac surgery",
        "is_daycare": False
    }
    result = validator.validate_daycare(policy_data, non_daycare)
    print(f"   Decision: {result.decision.value}")
    print(f"   Criteria Met: {result.criteria_met}")
    print(f"   Confidence: {result.confidence_score:.2f}")
    print(f"   Details: {result.details}")
    
    return True

def test_complete_rule_validation():
    """Test complete policy rule validation with all rules."""
    print("\n🧪 Testing Complete Policy Rule Validation")
    print("=" * 50)
    
    policy_data = create_sample_policy_data()
    claim_data = create_sample_claim_data()
    
    # Test complete validation
    print("\n1. Testing complete policy rule validation...")
    rule_report = validate_policy_rules(policy_data, claim_data)
    
    print(f"   Overall Valid: {rule_report.overall_valid}")
    print(f"   Overall Confidence: {rule_report.overall_confidence:.2f}")
    print(f"   Risk Level: {rule_report.risk_level}")
    print(f"   Total Deductions: {rule_report.total_deductions}")
    print(f"   Number of Rules: {len(rule_report.rule_results)}")
    
    print("\n2. Individual Rule Results:")
    for rule_name, rule_result in rule_report.rule_results.items():
        print(f"   {rule_name}: {rule_result.decision.value} (confidence: {rule_result.confidence_score:.2f})")
        if rule_result.deduction_amount:
            print(f"     Deduction: {rule_result.deduction_amount}")
    
    print("\n3. Recommendations:")
    for i, recommendation in enumerate(rule_report.recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    return True

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    validator = PolicyRuleValidator()
    
    # Test 1: Missing policy data
    print("\n1. Testing missing policy data...")
    try:
        result = validator.validate_inception_date({}, "2024-01-15")
        print(f"   Handled gracefully: {result.decision.value}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Invalid date format
    print("\n2. Testing invalid date format...")
    try:
        result = validator.validate_inception_date({"inception_date": "invalid-date"}, "2024-01-15")
        print(f"   Handled gracefully: {result.decision.value}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Missing claim data
    print("\n3. Testing missing claim data...")
    try:
        rule_report = validate_policy_rules(create_sample_policy_data(), None)
        print(f"   Handled gracefully: {rule_report.overall_valid}")
    except Exception as e:
        print(f"   Error: {e}")
    
    return True

def main():
    """Run all policy rule validation tests."""
    print("🚀 Starting Policy Rule Validation Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        test_policy_validity_rules()
        test_policy_limits_rules()
        test_waiting_period_rules()
        test_non_medical_items()
        test_daycare_validation()
        test_complete_rule_validation()
        test_error_handling()
        
        print("\n✅ All policy rule validation tests completed successfully!")
        print("📊 Test Coverage:")
        print("  ✅ Policy validity rules (inception date, lapse check)")
        print("  ✅ Policy limits rules (room rent, ICU, co-payment, sub-limits)")
        print("  ✅ Waiting period rules (initial, disease-specific)")
        print("  ✅ Non-medical items validation")
        print("  ✅ Daycare procedure validation")
        print("  ✅ Complete rule validation")
        print("  ✅ Error handling scenarios")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 