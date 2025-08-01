#!/usr/bin/env python3
"""
Test script for policy document classification system.
"""

import json
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from policy_classifier import PolicyClassifier, classify_policy_document, PolicyType, DocumentCategory

def create_test_documents():
    """Create test documents with different types and content."""
    return {
        "health_insurance_policy.pdf": {
            "content": "This is a health insurance policy document containing mediclaim coverage details. Room rent capping is 2% and ICU capping is 5%. The policy provides coverage for hospitalization expenses.",
            "expected_type": PolicyType.HEALTH_INSURANCE,
            "expected_category": DocumentCategory.POLICY
        },
        "master_policy_document.pdf": {
            "content": "Master Policy Document - Terms and Conditions. This document contains the base policy wordings and terms for health insurance coverage.",
            "expected_type": PolicyType.MASTER_POLICY,
            "expected_category": DocumentCategory.POLICY
        },
        "policy_schedule_individual.pdf": {
            "content": "Policy Schedule - Individual Member Details. This schedule contains the specific coverage details for the insured member.",
            "expected_type": PolicyType.POLICY_SCHEDULE,
            "expected_category": DocumentCategory.POLICY
        },
        "life_insurance_policy.pdf": {
            "content": "Life Insurance Policy - Term Life Coverage. This policy provides death benefit and maturity benefit as per the terms.",
            "expected_type": PolicyType.LIFE_INSURANCE,
            "expected_category": DocumentCategory.POLICY
        },
        "endorsement_rider.pdf": {
            "content": "Policy Endorsement - Additional Rider Coverage. This endorsement modifies the base policy to add additional coverage.",
            "expected_type": PolicyType.ENDORSEMENT,
            "expected_category": DocumentCategory.POLICY
        },
        "claim_form.pdf": {
            "content": "Claim Form - Hospitalization Claim Request. This form is for submitting a claim for hospitalization expenses.",
            "expected_type": PolicyType.CLAIM_DOCUMENT,
            "expected_category": DocumentCategory.CLAIM
        },
        "hospital_bill.pdf": {
            "content": "Hospital Bill - Itemized Charges. This document contains the detailed breakdown of hospital charges and costs.",
            "expected_type": PolicyType.HOSPITAL_BILL,
            "expected_category": DocumentCategory.CLAIM
        },
        "medical_report.pdf": {
            "content": "Medical Report - Diagnosis and Treatment. This report contains the doctor's diagnosis and treatment recommendations.",
            "expected_type": PolicyType.MEDICAL_REPORT,
            "expected_category": DocumentCategory.MEDICAL
        },
        "unknown_document.pdf": {
            "content": "This is a generic document with no specific policy-related content.",
            "expected_type": PolicyType.OTHER,
            "expected_category": DocumentCategory.ADMINISTRATIVE
        }
    }

def test_basic_classification():
    """Test basic classification functionality."""
    print("🧪 Testing Basic Classification")
    print("=" * 50)
    
    test_documents = create_test_documents()
    classifier = PolicyClassifier()
    
    correct_classifications = 0
    total_documents = len(test_documents)
    
    for filename, test_data in test_documents.items():
        print(f"\n📄 Testing: {filename}")
        
        # Classify document
        classification_result = classifier.classify_document(
            filename=filename,
            content=test_data["content"]
        )
        
        # Check results
        expected_type = test_data["expected_type"]
        expected_category = test_data["expected_category"]
        
        type_correct = classification_result.document_type == expected_type
        category_correct = classification_result.category == expected_category
        
        if type_correct and category_correct:
            correct_classifications += 1
            print(f"  ✅ Correctly classified as {classification_result.document_type.value}")
        else:
            print(f"  ❌ Expected: {expected_type.value}, Got: {classification_result.document_type.value}")
            print(f"  ❌ Expected category: {expected_category.value}, Got: {classification_result.category.value}")
        
        print(f"  Confidence: {classification_result.confidence_score:.2f}")
        print(f"  Policy Number: {classification_result.policy_number or 'Not found'}")
        print(f"  Policy Version: {classification_result.policy_version or 'Not found'}")
        
        if classification_result.recommendations:
            print(f"  Recommendations: {classification_result.recommendations[0]}")
    
    accuracy = (correct_classifications / total_documents) * 100
    print(f"\n📊 Classification Accuracy: {accuracy:.1f}% ({correct_classifications}/{total_documents})")
    
    return accuracy

