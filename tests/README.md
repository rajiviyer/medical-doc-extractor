# Tests Directory

This directory contains all test files for the medical-doc-extractor project.

## Test Categories

### 🔍 **Admission Date Extraction Tests**
- `test_admission_extraction_simple.py` - Simple verification of admission date extraction
- `test_admission_date_extraction.py` - Comprehensive admission date extraction testing
- `test_onboarding_only.py` - Testing extraction from onboarding form only
- `test_onboarding_text_extraction.py` - Text extraction verification from onboarding form

### 📅 **Date Format Tests**
- `test_date_extraction.py` - Basic date extraction functionality
- `test_date_formats.py` - Testing various date format patterns
- `test_date_validation.py` - Date validation logic testing
- `test_single_digit_dates.py` - Testing single-digit day/month date formats

### 📄 **Document Processing Tests**
- `test_document_discovery.py` - Testing document discovery and filtering
- `test_file_filtering.py` - File filtering logic testing
- `test_simple_extraction.py` - Simple document extraction testing

### 🧪 **Core System Tests**
- `test_accuracy_metrics.py` - Accuracy metrics testing
- `test_integration.py` - Integration testing
- `test_policy_classification.py` - Policy classification testing
- `test_policy_report.py` - Policy report generation testing
- `test_policy_rules.py` - Policy rules validation testing
- `test_validation.py` - General validation testing

### 🤖 **LLM and Configuration Tests**
- `test_llm_config.py` - LLM configuration testing
- `test_llm_provider.py` - LLM provider testing
- `test_prompt_system.py` - Prompt system testing

### 🐳 **Docker and Infrastructure Tests**
- `test_all_docker.py` - Docker environment testing
- `test_document_processor.py` - Document processor testing
- `test_text_extractor.py` - Text extraction testing
- `test_directory_scanner.py` - Directory scanning testing

## Running Tests

### From Project Root (Recommended)
```bash
# Run all tests
python -m pytest tests/

# Run specific test category
python -m pytest tests/test_admission_extraction_simple.py

# Run tests in Docker
docker exec -it medical-doc-interactive python -m pytest tests/
```

### From Tests Directory
```bash
cd tests
python test_admission_extraction_simple.py
```

## Test Dependencies

Most tests require:
- Docker container running (`medical-doc-interactive`)
- Test data in `data/` directory
- App modules in `app/` directory

## Recent Updates

### Admission Date Extraction (Latest)
- ✅ Fixed file filtering to include onboarding forms
- ✅ Enhanced document processing to include all relevant files
- ✅ Updated LLM prompts to look for admission dates
- ✅ Verified admission date extraction: `15/07/2025`

### Date Format Support
- ✅ Added support for DD/MM/YYYY format
- ✅ Added support for DD/MM/YY format  
- ✅ Added support for single-digit day/month formats (D/M/YY, DD/M/YY)
- ✅ Comprehensive date validation patterns 