#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from policy_rules import validate_policy_rules, RuleDecision

def test_status_logic():
    """Test the new status logic for all three conditions."""
    print("🧪 Testing New Status Logic")
    print("=" * 35)
    
    # Test Case 1: All rules pass (CLEARED)
    print("\n📋 Test Case 1: All Rules Pass (Should be CLEARED)")
    print("-" * 50)
    
    policy_data_1 = {
        "policy_start_date": "01/01/2024",
        "policy_end_date": "31/12/2024",
        "co_payment": "0",
        "room_rent_capping": 500000,
        "base_sum_assured": 500000
    }
    
    claim_data_1 = {
        "admission_date": "15/06/2024",  # Valid date
        "claim_amount": 50000,
        "condition": "general",
        "hospital_bill": {
            "room_rent": 5000,
            "icu_charges": 15000,
            "procedure": "general surgery",
            "procedure_cost": 30000
        }
    }
    
    result_1 = validate_policy_rules(policy_data_1, claim_data_1)
    print(f"Status: {result_1.status}")
    print(f"Total Deductions: ₹{result_1.total_deductions}")
    print(f"Rejected Rules: {sum(1 for r in result_1.rule_results.values() if r.decision == RuleDecision.REJECT)}")
    
    # Test Case 2: Some deductions but no rejections (CLEARED WITH DEDUCTIONS)
    print("\n📋 Test Case 2: Deductions but No Rejections (Should be CLEARED WITH DEDUCTIONS)")
    print("-" * 50)
    
    policy_data_2 = {
        "policy_start_date": "01/01/2024",
        "policy_end_date": "31/12/2024",
        "co_payment": "10",  # 10% co-payment
        "room_rent_capping": 500000,
        "base_sum_assured": 500000
    }
    
    claim_data_2 = {
        "admission_date": "15/06/2024",  # Valid date
        "claim_amount": 50000,
        "condition": "general",
        "hospital_bill": {
            "room_rent": 5000,
            "icu_charges": 15000,
            "procedure": "general surgery",
            "procedure_cost": 30000
        }
    }
    
    result_2 = validate_policy_rules(policy_data_2, claim_data_2)
    print(f"Status: {result_2.status}")
    print(f"Total Deductions: ₹{result_2.total_deductions}")
    print(f"Rejected Rules: {sum(1 for r in result_2.rule_results.values() if r.decision == RuleDecision.REJECT)}")
    
    # Test Case 3: Some rules rejected (REJECTED)
    print("\n📋 Test Case 3: Some Rules Rejected (Should be REJECTED)")
    print("-" * 50)
    
    policy_data_3 = {
        "policy_start_date": "01/01/2024",
        "policy_end_date": "31/12/2024",
        "co_payment": "0",
        "room_rent_capping": 500000,
        "base_sum_assured": 500000
    }
    
    claim_data_3 = {
        "admission_date": "15/01/2024",  # Too early - should fail waiting period
        "claim_amount": 50000,
        "condition": "cardiac",  # Cardiac condition requires waiting period
        "hospital_bill": {
            "room_rent": 5000,
            "icu_charges": 15000,
            "procedure": "cardiac surgery",
            "procedure_cost": 30000
        }
    }
    
    result_3 = validate_policy_rules(policy_data_3, claim_data_3)
    print(f"Status: {result_3.status}")
    print(f"Total Deductions: ₹{result_3.total_deductions}")
    print(f"Rejected Rules: {sum(1 for r in result_3.rule_results.values() if r.decision == RuleDecision.REJECT)}")
    
    # Summary
    print("\n📊 Summary:")
    print(f"✅ Test 1 (All Pass): {result_1.status}")
    print(f"⚠️  Test 2 (Deductions): {result_2.status}")
    print(f"❌ Test 3 (Rejected): {result_3.status}")

if __name__ == "__main__":
    test_status_logic() 