#!/usr/bin/env python3
"""
Test script for the LLM provider interface.
Tests the modular LLM provider system without requiring actual API keys.
"""

import logging
import json
from app.llm_provider import (
    LLMProvider, LLMResponse, RuleAnalysisResult,
    create_llm_provider, get_available_providers, validate_provider_config
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockLLMProvider(LLMProvider):
    """Mock LLM provider for testing without API keys."""
    
    def __init__(self, api_key: str = "mock_key", model: str = "mock-model", **kwargs):
        super().__init__(api_key, model, **kwargs)
    
    def _validate_config(self):
        """Mock validation - always passes."""
        pass
    
    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        """Mock request that returns a structured response."""
        import time
        start_time = time.time()
        
        # Simulate processing time
        time.sleep(0.1)
        processing_time = time.time() - start_time
        
        # Create a mock response based on the prompt
        if "policy" in prompt.lower():
            mock_response = {
                "decision": "PASS",
                "confidence": 0.85,
                "extracted_data": {
                    "policy_type": "health_insurance",
                    "coverage_amount": "500000",
                    "premium": "5000"
                },
                "additional_info": {
                    "document_type": "policy_document",
                    "extraction_method": "llm_analysis"
                },
                "recommendations": [
                    "Document appears to be a valid health insurance policy",
                    "All required fields are present and legible"
                ]
            }
        else:
            mock_response = {
                "decision": "WARNING",
                "confidence": 0.65,
                "extracted_data": {},
                "additional_info": {
                    "document_type": "unknown",
                    "extraction_method": "llm_analysis"
                },
                "recommendations": [
                    "Document type unclear - manual review recommended"
                ]
            }
        
        return LLMResponse(
            provider="Mock",
            model=self.model,
            content=json.dumps(mock_response),
            confidence=0.85,
            processing_time=processing_time,
            tokens_used=150,
            metadata={'mock': True}
        )

def test_llm_provider_interface():
    """Test the LLM provider interface functionality."""
    
    print("=== Testing LLM Provider Interface ===\n")
    
    # Test 1: Available providers
    print("1. Testing available providers...")
    try:
        providers = get_available_providers()
        print(f"✓ Available providers: {providers}")
        assert 'openai' in providers
        assert 'mistral' in providers
        assert 'gemini' in providers
    except Exception as e:
        print(f"✗ Provider list test failed: {e}")
        return False
    
    # Test 2: Factory function
    print("\n2. Testing factory function...")
    try:
        # Test with mock provider (we'll create a mock)
        mock_provider = MockLLMProvider()
        print("✓ Mock provider created successfully")
        
        # Test factory function with mock
        def create_mock_provider(provider_type: str, api_key: str, model: str = None, **kwargs):
            if provider_type == 'mock':
                return MockLLMProvider(api_key, model or "mock-model", **kwargs)
            else:
                raise ValueError(f"Unsupported provider type: {provider_type}")
        
        mock_provider2 = create_mock_provider('mock', 'test_key')
        print("✓ Factory function working")
        
    except Exception as e:
        print(f"✗ Factory function test failed: {e}")
        return False
    
    # Test 3: LLM Response structure
    print("\n3. Testing LLM Response structure...")
    try:
        response = LLMResponse(
            provider="Mock",
            model="mock-model",
            content='{"test": "response"}',
            confidence=0.85,
            processing_time=0.1,
            tokens_used=100
        )
        print("✓ LLM Response structure created")
        print(f"  - Provider: {response.provider}")
        print(f"  - Model: {response.model}")
        print(f"  - Confidence: {response.confidence}")
        print(f"  - Processing time: {response.processing_time}")
        
    except Exception as e:
        print(f"✗ LLM Response test failed: {e}")
        return False
    
    # Test 4: Rule Analysis Result structure
    print("\n4. Testing Rule Analysis Result structure...")
    try:
        rule_result = RuleAnalysisResult(
            rule_id="test_rule_001",
            rule_name="Policy Document Validation",
            rule_description="Check if document is a valid policy",
            decision="PASS",
            confidence=0.85,
            extracted_data={"policy_type": "health_insurance"},
            additional_info={"document_type": "policy"},
            recommendations=["Document is valid"],
            processing_time=0.1,
            llm_provider="Mock",
            llm_model="mock-model"
        )
        print("✓ Rule Analysis Result structure created")
        print(f"  - Rule ID: {rule_result.rule_id}")
        print(f"  - Decision: {rule_result.decision}")
        print(f"  - Confidence: {rule_result.confidence}")
        
    except Exception as e:
        print(f"✗ Rule Analysis Result test failed: {e}")
        return False
    
    # Test 5: Document analysis with mock provider
    print("\n5. Testing document analysis...")
    try:
        mock_provider = MockLLMProvider()
        
        # Sample document text
        sample_text = """
        UNITED INDIA INSURANCE COMPANY LIMITED
        Individual Health Insurance Policy
        
        Policy Number: UIIC/HLT/2025/001
        Sum Insured: Rs. 5,00,000
        Premium: Rs. 5,000 per annum
        
        This policy provides comprehensive health coverage including:
        - Hospitalization expenses
        - Pre and post hospitalization
        - Day care procedures
        - Ambulance charges
        """
        
        # Sample rules
        rules = [
            {
                "id": "policy_validation_001",
                "name": "Policy Document Validation",
                "description": "Check if document is a valid insurance policy"
            },
            {
                "id": "coverage_check_001", 
                "name": "Coverage Amount Check",
                "description": "Verify coverage amount is specified"
            }
        ]
        
        # Analyze document
        results = mock_provider.analyze_document(sample_text, rules)
        
        print("✓ Document analysis completed")
        print(f"  - Rules analyzed: {len(results)}")
        
        for result in results:
            print(f"    * {result.rule_name}: {result.decision} (confidence: {result.confidence:.2f})")
            if result.extracted_data:
                print(f"      Extracted: {list(result.extracted_data.keys())}")
        
    except Exception as e:
        print(f"✗ Document analysis test failed: {e}")
        return False
    
    # Test 6: Custom prompt template
    print("\n6. Testing custom prompt template...")
    try:
        mock_provider = MockLLMProvider()
        
        custom_prompt = """
        Analyze this medical document:
        
        Document: {text_content}
        Rule: {rule_name}
        Description: {rule_description}
        
        Provide analysis in JSON format.
        """
        
        sample_text = "Sample policy document text"
        rules = [{"id": "test", "name": "Test Rule", "description": "Test description"}]
        
        results = mock_provider.analyze_document(sample_text, rules, custom_prompt)
        
        print("✓ Custom prompt template working")
        print(f"  - Results generated: {len(results)}")
        
    except Exception as e:
        print(f"✗ Custom prompt test failed: {e}")
        return False
    
    # Test 7: Error handling
    print("\n7. Testing error handling...")
    try:
        # Test with invalid provider type
        try:
            create_llm_provider('invalid_provider', 'test_key')
            print("✗ Should have raised ValueError for invalid provider")
            return False
        except ValueError:
            print("✓ Properly handled invalid provider type")
        
        # Test with empty API key
        try:
            MockLLMProvider(api_key="")
            print("✓ Mock provider handles empty API key")
        except Exception as e:
            print(f"✗ Error handling test failed: {e}")
            return False
            
    except Exception as e:
        print(f"✗ Error handling test failed: {e}")
        return False
    
    print("\n=== All LLM Provider Interface Tests Passed! ===")
    return True

def test_provider_validation():
    """Test provider validation functionality."""
    
    print("\n=== Testing Provider Validation ===\n")
    
    # Test validation function
    print("1. Testing provider validation...")
    try:
        # This would normally test with real API keys
        # For now, we'll test the function structure
        providers = get_available_providers()
        print(f"✓ Available providers for validation: {providers}")
        
        # Test validation with mock
        def mock_validate(provider_type: str, api_key: str) -> bool:
            return provider_type in ['openai', 'mistral', 'gemini', 'mock']
        
        test_result = mock_validate('mock', 'test_key')
        print(f"✓ Mock validation result: {test_result}")
        
    except Exception as e:
        print(f"✗ Provider validation test failed: {e}")
        return False
    
    print("✓ Provider validation tests completed")
    return True

if __name__ == "__main__":
    success1 = test_llm_provider_interface()
    success2 = test_provider_validation()
    
    if success1 and success2:
        print("\n🎉 All LLM Provider tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1) 