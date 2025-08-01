#!/usr/bin/env python3
"""
Test script for the custom prompt system.
Tests prompt templates, generation, and integration with LLM configuration.
"""

import os
import tempfile
import json
import logging
from app.prompt_system import (
    PromptManager, PromptSystem, PromptType, ProviderType,
    PromptTemplate, PromptContext, GeneratedPrompt,
    create_prompt_system, create_prompt_manager
)
from app.llm_config import load_config_from_env

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_prompt_manager():
    """Test the prompt manager functionality."""
    
    print("=== Testing Prompt Manager ===\n")
    
    # Test 1: Basic prompt manager initialization
    print("1. Testing prompt manager initialization...")
    try:
        prompt_manager = create_prompt_manager()
        print("✓ Prompt manager created successfully")
        
        # Check default templates
        templates = prompt_manager.list_templates()
        print(f"  - Default templates loaded: {len(templates)}")
        
        for template in templates:
            print(f"    * {template.name} ({template.provider.value}) - {template.prompt_type.value}")
        
    except Exception as e:
        print(f"✗ Prompt manager initialization failed: {e}")
        return False
    
    # Test 2: Template management
    print("\n2. Testing template management...")
    try:
        # Create custom template
        custom_template = prompt_manager.create_custom_template(
            name="test_custom",
            prompt_type=PromptType.CUSTOM,
            provider=ProviderType.OPENAI,
            template="Analyze this document: {text_content}",
            variables=["text_content"],
            description="Test custom template"
        )
        print("✓ Custom template created")
        print(f"  - Template name: {custom_template.name}")
        print(f"  - Provider: {custom_template.provider.value}")
        print(f"  - Type: {custom_template.prompt_type.value}")
        
        # List templates for OpenAI
        openai_templates = prompt_manager.list_templates("openai")
        print(f"  - OpenAI templates: {len(openai_templates)}")
        
        # Get specific template
        template = prompt_manager.get_template("test_custom", "openai")
        if template:
            print("✓ Template retrieval working")
        
        # Update template
        success = prompt_manager.update_template("test_custom", "openai", description="Updated description")
        if success:
            print("✓ Template update working")
        
        # Delete template
        success = prompt_manager.delete_template("test_custom", "openai")
        if success:
            print("✓ Template deletion working")
        
    except Exception as e:
        print(f"✗ Template management test failed: {e}")
        return False
    
    # Test 3: Prompt generation
    print("\n3. Testing prompt generation...")
    try:
        # Create test context
        context = PromptContext(
            text_content="This is a test medical document about patient John Doe.",
            document_type="medical_report",
            metadata={"patient_id": "12345", "date": "2024-01-15"}
        )
        
        # Generate prompt
        generated_prompt = prompt_manager.generate_prompt(
            "medical_document_analysis_openai",
            "openai",
            context
        )
        
        print("✓ Prompt generation successful")
        print(f"  - Template: {generated_prompt.template_name}")
        print(f"  - Provider: {generated_prompt.provider}")
        print(f"  - Type: {generated_prompt.prompt_type}")
        print(f"  - Generation time: {generated_prompt.generation_time:.4f}s")
        print(f"  - Variables used: {list(generated_prompt.variables_used.keys())}")
        
        # Check if text_content was replaced
        if "This is a test medical document" in generated_prompt.final_prompt:
            print("✓ Variable substitution working")
        else:
            print("✗ Variable substitution failed")
            return False
        
    except Exception as e:
        print(f"✗ Prompt generation test failed: {e}")
        return False
    
    # Test 4: Rule checking prompt
    print("\n4. Testing rule checking prompt...")
    try:
        rules = [
            {"rule_id": "R001", "description": "Document must contain patient name"},
            {"rule_id": "R002", "description": "Document must contain diagnosis"}
        ]
        
        context = PromptContext(
            text_content="Patient John Doe diagnosed with diabetes.",
            rules=rules
        )
        
        generated_prompt = prompt_manager.generate_prompt(
            "rule_checking_openai",
            "openai",
            context
        )
        
        print("✓ Rule checking prompt generated")
        print(f"  - Rules included: {len(rules)}")
        print(f"  - Prompt length: {len(generated_prompt.final_prompt)} chars")
        
    except Exception as e:
        print(f"✗ Rule checking test failed: {e}")
        return False
    
    # Test 5: Template export/import
    print("\n5. Testing template export/import...")
    try:
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_file = f.name
        
        # Export templates
        prompt_manager.export_templates(temp_file)
        print("✓ Templates exported successfully")
        
        # Create new manager and import
        new_manager = create_prompt_manager()
        new_manager.import_templates(temp_file)
        print("✓ Templates imported successfully")
        
        # Verify import
        imported_templates = new_manager.list_templates()
        print(f"  - Imported templates: {len(imported_templates)}")
        
        # Clean up
        os.unlink(temp_file)
        print("  - Temporary file cleaned up")
        
    except Exception as e:
        print(f"✗ Export/import test failed: {e}")
        return False
    
    print("\n=== All Prompt Manager Tests Passed! ===")
    return True

