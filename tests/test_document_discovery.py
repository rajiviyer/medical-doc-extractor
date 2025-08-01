#!/usr/bin/env python3
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from loader import extract_all_relevant_docs_with_metadata

def test_document_discovery():
    """Test discovery of relevant documents including onboarding forms."""
    print("🧪 Testing Document Discovery")
    print("=" * 40)
    
    # Test directory path
    test_dir = "data/Dashrath Patel initial"
    
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    try:
        # Extract all relevant documents
        print(f"📄 Processing directory: {test_dir}")
        metadata_list = extract_all_relevant_docs_with_metadata(test_dir, test_dir)
        
        if not metadata_list:
            print("❌ No relevant documents found")
            return
        
        print(f"✅ Found {len(metadata_list)} relevant document(s)")
        
        # Display what documents were found
        print("\n📋 Documents Found:")
        for i, metadata in enumerate(metadata_list, 1):
            print(f"  {i}. {metadata.filename}")
            print(f"     Type: {metadata.type}")
            print(f"     Source: {metadata.source}")
            print(f"     Success: {metadata.extraction_success}")
            if metadata.text:
                print(f"     Text preview: {metadata.text[:200]}...")
            print()
        
        # Check if onboarding form was found
        onboarding_found = any('onboarding' in metadata.filename.lower() for metadata in metadata_list)
        if onboarding_found:
            print("✅ Onboarding form found!")
        else:
            print("❌ Onboarding form not found")
            
        # Check if policy documents were found
        policy_found = any('policy' in metadata.filename.lower() for metadata in metadata_list)
        if policy_found:
            print("✅ Policy documents found!")
        else:
            print("❌ Policy documents not found")
        
    except Exception as e:
        print(f"❌ Error during document discovery: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_document_discovery() 