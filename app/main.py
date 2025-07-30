import os
import logging
import sys
from dotenv import load_dotenv
from loader import extract_policy_docs_with_metadata, extract_single_file_with_metadata, process_single_file_for_llm
from openai_extract import extract_fields_with_openai
from mistral_extract import extract_fields_with_mistral
from gemini_extract import extract_fields_with_gemini
from prompts import get_openai_policy_prompt, get_mistral_policy_prompt, get_gemini_policy_prompt
from prompt_retrieve_text import get_openai_policy_prompt as get_openai_single_prompt, get_mistral_policy_prompt as get_mistral_single_prompt, get_gemini_policy_prompt as get_gemini_single_prompt
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def process_single_file(file_path):
    """Process a single file for policy extraction using prompt_retrieve_text.py."""
    logger.info("Starting single file policy capping extraction pipeline...")
    
    try:
        metadata_entry = extract_single_file_with_metadata(file_path)
        if not metadata_entry:
            raise Exception("Failed to extract metadata from the file.")
        
        if not metadata_entry['extraction_success']:
            raise Exception(f"Text extraction failed: {metadata_entry['error']}")
        
        metadata_list = [metadata_entry]
        metadata_json = json.dumps(metadata_list, indent=2, ensure_ascii=False)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        logger.info("File loaded. Beginning extraction...")
        result_json_openai = extract_fields_with_openai(get_openai_single_prompt(metadata_json))
        result_json_mistral = extract_fields_with_mistral(get_mistral_single_prompt(metadata_json))
        result_json_gemini = extract_fields_with_gemini(get_gemini_single_prompt(metadata_json))
        
        os.makedirs("output", exist_ok=True)
        
        # Save results to files
        with open("output/extracted_summary_openai.json", "w") as f:
            f.write(result_json_openai)
        print("✅ Extracted fields saved to output/extracted_summary_openai.json")

        with open("output/extracted_summary_mistral.json", "w") as f:
            f.write(result_json_mistral)
        print("✅ Extracted fields saved to output/extracted_summary_mistral.json")

        with open("output/extracted_summary_gemini.json", "w") as f:
            f.write(result_json_gemini)
        print("✅ Extracted fields saved to output/extracted_summary_gemini.json")

        # Print results
        print("✅ Extraction complete!")
        print("OpenAI Results:", result_json_openai)
        print("Mistral Results:", result_json_mistral)
        print("Gemini Results:", result_json_gemini)

    except Exception as e:
        logger.error(f"Error in single file policy capping extraction pipeline: {e}")

def process_directory(patient_dir):
    """Process a directory for policy extraction using prompts.py."""
    logger.info("Starting directory policy capping extraction pipeline...")
    
    try:
        metadata_list = extract_policy_docs_with_metadata(patient_dir, patient_dir)
        if not metadata_list:
            raise Exception("No policy documents found in the specified directory.")
        
        metadata_json = json.dumps(metadata_list, indent=2, ensure_ascii=False)
        logger.info("Policy documents loaded. Beginning extraction...")
        
        result_json_openai = extract_fields_with_openai(get_openai_policy_prompt(metadata_json))
        result_json_mistral = extract_fields_with_mistral(get_mistral_policy_prompt(metadata_json))
        result_json_gemini = extract_fields_with_gemini(get_gemini_policy_prompt(metadata_json))
        
        os.makedirs("output", exist_ok=True)
        
        # Save results to files
        with open("output/extracted_summary_openai.json", "w") as f:
            f.write(result_json_openai)
        print("✅ Extracted fields saved to output/extracted_summary_openai.json")

        with open("output/extracted_summary_mistral.json", "w") as f:
            f.write(result_json_mistral)
        print("✅ Extracted fields saved to output/extracted_summary_mistral.json")

        with open("output/extracted_summary_gemini.json", "w") as f:
            f.write(result_json_gemini)
        print("✅ Extracted fields saved to output/extracted_summary_gemini.json")

        # Print results
        print("✅ Extraction complete!")
        print("OpenAI Results:", result_json_openai)
        print("Mistral Results:", result_json_mistral)
        print("Gemini Results:", result_json_gemini)

    except Exception as e:
        logger.error(f"Error in directory policy capping extraction pipeline: {e}")

def find_first_policy_file():
    """Find the first available policy file in the docs directory."""
    for root, dirs, files in os.walk("docs"):
        for file in files:
            if 'policy' in file.lower() and file.endswith('.pdf'):
                return os.path.join(root, file)
    return None

if __name__ == "__main__":
    # Default file for Docker environment
    # default_file = "../docs/Master Policies/master policy-care classic mediclaim policy.pdf"
    # default_file = "../docs/Master Policies/Master policy-care-supreme---policy-terms-&-conditions-(effective-from-19-march-2025).pdf"
    # default_file = "../docs/Master Policies/Master policy-Family medicare policy.pdf"
    # default_file = "../docs/Master Policies/master policy-kotak-health-premier-policy-wording-1.pdf"
    # default_file = "../docs/Master Policies/Master policy-national young india mediclaim policy.pdf"
    # default_file = "../docs/Master Policies/Master policy-New India Floater Mediclaim Policy.pdf"
    #default_file = "../docs/Master Policies/Master Policy-ReAssure_Policy_Document.pdf"
    default_file = "../docs/Master Policies/medicare-policy-wordings.pdf"
    
    if len(sys.argv) == 1:
        # No arguments provided - use default single file processing for Docker
        logger.info("No arguments provided. Using default single file processing for Docker environment.")
        
        # Try the default file first
        if os.path.exists(default_file):
            process_single_file(default_file)
        else:
            # Try to find any available policy file
            logger.info("Default file not found. Searching for available policy files...")
            found_file = find_first_policy_file()
            
            if found_file:
                logger.info(f"Found policy file: {found_file}")
                process_single_file(found_file)
            else:
                logger.error("No policy files found. Please provide a file path.")
                # Try to find available policy files
                logger.info("Searching for available policy files...")
                available_files = []
                for root, dirs, files in os.walk("docs"):
                    for file in files:
                        if 'policy' in file.lower() and file.endswith('.pdf'):
                            rel_path = os.path.relpath(os.path.join(root, file), ".")
                            available_files.append(rel_path)
                
                if available_files:
                    logger.info("Available policy files found:")
                    for file in available_files[:5]:  # Show first 5 files
                        logger.info(f"  - {file}")
                    if len(available_files) > 5:
                        logger.info(f"  ... and {len(available_files) - 5} more files")
                else:
                    logger.info("No policy files found in docs directory.")
                
                print("Usage:")
                print("  python main.py --file <file_path>")
                print("  python main.py --dir <directory_path>")
                print("  python main.py <directory_path>  # legacy mode")
    elif len(sys.argv) == 3 and sys.argv[1] == "--file":
        process_single_file(sys.argv[2])
    elif len(sys.argv) == 3 and sys.argv[1] == "--dir":
        process_directory(sys.argv[2])
    elif len(sys.argv) == 2:
        # Legacy mode - treat as directory
        process_directory(sys.argv[1])
    else:
        print("Invalid arguments. Usage:")
        print("  python main.py --file <file_path>")
        print("  python main.py --dir <directory_path>")
        print("  python main.py <directory_path>  # legacy mode")
    