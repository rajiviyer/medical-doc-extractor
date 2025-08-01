import os
import pdfplumber
from utils import ocr_from_image, ocr_from_scanned_pdf
import logging
from pathlib import Path
from openai_extract import extract_fields_with_openai
from mistral_extract import extract_fields_with_mistral
from gemini_extract import extract_fields_with_gemini
import json
import sys
from prompts import get_openai_policy_prompt, get_mistral_policy_prompt, get_gemini_policy_prompt
from prompt_retrieve_text import get_openai_policy_prompt as get_openai_single_prompt, get_mistral_policy_prompt as get_mistral_single_prompt, get_gemini_policy_prompt as get_gemini_single_prompt
from validation import validate_extraction_result

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extract_single_file_with_metadata(file_path, base_dir=None):
    """Extract text and metadata from a single file."""
    if base_dir is None:
        base_dir = os.path.dirname(file_path)
    
    file_path = Path(file_path)
    if not file_path.exists():
        logger.error(f"File {file_path} does not exist.")
        return None
    
    rel_path = os.path.relpath(file_path, base_dir)
    file_type = 'pdf' if file_path.suffix.lower() == '.pdf' else 'image' if file_path.suffix.lower() in [".jpg", ".jpeg", ".png"] else 'other'
    
    entry = {
        'filename': str(rel_path),
        'type': file_type,
        'source': None,
        'extraction_success': False,
        'error': None,
        'text': None
    }
    
    if file_type == 'pdf':
        try:
            logger.info(f"Extracting text from {file_path}")
            with pdfplumber.open(file_path) as pdf:
                extracted = "\n".join([page.extract_text() or "" for page in pdf.pages])
                if extracted.strip():
                    entry['source'] = 'pdf_text'
                    entry['extraction_success'] = True
                    entry['text'] = extracted
                else:
                    logger.info(f"Text not found in {file_path}. Attempting OCR.")
                    ocr_text = ocr_from_scanned_pdf(str(file_path))
                    if ocr_text:
                        entry['source'] = 'ocr'
                        entry['extraction_success'] = True
                        entry['text'] = ocr_text
                        logger.info(f"OCR text: {ocr_text}")
                    else:
                        entry['source'] = 'ocr'
                        entry['error'] = 'OCR failed'
                        logger.error(f"OCR failed for {file_path}")
        except Exception as e:
            entry['source'] = 'pdf_text'
            entry['error'] = str(e)
            logger.error(f"Error extracting text from {file_path}: {e}")
    elif file_type == 'image':
        logger.info(f"Extracting text from {file_path}")
        try:
            ocr_text = ocr_from_image(str(file_path))
            if ocr_text:
                entry['source'] = 'image_ocr'
                entry['extraction_success'] = True
                entry['text'] = ocr_text
                logger.info(f"OCR text: {ocr_text}")
            else:
                entry['source'] = 'image_ocr'
                entry['error'] = 'OCR failed'
                logger.error(f"OCR failed for {file_path}")
        except Exception as e:
            entry['source'] = 'image_ocr'
            entry['error'] = str(e)
            logger.error(f"Error extracting text from {file_path}: {e}")
    else:
        entry['error'] = 'Unsupported file type'
    
    return entry

