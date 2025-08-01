#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from loader import extract_all_relevant_docs_with_metadata
from prompts import get_gemini_policy_prompt
from gemini_extract import extract_fields_with_gemini

def test_llm_input():
    """Test what input the LLM is receiving and why admission date extraction fails."""
    print("🧪 Testing LLM Input for Admission Date Extraction")
    print("=" * 55)
    
    # Test directory path
    test_dir = "data/Dashrath Patel initial"
    
    try:
        # Extract all relevant documents
        print(f"📄 Processing directory: {test_dir}")
        metadata_list = extract_all_relevant_docs_with_metadata(test_dir, test_dir)
        
        if not metadata_list:
            print("❌ No relevant documents found")
            return
        
        print(f"✅ Found {len(metadata_list)} relevant document(s)")
        
        # Show what documents were found
        print("\n📋 Documents Found:")
        onboarding_text = None
        for i, metadata in enumerate(metadata_list, 1):
            print(f"  {i}. {metadata.filename}")
            print(f"     Success: {metadata.extraction_success}")
            if metadata.text:
                print(f"     Text length: {len(metadata.text)} characters")
                # Check if admission date is in the text
                if 'Date of Admission' in metadata.text:
                    print(f"     ✅ Contains 'Date of Admission'")
                    onboarding_text = metadata.text
                    # Find the admission date in text
                    import re
                    admission_pattern = r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{4})'
                    match = re.search(admission_pattern, metadata.text)
                    if match:
                        print(f"     ✅ Found admission date: {match.group(1)}")
                    else:
                        print(f"     ❌ No admission date pattern found")
                elif 'admission' in metadata.text.lower():
                    print(f"     ✅ Contains 'admission' keyword")
                else:
                    print(f"     ❌ No admission-related keywords found")
            else:
                print(f"     ❌ No text extracted")
            print()
        
        # Convert to JSON for LLM
        metadata_json = json.dumps([metadata.__dict__ for metadata in metadata_list], indent=2)
        
        # Get the prompt
        prompt = get_gemini_policy_prompt(metadata_json)
        
        print(f"\n📄 LLM Prompt Analysis:")
        print("-" * 30)
        
        # Check if onboarding form text is in the prompt
        if onboarding_text:
            if onboarding_text in prompt:
                print(f"✅ Onboarding form text found in LLM prompt")
            else:
                print(f"❌ Onboarding form text NOT found in LLM prompt")
                print(f"   This is the issue - the onboarding form is not being sent to the LLM")
        
        # Check prompt length
        print(f"Prompt length: {len(prompt)} characters")
        
        # Show a sample of the prompt
        print(f"\n📄 Prompt Sample (first 500 chars):")
        print("-" * 50)
        print(prompt[:500])
        print("-" * 50)
        
        # Try LLM extraction
        print(f"\n🔍 Testing LLM Extraction...")
        extraction_result = extract_fields_with_gemini(prompt)
        
        if extraction_result:
            print(f"✅ LLM extraction completed")
            print(f"  date_of_admission: {extraction_result.get('date_of_admission', 'Not found')}")
            print(f"  policy_start_date: {extraction_result.get('policy_start_date', 'Not found')}")
            print(f"  policy_end_date: {extraction_result.get('policy_end_date', 'Not found')}")
            
            # Check if admission date is null
            if extraction_result.get('date_of_admission') == 'null':
                print(f"❌ ISSUE: LLM returned 'null' for admission date")
                print(f"   Even though the text contains: 'Date of Admission 15/07/2025'")
        else:
            print(f"❌ LLM extraction failed")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm_input() 