#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from loader import extract_all_relevant_docs_with_metadata
from prompts import get_gemini_policy_prompt

def test_document_inclusion():
    """Test if onboarding form is being included in LLM processing."""
    print("🧪 Testing Document Inclusion for LLM")
    print("=" * 45)
    
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
        onboarding_found = False
        for i, metadata in enumerate(metadata_list, 1):
            print(f"  {i}. {metadata.filename}")
            print(f"     Success: {metadata.extraction_success}")
            if metadata.text:
                print(f"     Text length: {len(metadata.text)} characters")
                # Check if admission date is in the text
                if 'Date of Admission' in metadata.text:
                    print(f"     ✅ Contains 'Date of Admission'")
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
                
                # Check if this is onboarding form
                if 'onboarding' in metadata.filename.lower():
                    onboarding_found = True
                    print(f"     ✅ ONBOARDING FORM IDENTIFIED!")
            else:
                print(f"     ❌ No text extracted")
            print()
        
        if onboarding_found:
            print("✅ Onboarding form found in processed documents")
        else:
            print("❌ Onboarding form NOT found in processed documents")
        
        # Convert to JSON for LLM
        metadata_json = json.dumps([metadata.__dict__ for metadata in metadata_list], indent=2)
        
        # Get the prompt
        prompt = get_gemini_policy_prompt(metadata_json)
        
        print(f"\n📄 Prompt Preview (first 1000 chars):")
        print("-" * 50)
        print(prompt[:1000])
        print("-" * 50)
        
        # Check if onboarding form text is in the prompt
        onboarding_text_found = False
        for metadata in metadata_list:
            if metadata.text and 'Date of Admission' in metadata.text:
                if metadata.text in prompt:
                    onboarding_text_found = True
                    print(f"✅ Onboarding form text found in LLM prompt")
                    break
        
        if not onboarding_text_found:
            print(f"❌ Onboarding form text NOT found in LLM prompt")
        
        print(f"\n📊 Summary:")
        print(f"  Total documents: {len(metadata_list)}")
        print(f"  Onboarding form found: {onboarding_found}")
        print(f"  Onboarding text in prompt: {onboarding_text_found}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_document_inclusion() 