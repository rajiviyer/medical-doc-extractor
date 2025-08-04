import sys
import os
import json
import logging
import re
from pathlib import Path
from loader import extract_single_file_with_metadata, extract_policy_docs_with_metadata, extract_all_relevant_docs_with_metadata
from prompts import get_openai_policy_prompt, get_mistral_policy_prompt, get_gemini_policy_prompt
from openai_extract import extract_fields_with_openai
from mistral_extract import extract_fields_with_mistral
from gemini_extract import extract_fields_with_gemini
from validation import validate_extraction_result
from policy_rules import validate_policy_rules
from accuracy_metrics import AccuracyTracker
from policy_classifier import classify_policy_document, PolicyType, DocumentCategory
from policy_report_generator import generate_policy_rule_report
from llm_config import get_enabled_llm_providers, is_llm_enabled, print_llm_configuration, validate_llm_configuration, LLMProvider

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def is_valid_result(result_json):
    """Safely check if a result is valid for processing."""
    if result_json is None:
        return False
    elif isinstance(result_json, dict):
        return True
    elif isinstance(result_json, str):
        return bool(result_json.strip())
    return False

def extract_admission_date_from_text(metadata_list):
    """Extract admission date from document text as fallback when LLM fails."""
    admission_patterns = [
        r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'Date of Admission\s+(\d{1,2}/\d{1,2}/\d{2})',
        r'Admission Date\s*:\s*(\d{1,2}/\d{1,2}/\d{4})',
        r'Admission Date\s*:\s*(\d{1,2}/\d{1,2}/\d{2})',
        r'Admitted on\s+(\d{1,2}/\d{1,2}/\d{4})',
        r'Admitted on\s+(\d{1,2}/\d{1,2}/\d{2})'
    ]
    
    for metadata in metadata_list:
        # Handle both object and dictionary metadata
        text = None
        if hasattr(metadata, 'text'):
            text = metadata.text
        elif isinstance(metadata, dict) and 'text' in metadata:
            text = metadata['text']
        
        if text:
            for pattern in admission_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    date_str = match.group(1)
                    # Convert 2-digit year to 4-digit year if needed
                    if len(date_str.split('/')[-1]) == 2:
                        year = int(date_str.split('/')[-1])
                        if year < 50:  # Assume 20xx for years < 50
                            year += 2000
                        else:
                            year += 1900
                        date_str = f"{date_str.split('/')[0]}/{date_str.split('/')[1]}/{year:04d}"
                    return date_str
    return None

