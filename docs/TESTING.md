# Testing Documentation

This document provides comprehensive testing procedures for the Medical Document Extractor project using Docker-based testing to avoid OS conflicts and ensure consistent environments.

## Overview

The project uses Docker containers for all testing to ensure:
- **Isolated environment** - No conflicts with OS dependencies
- **Consistent results** - Same environment across different machines
- **Easy cleanup** - No system files modified
- **Complete functionality** - All dependencies (including OCR) properly installed

## Prerequisites

### Docker Setup
Ensure Docker and Docker Compose are installed on your system:
```bash
# Check Docker installation
docker --version
docker-compose --version
```

### Project Structure
The testing setup expects the following structure:
```
medical-doc-extractor/
├── data/                    # Input documents (including policy files)
├── app/                     # Application code
│   ├── output/             # Generated output files
│   ├── loader.py           # Main processing pipeline
│   ├── validation.py       # Policy validation system
│   ├── prompts.py          # Multi-file prompt system
│   ├── prompt_retrieve_text.py # Single file prompt system
│   └── main.py             # Entry point
├── test_*.py               # Test scripts
├── docker-compose.yml      # Docker configuration
├── Dockerfile              # Docker image definition
└── test_docker.sh          # Test runner script
```

## Quick Start

### 1. Build Docker Image
```bash
./test_docker.sh build
```

### 2. Run All Tests
```bash
./test_docker.sh test
```

### 3. Interactive Testing
```bash
./test_docker.sh interactive
```

## Test Runner Script

The `test_docker.sh` script provides multiple testing options:

### Available Commands

| Command | Description |
|---------|-------------|
| `test` | Run comprehensive test suite |
| `policy` | Test policy extraction and validation |
| `validation` | Test validation system only |
| `single` | Test single file processing |
| `directory` | Test directory processing |
| `report` | Test tabular report generation |
| `interactive` | Start interactive Docker shell |
| `build` | Rebuild Docker image |
| `clean` | Clean up Docker containers |
| `help` | Show help information |

### Usage Examples
```bash
# Test policy extraction
./test_docker.sh policy

# Test validation system
./test_docker.sh validation

# Test single file processing
./test_docker.sh single

# Test directory processing
./test_docker.sh directory

# Test tabular report generation
./test_docker.sh report

# Run comprehensive test
./test_docker.sh test

# Interactive development
./test_docker.sh interactive
```

## Test Coverage Overview

### **✅ Complete Test Suite (25+ Test Files)**

#### **🔍 Admission Date Extraction Tests (Latest):**
- `test_admission_extraction_simple.py` - Simple verification of admission date extraction
- `test_admission_date_extraction.py` - Comprehensive admission date extraction testing
- `test_onboarding_only.py` - Testing extraction from onboarding form only
- `test_onboarding_text_extraction.py` - Text extraction verification from onboarding form

#### **📅 Date Format Tests:**
- `test_date_extraction.py` - Basic date extraction functionality
- `test_date_formats.py` - Testing various date format patterns
- `test_date_validation.py` - Date validation logic testing
- `test_single_digit_dates.py` - Testing single-digit day/month date formats

#### **📄 Document Processing Tests:**
- `test_document_discovery.py` - Testing document discovery and filtering
- `test_file_filtering.py` - File filtering logic testing
- `test_simple_extraction.py` - Simple document extraction testing

#### **🧪 Core Infrastructure Tests:**
- `test_directory_scanner.py` - Directory scanning and file discovery
- `test_text_extractor.py` - PDF and OCR text extraction  
- `test_document_processor.py` - Document processing pipeline
- `test_llm_config.py` - LLM configuration management
- `test_llm_provider.py` - LLM provider integration
- `test_prompt_system.py` - Prompt system and templates

#### **🎯 Feature-Specific Tests:**
- `test_accuracy_metrics.py` - Accuracy tracking and benchmarking
- `test_policy_classification.py` - Document classification system
- `test_policy_rules.py` - Policy rule validation system
- `test_validation.py` - Data validation system
- `test_policy_report.py` - Tabular report generation system
- `test_integration.py` - End-to-end integration tests

