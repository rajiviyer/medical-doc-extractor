#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from loader import extract_single_file_with_metadata
from prompts import get_gemini_policy_prompt
from gemini_extract import extract_fields_with_gemini

def test_onboarding_only():
    """Test extraction from onboarding form only."""
    print("🧪 Testing Onboarding Form Only")
    print("=" * 40)
    
    # Test file path
    onboarding_file = "data/Dashrath Patel initial/dashrath patel onboarding.pdf"
    
    if not os.path.exists(onboarding_file):
        print(f"❌ Onboarding file not found: {onboarding_file}")
        return
    
    try:
        print(f"📄 Processing onboarding file: {onboarding_file}")
        
        # Extract text from onboarding form
        metadata = extract_single_file_with_metadata(onboarding_file, "data/Dashrath Patel initial")
        
        if not metadata or not metadata.get('extraction_success'):
            print("❌ Failed to extract text from onboarding form")
            return
        
        print(f"✅ Successfully extracted text from onboarding form")
        print(f"  Source: {metadata.get('source')}")
        print(f"  Text length: {len(metadata.get('text', ''))} characters")
        
        # Show first 500 characters of extracted text
        text = metadata.get('text', '')
        print(f"\n📄 Extracted Text Preview:")
        print("-" * 50)
        print(text[:500])
        print("-" * 50)
        
        # Search for date patterns
        import re
        date_patterns = [
            r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
            r'\d{1,2}/\d{1,2}/\d{2}',   # DD/MM/YY
            r'\d{1,2}/\d{1}/\d{2}',     # DD/M/YY
            r'\d{1}/\d{1,2}/\d{2}',     # D/MM/YY
            r'\d{1}/\d{1}/\d{2}',       # D/M/YY
        ]
        
        print(f"\n🔍 Searching for date patterns:")
        found_dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                found_dates.extend(matches)
                print(f"  Pattern {pattern}: {matches}")
        
        if found_dates:
            print(f"\n✅ Found {len(found_dates)} potential dates:")
            for date in found_dates:
                print(f"  - {date}")
        else:
            print(f"\n❌ No date patterns found in the text")
        
        # Search for admission-related keywords
        admission_keywords = ['admission', 'admitted', 'admit', 'date of admission', 'admission date']
        print(f"\n🔍 Searching for admission-related keywords:")
        for keyword in admission_keywords:
            if keyword.lower() in text.lower():
                # Find the context around the keyword
                text_lower = text.lower()
                keyword_pos = text_lower.find(keyword.lower())
                if keyword_pos != -1:
                    start = max(0, keyword_pos - 50)
                    end = min(len(text), keyword_pos + len(keyword) + 50)
                    context = text[start:end]
                    print(f"  '{keyword}' found in context: ...{context}...")
            else:
                print(f"  '{keyword}' not found")
        
        # Try to extract using LLM
        print(f"\n🤖 Attempting LLM extraction...")
        metadata_json = json.dumps([metadata], indent=2)
        
        extraction_result = extract_fields_with_gemini(get_gemini_policy_prompt(metadata_json))
        
        if extraction_result:
            print(f"✅ LLM extraction completed")
            print(f"  date_of_admission: {extraction_result.get('date_of_admission', 'Not found')}")
            print(f"  policy_start_date: {extraction_result.get('policy_start_date', 'Not found')}")
            print(f"  policy_end_date: {extraction_result.get('policy_end_date', 'Not found')}")
        else:
            print(f"❌ LLM extraction failed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_onboarding_only() 