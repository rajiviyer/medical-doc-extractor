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
├── tests/                  # All test files (organized)
│   ├── test_*.py          # Python test files
│   ├── test_docker.sh     # Docker test runner
│   ├── run_tests_docker.sh # Comprehensive test runner
│   └── README.md          # Test documentation
├── docker-compose.yml      # Docker configuration
├── docker-compose.test.yml # Test-specific Docker configuration
└── Dockerfile              # Docker image definition
```

## Quick Start

### 1. Build Docker Image
```bash
# Using the test runner script
./tests/test_docker.sh build

# Or using the comprehensive runner
./tests/run_tests_docker.sh build
```

### 2. Run All Tests
```bash
# Using the test runner script
./tests/test_docker.sh test

# Or using the comprehensive runner
./tests/run_tests_docker.sh test
```

### 3. Interactive Testing
```bash
# Using the test runner script
./tests/test_docker.sh interactive

# Or using the comprehensive runner
./tests/run_tests_docker.sh interactive
```

## Test Runner Scripts

The project now has two test runner scripts in the `tests/` directory:

### 1. `test_docker.sh` - Basic Test Runner

**Available Commands:**

| Command | Description |
|---------|-------------|
| `test` | Run comprehensive test suite |
| `interactive` | Start interactive Docker shell |
| `directory` | Test directory scanner only |
| `extractor` | Test text extractor only |
| `processor` | Test document processor only |
| `config` | Test LLM configuration only |
| `prompt` | Test prompt system only |
| `build` | Rebuild Docker image |
| `clean` | Clean up Docker containers |
| `help` | Show help information |

### 2. `run_tests_docker.sh` - Comprehensive Test Runner

**Available Commands:**

| Command | Description |
|---------|-------------|
| `test` | Run all tests with pytest |
| `interactive` | Start interactive Docker shell for manual testing |
| `directory` | Test directory scanner only |
| `extractor` | Test text extractor only |
| `processor` | Test document processor only |
| `build` | Rebuild Docker image |
| `clean` | Clean up Docker containers and images |
| `help` | Show help message |

### Usage Examples
```bash
# Test policy extraction
./tests/test_docker.sh test

# Test validation system
./tests/test_docker.sh interactive

# Test single file processing
./tests/run_tests_docker.sh test

# Interactive development
./tests/run_tests_docker.sh interactive
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
- `test_text_report.py` - Text format report generation testing

#### **🐳 Integration Tests:**
- `test_all_docker.py` - End-to-end Docker testing

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
- **Text Report Generation**: Test text format report generation
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
📄 Processing directory: data/Dashrath Patel initial
✅ Found 1 relevant document(s)
📋 Documents Found:
  1. dashrath patel onboarding.pdf
     Success: True
     Text length: 1234 characters
     ✅ Contains 'Date of Admission'
     ✅ Found admission date: 15/07/2025
```

#### **B. Comprehensive Admission Date Test (`test_admission_date_extraction.py`)**

Tests comprehensive admission date extraction with multiple formats:

**What it tests:**
- Multiple date format patterns (DD/MM/YYYY, DD/MM/YY, D/M/YY)
- Fallback extraction when LLM fails
- Integration with document processing pipeline
- Error handling for missing dates

**Expected output:**
```
🧪 Comprehensive Admission Date Extraction Test
==================================================
📄 Processing directory: data/Dashrath Patel initial
✅ Found 1 relevant document(s)
📋 Documents Found:
  1. dashrath patel onboarding.pdf
     Success: True
     Text length: 1234 characters
     ✅ Contains 'Date of Admission'
     ✅ Found admission date: 15/07/2025
🔍 Testing LLM Extraction...
✅ LLM extraction completed
  date_of_admission: 15/07/2025
  policy_start_date: 01/01/2024
  policy_end_date: 31/12/2024
