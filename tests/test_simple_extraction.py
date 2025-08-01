#!/usr/bin/env python3
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from loader import extract_all_relevant_docs_with_metadata

def test_simple_extraction():
    """Simple test to check if the new extraction function works."""
    print("🧪 Simple Extraction Test")
    print("=" * 30)
    
    # Test directory path
    test_dir = "data/Dashrath Patel initial"
    
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    try:
        print(f"📄 Processing directory: {test_dir}")
        print("⏳ This may take a while...")
        
        # Extract all relevant documents
        metadata_list = extract_all_relevant_docs_with_metadata(test_dir, test_dir)
        
        if not metadata_list:
            print("❌ No relevant documents found")
            return
        
        print(f"✅ Found {len(metadata_list)} relevant document(s)")
        
        # Display what documents were found
        print("\n📋 Documents Found:")
        for i, metadata in enumerate(metadata_list, 1):
            print(f"  {i}. {metadata.filename}")
            print(f"     Success: {metadata.extraction_success}")
            if metadata.text:
                print(f"     Text length: {len(metadata.text)} characters")
                print(f"     Preview: {metadata.text[:100]}...")
            else:
                print(f"     No text extracted")
            print()
        
        # Check for onboarding form
        onboarding_found = any('onboarding' in metadata.filename.lower() for metadata in metadata_list)
        if onboarding_found:
            print("✅ Onboarding form found and processed!")
        else:
            print("❌ Onboarding form not found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple_extraction() 