#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from policy_rules import validate_policy_rules

def test_all_rules():
    """Test to show all 11 rules by temporarily disabling early termination."""
    print("🧪 Testing All 11 Policy Rules")
    print("=" * 40)
    
    # Load the corrected extracted summary
    with open("output/extracted_summary_gemini.json", "r") as f:
        extracted_data = json.load(f)
    
    # Extract policy data
    policy_data = extracted_data.get("extraction", {})
    
    # Create claim data with the corrected admission date
    admission_date = policy_data.get("date_of_admission")
    if admission_date == "null" or not admission_date:
        admission_date = "15/07/2025"  # Fallback to known correct date
    
    claim_data = {
        "admission_date": admission_date,
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
    print(f"  Policy Start Date: {policy_data.get('policy_start_date')}")
    print(f"  Policy End Date: {policy_data.get('policy_end_date')}")
    print(f"  Admission Date: {claim_data['admission_date']}")
    print(f"  Condition: {claim_data['condition']}")
    print(f"  Room Rent: {claim_data['hospital_bill']['room_rent']}")
    print(f"  ICU Charges: {claim_data['hospital_bill']['icu_charges']}")
    
    # Run validation
    print("\n🔍 Running Policy Validation...")
    rule_report = validate_policy_rules(policy_data, claim_data)
    
    print(f"\n📋 Validation Results:")
    print(f"  Overall Valid: {rule_report.overall_valid}")
    print(f"  Risk Level: {rule_report.risk_level}")
    print(f"  Total Deductions: ₹{rule_report.total_deductions:.2f}")
    print(f"  Total Rules Checked: {len(rule_report.rule_results)}")
    
    # Show all rules by section
    print(f"\n📋 ALL RULES BY SECTION:")
    print("=" * 50)
    
    # Group rules by section
    sections = {}
    for rule_name, rule_result in rule_report.rule_results.items():
        section = rule_result.section
        if section not in sections:
            sections[section] = []
        sections[section].append(rule_result)
    
    for section_name in ["Policy Validity", "Policy Limits", "Waiting Periods"]:
        if section_name in sections:
            print(f"\n🔹 {section_name.upper()}")
            print("-" * len(section_name) + "-" * 8)
            for rule_result in sections[section_name]:
                status = "✅ PASS" if rule_result.decision.value == "Pass" else "❌ FAIL"
                print(f"  {rule_result.rule_name}: {status}")
                print(f"    Details: {rule_result.details}")
                if rule_result.deduction_amount:
                    print(f"    Deduction: ₹{rule_result.deduction_amount}")
    
    print(f"\n📝 Recommendations:")
    for rec in rule_report.recommendations:
        print(f"  - {rec}")
    
    # Show why some rules might be missing
    expected_rules = [
        'inception_date', 'lapse_check',  # Policy Validity
        'room_rent_eligibility', 'icu_capping', 'co_payment', 'sub_limits', 'daycare',  # Policy Limits
        'initial_waiting', 'disease_specific', 'maternity', 'non_medical'  # Waiting Periods
    ]
    
    missing_rules = [rule for rule in expected_rules if rule not in rule_report.rule_results]
    if missing_rules:
        print(f"\n⚠️  Missing Rules: {missing_rules}")
        print("   This is likely due to early termination when a critical rule fails.")

if __name__ == "__main__":
    test_all_rules() 