def test_prompt_system():
    """Test the high-level prompt system."""
    
    print("\n=== Testing Prompt System ===\n")
    
    # Test 1: Prompt system initialization
    print("1. Testing prompt system initialization...")
    try:
        # Create config manager
        config_manager = load_config_from_env()
        
        # Create prompt system
        prompt_system = create_prompt_system(config_manager)
        print("✓ Prompt system created successfully")
        
    except Exception as e:
        print(f"✗ Prompt system initialization failed: {e}")
        return False
    
    # Test 2: Document analysis
    print("\n2. Testing document analysis...")
    try:
        text_content = "Patient Jane Smith, age 45, diagnosed with hypertension. Prescribed medication: Lisinopril 10mg daily."
        
        generated_prompt = prompt_system.analyze_document(
            text_content=text_content,
            prompt_type=PromptType.MEDICAL_DOCUMENT_ANALYSIS,
            provider="openai"
        )
        
        print("✓ Document analysis prompt generated")
        print(f"  - Template: {generated_prompt.template_name}")
        print(f"  - Provider: {generated_prompt.provider}")
        print(f"  - Prompt type: {generated_prompt.prompt_type}")
        
    except Exception as e:
        print(f"✗ Document analysis test failed: {e}")
        return False
    
    # Test 3: Rule checking
    print("\n3. Testing rule checking...")
    try:
        rules = [
            {"rule_id": "MED001", "description": "Document must contain patient information"},
            {"rule_id": "MED002", "description": "Document must contain diagnosis"},
            {"rule_id": "MED003", "description": "Document must contain treatment plan"}
        ]
        
        text_content = "Patient: John Doe, Diagnosis: Diabetes, Treatment: Insulin therapy"
        
        generated_prompt = prompt_system.check_rules(
            text_content=text_content,
            rules=rules,
            provider="openai"
        )
        
        print("✓ Rule checking prompt generated")
        print(f"  - Rules: {len(rules)}")
        print(f"  - Provider: {generated_prompt.provider}")
        
    except Exception as e:
        print(f"✗ Rule checking test failed: {e}")
        return False
    
    # Test 4: Available prompts
    print("\n4. Testing available prompts...")
    try:
        available_prompts = prompt_system.get_available_prompts("openai")
        
        print("✓ Available prompts retrieved")
        print(f"  - Prompt types: {list(available_prompts.keys())}")
        
        for prompt_type, templates in available_prompts.items():
            print(f"    * {prompt_type}: {len(templates)} templates")
        
    except Exception as e:
        print(f"✗ Available prompts test failed: {e}")
        return False
    
    print("\n=== All Prompt System Tests Passed! ===")
    return True

def test_prompt_integration():
    """Test integration with LLM configuration."""
    
    print("\n=== Testing Prompt Integration ===\n")
    
    # Test 1: Integration with configuration
    print("1. Testing configuration integration...")
    try:
        config_manager = load_config_from_env()
        prompt_system = create_prompt_system(config_manager)
        
        print("✓ Configuration integration working")
        print(f"  - Default provider: {config_manager.config_manager.default_provider}")
        
        # Test with default provider
        text_content = "Test document content"
        generated_prompt = prompt_system.analyze_document(
            text_content=text_content,
            prompt_type=PromptType.TEXT_SUMMARIZATION
        )
        
        print("✓ Default provider prompt generation working")
        print(f"  - Generated for provider: {generated_prompt.provider}")
        
    except Exception as e:
        print(f"✗ Configuration integration test failed: {e}")
        return False
    
    # Test 2: Custom prompt creation
    print("\n2. Testing custom prompt creation...")
    try:
        prompt_manager = create_prompt_manager()
        
        # Create a custom medical analysis prompt
        custom_template = prompt_manager.create_custom_template(
            name="custom_medical_analysis",
            prompt_type=PromptType.MEDICAL_DOCUMENT_ANALYSIS,
            provider=ProviderType.OPENAI,
            template="""Analyze this medical document and extract key information:

Document: {text_content}
Patient ID: {patient_id}
Date: {date}

Please provide:
1. Patient demographics
2. Primary diagnosis
3. Treatment plan
4. Medications prescribed
5. Follow-up recommendations

Format as JSON.""",
            variables=["text_content", "patient_id", "date"],
            description="Custom medical analysis template"
        )
        
        print("✓ Custom template created")
        print(f"  - Name: {custom_template.name}")
        print(f"  - Variables: {custom_template.variables}")
        
        # Test custom template
        context = PromptContext(
            text_content="Patient has diabetes and hypertension",
            custom_variables={
                "patient_id": "P12345",
                "date": "2024-01-15"
            }
        )
        
        generated_prompt = prompt_manager.generate_prompt(
            "custom_medical_analysis",
            "openai",
            context
        )
        
        print("✓ Custom template generation working")
        print(f"  - Final prompt length: {len(generated_prompt.final_prompt)} chars")
        
    except Exception as e:
        print(f"✗ Custom prompt creation test failed: {e}")
        return False
    
    print("\n=== All Integration Tests Passed! ===")
    return True

if __name__ == "__main__":
    success1 = test_prompt_manager()
    success2 = test_prompt_system()
    success3 = test_prompt_integration()
    
    if success1 and success2 and success3:
        print("\n🎉 All Prompt System tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1) 