def process_single_file(file_path):
    """Process a single file for policy extraction using configurable LLM selection."""
    logger.info("Starting single file policy capping extraction pipeline...")
    
    # Print LLM configuration
    print_llm_configuration()
    
    # Validate LLM configuration
    if not validate_llm_configuration():
        logger.error("LLM configuration validation failed. Please check your API keys.")
        return
    
    try:
        metadata_list = extract_all_relevant_docs_with_metadata(file_path, file_path)
        if not metadata_list:
            raise Exception("No relevant documents found in the specified file.")
        
        # Step 1: Classify the document
        logger.info("Classifying document...")
        classification_result = classify_policy_document(file_path, metadata_list[0])
        logger.info(f"  {os.path.basename(file_path)}: {classification_result.document_type.value} (confidence: {classification_result.confidence_score:.2f})")
        
        # Step 2: Extract policy information using LLMs
        logger.info("Policy documents loaded. Beginning extraction...")
        extraction_results = {}
        
        # Get enabled LLM providers
        enabled_providers = get_enabled_llm_providers()
        
        # Prepare metadata for LLM
        metadata_json = json.dumps([metadata.__dict__ for metadata in metadata_list], indent=2)
        
        # Extract with enabled LLMs
        if LLMProvider.OPENAI in enabled_providers:
            logger.info("Extracting with OpenAI...")
            extraction_results['openai'] = extract_fields_with_openai(get_openai_policy_prompt(metadata_json))
        
        if LLMProvider.MISTRAL in enabled_providers:
            logger.info("Extracting with Mistral...")
            extraction_results['mistral'] = extract_fields_with_mistral(get_mistral_policy_prompt(metadata_json))
        
        if LLMProvider.GEMINI in enabled_providers:
            logger.info("Extracting with Gemini...")
            extraction_results['gemini'] = extract_fields_with_gemini(get_gemini_policy_prompt(metadata_json))
        
        # Check if any LLMs are enabled
        if not extraction_results:
            raise Exception("No LLM providers are enabled. Please check your configuration.")
        
        logger.info(f"Extraction completed with {len(extraction_results)} LLM provider(s)")
        
        # Validate extraction results
        logger.info("Validating extraction results...")
        validation_results = {}
        
        for model, result_json in extraction_results.items():
            try:
                if is_valid_result(result_json):
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
                    
                    # Check if admission date was extracted, if not try fallback extraction
                    if not result_data.get('date_of_admission') or result_data.get('date_of_admission') == "null":
                        logger.info(f"Admission date not found in {model} extraction, trying fallback extraction...")
                        fallback_admission_date = extract_admission_date_from_text(metadata_list)
                        if fallback_admission_date:
                            result_data['date_of_admission'] = fallback_admission_date
                            logger.info(f"✅ Fallback admission date extracted: {fallback_admission_date}")
                        else:
                            logger.warning(f"No admission date found in any documents for {model}")
                    
                    validation_report = validate_extraction_result(result_data)
                    validation_results[model] = validation_report
                    logger.info(f"{model.upper()} validation - Overall valid: {validation_report.overall_valid}, Confidence: {validation_report.overall_confidence:.2f}")
                else:
                    logger.warning(f"No result from {model}")
            except Exception as e:
                logger.error(f"Validation failed for {model}: {e}")
        
        os.makedirs("output", exist_ok=True)
        
        # Save results to files with validation
        for model, result_json in extraction_results.items():
            # Convert validation report to dict for JSON serialization
            validation_dict = None
            if model in validation_results:
                validation_dict = validation_results[model].to_dict()
            
            output_data = {
                "extraction": result_json,
                "validation": validation_dict
            }
            
            with open(f"output/extracted_summary_{model}.json", "w") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Extracted fields and validation saved to output/extracted_summary_{model}.json")

        # Policy Rule Validation
        logger.info("Running policy rule validation...")
        policy_rule_results = {}
        
        for model, result_json in extraction_results.items():
            try:
                if is_valid_result(result_json):
                    # Parse the result data
                    result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
                    
                    # Create sample claim data for testing (in real scenario, this would come from claim documents)
                    # Use extracted admission date if available, otherwise leave as null
                    extracted_admission_date = result_data.get('date_of_admission')
                    if extracted_admission_date == "null" or not extracted_admission_date:
                        extracted_admission_date = None  # Don't hardcode, leave as null
                    sample_claim_data = {
                        "admission_date": extracted_admission_date,
                        "claim_amount": 50000,
                        "condition": "cardiac",
                        "hospital_bill": {
                            "room_rent": 5000,
                            "icu_charges": 15000,
                            "procedure": "cardiac surgery",
                            "procedure_cost": 30000,
                            "itemized_bill": {
                                "toiletries": 500,
                                "food": 1000
                            }
                        },
                        "discharge_summary": {
                            "procedure": "cardiac surgery",
                            "is_daycare": False
                        }
                    }
                    
                    rule_report = validate_policy_rules(result_data, sample_claim_data)
                    policy_rule_results[model] = rule_report
                    
                    logger.info(f"{model.upper()} Rule Validation - Overall valid: {rule_report.overall_valid}, Risk Level: {rule_report.risk_level}, Total Deductions: {rule_report.total_deductions}")
                else:
                    logger.warning(f"No result data available for {model} rule validation")
            except Exception as e:
                logger.error(f"Policy rule validation failed for {model}: {e}")
        
        # Print validation summary
        print("\n📊 Validation Summary:")
        for model, report in validation_results.items():
            print(f"  {model.upper()}: Valid={report.overall_valid}, Confidence={report.overall_confidence:.2f}")
            if report.recommendations:
                print(f"    Recommendations: {', '.join(report.recommendations[:3])}")
        
        # Print policy rule summary
        print("\n📋 Policy Rule Summary:")
        for model, rule_report in policy_rule_results.items():
            print(f"  {model.upper()}: Valid={rule_report.overall_valid}, Risk={rule_report.risk_level}, Deductions={rule_report.total_deductions}")
            if rule_report.recommendations:
                print(f"    Rule Recommendations: {', '.join(rule_report.recommendations[:3])}")
        
        # Generate detailed policy rule reports
        print("\n📊 Generating Policy Rule Reports...")
        for model, rule_report in policy_rule_results.items():
            try:
                # Generate markdown report
                report_content = generate_policy_rule_report(rule_report, format_type="markdown")
                report_file = f"output/policy_rule_report_{model}_{file_path}.md"
                os.makedirs("output", exist_ok=True)
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"✅ Policy rule report saved to {report_file}")
                
                # Generate text report
                text_report_content = generate_policy_rule_report(rule_report, format_type="text")
                text_report_file = f"output/policy_rule_report_{model}_{file_path}.txt"
                with open(text_report_file, 'w', encoding='utf-8') as f:
                    f.write(text_report_content)
                print(f"✅ Text policy rule report saved to {text_report_file}")
                
                # Also save as HTML for better viewing
                html_report_file = f"output/policy_rule_report_{model}_{file_path}.html"
                generate_policy_rule_report(rule_report, html_report_file, format_type="html")
                print(f"✅ HTML policy rule report saved to {html_report_file}")
                
            except Exception as e:
                logger.error(f"Failed to generate policy rule report for {model}: {e}")

        # Accuracy Tracking
        logger.info("Running accuracy analysis...")
        try:
            # Load ground truth data if available
            ground_truth_file = "data/ground_truth_sample.json"
            if os.path.exists(ground_truth_file):
                tracker = AccuracyTracker()
                ground_truth_data = tracker.load_ground_truth(ground_truth_file)
                
                if ground_truth_data:
                    # Prepare model results for accuracy analysis
                    model_results = {}
                    for model, result_json in extraction_results.items():
                        if is_valid_result(result_json):
                            if isinstance(result_json, str):
                                result_data = json.loads(result_json)
                            else:
                                result_data = result_json
                            model_results[model] = {
                                **result_data,
                                "processing_time": 30.0  # Estimated processing time
                            }
                    
                    # Generate accuracy report
                    accuracy_report = tracker.compare_models(
                        model_results, 
                        ground_truth_data.get("ground_truth_values", {}),
                        f"policy_extraction_{file_path}"
                    )
                    
                    # Save accuracy report
                    os.makedirs("output", exist_ok=True)
                    tracker.save_accuracy_report(accuracy_report, f"output/accuracy_report_{file_path}.json")
                    
                    # Print accuracy summary
                    print("\n📊 Accuracy Analysis:")
                    print(f"  Best Model: {accuracy_report.overall_best_model} ({accuracy_report.overall_accuracy:.1f}% accuracy)")
                    for model_name, model_accuracy in accuracy_report.model_comparison.items():
                        print(f"  {model_name.upper()}: {model_accuracy.accuracy_percentage:.1f}% accuracy, {model_accuracy.average_confidence:.2f} confidence")
                    
                    if accuracy_report.recommendations:
                        print(f"  Recommendations: {', '.join(accuracy_report.recommendations[:3])}")
                    
                    logger.info(f"Accuracy report saved to output/accuracy_report_{file_path}.json")
                else:
                    logger.warning("No ground truth data available for accuracy analysis")
            else:
                logger.info("Ground truth file not found, skipping accuracy analysis")
        except Exception as e:
            logger.error(f"Accuracy analysis failed: {e}")

        # Print classification summary
        print("\n📋 Document Classification Summary:")
        print(f"  Document Type: {classification_result.document_type.value}")
        print(f"  Category: {classification_result.category.value}")
        print(f"  Confidence: {classification_result.confidence_score:.2f}")
        if classification_result.policy_number:
            print(f"  Policy Number: {classification_result.policy_number}")
        if classification_result.policy_version:
            print(f"  Policy Version: {classification_result.policy_version}")
        
        if classification_result.recommendations:
            print(f"  Recommendations: {', '.join(classification_result.recommendations[:2])}")

        # Print results
        print("\n✅ Extraction complete!")
        for model, result in extraction_results.items():
            print(f"{model.upper()} Results:", result)

    except Exception as e:
        logger.error(f"Error in single file policy capping extraction pipeline: {e}")

