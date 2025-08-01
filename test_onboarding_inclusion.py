#!/usr/bin/env python3
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "app"))

from loader import extract_all_relevant_docs_with_metadata

def test_onboarding_inclusion():
    """Test if onboarding form is being included in document processing."""
    print("🧪 Testing Onboarding Form Inclusion")
    print("=" * 40)
    
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
            if 'onboarding' in metadata.filename.lower():
                onboarding_found = True
                print(f"     ✅ ONBOARDING FORM FOUND!")
                if metadata.text:
                    print(f"     Text length: {len(metadata.text)} characters")
                    # Check for admission date
                    if 'Date of Admission' in metadata.text:
                        print(f"     ✅ Contains 'Date of Admission'")
                        # Extract the date
                        import re
                        admission_pattern = r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{4})'
                        match = re.search(admission_pattern, metadata.text)
                        if match:
                            print(f"     ✅ Admission date found: {match.group(1)}")
                        else:
                            print(f"     ❌ Admission date pattern not found")
                    else:
                        print(f"     ❌ No 'Date of Admission' found in text")
                else:
                    print(f"     ❌ No text extracted from onboarding form")
            else:
                print(f"     Type: {metadata.filename.split('.')[-1]}")
        
        if onboarding_found:
            print(f"\n✅ SUCCESS: Onboarding form is being processed!")
        else:
            print(f"\n❌ FAILURE: Onboarding form is NOT being processed!")
            print("This means the admission date won't be extracted.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_onboarding_inclusion() 