```

#### **C. Onboarding Form Test (`test_onboarding_only.py`)**

Tests extraction specifically from onboarding forms:

**What it tests:**
- Document filtering to include onboarding forms
- Text extraction from onboarding documents
- Admission date extraction from onboarding forms
- Integration with LLM extraction

#### **D. Onboarding Text Extraction Test (`test_onboarding_text_extraction.py`)**

Tests text extraction verification from onboarding forms:

**What it tests:**
- Text extraction quality from onboarding forms
- Document processing pipeline integration
- Error handling for text extraction failures

### 2. Date Format Tests

#### **A. Basic Date Extraction (`test_date_extraction.py`)**

Tests basic date extraction functionality:

**What it tests:**
- Basic date pattern matching
- Date format validation
- Error handling for invalid dates

#### **B. Date Format Patterns (`test_date_formats.py`)**

Tests various date format patterns:

**What it tests:**
- DD/MM/YYYY format
- DD/MM/YY format
- D/M/YY format
- DD/M/YY format
- Date validation logic

#### **C. Date Validation (`test_date_validation.py`)**

Tests date validation logic:

**What it tests:**
- Date format validation
- Date range validation
- Error handling for invalid dates

#### **D. Single Digit Dates (`test_single_digit_dates.py`)**

Tests single-digit day/month date formats:

**What it tests:**
- D/M/YY format
- DD/M/YY format
- Date parsing logic
- Error handling for malformed dates

### 3. Document Processing Tests

#### **A. Document Discovery (`test_document_discovery.py`)**

Tests document discovery and filtering:

**What it tests:**
- File discovery in directories
- Document type filtering
- File extension validation

#### **B. File Filtering (`test_file_filtering.py`)**

Tests file filtering logic:

**What it tests:**
- Policy document filtering
- Onboarding document filtering
- File extension filtering
- Directory traversal

#### **C. Simple Extraction (`test_simple_extraction.py`)**

Tests simple document extraction:

**What it tests:**
- Basic text extraction
- PDF processing
- Image processing
- Error handling

### 4. Core Infrastructure Tests

#### **A. Directory Scanner (`test_directory_scanner.py`)**

Tests directory scanning and file discovery:

**What it tests:**
- Directory traversal
- File discovery
- File type detection
- Error handling

#### **B. Text Extractor (`test_text_extractor.py`)**

Tests PDF and OCR text extraction:

**What it tests:**
- PDF text extraction
- OCR text extraction
- Image processing
- Text quality assessment

#### **C. Document Processor (`test_document_processor.py`)**

Tests document processing pipeline:

**What it tests:**
- Document processing pipeline
- Text extraction integration
- Error handling
- Performance metrics

#### **D. LLM Configuration (`test_llm_config.py`)**

Tests LLM configuration management:

**What it tests:**
- LLM configuration loading
- API key validation
- Model selection
- Error handling

#### **E. LLM Provider (`test_llm_provider.py`)**

Tests LLM provider integration:

**What it tests:**
- OpenAI integration
- Mistral integration
- Gemini integration
- Error handling

#### **F. Prompt System (`test_prompt_system.py`)**

Tests prompt system and templates:

**What it tests:**
- Prompt template loading
- Prompt generation
- Template validation
- Error handling

### 5. Feature-Specific Tests

#### **A. Accuracy Metrics (`test_accuracy_metrics.py`)**

Tests accuracy tracking and benchmarking:

**What it tests:**
- Field-level accuracy calculation
- Model comparison
- Confidence scoring
- Error classification

#### **B. Policy Classification (`test_policy_classification.py`)**

Tests document classification system:

**What it tests:**
- Document type classification
- Policy type detection
- Classification accuracy
- Error handling

#### **C. Policy Rules (`test_policy_rules.py`)**

Tests policy rule validation system:

**What it tests:**
- Policy validity rules
- Policy limit rules
- Waiting period rules
- Risk assessment

#### **D. Validation (`test_validation.py`)**

Tests data validation system:

**What it tests:**
- Data validation logic
- Error handling
- Validation reporting
- Quality assessment

#### **E. Policy Report (`test_policy_report.py`)**

Tests tabular report generation system:

**What it tests:**
- Report generation
- Format conversion
- Data presentation
- Error handling

#### **F. Integration (`test_integration.py`)**

Tests end-to-end integration:

**What it tests:**
- Complete pipeline integration
- Error handling
- Performance metrics
- Quality assessment

#### **G. Text Report (`test_text_report.py`)**

Tests text format report generation:

**What it tests:**
- Text report generation
- Format conversion
- Data presentation
- Error handling

### 6. Integration Tests

#### **A. All Docker (`test_all_docker.py`)**

Tests end-to-end Docker environment:

**What it tests:**
- Docker environment setup
- Container functionality
- Service integration
- Error handling

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

### Using Docker Test Runners
```bash
# Using basic test runner
./tests/test_docker.sh test

# Using comprehensive test runner
./tests/run_tests_docker.sh test

