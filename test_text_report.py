#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from policy_rules import validate_policy_rules
from policy_report_generator import generate_policy_rule_report

def test_text_report():
    """Test generating a text format policy rule validation report."""
    print("🧪 Testing Text Format Report Generation")
    print("=" * 45)
    
    # Create test policy data
    policy_data = {
        "policy_start_date": "01/01/2024",
        "policy_end_date": "31/12/2024",
        "co_payment": "10",  # 10% co-payment to test deductions
        "room_rent_capping": 500000,
        "base_sum_assured": 500000
    }
    
    # Create claim data
    claim_data = {
        "admission_date": "15/06/2024",  # Valid date
        "claim_amount": 50000,
        "condition": "general",
        "hospital_bill": {
            "room_rent": 5000,
            "icu_charges": 15000,
            "procedure": "general surgery",
            "procedure_cost": 30000,
            "itemized_bill": {
                "toiletries": 500,
                "food": 1000
            }
        }
    }
    
    print("📊 Test Data:")
    print(f"  Policy Start: {policy_data['policy_start_date']}")
    print(f"  Policy End: {policy_data['policy_end_date']}")
    print(f"  Co-payment: {policy_data['co_payment']}%")
    print(f"  Admission Date: {claim_data['admission_date']}")
    
    # Run validation
    print("\n🔍 Running Policy Validation...")
    rule_report = validate_policy_rules(policy_data, claim_data)
    
    print("✅ Validation completed!")
    print(f"📊 Status: {rule_report.status}")
    print(f"📊 Total Deductions: ₹{rule_report.total_deductions}")
    
    # Generate text format report
    print("\n📄 Generating Text Format Report...")
    text_report = generate_policy_rule_report(rule_report, format_type="text")
    
    # Save text report
    output_file = "output/policy_rule_report_text.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text_report)
    
    print(f"✅ Text report saved to: {output_file}")
    
    # Display a preview of the text report
    print("\n📋 Text Report Preview:")
    print("=" * 50)
    lines = text_report.split('\n')
    for i, line in enumerate(lines[:30]):  # Show first 30 lines
        print(line)
    if len(lines) > 30:
        print("...")
        print(f"(Report has {len(lines)} total lines)")

if __name__ == "__main__":
    test_text_report() 