def extract_all_relevant_docs_with_metadata(folder_path, base_dir=None):
    """Extract text and metadata from all relevant documents including policy and onboarding forms."""
    if base_dir is None:
        base_dir = folder_path
    extracted_files = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in sorted(filenames):
            # Include policy documents and onboarding/admission forms
            relevant_keywords = ['policy', 'onboarding', 'admission', 'cons', 'consultation', 'investigation']
            if not any(keyword in file.lower() for keyword in relevant_keywords):
                continue
            path = os.path.join(dirpath, file)
            rel_path = os.path.relpath(path, base_dir)
            file_type = 'pdf' if file.lower().endswith('.pdf') else 'image' if file.lower().endswith((".jpg", ".jpeg", ".png")) else 'other'
            entry = {
                'filename': rel_path,
                'type': file_type,
                'source': None,
                'extraction_success': False,
                'error': None,
                'text': None
            }
            if file_type == 'pdf':
                try:
                    logger.info(f"Extracting text from {path}")
                    with pdfplumber.open(path) as pdf:
                        extracted = "\n".join([page.extract_text() or "" for page in pdf.pages])
                        if extracted.strip():
                            entry['source'] = 'pdf_text'
                            entry['extraction_success'] = True
                            entry['text'] = extracted
                        else:
                            logger.info(f"Text not found in {path}. Attempting OCR.")
                            ocr_text = ocr_from_scanned_pdf(path)
                            if ocr_text:
                                entry['source'] = 'ocr'
                                entry['extraction_success'] = True
                                entry['text'] = ocr_text
                                logger.info(f"OCR text: {ocr_text}")
                            else:
                                entry['source'] = 'ocr'
                                entry['error'] = 'OCR failed'
                                logger.error(f"OCR failed for {path}")
                except Exception as e:
                    entry['source'] = 'pdf_text'
                    entry['error'] = str(e)
                    logger.error(f"Error extracting text from {path}: {e}")
            elif file_type == 'image':
                logger.info(f"Extracting text from {path}")
                try:
                    ocr_text = ocr_from_image(path)
                    if ocr_text:
                        entry['source'] = 'image_ocr'
                        entry['extraction_success'] = True
                        entry['text'] = ocr_text
                        logger.info(f"OCR text: {ocr_text}")
                    else:
                        entry['source'] = 'image_ocr'
                        entry['error'] = 'OCR failed'
                        logger.error(f"OCR failed for {path}")
                except Exception as e:
                    entry['source'] = 'image_ocr'
                    entry['error'] = str(e)
                    logger.error(f"Error extracting text from {path}: {e}")
            else:
                entry['error'] = 'Unsupported file type'
            extracted_files.append(entry)
    return extracted_files

def extract_policy_docs_with_metadata(folder_path, base_dir=None):
    if base_dir is None:
        base_dir = folder_path
    extracted_files = []
    for dirpath, dirnames, filenames in os.walk(folder_path):
        for file in sorted(filenames):
            if 'policy' not in file.lower():
                continue
            path = os.path.join(dirpath, file)
            rel_path = os.path.relpath(path, base_dir)
            file_type = 'pdf' if file.lower().endswith('.pdf') else 'image' if file.lower().endswith((".jpg", ".jpeg", ".png")) else 'other'
            entry = {
                'filename': rel_path,
                'type': file_type,
                'source': None,
                'extraction_success': False,
                'error': None,
                'text': None
            }
            if file_type == 'pdf':
                try:
                    logger.info(f"Extracting text from {path}")
                    with pdfplumber.open(path) as pdf:
                        extracted = "\n".join([page.extract_text() or "" for page in pdf.pages])
                        if extracted.strip():
                            entry['source'] = 'pdf_text'
                            entry['extraction_success'] = True
                            entry['text'] = extracted
                        else:
                            logger.info(f"Text not found in {path}. Attempting OCR.")
                            ocr_text = ocr_from_scanned_pdf(path)
                            if ocr_text:
                                entry['source'] = 'ocr'
                                entry['extraction_success'] = True
                                entry['text'] = ocr_text
                                logger.info(f"OCR text: {ocr_text}")
                            else:
                                entry['source'] = 'ocr'
                                entry['error'] = 'OCR failed'
                                logger.error(f"OCR failed for {path}")
                except Exception as e:
                    entry['source'] = 'pdf_text'
                    entry['error'] = str(e)
                    logger.error(f"Error extracting text from {path}: {e}")
            elif file_type == 'image':
                logger.info(f"Extracting text from {path}")
                try:
                    ocr_text = ocr_from_image(path)
                    if ocr_text:
                        entry['source'] = 'image_ocr'
                        entry['extraction_success'] = True
                        entry['text'] = ocr_text
                        logger.info(f"OCR text: {ocr_text}")
                    else:
                        entry['source'] = 'image_ocr'
                        entry['error'] = 'OCR failed'
                        logger.error(f"OCR failed for {path}")
                except Exception as e:
                    entry['source'] = 'image_ocr'
                    entry['error'] = str(e)
                    logger.error(f"Error extracting text from {path}: {e}")
            else:
                entry['error'] = 'Unsupported file type'
            extracted_files.append(entry)
    return extracted_files

