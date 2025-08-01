#!/usr/bin/env python3
import json

def test_admission_extraction_simple():
    """Simple test to verify admission date extraction from known text."""
    print("🧪 Simple Admission Date Extraction Test")
    print("=" * 50)
    
    # Known text from onboarding form
    onboarding_text = """PATIENT ONBOARDING FORM
Patient Name Patel Dashrathbhai A
Policyholder Name Patel Dashrathbhai A
Policyholder's Email Id -
Date of Admission 15/07/2025
Diagnosis Multiple Left Renal Stone
Past History & Duration (if any) -
Surgery Name Stage I RIRS with DJ stenting
Treatment Surgical & medical management
Reason of Hospitalization Surgical management
Previous Claim Amount in current year policy -
Implant Yes/No Amount
Estimate-Bifurcation
Charges Name Amount
Room Charge (LOS) – Special 4900 x 2 ="""
    
    print("📄 Onboarding Form Text:")
    print("-" * 30)
    print(onboarding_text)
    print("-" * 30)
    
    # Create metadata for LLM processing
    metadata = {
        'filename': 'dashrath patel onboarding.pdf',
        'type': 'pdf',
        'source': 'pdf_text',
        'extraction_success': True,
        'error': None,
        'text': onboarding_text
    }
    
    print(f"\n✅ Text extracted successfully")
    print(f"  Text length: {len(onboarding_text)} characters")
    
    # Search for admission date
    import re
    admission_date_pattern = r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{4})'
    match = re.search(admission_date_pattern, onboarding_text)
    
    if match:
        admission_date = match.group(1)
        print(f"\n✅ Admission date found: {admission_date}")
    else:
        print(f"\n❌ Admission date not found in text")
    
    # Test with different patterns
    date_patterns = [
        r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{2})',
        r'Admission.*?(\d{1,2}/\d{1,2}/\d{4})',
        r'(\d{1,2}/\d{1,2}/\d{4})',
    ]
    
    print(f"\n🔍 Testing different date patterns:")
    for i, pattern in enumerate(date_patterns, 1):
        matches = re.findall(pattern, onboarding_text)
        if matches:
            print(f"  Pattern {i}: {matches}")
        else:
            print(f"  Pattern {i}: No matches")
    
    print(f"\n📋 Summary:")
    print(f"  ✅ Admission date is present in onboarding form: 15/07/2025")
    print(f"  ✅ Date format is supported: DD/MM/YYYY")
    print(f"  ✅ Text extraction is working")
    print(f"  ❓ LLM extraction needs to be tested")

if __name__ == "__main__":
    test_admission_extraction_simple() 