# Interactive testing
./tests/test_docker.sh interactive
```

## Test Dependencies

Most tests require:
- Docker container running (`medical-doc-interactive`)
- Test data in `data/` directory
- App modules in `app/` directory
- Python dependencies installed in container

## Recent Updates

### Test File Cleanup (Latest)
- ✅ **Moved all test files to `tests/` directory**
- ✅ **Removed debugging/development tools from root directory**
- ✅ **Organized test structure for better maintainability**
- ✅ **Added comprehensive test runners**

### Admission Date Extraction (Latest)
- ✅ Fixed file filtering to include onboarding forms
- ✅ Enhanced document processing to include all relevant files
- ✅ Updated LLM prompts to look for admission dates
- ✅ Verified admission date extraction: `15/07/2025`
- ✅ Added fallback extraction when LLM fails

### Date Format Support
- ✅ Added support for DD/MM/YYYY format
- ✅ Added support for DD/MM/YY format  
- ✅ Added support for single-digit day/month formats (D/M/YY, DD/M/YY)
- ✅ Comprehensive date validation patterns

### Report Generation
- ✅ Added text format report generation
- ✅ Enhanced multi-format report support
- ✅ Improved report structure and formatting

### Policy Rule Validation
- ✅ Enhanced policy rule validation system
- ✅ Added comprehensive rule testing
- ✅ Improved deduction calculation
- ✅ Added risk assessment functionality

## Test Environment Setup

### Docker Environment
```bash
# Build test environment
docker-compose -f docker-compose.test.yml build

# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run tests
docker-compose -f docker-compose.test.yml run --rm test python -m pytest tests/
```

### Local Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/
```

## Troubleshooting

### Common Issues

1. **Docker container not starting**
   ```bash
   # Check Docker logs
   docker-compose -f docker-compose.test.yml logs
   
   # Rebuild container
   docker-compose -f docker-compose.test.yml build --no-cache
   ```

2. **Test data not found**
   ```bash
   # Ensure test data exists
   ls -la data/
   
   # Check file permissions
   chmod -R 755 data/
   ```

3. **LLM API errors**
   ```bash
   # Check API keys
   cat .env
   
   # Test API connectivity
   python -c "import openai; print('OpenAI OK')"
   ```

4. **OCR dependencies missing**
   ```bash
   # Rebuild with OCR dependencies
   docker-compose -f docker-compose.test.yml build --no-cache
   ```

### Performance Optimization

1. **Parallel test execution**
   ```bash
   # Run tests in parallel
   python -m pytest tests/ -n auto
   ```

2. **Test caching**
   ```bash
   # Use pytest cache
   python -m pytest tests/ --cache-clear
   ```

3. **Selective testing**
   ```bash
   # Run only specific test categories
   python -m pytest tests/test_admission_*.py
   ```

## Continuous Integration

### GitHub Actions
```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run tests
        run: |
          docker-compose -f docker-compose.test.yml build
          docker-compose -f docker-compose.test.yml run --rm test python -m pytest tests/
```

### Local CI
```bash
# Run full test suite
./tests/run_tests_docker.sh test

# Run with coverage
docker-compose -f docker-compose.test.yml run --rm test python -m pytest tests/ --cov=app
```

## Test Data Management

### Test Data Structure
```
data/
├── Dashrath Patel initial/
│   ├── dashrath patel onboarding.pdf
│   └── policy_documents/
├── Test Patient/
│   ├── test_onboarding.pdf
│   └── policy_documents/
└── Sample Data/
    ├── sample_onboarding.pdf
    └── policy_documents/
```

### Test Data Validation
```bash
# Validate test data structure
python -c "
import os
data_dir = 'data'
for patient_dir in os.listdir(data_dir):
    patient_path = os.path.join(data_dir, patient_dir)
    if os.path.isdir(patient_path):
        print(f'✅ {patient_dir}: {len(os.listdir(patient_path))} files')
"
```

## Quality Assurance

### Code Coverage
```bash
# Generate coverage report
python -m pytest tests/ --cov=app --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Performance Testing
```bash
# Run performance tests
python -m pytest tests/test_performance.py -v

# Generate performance report
python -m pytest tests/test_performance.py --benchmark-only
```

### Security Testing
```bash
# Run security tests
python -m pytest tests/test_security.py -v

# Check for vulnerabilities
safety check
```

## Documentation

### Test Documentation
- **`tests/README.md`** - Test directory documentation
- **`docs/TESTING.md`** - Comprehensive testing guide
- **`docs/USER_GUIDE.md`** - User guide with testing section

### API Documentation
- **`docs/API.md`** - API documentation
- **`docs/DEVELOPMENT.md`** - Development guide

### Troubleshooting
- **`docs/TROUBLESHOOTING.md`** - Common issues and solutions
- **`docs/PERFORMANCE.md`** - Performance optimization guide

## Support

For testing-related issues:
1. Check the troubleshooting section above
2. Review test logs and error messages
3. Verify test data and environment setup
4. Consult the test documentation
5. Open an issue with detailed error information 