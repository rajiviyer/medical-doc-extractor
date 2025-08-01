#!/usr/bin/env python3
"""
Test script for the modular directory scanner.
"""

import logging
from app.directory_scanner import DirectoryScanner, create_policy_document_scanner

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_directory_scanner():
    """Test the directory scanner functionality."""
    
    print("=== Testing Directory Scanner ===\n")
    
    # Test 1: Basic scanner initialization
    print("1. Testing basic scanner initialization...")
    try:
        scanner = DirectoryScanner(base_directory="data")
        print("✓ Scanner initialized successfully")
    except Exception as e:
        print(f"✗ Scanner initialization failed: {e}")
        return
    
    # Test 2: List available directories
    print("\n2. Testing directory listing...")
    try:
        directories = scanner.list_available_directories()
        print(f"✓ Found {len(directories)} directories:")
        for dir_name in directories:
            print(f"  - {dir_name}")
    except Exception as e:
        print(f"✗ Directory listing failed: {e}")
    
    # Test 3: Get directory structure
    print("\n3. Testing directory structure...")
    try:
        structure = scanner.get_directory_structure(max_depth=2)
        print("✓ Directory structure retrieved")
        print(f"  Structure keys: {list(structure.keys())}")
    except Exception as e:
        print(f"✗ Directory structure failed: {e}")
    
    # Test 4: Scan specific directory
    print("\n4. Testing specific directory scan...")
    try:
        # Try to scan the first available directory
        if directories:
            target_dir = directories[0]
            print(f"  Scanning directory: {target_dir}")
            files = scanner.scan_by_directory_name(target_dir, recursive=True)
            print(f"✓ Found {len(files)} files in {target_dir}")
            
            # Show file details
            for file_info in files[:3]:  # Show first 3 files
                print(f"  - {file_info.filename} ({file_info.file_type}, {file_info.file_size} bytes)")
            if len(files) > 3:
                print(f"  ... and {len(files) - 3} more files")
        else:
            print("  No directories available for testing")
    except Exception as e:
        print(f"✗ Directory scan failed: {e}")
    
    # Test 5: Policy document scanner
    print("\n5. Testing policy document scanner...")
    try:
        policy_scanner = create_policy_document_scanner("data")
        policy_files = policy_scanner.scan_directory()
        print(f"✓ Policy scanner found {len(policy_files)} files")
    except Exception as e:
        print(f"✗ Policy scanner failed: {e}")
    
    # Test 6: File filtering
    print("\n6. Testing file filtering...")
    try:
        from app.directory_scanner import filter_by_filename_pattern
        pdf_filter = filter_by_filename_pattern("policy")
        filtered_files = scanner.scan_directory(file_filter=pdf_filter)
        print(f"✓ Filtered scan found {len(filtered_files)} files with 'policy' in name")
    except Exception as e:
        print(f"✗ File filtering failed: {e}")
    
    print("\n=== Directory Scanner Test Complete ===")

if __name__ == "__main__":
    test_directory_scanner() 