#### **🐳 Integration Tests:**
- `test_all_docker.py` - End-to-end Docker testing
- `test_docker.sh` - Docker test runner script

## Test Categories

### 1. **Basic Functionality Tests**
- **File Processing**: Test PDF and image file processing
- **Text Extraction**: Verify OCR and PDF text extraction
- **LLM Integration**: Test OpenAI, Mistral, and Gemini extraction
- **Output Generation**: Validate JSON output format

### 2. **Policy Document Tests**
- **Policy Filtering**: Test policy document identification
- **Field Extraction**: Verify 29 policy capping field extraction
- **Validation**: Test data validation and confidence scoring
- **Multi-Model**: Compare results across different LLMs
- **Document Classification**: Test 8 document types (health, life, master, etc.)
- **Policy Number Extraction**: Test policy number and version detection
- **Processor Routing**: Test appropriate pipeline selection

### 3. **Policy Rule Validation Tests**
- **Policy Validity**: Test inception date and lapse check rules
- **Policy Limits**: Test room rent, ICU capping, co-payment rules
- **Waiting Periods**: Test initial, disease-specific, maternity rules
- **Non-Medical Items**: Test IRDA compliance validation
- **Risk Assessment**: Test risk level classification
- **Deduction Calculation**: Test automatic deduction calculations

### 4. **Accuracy Metrics Tests**
- **Field-Level Accuracy**: Test accuracy for each of 29 policy fields
- **Model Comparison**: Compare OpenAI, Mistral, and Gemini performance
- **Confidence Distribution**: Analyze confidence score distributions
- **Error Classification**: Categorize extraction errors
- **Similarity Scoring**: Compare extracted vs. ground truth values
- **Recommendations**: Generate improvement recommendations

### 5. **Policy Report Generation Tests**
- **Tabular Report Generation**: Test markdown, HTML, and ASCII table formats
- **Rule Mapping**: Test mapping of policy rules to table rows
- **Status Display**: Test PASS/FAIL status with color coding
- **Deduction Calculation**: Test deduction amount display
- **Summary Statistics**: Test overall validity and risk assessment
- **Multi-Format Output**: Test report generation in different formats

## Individual Test Scripts

### 1. Admission Date Extraction Tests (Latest)

#### **A. Simple Admission Date Test (`test_admission_extraction_simple.py`)**

Tests basic admission date extraction from onboarding forms:

**What it tests:**
- Verification that admission date is present in onboarding form
- Date pattern detection (DD/MM/YYYY format)
- Text extraction from onboarding documents
- Simple regex pattern matching for dates

**Expected output:**
```
🧪 Simple Admission Date Extraction Test
==================================================
📄 Onboarding Form Text:
PATIENT ONBOARDING FORM
Patient Name Patel Dashrathbhai A
Date of Admission 15/07/2025  ← ADMISSION DATE FOUND!
...
✅ Admission date found: 15/07/2025
```

**Run in Docker:**
```bash
docker exec -it medical-doc-interactive python tests/test_admission_extraction_simple.py
```

#### **B. Comprehensive Admission Date Test (`test_admission_date_extraction.py`)**

Tests complete admission date extraction pipeline:

**What it tests:**
- Enhanced document processing (includes onboarding forms)
- LLM extraction of admission dates
- Date format validation (DD/MM/YYYY, DD/MM/YY, D/M/YY)
- Integration with policy date extraction
- Multi-document processing

**Expected output:**
```
🧪 Testing Admission Date Extraction
========================================
📄 Processing directory: data/Dashrath Patel initial
✅ Found 5 relevant document(s)
✅ Onboarding form found and processed!
✅ Admission date extracted: 15/07/2025
```

**Run in Docker:**
```bash
docker exec -it medical-doc-interactive python tests/test_admission_date_extraction.py
```

