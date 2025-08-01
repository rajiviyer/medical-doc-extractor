# Medical Document Extractor - Requirements Specification

## Project Overview

The Medical Document Extractor is a comprehensive system for processing medical documents, with a focus on policy document extraction and claims processing validation. The system supports multiple document types, LLM integration, and automated business rule validation.

---

## Core Requirements

### 1. Document Processing Requirements

#### 1.1 File Support
- **PDF Documents**: Digital and scanned PDFs
- **Image Files**: JPEG, PNG, TIFF formats
- **Handwritten Documents**: OCR support for handwritten text
- **Mixed Content**: Documents with both text and images

#### 1.2 Extraction Capabilities
- **Text Extraction**: Primary text content extraction
- **Metadata Capture**: File information, extraction method, confidence scores
- **Error Handling**: Graceful handling of corrupted or unsupported files
- **Fallback Mechanisms**: Multiple extraction methods with automatic fallback

### 2. LLM Integration Requirements

#### 2.1 Supported Models
- **OpenAI**: GPT-4, GPT-3.5-turbo
- **Mistral**: Mistral-7B, Mixtral-8x7B
- **Gemini**: Gemini Pro, Gemini Pro Vision

#### 2.2 Extraction Features
- **Policy Capping Fields**: 29 specific policy fields (room rent, ICU, etc.)
- **Structured Output**: JSON format with validation
- **Model-Specific Prompts**: Optimized prompts for each LLM
- **Confidence Scoring**: Extraction confidence assessment

### 3. Policy Document Processing Requirements

#### 3.1 Document Classification
- **Policy Filtering**: Identify policy-related documents by filename
- **Document Types**: Master policies, policy schedules, endorsements
- **Recursive Processing**: Process subdirectories within data folder

#### 3.2 Extraction Fields
The system must extract the following 29 policy capping fields:

1. **Room rent capping**
2. **ICU capping**
3. **Room category capping**
4. **Medical practitioners capping**
5. **Treatment related to participation as a non-professional in hazardous or adventure sports**
6. **Other expenses capping**
7. **Modern treatment capping**
8. **Cataract capping**
9. **Hernia capping**
10. **Joint replacement capping**
11. **Any kind of surgery specific capping**
12. **Treatment-based capping**
    - Dialysis
    - Chemotherapy
    - Radiotherapy
13. **Consumable & non-medical items capping**
14. **Maternity capping**
15. **Ambulance charge capping**
16. **Daily cash benefit**
17. **Co-payment**
18. **OPD / Daycare / Domiciliary treatment capping**
19. **Pre-post hospitalization expenses capping**
20. **Diagnostic tests & investigation capping**
21. **Implants / Stents / Prosthetics capping**
22. **Mental illness treatment capping**
23. **Organ donor expenses capping**
24. **Bariatric / Obesity surgery capping**
25. **Cancer treatment capping in specific plans**
26. **Internal (congenital) disease capping**
27. **AYUSH hospitalization capping (Ayurveda, Homeo)**
28. **Vaccination / Preventive health check-up capping**
29. **Artificial prostheses, aids capping**

### 4. Policy Rule Validation Requirements

#### 4.1 Policy Validity Rules

**Rule 1: Inception Date**
- **Section**: Policy Validity
- **Rule**: Inception Date
- **Documents Required**: Policy Master Document, Policy Document
- **Criteria**: Policy must be active on date of admission
- **Decision**: Pass or Reject

**Rule 2: Lapse Check**
- **Section**: Policy Validity
- **Rule**: Lapse Check
- **Documents Required**: Policy Master Document, Policy Document, Payment Receipt
- **Criteria**: Policy should not be in grace/lapse
- **Decision**: Pass or Reject

#### 4.2 Policy Limits Rules

**Rule 3: Room Rent Eligibility**
- **Section**: Policy Limits
- **Rule**: Room Rent Eligibility
- **Documents Required**: Policy Master Document, Policy Document, Hospital Bill
- **Criteria**: Room rent within entitled limit
- **Decision**: Pass or Proportionate Deduction
- **Deduction Amount**: If Proportionate Deduction

**Rule 4: ICU Capping**
- **Section**: Policy Limits
- **Rule**: ICU Capping
- **Documents Required**: Policy Master Document, Policy Document, Hospital Bill
- **Criteria**: ICU charges within cap
- **Decision**: Pass or Deduct
- **Deduction Amount**: If Deduct

**Rule 5: Co-payment**
- **Section**: Policy Limits
- **Rule**: Co-payment
- **Documents Required**: Policy Master Document, Policy Document
- **Criteria**: Co-pay % as per policy
- **Decision**: Pass or Deduct
- **Deduction Amount**: If Deduct

**Rule 6: Sub-limits**
- **Section**: Policy Limits
- **Rule**: Sub-limits
- **Documents Required**: Policy Master Document, Policy Document, Hospital Bill
- **Criteria**: Procedure under cap limit
- **Decision**: Pass or Cap Limit Applied

**Rule 7: Daycare**
- **Section**: Policy Limits
- **Rule**: Daycare
- **Documents Required**: Policy Master Document, Policy Document, Discharge Summary
- **Criteria**: Within IRDA-approved daycare
- **Decision**: Pass or Reject

#### 4.3 Waiting Period Rules

**Rule 8: Initial Waiting**
- **Section**: Waiting Periods
- **Rule**: Initial Waiting
- **Documents Required**: Policy Master Document, Policy Document
- **Criteria**: <30 days for non-accident
- **Decision**: Pass or Reject

