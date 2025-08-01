#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from policy_rules import validate_policy_rules
from schemas import ExtractedFields
from policy_report_generator import generate_policy_rule_report
from loader import extract_all_relevant_docs_with_metadata
import re

def extract_admission_date_from_text(metadata_list):
    """Extract admission date from document text as fallback when LLM fails."""
    admission_patterns = [
        r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{2})',
        r'Admission Date\s*:\s*(\d{1,2}/\d{1,2}/\d{4})',
        r'Admission Date\s*:\s*(\d{1,2}/\d{1,2}/\d{2})',
        r'Admitted on\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'Admitted on\s+(\d{1,2}/\d{1,2}/\d{2})'
    ]
    
    for metadata in metadata_list:
        if metadata.text:
            for pattern in admission_patterns:
                match = re.search(pattern, metadata.text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    # Convert 2-digit year to 4-digit year if needed
                    if len(date_str.split('/')[-1]) == 2:
                        year = int(date_str.split('/')[-1])
                        if year < 50:  # Assume 20xx for years < 50
                            year += 2000
                        else:
                            year += 1900
                        date_str = f"{date_str.split('/')[0]}/{date_str.split('/')[1]}/{year:04d}"
                    return date_str
    return None

def regenerate_validation():
    """Regenerate policy validation with corrected admission date."""
    print("🔄 Regenerating Policy Validation")
    print("=" * 35)
    
    # Load the corrected extracted summary
    with open("output/extracted_summary_gemini.json", "r") as f:
        extracted_data = json.load(f)
    
    # Extract policy data
    policy_data = extracted_data.get("extraction", {})
    
    # Create claim data with the corrected admission date using the same logic as main app
    admission_date = policy_data.get("date_of_admission")
    if admission_date == "null" or not admission_date:
        # Try to extract admission date from document text as fallback (same as main app)
        try:
            # Load document metadata to extract admission date
            metadata_list = extract_all_relevant_docs_with_metadata("data/Dashrath Patel initial", "data/Dashrath Patel initial")
            admission_date = extract_admission_date_from_text(metadata_list)
            if not admission_date:
                admission_date = "2024-01-15"  # Default fallback (same as main app)
        except Exception as e:
            print(f"⚠️  Warning: Could not extract admission date from documents: {e}")
            admission_date = "2024-01-15"  # Default fallback (same as main app)
    
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
    
    print("📊 Using Data:")
    print(f"  Policy Start Date: {policy_data.get('policy_start_date')}")
    print(f"  Policy End Date: {policy_data.get('policy_end_date')}")
    print(f"  Admission Date: {claim_data['admission_date']}")
    
    # Run validation
    print("\n🔍 Running Policy Validation...")
    rule_report = validate_policy_rules(policy_data, claim_data)
    
    # Generate the report using the proper report generator
    report_content = generate_policy_rule_report(rule_report, format_type="markdown")
    
    # Write the report
    with open("output/policy_rule_report_gemini_Dashrath Patel initial.md", "w") as f:
        f.write(report_content)
    
    print("✅ Validation report regenerated!")
    print(f"📄 Report saved to: output/policy_rule_report_gemini_Dashrath Patel initial.md")
    
    # Show key results
    print(f"\n📋 Key Results:")
    print(f"  Overall Valid: {rule_report.overall_valid}")
    print(f"  Risk Level: {rule_report.risk_level}")
    
    # Check inception date specifically
    inception_result = rule_report.rule_results.get('inception_date')
    if inception_result:
        print(f"  Inception Date Validation: {inception_result.decision.value}")
        print(f"  Details: {inception_result.details}")

if __name__ == "__main__":
    regenerate_validation() 