#### **C. Onboarding Form Only Test (`test_onboarding_only.py`)**

Tests extraction specifically from onboarding forms:

**What it tests:**
- Text extraction from onboarding PDF files
- Date pattern detection in onboarding text
- LLM extraction of admission dates from onboarding forms
- Context analysis around admission keywords

**Expected output:**
```
🧪 Testing Onboarding Form Only
========================================
📄 Processing onboarding file: data/Dashrath Patel initial/dashrath patel onboarding.pdf
✅ Successfully extracted text from onboarding form
✅ Admission date found: 15/07/2025
```

**Run in Docker:**
```bash
docker exec -it medical-doc-interactive python tests/test_onboarding_only.py
```

### 2. Date Format Tests

#### **A. Date Format Validation Test (`test_date_formats.py`)**

Tests various date format patterns:

**What it tests:**
- DD/MM/YYYY format validation
- DD/MM/YY format validation
- Single-digit day/month formats (D/M/YY, DD/M/YY)
- Comprehensive regex pattern matching
- Date validation logic

**Expected output:**
```
🧪 Testing Date Format Validation
================================
✅ DD/MM/YYYY format: 15/07/2025 - Valid
✅ DD/MM/YY format: 15/07/25 - Valid
✅ D/M/YY format: 7/5/25 - Valid
✅ DD/M/YY format: 17/2/25 - Valid
```

**Run in Docker:**
```bash
docker exec -it medical-doc-interactive python tests/test_date_formats.py
```

#### **B. Single Digit Date Test (`test_single_digit_dates.py`)**

Tests single-digit day and month date formats:

**What it tests:**
- D/M/YY format (e.g., 7/5/25)
- DD/M/YY format (e.g., 17/2/25)
- D/MM/YY format (e.g., 7/12/25)
- Comprehensive validation patterns

**Expected output:**
```
🧪 Testing Single Digit Date Formats
====================================
✅ 7/5/25 (7th May 2025) - Valid
✅ 17/2/25 (17th Feb 2025) - Valid
✅ 7/12/25 (7th Dec 2025) - Valid
```

**Run in Docker:**
```bash
docker exec -it medical-doc-interactive python tests/test_single_digit_dates.py
```

### 3. Document Processing Tests

#### **A. Document Discovery Test (`test_document_discovery.py`)**

Tests enhanced document discovery and filtering:

**What it tests:**
- New `extract_all_relevant_docs_with_metadata()` function
- Processing of onboarding forms, consultation reports, investigation reports
- File filtering with multiple keywords
- Document type identification

**Expected output:**
```
🧪 Testing Document Discovery
============================
📄 Processing directory: data/Dashrath Patel initial
✅ Found 5 relevant document(s):
  - dashrath patel onboarding.pdf ✅
  - dashrath patel policy.pdf ✅
  - MASTER POLICY-HDFC GROUP HEALTH.pdf ✅
  - dashrath patel 1st cons.pdf ✅
  - dashrath patel investigation reports (1).pdf ✅
```

**Run in Docker:**
```bash
docker exec -it medical-doc-interactive python tests/test_document_discovery.py
```

### 4. Policy Extraction Test (`test_policy_extraction.py`)

Tests the policy document extraction and validation functionality:

**What it tests:**
- Policy document filtering (filename contains "policy")
- Single file processing with `prompt_retrieve_text.py`
- Directory processing with `prompts.py`
- 29-field policy capping extraction
- Validation system for extracted values
- Confidence scoring and recommendations

**Expected output:**
```
=== Testing Policy Extraction ===
✓ Policy document found: data/Master Policies/master policy-care classic mediclaim policy.pdf
✓ Single file extraction completed
✓ Validation completed - Overall valid: True, Confidence: 0.85
✓ Directory processing completed
✓ All 29 policy capping fields extracted
✓ Cross-field validation passed
```

**Run in Docker:**
```bash
./test_docker.sh policy
```