**Rule 9: Disease Specific**
- **Section**: Waiting Periods
- **Rule**: Disease Specific
- **Documents Required**: Policy Master Document, Policy Document
- **Criteria**: Condition covered post waiting period
- **Decision**: Pass or Reject

**Rule 10: Maternity**
- **Section**: Waiting Periods
- **Rule**: Maternity
- **Documents Required**: Policy Master Document, Policy Document
- **Criteria**: Covered with waiting period
- **Decision**: Pass or Reject

**Rule 11: Non-Medical**
- **Section**: Waiting Periods
- **Rule**: Non-Medical
- **Documents Required**: Policy Master Document, Policy Document, Hospital Bill, Itemized Bill
- **Criteria**: IRDA non-payables
- **Decision**: Pass or Deduct
- **Deduction Amount**: If Deduct

### 5. Validation Requirements

#### 5.1 Data Validation
- **Range Checking**: Validate numerical values against expected ranges
- **Format Validation**: Ensure proper data types and formats
- **Cross-Field Validation**: Check consistency between related fields
- **Confidence Scoring**: Assess validation confidence levels

#### 5.2 Rule Validation
- **Risk Assessment**: Low/Medium/High risk classification
- **Deduction Calculation**: Automatic calculation of applicable deductions
- **Recommendations**: Actionable recommendations for claims processing
- **Compliance Checking**: IRDA guideline compliance validation

### 6. Output Requirements

#### 6.1 File Structure
- **Input Directory**: `data/` folder for policy documents
- **Output Directory**: `output/` folder for results
- **File Naming**: `extracted_summary_{model}.json` for each LLM

#### 6.2 Output Format
```json
{
  "extraction": {
    "room_rent_capping": "2%",
    "icu_capping": "5%",
    "co_payment": "10%",
    // ... other extracted fields
  },
  "validation": {
    "overall_valid": true,
    "overall_confidence": 0.85,
    "field_results": {
      // ... validation details for each field
    }
  },
  "policy_rules": {
    "overall_valid": true,
    "risk_level": "Medium",
    "total_deductions": 2500.0,
    "rule_results": {
      // ... individual rule validation results
    },
    "recommendations": [
      "Room rent deduction: 1500.0",
      "Co-payment deduction: 1000.0"
    ]
  }
}
```

### 7. Docker Requirements

#### 7.1 Containerization
- **Multi-Service Architecture**: Main, test, and interactive services
- **Profile Support**: Service selection via Docker Compose profiles
- **Volume Mounting**: Data and output directory persistence
- **Environment Management**: Environment variable configuration

#### 7.2 Deployment
- **CPU Optimization**: CPU-specific Docker Compose configuration
- **Startup Scripts**: Automated service management
- **Error Handling**: Graceful error handling and recovery
- **Logging**: Comprehensive logging for debugging

### 8. Performance Requirements

#### 8.1 Processing Speed
- **Single File**: <30 seconds for typical policy documents
- **Directory Processing**: <5 minutes for 100+ documents
- **Concurrent Processing**: Support for multiple LLM calls

#### 8.2 Resource Usage
- **Memory**: <2GB RAM for typical processing
- **CPU**: Efficient CPU utilization
- **Storage**: Minimal temporary file usage

### 9. Security Requirements

#### 9.1 Data Protection
- **API Key Security**: Secure storage of LLM API keys
- **Document Privacy**: No unauthorized access to medical documents
- **Audit Trail**: Comprehensive logging for compliance

#### 9.2 Error Handling
- **Graceful Degradation**: Continue processing on partial failures
- **Error Recovery**: Automatic retry mechanisms
- **User Feedback**: Clear error messages and recommendations

### 10. Usability Requirements

#### 10.1 Command Line Interface
- **Flexible Input**: Support for single files and directories
- **Default Behavior**: Docker-friendly default processing
- **Help System**: Comprehensive help and usage examples

#### 10.2 Documentation
- **User Guide**: Step-by-step usage instructions
- **API Documentation**: Clear interface documentation
- **Troubleshooting**: Common issues and solutions

---

## Non-Functional Requirements

### 1. Scalability
- **Horizontal Scaling**: Support for multiple processing instances
- **Batch Processing**: Efficient handling of large document sets
- **Modular Design**: Pluggable components for easy extension

### 2. Maintainability
- **Code Quality**: Clean, well-documented code
- **Testing**: Comprehensive unit and integration tests
- **Version Control**: Proper version management

### 3. Extensibility
- **New LLM Providers**: Easy addition of new LLM services
- **Custom Rules**: Extensible rule validation system
- **Document Types**: Support for additional document formats

### 4. Reliability
- **Error Recovery**: Robust error handling and recovery
- **Data Integrity**: Validation of all processed data
- **Backup Systems**: Fallback mechanisms for critical components

---

## Success Criteria

### 1. Functional Success
- ✅ Extract all 29 policy capping fields accurately
- ✅ Validate policy rules with 95%+ accuracy
- ✅ Process documents from `data/` directory successfully
- ✅ Generate structured JSON output for all LLM models

### 2. Performance Success
- ✅ Process single files in <30 seconds
- ✅ Handle directory processing efficiently
- ✅ Maintain low resource usage

### 3. Quality Success
- ✅ Comprehensive error handling
- ✅ Detailed logging and debugging
- ✅ User-friendly documentation
- ✅ Docker deployment success

---

**Document Version**: 2.0  
**Last Updated**: Current  
**Status**: Active Implementation 