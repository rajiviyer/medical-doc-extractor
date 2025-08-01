#!/usr/bin/env python3
"""
Complete List of Policy Rules with Sections and Criteria
=======================================================

This document provides the complete list of all policy rules used in the validation system,
organized by their respective sections with detailed criteria and decision logic.
"""

def get_all_policy_rules():
    """Return complete list of all policy rules with their sections and criteria."""
    
    rules = {
        # POLICY VALIDITY SECTION
        "inception_date": {
            "section": "Policy Validity",
            "rule_name": "Inception Date",
            "criteria": "Policy must be active on date of admission",
            "decision_if_fails": "Reject",
            "document_required": ["Policy Master Document", "Policy Document"],
            "description": "Validates that the policy start date is before or equal to the admission date"
        },
        "lapse_check": {
            "section": "Policy Validity", 
            "rule_name": "Lapse Check",
            "criteria": "Policy should not be in grace/lapse period",
            "decision_if_fails": "Reject",
            "document_required": ["Policy Master Document", "Policy Document", "Payment Receipt"],
            "description": "Checks if policy is active and not in grace/lapse period"
        },
        
        # POLICY LIMITS SECTION
        "room_rent_eligibility": {
            "section": "Policy Limits",
            "rule_name": "Room Rent Eligibility", 
            "criteria": "Room rent within entitled limit",
            "decision_if_fails": "Proportionate Deduction",
            "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill"],
            "description": "Validates room rent charges against policy room rent capping"
        },
        "icu_capping": {
            "section": "Policy Limits",
            "rule_name": "ICU Capping",
            "criteria": "ICU charges within cap",
            "decision_if_fails": "Deduct",
            "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill"],
            "description": "Validates ICU charges against policy ICU capping limit"
        },
        "co_payment": {
            "section": "Policy Limits",
            "rule_name": "Co-payment",
            "criteria": "Co-pay % as per policy",
            "decision_if_fails": "Deduct",
            "document_required": ["Policy Master Document", "Policy Document"],
            "description": "Applies co-payment percentage to claim amount"
        },
        "sub_limits": {
            "section": "Policy Limits",
            "rule_name": "Sub-limits",
            "criteria": "Procedure under cap limit",
            "decision_if_fails": "Cap Limit Applied",
            "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill"],
            "description": "Validates procedure costs against specific sub-limits (cataract, hernia, etc.)"
        },
        "daycare": {
            "section": "Policy Limits",
            "rule_name": "Daycare",
            "criteria": "Within IRDA-approved daycare",
            "decision_if_fails": "Reject",
            "document_required": ["Policy Master Document", "Policy Document", "Discharge Summary"],
            "description": "Validates daycare procedures against IRDA-approved list"
        },
        
        # WAITING PERIODS SECTION
        "initial_waiting": {
            "section": "Waiting Periods",
            "rule_name": "Initial Waiting",
            "criteria": "<30 days for non-accident",
            "decision_if_fails": "Reject",
            "document_required": ["Policy Master Document", "Policy Document"],
            "description": "Validates that policy is at least 30 days old for non-accident claims"
        },
        "disease_specific": {
            "section": "Waiting Periods",
            "rule_name": "Disease Specific",
            "criteria": "Condition covered post waiting period",
            "decision_if_fails": "Reject",
            "document_required": ["Policy Master Document", "Policy Document"],
            "description": "Validates disease-specific waiting periods (diabetes: 90 days, cardiac: 180 days, cancer: 365 days, etc.)"
        },
        "maternity": {
            "section": "Waiting Periods",
            "rule_name": "Maternity",
            "criteria": "Covered with waiting period",
            "decision_if_fails": "Reject",
            "document_required": ["Policy Master Document", "Policy Document"],
            "description": "Validates maternity waiting period (270 days)"
        },
        "non_medical": {
            "section": "Waiting Periods",
            "rule_name": "Non-Medical",
            "criteria": "IRDA non-payables",
            "decision_if_fails": "Deduct",
            "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill", "Itemized Bill"],
            "description": "Identifies and deducts non-medical items as per IRDA guidelines"
        }
    }
    
    return rules

def print_rules_by_section():
    """Print all rules organized by section."""
    rules = get_all_policy_rules()
    
    # Group rules by section
    sections = {}
    for rule_id, rule_data in rules.items():
        section = rule_data["section"]
        if section not in sections:
            sections[section] = []
        sections[section].append(rule_data)
    
    print("📋 COMPLETE POLICY RULES LIST")
    print("=" * 50)
    print()
    
    for section_name, section_rules in sections.items():
        print(f"🔹 {section_name.upper()}")
        print("-" * len(section_name) + "-" * 8)
        print()
        
        for i, rule in enumerate(section_rules, 1):
            print(f"  {i}. {rule['rule_name']}")
            print(f"     Criteria: {rule['criteria']}")
            print(f"     Decision if fails: {rule['decision_if_fails']}")
            print(f"     Documents required: {', '.join(rule['document_required'])}")
            print(f"     Description: {rule['description']}")
            print()
    
    print("📊 SUMMARY BY SECTION")
    print("=" * 25)
    for section_name, section_rules in sections.items():
        print(f"  {section_name}: {len(section_rules)} rules")
    
    print(f"\n📈 TOTAL RULES: {len(rules)}")

def print_rules_table():
    """Print rules in a table format."""
    rules = get_all_policy_rules()
    
    print("📋 POLICY RULES TABLE")
    print("=" * 120)
    print(f"{'SECTION':<20} {'RULE':<25} {'CRITERIA':<40} {'DECISION IF FAILS':<20}")
    print("-" * 120)
    
    for rule_id, rule_data in rules.items():
        section = rule_data["section"]
        rule_name = rule_data["rule_name"]
        criteria = rule_data["criteria"]
        decision = rule_data["decision_if_fails"]
        
        print(f"{section:<20} {rule_name:<25} {criteria:<40} {decision:<20}")
    
    print("-" * 120)

if __name__ == "__main__":
    print_rules_by_section()
    print("\n" + "="*50 + "\n")
    print_rules_table() 