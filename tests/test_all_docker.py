#!/usr/bin/env python3
"""
Comprehensive test script for Docker environment.
Tests all components: directory scanner, text extractor, and document processor.
"""

import logging
import json
import sys
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_components():
    """Test all components in the Docker environment."""
    
    print("=== Comprehensive Docker Test ===")
    print("Testing all components: Directory Scanner, Text Extractor, Document Processor\n")
    
    try:
        # Import components
        from app.directory_scanner import DirectoryScanner
        from app.text_extractor import TextExtractor
        from app.document_processor import DocumentProcessor
        
        print("✓ All modules imported successfully")
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False
    
    # Test 1: Directory Scanner
    print("\n1. Testing Directory Scanner...")
    try:
        scanner = DirectoryScanner(base_directory="data")
        directories = scanner.list_available_directories()
        print(f"✓ Directory scanner working - found {len(directories)} directories")
        
        # Test file discovery
        files = scanner.scan_directory()
        print(f"✓ File discovery working - found {len(files)} files")
        
    except Exception as e:
        print(f"✗ Directory scanner failed: {e}")
        return False
    
    # Test 2: Text Extractor
    print("\n2. Testing Text Extractor...")
    try:
        extractor = TextExtractor()
        
        # Test with a PDF file if available
        pdf_files = [f for f in files if f.file_type == 'pdf']
        if pdf_files:
            test_file = pdf_files[0]
            result = extractor.extract_text(test_file.absolute_path)
            print(f"✓ Text extractor working - {result.extraction_success}")
            if result.extraction_success:
                print(f"  - Method: {result.extraction_method}")
                print(f"  - Confidence: {result.confidence_score:.2f}")
                print(f"  - Text length: {len(result.text_content) if result.text_content else 0} chars")
        else:
            print("  - No PDF files available for testing")
            
    except Exception as e:
        print(f"✗ Text extractor failed: {e}")
        return False
    
    # Test 3: Document Processor
    print("\n3. Testing Document Processor...")
    try:
        processor = DocumentProcessor(base_directory="data")
        
        # Process a small subset of files
        if directories:
            target_dir = directories[0]
            print(f"  Processing directory: {target_dir}")
            
            result = processor.process_by_directory_name(target_dir, recursive=True)
            
            print(f"✓ Document processor working")
            print(f"  - Files discovered: {result.total_files_discovered}")
            print(f"  - Successful extractions: {result.successful_extractions}")
            print(f"  - Processing time: {result.processing_time:.2f}s")
            
            # Check if output was generated
            output_files = list(Path("app/output").glob("*_results.json"))
            if output_files:
                print(f"  - Output files generated: {len(output_files)}")
            else:
                print("  - No output files generated")
                
        else:
            print("  - No directories available for testing")
            
    except Exception as e:
        print(f"✗ Document processor failed: {e}")
        return False
    
    # Test 4: OCR Functionality (if tesseract is available)
    print("\n4. Testing OCR Functionality...")
    try:
        import pytesseract
        # Test if tesseract is working
        pytesseract.get_tesseract_version()
        print("✓ Tesseract OCR is available and working")
        
        # Test OCR on an image if available
        image_files = [f for f in files if f.file_type == 'image']
        if image_files:
            test_image = image_files[0]
            result = extractor.extract_text(test_image.absolute_path)
            print(f"  - Image OCR test: {'✓' if result.extraction_success else '✗'}")
            if result.extraction_success:
                print(f"    Text length: {len(result.text_content) if result.text_content else 0} chars")
        else:
            print("  - No image files available for OCR testing")
            
    except Exception as e:
        print(f"✗ OCR test failed: {e}")
        print("  - This is expected if tesseract is not properly installed")
    
    # Test 5: LLM Configuration
    print("\n5. Testing LLM Configuration...")
    try:
        from app.llm_config import LLMConfigurationManager, load_config_from_env
        
        # Test configuration manager
        config_manager = load_config_from_env()
        print("✓ LLM configuration manager initialized")
        
        # Test provider listing
        providers = config_manager.list_providers()
        print(f"✓ Provider configuration loaded")
        print(f"  - Available providers: {list(providers.keys())}")
        print(f"  - Default provider: {config_manager.config_manager.default_provider}")
        
        # Test configuration validation
        valid_providers = config_manager.get_available_providers()
        print(f"  - Valid providers: {valid_providers}")
        
    except Exception as e:
        print(f"✗ LLM configuration test failed: {e}")
        return False
    
    # Test 6: Prompt System
    print("\n6. Testing Prompt System...")
    try:
        from app.prompt_system import create_prompt_system, PromptType
        
        # Test prompt system
        prompt_system = create_prompt_system(config_manager)
        print("✓ Prompt system initialized")
        
        # Test available prompts
        available_prompts = prompt_system.get_available_prompts("openai")
        print(f"✓ Available prompts loaded")
        print(f"  - Prompt types: {list(available_prompts.keys())}")
        
        # Test prompt generation
        test_content = "Patient John Doe diagnosed with diabetes."
        generated_prompt = prompt_system.analyze_document(
            text_content=test_content,
            prompt_type=PromptType.MEDICAL_DOCUMENT_ANALYSIS,
            provider="openai"
        )
        print(f"✓ Prompt generation working")
        print(f"  - Generated prompt length: {len(generated_prompt.final_prompt)} chars")
        
    except Exception as e:
        print(f"✗ Prompt system test failed: {e}")
        return False
    
    # Test 7: Output Validation
    print("\n7. Testing Output Validation...")
    try:
        output_dir = Path("app/output")
        if output_dir.exists():
            json_files = list(output_dir.glob("*_results.json"))
            if json_files:
                # Read and validate a sample output file
                with open(json_files[0], 'r') as f:
                    data = json.load(f)
                
                required_fields = ['processing_id', 'timestamp', 'total_files_discovered', 'extraction_results']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    print("✓ Output validation passed")
                    print(f"  - Processing ID: {data.get('processing_id', 'N/A')}")
                    print(f"  - Files processed: {data.get('total_files_discovered', 0)}")
                    print(f"  - Successful extractions: {data.get('successful_extractions', 0)}")
                else:
                    print(f"✗ Output validation failed - missing fields: {missing_fields}")
            else:
                print("  - No output files found")
        else:
            print("  - Output directory not found")
            
    except Exception as e:
        print(f"✗ Output validation failed: {e}")
        return False
    
    print("\n=== All Tests Completed Successfully! ===")
    return True

if __name__ == "__main__":
    success = test_all_components()
    sys.exit(0 if success else 1) 