def build_policy_fields_prompt(metadata_list):
    fields = [
        "Room rent capping",
        "ICU capping",
        "Room category capping",
        "Medical practitioners capping",
        "Treatment related to participation as a non-professional in hazardous or adventure sports",
        "Other expenses capping",
        "Modern treatment capping",
        "Cataract capping",
        "Hernia capping",
        "Joint replacement capping",
        "Any kind of surgery specific capping",
        "Treatment-based capping - Dialysis",
        "Treatment-based capping - Chemotherapy",
        "Treatment-based capping - Radiotherapy",
        "Consumable & non-medical items capping",
        "Maternity capping",
        "Ambulance charge capping",
        "Daily cash benefit",
        "Co-payment",
        "OPD / Daycare / Domiciliary treatment capping",
        "Pre-post hospitalization expenses capping",
        "Diagnostic tests & investigation capping",
        "Implants / Stents / Prosthetics capping",
        "Mental illness treatment capping",
        "Organ donor expenses capping",
        "Bariatric / Obesity surgery capping",
        "Cancer treatment capping in specific plans",
        "Internal (congenital) disease capping",
        "AYUSH hospitalization capping (Ayurveda, Homeo)",
        "Vaccination / Preventive health check-up capping",
        "Artificial prostheses, aids capping"
    ]
    prompt = (
        "You are given a list of policy document text segments, each with metadata about its source file, extraction method, and success status. "
        "Extract ONLY the numbers or limits for the following fields from the policy documents. "
        "If a field is not found, return null or an empty string for that field. "
        "Fields to extract: " + ", ".join(fields) + ". "
        "Here is the list of policy document segments (as JSON):\n" + json.dumps(metadata_list, indent=2, ensure_ascii=False)
    )
    return prompt