def test_policy_number_extraction():
    """Test policy number extraction functionality."""
    print("\n🧪 Testing Policy Number Extraction")
    print("=" * 50)
    
    test_cases = [
        ("POL-2024-001234.pdf", "2024001234"),
        ("Policy_No_2024_001234.pdf", "2024001234"),
        ("Policy Number 2024-001234.pdf", "2024001234"),
        ("2024001234_policy.pdf", "2024001234"),
        ("POL2024001234.pdf", "2024001234"),
        ("policy_without_number.pdf", None)
    ]
    
    classifier = PolicyClassifier()
    correct_extractions = 0
    
    for filename, expected_number in test_cases:
        print(f"\n📄 Testing: {filename}")
        
        extracted_number = classifier._extract_policy_number(filename)
        
        if extracted_number == expected_number:
            correct_extractions += 1
            print(f"  ✅ Correctly extracted: {extracted_number}")
        else:
            print(f"  ❌ Expected: {expected_number}, Got: {extracted_number}")
    
    accuracy = (correct_extractions / len(test_cases)) * 100
    print(f"\n📊 Policy Number Extraction Accuracy: {accuracy:.1f}% ({correct_extractions}/{len(test_cases)})")
    
    return accuracy

def test_policy_version_extraction():
    """Test policy version extraction functionality."""
    print("\n🧪 Testing Policy Version Extraction")
    print("=" * 50)
    
    test_cases = [
        ("policy_v1.2.pdf", "1.2"),
        ("policy_version_2.1.pdf", "2.1"),
        ("policy_ver_3.0.pdf", "3.0"),
        ("policy_2024-01-15.pdf", "2024-01-15"),
        ("policy_rev_5.pdf", "5"),
        ("policy_without_version.pdf", None)
    ]
    
    classifier = PolicyClassifier()
    correct_extractions = 0
    
    for filename, expected_version in test_cases:
        print(f"\n📄 Testing: {filename}")
        
        extracted_version = classifier._extract_policy_version(filename)
        
        if extracted_version == expected_version:
            correct_extractions += 1
            print(f"  ✅ Correctly extracted: {extracted_version}")
        else:
            print(f"  ❌ Expected: {expected_version}, Got: {extracted_version}")
    
    accuracy = (correct_extractions / len(test_cases)) * 100
    print(f"\n📊 Policy Version Extraction Accuracy: {accuracy:.1f}% ({correct_extractions}/{len(test_cases)})")
    
    return accuracy

def test_processor_routing():
    """Test processor routing functionality."""
    print("\n🧪 Testing Processor Routing")
    print("=" * 50)
    
    test_cases = [
        (PolicyType.HEALTH_INSURANCE, "health_policy_processor"),
        (PolicyType.LIFE_INSURANCE, "life_policy_processor"),
        (PolicyType.MASTER_POLICY, "master_policy_processor"),
        (PolicyType.POLICY_SCHEDULE, "policy_schedule_processor"),
        (PolicyType.ENDORSEMENT, "endorsement_processor"),
        (PolicyType.CLAIM_DOCUMENT, "claim_processor"),
        (PolicyType.MEDICAL_REPORT, "medical_processor"),
        (PolicyType.HOSPITAL_BILL, "bill_processor"),
        (PolicyType.OTHER, "general_processor")
    ]
    
    classifier = PolicyClassifier()
    correct_routings = 0
    
    for policy_type, expected_processor in test_cases:
        # Create a mock classification result
        from policy_classifier import ClassificationResult
        mock_result = ClassificationResult(
            document_type=policy_type,
            category=DocumentCategory.POLICY,
            confidence_score=0.9,
            extraction_method="test"
        )
        
        routed_processor = classifier.route_to_processor(mock_result)
        
        if routed_processor == expected_processor:
            correct_routings += 1
            print(f"  ✅ {policy_type.value} -> {routed_processor}")
        else:
            print(f"  ❌ {policy_type.value} -> Expected: {expected_processor}, Got: {routed_processor}")
    
    accuracy = (correct_routings / len(test_cases)) * 100
    print(f"\n📊 Processor Routing Accuracy: {accuracy:.1f}% ({correct_routings}/{len(test_cases)})")
    
    return accuracy

