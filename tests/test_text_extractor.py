#!/usr/bin/env python3
"""
Test script for the modular text extractor.
"""

import logging
from pathlib import Path
from app.text_extractor import TextExtractor, create_pdf_extractor, create_image_extractor
from app.directory_scanner import DirectoryScanner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_text_extractor():
    """Test the text extractor functionality."""
    
    print("=== Testing Text Extractor ===\n")
    
    # Test 1: Basic extractor initialization
    print("1. Testing basic extractor initialization...")
    try:
        extractor = TextExtractor()
        print("✓ Text extractor initialized successfully")
    except Exception as e:
        print(f"✗ Text extractor initialization failed: {e}")
        return
    
    # Test 2: PDF extractor
    print("\n2. Testing PDF extractor...")
    try:
        pdf_extractor = create_pdf_extractor()
        print("✓ PDF extractor created successfully")
    except Exception as e:
        print(f"✗ PDF extractor creation failed: {e}")
    
    # Test 3: Image extractor
    print("\n3. Testing image extractor...")
    try:
        image_extractor = create_image_extractor()
        print("✓ Image extractor created successfully")
    except Exception as e:
        print(f"✗ Image extractor creation failed: {e}")
    
    # Test 4: Find test files
    print("\n4. Finding test files...")
    try:
        scanner = DirectoryScanner(base_directory="data")
        files = scanner.scan_directory()
        
        # Separate files by type
        pdf_files = [f for f in files if f.file_type == 'pdf']
        image_files = [f for f in files if f.file_type == 'image']
        
        print(f"✓ Found {len(pdf_files)} PDF files and {len(image_files)} image files")
        
        if not pdf_files and not image_files:
            print("  No test files found")
            return
            
    except Exception as e:
        print(f"✗ File discovery failed: {e}")
        return
    
    # Test 5: Extract from PDF files
    print("\n5. Testing PDF text extraction...")
    if pdf_files:
        try:
            test_pdf = pdf_files[0]
            print(f"  Testing with: {test_pdf.filename}")
            
            result = pdf_extractor.extract_text(test_pdf.absolute_path)
            
            print(f"✓ PDF extraction completed")
            print(f"  - Success: {result.extraction_success}")
            print(f"  - Method: {result.extraction_method}")
            print(f"  - Confidence: {result.confidence_score:.2f}")
            print(f"  - Processing time: {result.processing_time:.2f}s")
            print(f"  - Page count: {result.page_count}")
            
            if result.extraction_success and result.text_content:
                text_preview = result.text_content[:200] + "..." if len(result.text_content) > 200 else result.text_content
                print(f"  - Text preview: {text_preview}")
            elif result.error_message:
                print(f"  - Error: {result.error_message}")
                
        except Exception as e:
            print(f"✗ PDF extraction failed: {e}")
    else:
        print("  No PDF files available for testing")
    
    # Test 6: Extract from image files
    print("\n6. Testing image text extraction...")
    if image_files:
        try:
            test_image = image_files[0]
            print(f"  Testing with: {test_image.filename}")
            
            result = image_extractor.extract_text(test_image.absolute_path)
            
            print(f"✓ Image extraction completed")
            print(f"  - Success: {result.extraction_success}")
            print(f"  - Method: {result.extraction_method}")
            print(f"  - Confidence: {result.confidence_score:.2f}")
            print(f"  - Processing time: {result.processing_time:.2f}s")
            
            if result.extraction_success and result.text_content:
                text_preview = result.text_content[:200] + "..." if len(result.text_content) > 200 else result.text_content
                print(f"  - Text preview: {text_preview}")
            elif result.error_message:
                print(f"  - Error: {result.error_message}")
                
        except Exception as e:
            print(f"✗ Image extraction failed: {e}")
    else:
        print("  No image files available for testing")
    
    # Test 7: Batch extraction
    print("\n7. Testing batch extraction...")
    try:
        # Test with a small batch of files
        test_files = pdf_files[:2] + image_files[:1]  # Up to 3 files
        if test_files:
            file_paths = [f.absolute_path for f in test_files]
            print(f"  Testing batch extraction with {len(file_paths)} files")
            
            results = extractor.batch_extract(file_paths)
            
            success_count = sum(1 for r in results if r.extraction_success)
            avg_time = sum(r.processing_time for r in results) / len(results) if results else 0
            
            print(f"✓ Batch extraction completed")
            print(f"  - Success rate: {success_count}/{len(results)}")
            print(f"  - Average time: {avg_time:.2f}s per file")
            
            # Show individual results
            for i, result in enumerate(results):
                status = "✓" if result.extraction_success else "✗"
                print(f"    {status} {result.filename} ({result.extraction_method})")
                
        else:
            print("  No files available for batch testing")
            
    except Exception as e:
        print(f"✗ Batch extraction failed: {e}")
    
    print("\n=== Text Extractor Test Complete ===")

if __name__ == "__main__":
    test_text_extractor() 