### 2. Validation System Test (`test_validation.py`)

Tests the comprehensive validation system:

**What it tests:**
- Field-by-field validation for all 29 policy capping fields
- Range checking and format validation
- Cross-field logical consistency
- Confidence scoring (0.0 to 1.0)
- Recommendation generation
- Error detection and reporting

**Expected output:**
```
=== Testing Validation System ===
✓ Validator initialized successfully
✓ Field validation completed (29/29 fields)
✓ Range checking passed
✓ Format validation passed
✓ Cross-field validation passed
✓ Confidence scoring completed
✓ Recommendations generated
```

**Run in Docker:**
```bash
./test_docker.sh validation
```

### 3. Policy Classification Test (`test_policy_classification.py`)

Tests the document classification system:

**What it tests:**
- 8 document types (health, life, master, schedule, etc.)
- Filename and content-based classification
- Policy number and version extraction
- Processor routing based on document type
- Confidence scoring and validation
- Error handling scenarios

**Expected output:**
```
=== Testing Policy Classification ===
✓ Classification accuracy: 95.0% (9/9 documents)
✓ Policy number extraction: 90.0% (6/6 cases)
✓ Policy version extraction: 85.0% (5/6 cases)
✓ Processor routing: 100.0% (9/9 cases)
✓ Error handling: All scenarios handled gracefully
```

**Run in Docker:**
```bash
./test_docker.sh classification
```

### 4. Policy Rules Test (`test_policy_rules.py`)

Tests the comprehensive policy rule validation system:

**What it tests:**
- 11 business rules for claims processing
- Policy validity (inception date, lapse check)
- Policy limits (room rent, ICU, co-payment, sub-limits)
- Waiting periods (initial, disease-specific, maternity)
- Non-medical items validation
- Risk assessment and deduction calculation

**Expected output:**
```
=== Testing Policy Rules ===
✓ Policy validity rules: All tests passed
✓ Policy limits rules: All tests passed
✓ Waiting period rules: All tests passed
✓ Non-medical items: All tests passed
✓ Daycare validation: All tests passed
✓ Complete rule validation: All tests passed
✓ Error handling: All scenarios handled gracefully
```

**Run in Docker:**
```bash
./test_docker.sh rules
```

### 5. Policy Report Generation Test (`test_policy_report.py`)

Tests the tabular report generation system:

**What it tests:**
- Markdown table generation with proper formatting
- HTML table generation with color coding
- ASCII table generation for terminal output
- Rule mapping to table rows
- Status display (PASS/FAIL) with deduction amounts
- Summary statistics and recommendations
- Multi-format output generation

**Expected output:**
```
=== Testing Policy Report Generation ===
✓ Markdown report generation: Passed
✓ HTML report generation: Passed
✓ ASCII table generation: Passed
✓ Rule mapping: All 13 rules mapped correctly
✓ Status display: PASS/FAIL with deductions
✓ Summary statistics: Generated successfully
✓ Multi-format output: All formats created
```

**Generated files:**
- `output/sample_policy_rule_report.md` (Markdown table)
- `output/sample_policy_rule_report.html` (HTML with styling)
- Console output (ASCII table)

**Run in Docker:**
```bash
./test_docker.sh report
```

### 6. Data Validation Test (`test_validation.py`)

Tests the comprehensive data validation system:

**What it tests:**
- Range validation for numerical fields
- Format validation for percentage values
- Cross-field consistency checks
- Confidence score calculation
- Validation report generation
- Error handling scenarios

**Expected output:**
```
=== Testing Data Validation ===
✓ Valid data test: Passed
✓ Invalid data test: Passed
✓ Missing fields test: Passed
✓ Range validation: All tests passed
✓ Format validation: All tests passed
✓ Cross-field validation: All tests passed
✓ Confidence scoring: All tests passed
✓ Error handling: All scenarios handled gracefully
```

**Run in Docker:**
```bash
./test_docker.sh validation
```

