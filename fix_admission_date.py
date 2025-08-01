#!/usr/bin/env python3
import re

def fix_admission_date():
    """Fix admission date extraction to use policy_start_date as fallback."""
    
    # Read the file
    with open('app/main.py', 'r') as f:
        content = f.read()
    
    # Replace both instances
    old_pattern = r"extracted_admission_date = result_data\.get\('date_of_admission', \"2024-01-15\"\)"
    new_pattern = r"extracted_admission_date = result_data.get('date_of_admission') or result_data.get('policy_start_date') or \"2024-01-15\""
    
    content = re.sub(old_pattern, new_pattern, content)
    
    # Write back the file
    with open('app/main.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed admission date extraction to use policy_start_date as fallback")

if __name__ == "__main__":
    fix_admission_date() 