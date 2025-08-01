#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from loader import extract_all_relevant_docs_with_metadata
from prompts import get_gemini_policy_prompt
from gemini_extract import extract_fields_with_gemini
from validation import validate_extraction_result

def test_admission_date_extraction():
    """Test extraction of admission date from onboarding forms."""
    print("🧪 Testing Admission Date Extraction from Onboarding Forms")
    print("=" * 60)
    
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
                print(f"     Text preview: {metadata.text[:100]}...")
            print()
        
        # Prepare metadata for LLM
        metadata_json = json.dumps([metadata.__dict__ for metadata in metadata_list], indent=2)
        
        # Extract with Gemini
        print("🤖 Extracting with Gemini...")
        extraction_result = extract_fields_with_gemini(get_gemini_policy_prompt(metadata_json))
        
        if extraction_result is None:
            print("❌ Extraction failed")
            return
        
        print("✅ Extraction completed")
        print("\n📊 Extracted Fields:")
        print("=" * 60)
        
        # Check for date fields
        date_fields = ['policy_start_date', 'policy_end_date', 'date_of_admission']
        
        for field in date_fields:
            value = extraction_result.get(field, "Not found")
            print(f"{field}: {value}")
        
        print("\n📋 All Extracted Fields:")
        for key, value in extraction_result.items():
            print(f"  {key}: {value}")
        
        # Validate the extraction
        print("\n🔍 Validating extraction...")
        validation_result = validate_extraction_result(extraction_result)
        
        print(f"Overall Valid: {validation_result.overall_valid}")
        print(f"Overall Confidence: {validation_result.overall_confidence:.3f}")
        
        # Check validation for date fields
        print("\n📅 Date Field Validation:")
        for field in date_fields:
            if field in validation_result.field_results:
                result = validation_result.field_results[field]
                print(f"  {field}:")
                print(f"    Valid: {result.is_valid}")
                print(f"    Confidence: {result.confidence_score:.3f}")
                print(f"    Value: {result.value}")
                if result.validation_messages:
                    print(f"    Messages: {result.validation_messages}")
        
        # Save results
        output_data = {
            "extraction": extraction_result,
            "validation": validation_result.to_dict()
        }
        
        os.makedirs("output", exist_ok=True)
        with open("output/extracted_summary_with_admission.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to output/extracted_summary_with_admission.json")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admission_date_extraction() 