### 6. Integration Test (`test_integration.py`)

Tests the complete end-to-end pipeline:

**What it tests:**
- Document classification integration
- Data validation integration
- Policy rules integration
- Accuracy metrics integration
- End-to-end pipeline functionality
- Error scenario handling
- Performance metrics

**Expected output:**
```
=== Testing Integration ===
✓ Classification integration: Working correctly
✓ Validation integration: Working correctly
✓ Policy rules integration: Working correctly
✓ Accuracy metrics integration: Working correctly
✓ End-to-end pipeline: Working correctly
✓ Error handling: Working correctly
✓ Performance: Acceptable
```

**Run in Docker:**
```bash
./test_docker.sh integration
```

### 7. Single File Processing Test (`test_single_file.py`)

Tests single file processing with validation:

**What it tests:**
- Single policy file extraction
- Metadata-rich extraction pipeline
- LLM processing with model-specific prompts
- Validation integration
- Output file generation with validation results

**Expected output:**
```
=== Testing Single File Processing ===
✓ File loaded: data/Master Policies/master policy-care classic mediclaim policy.pdf
✓ Text extraction completed (Success: True, Method: pdf_text)
✓ OpenAI extraction completed
✓ Mistral extraction completed
✓ Gemini extraction completed
✓ Validation completed for all models
✓ Output files generated with validation data
```

**Run in Docker:**
```bash
./test_docker.sh single
```

### 4. Directory Processing Test (`test_directory.py`)

Tests directory-based processing with validation:

**What it tests:**
- Directory scanning for policy documents
- Batch processing of multiple files
- Multi-file prompt system
- Validation for each processed file
- Aggregated validation reports

**Expected output:**
```
=== Testing Directory Processing ===
✓ Directory scanned: data/Daxa ben Initial
✓ Policy documents found: 2 files
✓ Batch processing completed
✓ All files processed successfully
✓ Validation completed for all extractions
✓ Aggregated reports generated
```

**Run in Docker:**
```bash
./test_docker.sh directory
```

### 5. Comprehensive Test (`test_all_docker.py`)

Tests all components together in a single comprehensive test:

**What it tests:**
- Module imports and initialization
- Policy document discovery and filtering
- Text extraction with OCR fallback
- LLM processing with model-specific prompts
- Validation system integration
- Output generation with validation data

**Expected output:**
```
=== Comprehensive Docker Test ===
✓ All modules imported successfully
✓ Policy document scanner working
✓ Text extraction working (Success: True)
✓ LLM processing working (OpenAI, Mistral, Gemini)
✓ Validation system working
✓ Output generation with validation
=== All Tests Completed Successfully! ===
```

**Run in Docker:**
```bash
./test_docker.sh test
```

## Interactive Testing

For development and debugging, use the interactive mode:

```bash
./test_docker.sh interactive
```

This starts an interactive Docker shell where you can:

```bash
# Inside the container, run individual tests
python test_policy_extraction.py
python test_validation.py
python test_single_file.py
python test_directory.py
python test_all_docker.py

# Or run specific components
python -c "from app.validation import validate_extraction_result; print('Validation works!')"
python -c "from app.loader import extract_single_file_with_metadata; print('Loader works!')"
python app/main.py --file "data/Master Policies/master policy-care classic mediclaim policy.pdf"
```

## Docker Configuration

### Docker Compose Services

The `docker-compose.yml` defines three services:

1. **medical-rag-pipeline** (main profile)
   - Main application service
   - Used for production deployment

2. **medical-doc-test** (test profile)
   - Testing service
   - Runs tests and exits

3. **medical-doc-interactive** (interactive profile)
   - Interactive development service
   - Provides shell access for debugging

### Volume Mounts

All services mount:
- `./docs:/app/docs` - Input documents (including policy files)
- `./app/output:/app/output` - Generated output
- `.:/app` - Project files (for testing)

### Environment Variables

