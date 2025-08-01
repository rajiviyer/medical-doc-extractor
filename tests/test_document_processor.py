#!/usr/bin/env python3
"""
Test script for the comprehensive document processor.
"""

import logging
import json
from pathlib import Path
from app.document_processor import DocumentProcessor, create_policy_processor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_document_processor():
    """Test the complete document processor functionality."""
    
    print("=== Testing Document Processor ===\n")
    
    # Test 1: Basic processor initialization
    print("1. Testing basic processor initialization...")
    try:
        processor = DocumentProcessor(base_directory="data")
        print("✓ Document processor initialized successfully")
    except Exception as e:
        print(f"✗ Document processor initialization failed: {e}")
        return
    
    # Test 2: Policy processor
    print("\n2. Testing policy processor...")
    try:
        policy_processor = create_policy_processor(base_dir="data")
        print("✓ Policy processor created successfully")
    except Exception as e:
        print(f"✗ Policy processor creation failed: {e}")
    
    # Test 3: Get available directories
    print("\n3. Testing directory listing...")
    try:
        directories = processor.get_available_directories()
        print(f"✓ Found {len(directories)} available directories:")
        for dir_name in directories[:5]:  # Show first 5
            print(f"  - {dir_name}")
        if len(directories) > 5:
            print(f"  ... and {len(directories) - 5} more")
    except Exception as e:
        print(f"✗ Directory listing failed: {e}")
    
    # Test 4: Process specific directory
    print("\n4. Testing directory processing...")
    try:
        if directories:
            target_dir = directories[0]  # Use first available directory
            print(f"  Processing directory: {target_dir}")
            
            result = processor.process_by_directory_name(target_dir, recursive=True)
            
            print(f"✓ Directory processing completed")
            print(f"  - Processing ID: {result.processing_id}")
            print(f"  - Files discovered: {result.total_files_discovered}")
            print(f"  - Successful extractions: {result.successful_extractions}")
            print(f"  - Failed extractions: {result.failed_extractions}")
            print(f"  - Processing time: {result.processing_time:.2f}s")
            print(f"  - Total text length: {result.metadata.get('total_text_length', 0)} characters")
            print(f"  - Average confidence: {result.metadata.get('average_confidence', 0):.2f}")
            
            if result.errors:
                print(f"  - Errors: {len(result.errors)}")
                for error in result.errors[:3]:  # Show first 3 errors
                    print(f"    * {error}")
                if len(result.errors) > 3:
                    print(f"    ... and {len(result.errors) - 3} more errors")
            
            # Show sample extraction results
            if result.extraction_results:
                print(f"  - Sample results:")
                for i, extraction in enumerate(result.extraction_results[:3]):
                    status = "✓" if extraction.extraction_success else "✗"
                    print(f"    {status} {extraction.filename} ({extraction.extraction_method})")
                if len(result.extraction_results) > 3:
                    print(f"    ... and {len(result.extraction_results) - 3} more files")
                    
        else:
            print("  No directories available for testing")
            
    except Exception as e:
        print(f"✗ Directory processing failed: {e}")
    
    # Test 5: Process with file filter
    print("\n5. Testing file filtering...")
    try:
        print("  Processing files with 'policy' in filename...")
        result = processor.process_directory(file_filter="policy")
        
        print(f"✓ Filtered processing completed")
        print(f"  - Files discovered: {result.total_files_discovered}")
        print(f"  - Successful extractions: {result.successful_extractions}")
        print(f"  - Processing time: {result.processing_time:.2f}s")
        
    except Exception as e:
        print(f"✗ File filtering failed: {e}")
    
    # Test 6: Check output files
    print("\n6. Testing output file generation...")
    try:
        output_dir = Path("app/output")
        if output_dir.exists():
            json_files = list(output_dir.glob("*_results.json"))
            print(f"✓ Found {len(json_files)} output files:")
            for json_file in json_files[:3]:  # Show first 3
                print(f"  - {json_file.name}")
            if len(json_files) > 3:
                print(f"  ... and {len(json_files) - 3} more")
                
            # Show sample output structure
            if json_files:
                with open(json_files[0], 'r') as f:
                    sample_data = json.load(f)
                print(f"  - Sample output structure:")
                print(f"    * Processing ID: {sample_data.get('processing_id', 'N/A')}")
                print(f"    * Timestamp: {sample_data.get('timestamp', 'N/A')}")
                print(f"    * Total files: {sample_data.get('total_files_discovered', 0)}")
                print(f"    * Successful: {sample_data.get('successful_extractions', 0)}")
        else:
            print("  No output directory found")
            
    except Exception as e:
        print(f"✗ Output file check failed: {e}")
    
    print("\n=== Document Processor Test Complete ===")

if __name__ == "__main__":
    test_document_processor() 