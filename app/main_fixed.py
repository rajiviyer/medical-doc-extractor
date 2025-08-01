import sys
import os
import json
import logging
from pathlib import Path
from loader import extract_single_file_with_metadata, extract_policy_docs_with_metadata
from prompts import get_openai_policy_prompt, get_mistral_policy_prompt, get_gemini_policy_prompt
from openai_extract import extract_fields_with_openai
from mistral_extract import extract_fields_with_mistral
from gemini_extract import extract_fields_with_gemini
from validation import validate_extraction_result
from policy_rules import validate_policy_rules
from accuracy_metrics import AccuracyTracker
from policy_classifier import classify_policy_document, PolicyType, DocumentCategory

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_single_file(file_path):
    """Process a single file for policy extraction using prompt_retrieve_text.py."""
    logger.info("Starting single file policy capping extraction pipeline...")
    
    try:
        # Step 1: Extract metadata from file
        metadata_entry = extract_single_file_with_metadata(file_path)
        if not metadata_entry:
            raise Exception("Failed to extract metadata from the file.")
        
        if not metadata_entry['extraction_success']:
            raise Exception(f"Text extraction failed: {metadata_entry['error']}")
        
        # Step 2: Classify the document
        logger.info("Classifying document...")
        classification_result = classify_policy_document(
            filename=os.path.basename(file_path),
            content=metadata_entry.get('text', ''),
            metadata=metadata_entry
        )
        
        logger.info(f"Document classified as: {classification_result.document_type.value}")
        logger.info(f"Confidence: {classification_result.confidence_score:.2f}")
        logger.info(f"Category: {classification_result.category.value}")
        
        # Step 3: Route to appropriate processor based on classification
        if classification_result.document_type in [PolicyType.HEALTH_INSURANCE, PolicyType.MASTER_POLICY]:
            logger.info("Using health insurance extraction pipeline")
            # Continue with policy extraction
        elif classification_result.document_type == PolicyType.LIFE_INSURANCE:
            logger.info("Using life insurance extraction pipeline")
            # TODO: Implement life insurance specific extraction
        elif classification_result.document_type in [PolicyType.CLAIM_DOCUMENT, PolicyType.HOSPITAL_BILL]:
            logger.info("Using claim processing pipeline")
            # TODO: Implement claim processing
        elif classification_result.document_type == PolicyType.MEDICAL_REPORT:
            logger.info("Using medical document processing pipeline")
            # TODO: Implement medical document processing
        else:
            logger.warning(f"Unknown document type: {classification_result.document_type.value}")
            logger.info("Using general processing pipeline")
        
        metadata_list = [metadata_entry]
        metadata_json = json.dumps(metadata_list, indent=2, ensure_ascii=False)
        file_name = os.path.splitext(os.path.basename(file_path))[0]
        
        # Extract fields using different LLMs
        result_json_openai = extract_fields_with_openai(get_openai_policy_prompt(metadata_json))
        result_json_mistral = extract_fields_with_mistral(get_mistral_policy_prompt(metadata_json))
        result_json_gemini = extract_fields_with_gemini(get_gemini_policy_prompt(metadata_json))
        
        # Validate extraction results
        logger.info("Validating extraction results...")
        validation_results = {}
        
        for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
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
                    
                    validation_report = validate_extraction_result(result_data)
                    validation_results[model] = validation_report
                    logger.info(f"{model.upper()} validation - Overall valid: {validation_report.overall_valid}, Confidence: {validation_report.overall_confidence:.2f}")
                else:
                    logger.warning(f"No result from {model}")
            except Exception as e:
                logger.error(f"Validation failed for {model}: {e}")
        
        os.makedirs("output", exist_ok=True)
        
        # Save results to files with validation
        for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
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
        
        for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
            try:
                if result_json and result_json.strip():
                    # Parse the result data
                    result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
                    
                    # Create sample claim data for testing (in real scenario, this would come from claim documents)
                    sample_claim_data = {
                        "admission_date": "2024-01-15",
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
                    for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
                        if result_json and result_json.strip():
                            result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
                            model_results[model] = {
                                **result_data,
                                "processing_time": 30.0  # Estimated processing time
                            }
                    
                    # Generate accuracy report
                    accuracy_report = tracker.compare_models(
                        model_results, 
                        ground_truth_data.get("ground_truth_values", {}),
                        f"policy_extraction_{file_name}"
                    )
                    
                    # Save accuracy report
                    os.makedirs("output", exist_ok=True)
                    tracker.save_accuracy_report(accuracy_report, f"output/accuracy_report_{file_name}.json")
                    
                    # Print accuracy summary
                    print("\n📊 Accuracy Analysis:")
                    print(f"  Best Model: {accuracy_report.overall_best_model} ({accuracy_report.overall_accuracy:.1f}% accuracy)")
                    for model_name, model_accuracy in accuracy_report.model_comparison.items():
                        print(f"  {model_name.upper()}: {model_accuracy.accuracy_percentage:.1f}% accuracy, {model_accuracy.average_confidence:.2f} confidence")
                    
                    if accuracy_report.recommendations:
                        print(f"  Recommendations: {', '.join(accuracy_report.recommendations[:3])}")
                    
                    logger.info(f"Accuracy report saved to output/accuracy_report_{file_name}.json")
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
        
        result_json_openai = extract_fields_with_openai(get_openai_policy_prompt(metadata_json))
        result_json_mistral = extract_fields_with_mistral(get_mistral_policy_prompt(metadata_json))
        result_json_gemini = extract_fields_with_gemini(get_gemini_policy_prompt(metadata_json))
        
        # Validate extraction results
        logger.info("Validating extraction results...")
        validation_results = {}
        
        for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
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
                    
                    validation_report = validate_extraction_result(result_data)
                    validation_results[model] = validation_report
                    logger.info(f"{model.upper()} validation - Overall valid: {validation_report.overall_valid}, Confidence: {validation_report.overall_confidence:.2f}")
                else:
                    logger.warning(f"No result from {model}")
            except Exception as e:
                logger.error(f"Validation failed for {model}: {e}")
        
        os.makedirs("output", exist_ok=True)
        
        # Save results to files with validation
        for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
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
        
        for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
            try:
                if result_json and result_json.strip():
                    # Parse the result data
                    result_data = json.loads(result_json) if isinstance(result_json, str) else result_json
                    
                    # Create sample claim data for testing (in real scenario, this would come from claim documents)
                    sample_claim_data = {
                        "admission_date": "2024-01-15",
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
                    for model, result_json in [("openai", result_json_openai), ("mistral", result_json_mistral), ("gemini", result_json_gemini)]:
                        if result_json and result_json.strip():
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
        print("OpenAI Results:", result_json_openai)
        print("Mistral Results:", result_json_mistral)
        print("Gemini Results:", result_json_gemini)

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