def process_single_file_for_llm(file_path, output_root):
    """Process a single file for LLM extraction using prompt_retrieve_text.py."""
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    logger.info(f"Processing single file: {file_path}")
    metadata_entry = extract_single_file_with_metadata(file_path)
    if not metadata_entry:
        logger.error(f"Failed to extract metadata from {file_path}")
        return
    
    if not metadata_entry['extraction_success']:
        logger.error(f"Text extraction failed for {file_path}: {metadata_entry['error']}")
        return
    
    metadata_list = [metadata_entry]
    results = {"openai": {}, "mistral": {}, "gemini": {}}
    validation_results = {}
    
    metadata_json = json.dumps(metadata_list, indent=2, ensure_ascii=False)
    file_name = Path(file_path).stem
    
    for model, extractor, prompt_func in [
        ("openai", extract_fields_with_openai, get_openai_single_prompt),
        ("mistral", extract_fields_with_mistral, get_mistral_single_prompt),
        ("gemini", extract_fields_with_gemini, get_gemini_single_prompt),
    ]:
        try:
            logger.info(f"Extracting policy capping fields with {model} for {file_name}")
            prompt = prompt_func(metadata_json)
            result_json = extractor(prompt)
            try:
                if result_json and result_json.strip():
                    # Try to parse JSON if it's a string
                    if isinstance(result_json, str):
                        try:
                            result_data = json.loads(result_json)
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON from {model}: {e}")
                            logger.error(f"Raw response: {result_json[:200]}...")
                            continue
                    else:
                        result_data = result_json
                    
                    results[model][file_name] = result_data
                    
                    # Validate the extraction result
                    validation_report = validate_extraction_result(result_data)
                    validation_results[model] = validation_report
                    logger.info(f"{model.upper()} validation - Overall valid: {validation_report.overall_valid}, Confidence: {validation_report.overall_confidence:.2f}")
                else:
                    logger.warning(f"No result from {model}")
                    
            except Exception as e:
                logger.error(f"Failed to parse or validate {model} result: {e}")
                results[model][file_name] = result_json
        except Exception as e:
            logger.error(f"Failed {model} extraction for {file_name}: {e}")

    # Write results to their respective files with validation
    for model in ["openai", "mistral", "gemini"]:
        output_file = output_root / f"extracted_summary_{model}.json"
        try:
            # Convert validation report to dict for JSON serialization
            validation_dict = None
            if model in validation_results:
                validation_dict = validation_results[model].to_dict()
            
            output_data = {
                "extraction": results[model],
                "validation": validation_dict
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Wrote {model} results with validation to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write {model} output: {e}")

def process_policy_docs_for_llm(docs_root, output_root, patient_dir_name):
    docs_root = Path(docs_root)
    output_root = Path(output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    main_dir = docs_root / patient_dir_name
    if not main_dir.is_dir():
        logger.error(f"Directory {main_dir} does not exist.")
        return

    logger.info(f"Processing directory: {main_dir.name}")
    metadata_list = extract_policy_docs_with_metadata(str(main_dir), str(main_dir))
    results = {"openai": {}, "mistral": {}, "gemini": {}}
    validation_results = {}
    
    if metadata_list:
        metadata_json = json.dumps(metadata_list, indent=2, ensure_ascii=False)
        for model, extractor, prompt_func in [
            ("openai", extract_fields_with_openai, get_openai_policy_prompt),
            ("mistral", extract_fields_with_mistral, get_mistral_policy_prompt),
            ("gemini", extract_fields_with_gemini, get_gemini_policy_prompt),
        ]:
            try:
                logger.info(f"Extracting policy capping fields with {model} for {main_dir.name}")
                prompt = prompt_func(metadata_json)
                result_json = extractor(prompt)
                try:
                    if result_json and result_json.strip():
                        # Try to parse JSON if it's a string
                        if isinstance(result_json, str):
                            try:
                                result_data = json.loads(result_json)
                            except json.JSONDecodeError as e:
                                logger.error(f"Invalid JSON from {model}: {e}")
                                logger.error(f"Raw response: {result_json[:200]}...")
                                continue
                        else:
                            result_data = result_json
                        
                        results[model][main_dir.name] = result_data
                        
                        # Validate the extraction result
                        validation_report = validate_extraction_result(result_data)
                        validation_results[model] = validation_report
                        logger.info(f"{model.upper()} validation - Overall valid: {validation_report.overall_valid}, Confidence: {validation_report.overall_confidence:.2f}")
                    else:
                        logger.warning(f"No result from {model}")
                        
                except Exception as e:
                    logger.error(f"Failed to parse or validate {model} result: {e}")
                    results[model][main_dir.name] = result_json
            except Exception as e:
                logger.error(f"Failed {model} extraction for {main_dir.name}: {e}")
    else:
        logger.warning(f"No policy documents found for {main_dir.name}, skipping LLM extraction.")

    # Write results to their respective files with validation
    for model in ["openai", "mistral", "gemini"]:
        output_file = output_root / f"extracted_summary_{model}.json"
        try:
            output_data = {
                "extraction": results[model],
                "validation": validation_results.get(model, None)
            }
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Wrote {model} results with validation to {output_file}")
        except Exception as e:
            logger.error(f"Failed to write {model} output: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python loader.py <directory_name> or python loader.py --file <file_path>")
    elif len(sys.argv) == 3 and sys.argv[1] == "--file":
        process_single_file_for_llm(sys.argv[2], "app/output")
    else:
        process_policy_docs_for_llm("data", "app/output", sys.argv[1])
