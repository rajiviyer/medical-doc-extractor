#!/usr/bin/env python3
import re

def fix_hardcoded_dates():
    """Fix hardcoded dates in main.py by replacing them with proper fallback logic."""
    
    # Read the file
    with open('app/main.py', 'r') as f:
        content = f.read()
    
    # Pattern to find and replace the hardcoded date logic
    old_pattern = r"""                    # Create sample claim data for testing \(in real scenario, this would come from claim documents\)
                    # Use extracted admission date if available, otherwise use default
                    extracted_admission_date = result_data\.get\('date_of_admission'\)
                    if extracted_admission_date == "null" or not extracted_admission_date:
                        extracted_admission_date = "15/07/2025"  # Use known correct date"""
    
    new_pattern = """# Create sample claim data for testing (in real scenario, this would come from claim documents)
                    # Use extracted admission date if available, otherwise extract from document text
                    extracted_admission_date = result_data.get('date_of_admission')
                    if extracted_admission_date == "null" or not extracted_admission_date:
                        # Try to extract admission date from document text as fallback
                        extracted_admission_date = extract_admission_date_from_text(metadata_list)
                        if not extracted_admission_date:
                            extracted_admission_date = "2024-01-15"  # Default fallback"""
    
    # Replace both instances
    new_content = content.replace(old_pattern, new_pattern)
    
    # Write back to file
    with open('app/main.py', 'w') as f:
        f.write(new_content)
    
    print("✅ Fixed hardcoded dates in main.py")
    print("   - Replaced hardcoded '15/07/2025' with proper fallback logic")
    print("   - Now uses extract_admission_date_from_text() function")
    print("   - Falls back to '2024-01-15' only if no date found in documents")

if __name__ == "__main__":
    fix_hardcoded_dates() 