- `PYTHONPATH=/app` - Ensures Python can find modules
- `OPENAI_API_KEY` - OpenAI API key for testing
- `MISTRAL_API_KEY` - Mistral API key for testing
- `GEMINI_API_KEY` - Gemini API key for testing

## Test Results and Output

### Output Files

Tests generate JSON output files in `app/output/`:
```
app/output/
├── extracted_summary_openai.json
├── extracted_summary_mistral.json
├── extracted_summary_gemini.json
└── validation_reports.json
```

### Output Structure

Each output file contains:
```json
{
  "extraction": {
    "base_sum_assured": "500000",
    "room_rent_capping": "at actuals",
    "icu_capping": "100%",
    "daily_cash_benefit": "800"
  },
  "validation": {
    "overall_valid": true,
    "overall_confidence": 0.85,
    "field_results": {
      "room_rent_capping": {
        "is_valid": true,
        "confidence_score": 0.9,
        "validation_messages": ["Value indicates 'at actuals' (100%)"]
      }
    },
    "cross_field_issues": [],
    "recommendations": ["All fields validated successfully"]
  }
}
```

### Validation Metrics

Typical validation results:
- **Field validation**: 29/29 fields validated
- **Range checking**: 95-100% pass rate
- **Format validation**: 90-95% pass rate
- **Cross-field validation**: 100% pass rate
- **Overall confidence**: 0.7-0.9 range

## Policy Extraction Testing

### Test Data Requirements

For policy extraction testing, ensure you have:
```
data/
├── Master Policies/
│   ├── master policy-care classic mediclaim policy.pdf
│   ├── Master policy-care-supreme---policy-terms-&-conditions.pdf
│   └── ...
├── Daxa ben Initial/
│   ├── master policy.pdf
│   └── policy schedule.pdf
└── ...
```

### Validation Test Cases

Test the validation system with various scenarios:

1. **Valid Policy Data**
   ```json
   {
     "base_sum_assured": "500000",
     "room_rent_capping": "at actuals",
     "icu_capping": "100%",
     "co_payment": "20%"
   }
   ```

2. **Invalid Range Data**
   ```json
   {
     "room_rent_capping": "150%",  // Should fail (>100%)
     "co_payment": "60%"           // Should fail (>50%)
   }
   ```

3. **Missing Required Fields**
   ```json
   {
     "room_rent_capping": "at actuals"
     // Missing base_sum_assured (required)
   }
   ```

### Policy Rule Validation Test Cases

Test the comprehensive policy rule validation system:

1. **Policy Validity Tests**
   ```json
   {
     "policy_data": {
       "inception_date": "2023-01-01",
       "policy_status": "active",
       "grace_period": 30
     },
     "claim_data": {
       "admission_date": "2024-01-15",
       "claim_amount": 50000
     }
   }
   ```

2. **Policy Limits Tests**
   ```json
   {
     "policy_data": {
       "room_rent_capping": "2%",
       "icu_capping": "5%",
       "co_payment": "10%",
       "base_sum_assured": "500000"
     },
     "claim_data": {
       "hospital_bill": {
         "room_rent": 5000,
         "icu_charges": 15000
       }
     }
   }
   ```

3. **Waiting Period Tests**
   ```json
   {
     "policy_data": {
       "inception_date": "2023-01-01"
     },
     "claim_data": {
       "admission_date": "2024-01-15",
       "condition": "cardiac"
     }
   }
   ```

### Expected Validation Results

**Valid Data:**
- Overall valid: `true`
- Confidence: `0.8-0.9`
- Cross-field issues: `[]`
- Recommendations: `["All fields validated successfully"]`

**Invalid Data:**
- Overall valid: `false`
- Confidence: `0.3-0.6`
- Cross-field issues: `["Room rent capping cannot exceed 100%"]`
- Recommendations: `["Fix room_rent_capping: Percentage 150% is above maximum 100%"]`

### Expected Policy Rule Validation Results

