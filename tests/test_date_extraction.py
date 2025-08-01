#!/usr/bin/env python3
import sys
import os
import json
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from loader import extract_policy_docs_with_metadata
from prompts import get_gemini_policy_prompt
from gemini_extract import extract_fields_with_gemini
from validation import validate_extraction_result

def test_date_extraction():
    """Test extraction with new date fields."""
    print("🧪 Testing Date Field Extraction")
    
    # Test file path
    test_file = "data/Dashrath Patel initial/dashrath patel policy.pdf"
    
    if not os.path.exists(test_file):
        print(f"❌ Test file not found: {test_file}")
        return
    
    try:
        # Extract policy documents
        print(f"📄 Processing file: {test_file}")
        metadata_list = extract_policy_docs_with_metadata(test_file, test_file)
        
        if not metadata_list:
            print("❌ No policy documents found")
            return
        
        print(f"✅ Found {len(metadata_list)} policy document(s)")
        
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
        
        # Check for new date fields
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
        with open("output/extracted_summary_with_dates.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Results saved to output/extracted_summary_with_dates.json")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_date_extraction() 