def test_confidence_scoring():
    """Test confidence scoring for different scenarios."""
    print("\n🧪 Testing Confidence Scoring")
    print("=" * 50)
    
    test_scenarios = [
        {
            "filename": "mediclaim_policy.pdf",
            "content": "This is a mediclaim policy with room rent capping and ICU coverage.",
            "description": "High confidence - filename and content match"
        },
        {
            "filename": "document.pdf",
            "content": "This document contains mediclaim policy details with health insurance coverage.",
            "description": "Medium confidence - only content matches"
        },
        {
            "filename": "unknown.pdf",
            "content": "This is a generic document with no specific policy content.",
            "description": "Low confidence - no clear indicators"
        }
    ]
    
    classifier = PolicyClassifier()
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n📄 Scenario {i}: {scenario['description']}")
        
        classification_result = classifier.classify_document(
            filename=scenario["filename"],
            content=scenario["content"]
        )
        
        print(f"  Document Type: {classification_result.document_type.value}")
        print(f"  Confidence: {classification_result.confidence_score:.2f}")
        print(f"  Category: {classification_result.category.value}")
        
        # Validate classification
        is_valid = classifier.validate_classification(classification_result)
        print(f"  Valid Classification: {'✅ Yes' if is_valid else '❌ No'}")

def test_error_handling():
    """Test error handling scenarios."""
    print("\n🧪 Testing Error Handling")
    print("=" * 50)
    
    classifier = PolicyClassifier()
    
    # Test with invalid input
    try:
        result = classifier.classify_document(filename="", content=None)
        print("✅ Handled empty filename gracefully")
    except Exception as e:
        print(f"❌ Failed to handle empty filename: {e}")
    
    # Test with malformed content
    try:
        result = classifier.classify_document(
            filename="test.pdf",
            content="This is a test document with mediclaim policy details."
        )
        print("✅ Handled normal content successfully")
    except Exception as e:
        print(f"❌ Failed to handle normal content: {e}")

def main():
    """Run all classification tests."""
    print("🚀 Starting Policy Document Classification Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        classification_accuracy = test_basic_classification()
        policy_number_accuracy = test_policy_number_extraction()
        policy_version_accuracy = test_policy_version_extraction()
        routing_accuracy = test_processor_routing()
        
        test_confidence_scoring()
        test_error_handling()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Classification Accuracy: {classification_accuracy:.1f}%")
        print(f"Policy Number Extraction: {policy_number_accuracy:.1f}%")
        print(f"Policy Version Extraction: {policy_version_accuracy:.1f}%")
        print(f"Processor Routing: {routing_accuracy:.1f}%")
        
        overall_score = (classification_accuracy + policy_number_accuracy + 
                        policy_version_accuracy + routing_accuracy) / 4
        
        print(f"\nOverall System Score: {overall_score:.1f}%")
        
        if overall_score >= 80:
            print("✅ Classification system is performing well!")
        elif overall_score >= 60:
            print("⚠️  Classification system needs improvement")
        else:
            print("❌ Classification system needs significant improvement")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 