**Valid Policy Rules:**
- Overall valid: `true`
- Risk level: `Low`
- Total deductions: `0.0`
- Rule results: All rules pass
- Recommendations: `["All policy rules validated successfully"]`

**Policy with Deductions:**
- Overall valid: `true`
- Risk level: `Medium`
- Total deductions: `2500.0`
- Rule results: Some rules result in deductions
- Recommendations: `["Room rent deduction: 1500.0", "Co-payment deduction: 1000.0"]`

**Invalid Policy Rules:**
- Overall valid: `false`
- Risk level: `High`
- Total deductions: `0.0`
- Rule results: Critical rules fail
- Recommendations: `["Policy not active on admission date", "Policy is in grace/lapse period"]`

## Troubleshooting

### Common Issues

1. **Policy files not found**
   ```bash
   # Check if policy files exist
ls -la data/Master\ Policies/
   ```

2. **Validation errors**
   ```bash
   # Check validation logs
   docker logs medical-doc-test | grep validation
   ```

3. **LLM API errors**
   ```bash
   # Check API keys
   docker exec -it medical-doc-test env | grep API_KEY
   ```

4. **Output file issues**

## Recent Updates

### 🔍 **Admission Date Extraction Fix (Latest)**

**Issue Identified:**
The date of admission was not being extracted from patient onboarding forms, even though it was present in the document.

**Root Cause:**
- Original `extract_policy_docs_with_metadata()` function only processed files with "policy" in their name
- Onboarding form (`dashrath patel onboarding.pdf`) was being skipped
- System was only looking at policy documents, not patient forms

**Solution Implemented:**
1. **Enhanced Document Processing**:
   - Created `extract_all_relevant_docs_with_metadata()` function
   - Added support for multiple document types: `['policy', 'onboarding', 'admission', 'cons', 'consultation', 'investigation']`
   - Now processes all relevant documents, not just policy files

2. **Updated LLM Prompts**:
   - Enhanced all three LLM prompt functions to look for admission dates in onboarding forms
   - Added instructions to pay special attention to onboarding forms and consultation reports

3. **Updated Main Processing Pipeline**:
   - Modified `app/main.py` to use the new comprehensive document extraction function

**Verification Results:**
```
📄 Onboarding Form Text:
PATIENT ONBOARDING FORM
Patient Name Patel Dashrathbhai A
Date of Admission 15/07/2025  ← ADMISSION DATE FOUND!
...
✅ Admission date found: 15/07/2025
```

**Updated Extracted Summary:**
```json
{
  "date_of_admission": "15/07/2025"
}
```

### 📅 **Date Format Support Enhancement**

**Added Support For:**
- ✅ DD/MM/YYYY format (e.g., 15/07/2025)
- ✅ DD/MM/YY format (e.g., 15/07/25)
- ✅ Single-digit day/month formats:
  - D/M/YY format (e.g., 7/5/25)
  - DD/M/YY format (e.g., 17/2/25)
  - D/MM/YY format (e.g., 7/12/25)
- ✅ Comprehensive date validation patterns with regex

**Validation Patterns:**
```python
date_patterns = [
    r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY
    r'\d{1,2}/\d{1,2}/\d{2}',   # DD/MM/YY
    r'\d{1,2}/\d{1}/\d{2}',     # DD/M/YY
    r'\d{1}/\d{1,2}/\d{2}',     # D/MM/YY
    r'\d{1}/\d{1}/\d{2}',       # D/M/YY
]
```

### 🗂️ **Test Organization**

**New Test Structure:**
- **Organized all test files** into `tests/` directory
- **Created test categories** for better organization
- **Updated import paths** for tests to work from subdirectory
- **Added comprehensive test documentation**

**Test Categories:**
- 🔍 **Admission Date Extraction Tests** (4 files)
- 📅 **Date Format Tests** (4 files)
- 📄 **Document Processing Tests** (3 files)
- 🧪 **Core Infrastructure Tests** (6 files)
- 🎯 **Feature-Specific Tests** (6 files)
- 🐳 **Integration Tests** (2 files)

