#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from loader import extract_all_relevant_docs_with_metadata
from prompts import get_gemini_policy_prompt
from gemini_extract import extract_fields_with_gemini

def test_llm_extraction_debug():
    """Debug why LLM is not extracting admission date."""
    print("🧪 Debugging LLM Extraction")
    print("=" * 35)
    
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
        for i, metadata in enumerate(metadata_list, 1):
            print(f"  {i}. {metadata.filename}")
            print(f"     Success: {metadata.extraction_success}")
            if metadata.text:
                print(f"     Text length: {len(metadata.text)} characters")
                # Check if admission date is in the text
                if 'admission' in metadata.text.lower():
                    print(f"     ✅ Contains 'admission' keyword")
                    # Find the admission date in text
                    import re
                    admission_pattern = r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{4})'
                    match = re.search(admission_pattern, metadata.text)
                    if match:
                        print(f"     ✅ Found admission date: {match.group(1)}")
                    else:
                        print(f"     ❌ No admission date pattern found")
                else:
                    print(f"     ❌ No 'admission' keyword found")
            else:
                print(f"     ❌ No text extracted")
            print()
        
        # Check if onboarding form is included
        onboarding_found = any('onboarding' in metadata.filename.lower() for metadata in metadata_list)
        if onboarding_found:
            print("✅ Onboarding form found in processed documents")
        else:
            print("❌ Onboarding form NOT found in processed documents")
        
        # Try LLM extraction with first few documents
        print(f"\n🤖 Testing LLM extraction with {min(3, len(metadata_list))} documents...")
        test_metadata_list = metadata_list[:3]  # Use first 3 documents
        
        # Convert to JSON for LLM
        metadata_json = json.dumps([metadata.__dict__ for metadata in test_metadata_list], indent=2)
        
        # Get the prompt
        prompt = get_gemini_policy_prompt(metadata_json)
        
        print(f"\n📄 Prompt Preview (first 500 chars):")
        print("-" * 50)
        print(prompt[:500])
        print("-" * 50)
        
        # Try LLM extraction
        print(f"\n🔍 Running LLM extraction...")
        extraction_result = extract_fields_with_gemini(prompt)
        
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
    test_llm_extraction_debug() 