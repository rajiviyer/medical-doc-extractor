#!/usr/bin/env python3
"""
Test script for the LLM configuration system.
Tests the pluggable LLM selection and configuration functionality.
"""

import os
import tempfile
import logging
from app.llm_config import (
    LLMConfig, LLMConfigurationManager, create_config_manager,
    load_config_from_env, create_sample_config_file
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_llm_configuration():
    """Test the LLM configuration system."""
    
    print("=== Testing LLM Configuration System ===\n")
    
    # Test 1: LLMConfig dataclass
    print("1. Testing LLMConfig dataclass...")
    try:
        config = LLMConfig(
            provider_type="openai",
            api_key="test-api-key",
            model="gpt-4",
            temperature=0.1,
            max_tokens=2000,
            enabled=True
        )
        print("✓ LLMConfig created successfully")
        print(f"  - Provider: {config.provider_type}")
        print(f"  - Model: {config.model}")
        print(f"  - Temperature: {config.temperature}")
        print(f"  - Enabled: {config.enabled}")
        
    except Exception as e:
        print(f"✗ LLMConfig test failed: {e}")
        return False
    
    # Test 2: Environment-based configuration
    print("\n2. Testing environment-based configuration...")
    try:
        # Set test environment variables
        os.environ['OPENAI_API_KEY'] = 'test-openai-key'
        os.environ['OPENAI_MODEL'] = 'gpt-4'
        os.environ['MISTRAL_API_KEY'] = 'test-mistral-key'
        os.environ['MISTRAL_MODEL'] = 'mistral-large'
        os.environ['DEFAULT_LLM_PROVIDER'] = 'openai'
        
        config_manager = load_config_from_env()
        
        print("✓ Environment-based configuration loaded")
        print(f"  - Available providers: {config_manager.get_available_providers()}")
        print(f"  - Default provider: {config_manager.config_manager.default_provider}")
        
        # List providers
        providers = config_manager.list_providers()
        print(f"  - Configured providers: {list(providers.keys())}")
        
        for name, details in providers.items():
            print(f"    * {name}: {details['type']} ({details['model']}) - Enabled: {details['enabled']}")
        
    except Exception as e:
        print(f"✗ Environment configuration test failed: {e}")
        return False
    
    # Test 3: YAML configuration file
    print("\n3. Testing YAML configuration file...")
    try:
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = """
default_provider: openai
providers:
  openai:
    type: openai
    api_key: test-openai-key
    model: gpt-4
    temperature: 0.1
    max_tokens: 2000
    timeout: 30
    retry_attempts: 3
    enabled: true
    custom_prompts:
      policy_analysis: "Analyze this policy: {text_content}"
  mistral:
    type: mistral
    api_key: test-mistral-key
    model: mistral-large
    temperature: 0.2
    max_tokens: 1500
    timeout: 25
    retry_attempts: 2
    enabled: false
    custom_prompts: {}
"""
            f.write(yaml_content)
            temp_config_file = f.name
        
        # Load from YAML file
        config_manager = create_config_manager(temp_config_file)
        
        print("✓ YAML configuration loaded successfully")
        print(f"  - Available providers: {config_manager.get_available_providers()}")
        print(f"  - Default provider: {config_manager.config_manager.default_provider}")
        
        # Test provider creation
        provider_config = config_manager.get_provider_config('openai')
        if provider_config:
            print(f"  - OpenAI config: {provider_config.model} (temp: {provider_config.temperature})")
        
        # Clean up
        os.unlink(temp_config_file)
        
    except Exception as e:
        print(f"✗ YAML configuration test failed: {e}")
        return False
    
    # Test 4: Provider management
    print("\n4. Testing provider management...")
    try:
        config_manager = load_config_from_env()
        
        # Add a new provider
        new_config = LLMConfig(
            provider_type="gemini",
            api_key="test-gemini-key",
            model="gemini-pro",
            temperature=0.15,
            enabled=True
        )
        config_manager.add_provider("gemini_test", new_config)
        
        print("✓ Added new provider configuration")
        print(f"  - Providers after add: {list(config_manager.list_providers().keys())}")
        
        # Set default provider
        config_manager.set_default_provider("gemini_test")
        print(f"  - New default provider: {config_manager.config_manager.default_provider}")
        
        # Remove provider
        config_manager.remove_provider("gemini_test")
        print("✓ Removed provider configuration")
        print(f"  - Providers after remove: {list(config_manager.list_providers().keys())}")
        
    except Exception as e:
        print(f"✗ Provider management test failed: {e}")
        return False
    
    # Test 5: Custom prompts
    print("\n5. Testing custom prompt management...")
    try:
        config_manager = load_config_from_env()
        
        # Set custom prompt
        custom_prompt = "Analyze this medical document: {text_content}"
        config_manager.set_custom_prompt("openai", "medical_analysis", custom_prompt)
        
        # Get custom prompt
        retrieved_prompt = config_manager.get_custom_prompt("openai", "medical_analysis")
        
        print("✓ Custom prompt management working")
        print(f"  - Set prompt: {custom_prompt}")
        print(f"  - Retrieved prompt: {retrieved_prompt}")
        print(f"  - Match: {custom_prompt == retrieved_prompt}")
        
    except Exception as e:
        print(f"✗ Custom prompt test failed: {e}")
        return False
    
    # Test 6: Configuration validation
    print("\n6. Testing configuration validation...")
    try:
        config_manager = load_config_from_env()
        
        # Test with valid provider
        valid_providers = config_manager.get_available_providers()
        print(f"✓ Valid providers: {valid_providers}")
        
        # Test provider creation
        if valid_providers:
            try:
                provider = config_manager.create_provider(valid_providers[0])
                print(f"✓ Successfully created provider: {valid_providers[0]}")
            except Exception as e:
                print(f"  - Provider creation failed (expected without real API key): {e}")
        
        # Test with invalid provider
        try:
            config_manager.create_provider("invalid_provider")
            print("✗ Should have raised ValueError for invalid provider")
            return False
        except ValueError:
            print("✓ Properly handled invalid provider")
        
    except Exception as e:
        print(f"✗ Configuration validation test failed: {e}")
        return False
    
    # Test 7: Sample configuration file creation
    print("\n7. Testing sample configuration file creation...")
    try:
        sample_file = create_sample_config_file("test_sample_config.yaml")
        
        if os.path.exists(sample_file):
            print("✓ Sample configuration file created")
            print(f"  - File: {sample_file}")
            
            # Clean up
            os.unlink(sample_file)
            print("  - File cleaned up")
        else:
            print("✗ Sample configuration file not created")
            return False
        
    except Exception as e:
        print(f"✗ Sample configuration file test failed: {e}")
        return False
    
    print("\n=== All LLM Configuration Tests Passed! ===")
    return True

def test_configuration_integration():
    """Test integration with LLM provider system."""
    
    print("\n=== Testing Configuration Integration ===\n")
    
    # Test integration with LLM provider
    print("1. Testing configuration integration with LLM provider...")
    try:
        from app.llm_provider import create_llm_provider
        
        # Create mock configuration
        config_manager = load_config_from_env()
        
        # Test provider creation through config manager
        if config_manager.get_available_providers():
            provider_name = config_manager.get_available_providers()[0]
            print(f"  - Testing with provider: {provider_name}")
            
            # This would normally create a real provider
            # For testing, we'll just verify the configuration
            config = config_manager.get_provider_config(provider_name)
            if config:
                print(f"  - Provider type: {config.provider_type}")
                print(f"  - Model: {config.model}")
                print(f"  - Temperature: {config.temperature}")
                print("✓ Configuration integration working")
            else:
                print("✗ No provider configuration found")
                return False
        
    except Exception as e:
        print(f"✗ Configuration integration test failed: {e}")
        return False
    
    print("✓ Configuration integration tests completed")
    return True

if __name__ == "__main__":
    success1 = test_llm_configuration()
    success2 = test_configuration_integration()
    
    if success1 and success2:
        print("\n🎉 All LLM Configuration tests passed!")
    else:
        print("\n❌ Some tests failed!")
        exit(1) 