#!/usr/bin/env python3
import os

def test_file_filtering():
    """Test the file filtering logic for relevant documents."""
    print("🧪 Testing File Filtering Logic")
    print("=" * 40)
    
    # Test directory path
    test_dir = "data/Dashrath Patel initial"
    
    if not os.path.exists(test_dir):
        print(f"❌ Test directory not found: {test_dir}")
        return
    
    # List all files in the directory
    print(f"📄 Files in directory: {test_dir}")
    files = os.listdir(test_dir)
    for file in files:
        print(f"  - {file}")
    
    print("\n🔍 Checking which files should be included:")
    
    # Test the filtering logic
    relevant_keywords = ['policy', 'onboarding', 'admission', 'cons', 'consultation', 'investigation']
    
    for file in files:
        file_lower = file.lower()
        should_include = any(keyword in file_lower for keyword in relevant_keywords)
        status = "✅ INCLUDED" if should_include else "❌ EXCLUDED"
        matching_keywords = [keyword for keyword in relevant_keywords if keyword in file_lower]
        print(f"  {file}: {status}")
        if matching_keywords:
            print(f"    Matching keywords: {matching_keywords}")
    
    # Count how many should be included
    included_files = [file for file in files if any(keyword in file.lower() for keyword in relevant_keywords)]
    print(f"\n📊 Summary:")
    print(f"  Total files: {len(files)}")
    print(f"  Files that should be included: {len(included_files)}")
    print(f"  Files that should be excluded: {len(files) - len(included_files)}")

if __name__ == "__main__":
    test_file_filtering() 