def process_directory(patient_dir):
    """Process a directory for policy extraction using configurable LLM selection."""
    logger.info("Starting directory policy capping extraction pipeline...")
    
    # Print LLM configuration
    print_llm_configuration()
    
    # Validate LLM configuration
    if not validate_llm_configuration():
        logger.error("LLM configuration validation failed. Please check your API keys.")
        return
    
    try:
        metadata_list = extract_all_relevant_docs_with_metadata(patient_dir, patient_dir)
        if not metadata_list:
            raise Exception("No policy documents found in the specified directory.")
        
        # Step 1: Classify all documents in the directory
        logger.info("Classifying documents in directory...")
        classification_results = []
        
        for metadata_entry in metadata_list:
            if metadata_entry.get('extraction_success'):
                classification_result = classify_policy_document(
                    filename=metadata_entry.get('filename', ''),
                    content=metadata_entry.get('text', ''),
                    metadata=metadata_entry
                )
                classification_results.append(classification_result)
                
                logger.info(f"  {metadata_entry.get('filename', '')}: {classification_result.document_type.value} (confidence: {classification_result.confidence_score:.2f})")
        
        # Step 2: Determine primary document type for the directory
        if classification_results:
            # Count document types
            type_counts = {}
            for result in classification_results:
                doc_type = result.document_type.value
                type_counts[doc_type] = type_counts.get(doc_type, 0) + 1
            
            # Find most common type
            primary_type = max(type_counts.keys(), key=lambda k: type_counts[k])
            logger.info(f"Primary document type for directory: {primary_type}")
            
            # Route to appropriate processor
            if primary_type in ['health_insurance', 'master_policy']:
                logger.info("Using health insurance extraction pipeline")
            elif primary_type == 'life_insurance':
                logger.info("Using life insurance extraction pipeline")
            elif primary_type in ['claim_document', 'hospital_bill']:
                logger.info("Using claim processing pipeline")
            elif primary_type == 'medical_report':
                logger.info("Using medical document processing pipeline")
            else:
                logger.info("Using general processing pipeline")
        
        metadata_json = json.dumps(metadata_list, indent=2, ensure_ascii=False)
        logger.info("Policy documents loaded. Beginning extraction...")
        
        # Extract fields using enabled LLMs only
        extraction_results = {}
        
        if is_llm_enabled('openai'):
            logger.info("Extracting with OpenAI...")
            extraction_results['openai'] = extract_fields_with_openai(get_openai_policy_prompt(metadata_json))
        
        if is_llm_enabled('mistral'):
            logger.info("Extracting with Mistral...")
            extraction_results['mistral'] = extract_fields_with_mistral(get_mistral_policy_prompt(metadata_json))
        
        if is_llm_enabled('gemini'):
            logger.info("Extracting with Gemini...")
            extraction_results['gemini'] = extract_fields_with_gemini(get_gemini_policy_prompt(metadata_json))
        
        # Check if any LLMs are enabled
        if not extraction_results:
            raise Exception("No LLM providers are enabled. Please check your configuration.")
        
        logger.info(f"Extraction completed with {len(extraction_results)} LLM provider(s)")
        
        # Validate extraction results
        logger.info("Validating extraction results...")
        validation_results = {}
        
        for model, result_json in extraction_results.items():
            try:
                if is_valid_result(result_json):
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
                    
                    # Check if admission date was extracted, if not try fallback extraction
                    if not result_data.get('date_of_admission') or result_data.get('date_of_admission') == "null":
                        logger.info(f"Admission date not found in {model} extraction, trying fallback extraction...")
                        fallback_admission_date = extract_admission_date_from_text(metadata_list)
                        if fallback_admission_date:
                            result_data['date_of_admission'] = fallback_admission_date
                            logger.info(f"✅ Fallback admission date extracted: {fallback_admission_date}")
                        else:
                            logger.warning(f"No admission date found in any documents for {model}")
                    
                    validation_report = validate_extraction_result(result_data)
                    validation_results[model] = validation_report
                    logger.info(f"{model.upper()} validation - Overall valid: {validation_report.overall_valid}, Confidence: {validation_report.overall_confidence:.2f}")
                else:
                    logger.warning(f"No result from {model}")
            except Exception as e:
                logger.error(f"Validation failed for {model}: {e}")
        
        os.makedirs("output", exist_ok=True)
        
        # Save results to files with validation
        for model, result_json in extraction_results.items():
            # Convert validation report to dict for JSON serialization
            validation_dict = None
            if model in validation_results:
                validation_dict = validation_results[model].to_dict()
            
            # Parse the extraction result to store as proper JSON object
            if isinstance(result_json, str):
                try:
                    extraction_data = json.loads(result_json)
                    logger.info(f"Successfully parsed {model} response as JSON")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse {model} response as JSON: {e}")
                    logger.error(f"Raw response: {result_json[:200]}...")
                    # Try to clean up the response and parse again
                    cleaned_response = result_json.strip()
                    if cleaned_response.startswith("```json"):
                        json_start = cleaned_response.find("```json") + 7
                        json_end = cleaned_response.rfind("```")
                        if json_end > json_start:
                            cleaned_response = cleaned_response[json_start:json_end].strip()
                    elif cleaned_response.startswith("```"):
                        json_start = cleaned_response.find("```") + 3
                        json_end = cleaned_response.rfind("```")
                        if json_end > json_start:
                            cleaned_response = cleaned_response[json_start:json_end].strip()
                    
                    try:
                        extraction_data = json.loads(cleaned_response)
                        logger.info(f"Successfully parsed {model} response after cleanup")
                    except json.JSONDecodeError:
                        extraction_data = result_json  # Keep as string if parsing fails
            else:
                extraction_data = result_json
                logger.info(f"{model} response is already a parsed object")
            
            output_data = {
                "extraction": extraction_data,
                "validation": validation_dict
            }
            
            with open(f"output/extracted_summary_{model}.json", "w") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Extracted fields and validation saved to output/extracted_summary_{model}.json")

        # Policy Rule Validation
        logger.info("Running policy rule validation...")
        policy_rule_results = {}
        
        for model, result_json in extraction_results.items():
            try:
                if is_valid_result(result_json):
                    # Parse the result data
                    result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
                    
                    # Create sample claim data for testing (in real scenario, this would come from claim documents)
                    # Use extracted admission date if available, otherwise leave as null
                    extracted_admission_date = result_data.get('date_of_admission')
                    if extracted_admission_date == "null" or not extracted_admission_date:
                        # For testing purposes, use a sample date to validate all rules
                        # In production, this would be None when no date is available
                        # To test with complete validation: extracted_admission_date = "15/06/2024"
                        # To test with partial validation: extracted_admission_date = None
                        extracted_admission_date = "15/06/2024"  # Sample date for complete rule validation
                    sample_claim_data = {
                        "admission_date": extracted_admission_date,
                        "claim_amount": 50000,
                        "condition": "cardiac",
                        "hospital_bill": {
                            "room_rent": 5000,
                            "icu_charges": 15000,
                            "procedure": "cardiac surgery",
                            "procedure_cost": 30000,
                            "itemized_bill": {
                                "toiletries": 500,
                                "food": 1000
                            }
                        },
                        "discharge_summary": {
                            "procedure": "cardiac surgery",
                            "is_daycare": False
                        }
                    }
                    
                    rule_report = validate_policy_rules(result_data, sample_claim_data)
                    policy_rule_results[model] = rule_report
                    
                    logger.info(f"{model.upper()} Rule Validation - Overall valid: {rule_report.overall_valid}, Risk Level: {rule_report.risk_level}, Total Deductions: {rule_report.total_deductions}")
                else:
                    logger.warning(f"No result data available for {model} rule validation")
            except Exception as e:
                logger.error(f"Policy rule validation failed for {model}: {e}")
        
        # Print validation summary
        print("\n📊 Validation Summary:")
        for model, report in validation_results.items():
            print(f"  {model.upper()}: Valid={report.overall_valid}, Confidence={report.overall_confidence:.2f}")
            if report.recommendations:
                print(f"    Recommendations: {', '.join(report.recommendations[:3])}")
        
        # Print policy rule summary
        print("\n📋 Policy Rule Summary:")
        for model, rule_report in policy_rule_results.items():
            print(f"  {model.upper()}: Valid={rule_report.overall_valid}, Risk={rule_report.risk_level}, Deductions={rule_report.total_deductions}")
            if rule_report.recommendations:
                print(f"    Rule Recommendations: {', '.join(rule_report.recommendations[:3])}")
        
        # Generate detailed policy rule reports
        print("\n📊 Generating Policy Rule Reports...")
        for model, rule_report in policy_rule_results.items():
            try:
                # Get directory name for accuracy report
                main_dir = Path(patient_dir)
                
                # Generate markdown report
                report_content = generate_policy_rule_report(rule_report, format_type="markdown")
                report_file = f"output/policy_rule_report_{model}_{main_dir.name}.md"
                os.makedirs("output", exist_ok=True)
                with open(report_file, 'w', encoding='utf-8') as f:
                    f.write(report_content)
                print(f"✅ Policy rule report saved to {report_file}")
                
                # Generate text report
                text_report_content = generate_policy_rule_report(rule_report, format_type="text")
                text_report_file = f"output/policy_rule_report_{model}_{main_dir.name}.txt"
                with open(text_report_file, 'w', encoding='utf-8') as f:
                    f.write(text_report_content)
                print(f"✅ Text policy rule report saved to {text_report_file}")
                
                # Also save as HTML for better viewing
                html_report_file = f"output/policy_rule_report_{model}_{main_dir.name}.html"
                generate_policy_rule_report(rule_report, html_report_file, format_type="html")
                print(f"✅ HTML policy rule report saved to {html_report_file}")
                
            except Exception as e:
                logger.error(f"Failed to generate policy rule report for {model}: {e}")

        # Accuracy Tracking
        logger.info("Running accuracy analysis...")
        try:
            # Load ground truth data if available
            ground_truth_file = "data/ground_truth_sample.json"
            if os.path.exists(ground_truth_file):
                tracker = AccuracyTracker()
                ground_truth_data = tracker.load_ground_truth(ground_truth_file)
                
                if ground_truth_data:
                    # Prepare model results for accuracy analysis
                    model_results = {}
                    for model, result_json in extraction_results.items():
                        if is_valid_result(result_json):
                            result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
                            model_results[model] = {
                                **result_data,
                                "processing_time": 30.0  # Estimated processing time
                            }
                    
                    # Get directory name for accuracy report
                    main_dir = Path(patient_dir)
                    
                    # Generate accuracy report
                    accuracy_report = tracker.compare_models(
                        model_results, 
                        ground_truth_data.get("ground_truth_values", {}),
                        f"policy_extraction_{main_dir.name}"
                    )
                    
                    # Save accuracy report
                    os.makedirs("output", exist_ok=True)
                    tracker.save_accuracy_report(accuracy_report, f"output/accuracy_report_{main_dir.name}.json")
                    
                    # Print accuracy summary
                    print("\n📊 Accuracy Analysis:")
                    print(f"  Best Model: {accuracy_report.overall_best_model} ({accuracy_report.overall_accuracy:.1f}% accuracy)")
                    for model_name, model_accuracy in accuracy_report.model_comparison.items():
                        print(f"  {model_name.upper()}: {model_accuracy.accuracy_percentage:.1f}% accuracy, {model_accuracy.average_confidence:.2f} confidence")
                    
                    if accuracy_report.recommendations:
                        print(f"  Recommendations: {', '.join(accuracy_report.recommendations[:3])}")
                    
                    logger.info(f"Accuracy report saved to output/accuracy_report_{main_dir.name}.json")
                else:
                    logger.warning("No ground truth data available for accuracy analysis")
            else:
                logger.info("Ground truth file not found, skipping accuracy analysis")
        except Exception as e:
            logger.error(f"Accuracy analysis failed: {e}")

        # Print results
        print("\n✅ Extraction complete!")
        for model, result in extraction_results.items():
            print(f"{model.upper()} Results:", result)

    except Exception as e:
        logger.error(f"Error in directory policy capping extraction pipeline: {e}")

