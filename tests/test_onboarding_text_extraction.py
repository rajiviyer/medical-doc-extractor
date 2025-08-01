#!/usr/bin/env python3
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from loader import extract_all_relevant_docs_with_metadata

def test_onboarding_text_extraction():
    """Test text extraction from onboarding form to check for admission date."""
    print("🧪 Testing Onboarding Form Text Extraction")
    print("=" * 50)
    
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
        
        # Find the onboarding form
        onboarding_metadata = None
        for metadata in metadata_list:
            if 'onboarding' in metadata.filename.lower():
                onboarding_metadata = metadata
                break
        
        if not onboarding_metadata:
            print("❌ Onboarding form not found in processed documents")
            return
        
        print(f"\n📋 Onboarding Form Details:")
        print(f"  Filename: {onboarding_metadata.filename}")
        print(f"  Type: {onboarding_metadata.type}")
        print(f"  Source: {onboarding_metadata.source}")
        print(f"  Success: {onboarding_metadata.extraction_success}")
        
        if onboarding_metadata.text:
            print(f"\n📄 Extracted Text (first 1000 characters):")
            print("-" * 50)
            print(onboarding_metadata.text[:1000])
            print("-" * 50)
            
            # Search for date patterns in the text
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
                matches = re.findall(pattern, onboarding_metadata.text)
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
                if keyword.lower() in onboarding_metadata.text.lower():
                    # Find the context around the keyword
                    text_lower = onboarding_metadata.text.lower()
                    keyword_pos = text_lower.find(keyword.lower())
                    if keyword_pos != -1:
                        start = max(0, keyword_pos - 50)
                        end = min(len(onboarding_metadata.text), keyword_pos + len(keyword) + 50)
                        context = onboarding_metadata.text[start:end]
                        print(f"  '{keyword}' found in context: ...{context}...")
                else:
                    print(f"  '{keyword}' not found")
        else:
            print("❌ No text extracted from onboarding form")
        
    except Exception as e:
        print(f"❌ Error during text extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_onboarding_text_extraction() 