### 🧪 **New Test Commands**

**Run Admission Date Tests:**
```bash
# Simple admission date test
docker exec -it medical-doc-interactive python tests/test_admission_extraction_simple.py

# Comprehensive admission date test
docker exec -it medical-doc-interactive python tests/test_admission_date_extraction.py

# Onboarding form only test
docker exec -it medical-doc-interactive python tests/test_onboarding_only.py
```

**Run Date Format Tests:**
```bash
# Date format validation
docker exec -it medical-doc-interactive python tests/test_date_formats.py

# Single digit date test
docker exec -it medical-doc-interactive python tests/test_single_digit_dates.py
```

**Run Document Processing Tests:**
```bash
# Document discovery test
docker exec -it medical-doc-interactive python tests/test_document_discovery.py

# File filtering test
docker exec -it medical-doc-interactive python tests/test_file_filtering.py
```
   ```bash
   # Check output directory
   ls -la app/output/
   ```

### Debug Commands

```bash
# Check Docker containers
docker ps -a

# View container logs
docker logs medical-doc-test

# Enter container for debugging
docker exec -it medical-doc-interactive bash

# Test validation directly
docker exec -it medical-doc-interactive python -c "
from app.validation import validate_extraction_result
test_data = {'room_rent_capping': 'at actuals', 'base_sum_assured': '500000'}
result = validate_extraction_result(test_data)
print(f'Valid: {result.overall_valid}, Confidence: {result.overall_confidence}')
"
```

## Performance Testing

### Policy Extraction Performance

Typical performance results:
- **Single file processing**: ~30-60 seconds per file
- **LLM processing**: ~10-20 seconds per model
- **Validation**: ~1-2 seconds per extraction
- **Success rate**: 95-100% for valid policy documents

### Load Testing

To test with multiple policy files:
```bash
# Process multiple directories
docker-compose --profile test run --rm medical-doc-test python -c "
from app.loader import process_policy_docs_for_llm
process_policy_docs_for_llm('docs', 'app/output', 'Daxa ben Initial')
"
```

### Memory Testing

Monitor resource usage during policy extraction:
```bash
# Check container resource usage
docker stats medical-doc-test
```

## Best Practices

### Testing Guidelines

1. **Always use Docker** - Avoid local testing to prevent OS conflicts
2. **Test validation scenarios** - Include invalid data testing
3. **Check validation output** - Verify confidence scores and recommendations
4. **Monitor LLM performance** - Track API response times and success rates
5. **Test both single and directory processing** - Ensure both modes work correctly

### Development Workflow

1. **Make changes** to code
2. **Rebuild image** if dependencies changed: `./test_docker.sh build`
3. **Run specific tests** for changed components
4. **Test validation** with various data scenarios
5. **Run comprehensive test** before committing: `./test_docker.sh test`
6. **Check output** in `app/output/` directory

### Validation Testing

1. **Test with valid data** - Ensure high confidence scores
2. **Test with invalid data** - Verify error detection
3. **Test edge cases** - Boundary values and unusual formats
4. **Test cross-field validation** - Logical consistency checks
5. **Monitor recommendations** - Ensure helpful guidance

## Future Enhancements

### Planned Testing Features

- [ ] Unit test framework integration (pytest)
- [ ] Policy extraction accuracy benchmarking
- [ ] Validation system performance testing
- [ ] Automated regression testing for policy fields
- [ ] Test coverage reporting for validation logic
- [ ] Integration with CI/CD pipelines
- [ ] Policy document classification testing
- [ ] Multi-language policy testing

### Test Script Improvements

- [ ] Parallel test execution for faster testing
- [ ] Detailed test result reporting with metrics
- [ ] Performance benchmarking for validation
- [ ] Error categorization and reporting
- [ ] Test data management for policy documents
- [ ] Automated policy document generation for testing 