def find_first_policy_file():
    """Find the first available policy file in the data directory."""
    for root, dirs, files in os.walk("data"):
        for file in files:
            if 'policy' in file.lower() and file.endswith('.pdf'):
                return os.path.join(root, file)
    return None

if __name__ == "__main__":
    # Default file for Docker environment
    default_file = "./data/Master Policies/master policy-care classic mediclaim policy.pdf"
    
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
                print("Usage: python main.py --file <file_path>")
                print("       python main.py --dir <directory_path>")
                print("       python main.py <directory_path> # legacy mode")
                sys.exit(1)
    
    elif len(sys.argv) == 2:
        # Single argument - treat as directory path (legacy mode)
        directory_path = sys.argv[1]
        if os.path.isdir(directory_path):
            process_directory(directory_path)
        else:
            logger.error(f"Directory not found: {directory_path}")
            sys.exit(1)
    
    elif len(sys.argv) == 3:
        # Two arguments - check for --file or --dir flag
        if sys.argv[1] == "--file":
            file_path = sys.argv[2]
            if os.path.isfile(file_path):
                process_single_file(file_path)
            else:
                logger.error(f"File not found: {file_path}")
                sys.exit(1)
        elif sys.argv[1] == "--dir":
            directory_path = sys.argv[2]
            if os.path.isdir(directory_path):
                process_directory(directory_path)
            else:
                logger.error(f"Directory not found: {directory_path}")
                sys.exit(1)
        else:
            logger.error("Invalid arguments")
            print("Usage: python main.py --file <file_path>")
            print("       python main.py --dir <directory_path>")
            sys.exit(1)
    
    else:
        logger.error("Invalid number of arguments")
        print("Usage: python main.py --file <file_path>")
        print("       python main.py --dir <directory_path>")
        print("       python main.py <directory_path> # legacy mode")
        sys.exit(1) 