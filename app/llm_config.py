"""
Pluggable LLM Configuration System

This module provides a flexible configuration system for managing multiple LLM providers,
allowing easy switching between providers and managing their settings.
"""

import os
import logging
from typing import List, Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Available LLM providers."""
    OPENAI = "openai"
    MISTRAL = "mistral"
    GEMINI = "gemini"

class LLMConfig:
    """Configuration for LLM providers and selection."""
    
    def __init__(self):
        self.enabled_providers = self._get_enabled_providers()
        self.provider_settings = self._get_provider_settings()
        logger.info(f"LLM Configuration initialized. Enabled providers: {self.enabled_providers}")
    
    def _get_enabled_providers(self) -> List[LLMProvider]:
        """Get list of enabled LLM providers from environment variables."""
        enabled = []
        
        # Check environment variables for each provider
        if os.getenv('ENABLE_OPENAI', 'true').lower() == 'true':
            enabled.append(LLMProvider.OPENAI)
        
        if os.getenv('ENABLE_MISTRAL', 'true').lower() == 'true':
            enabled.append(LLMProvider.MISTRAL)
        
        if os.getenv('ENABLE_GEMINI', 'true').lower() == 'true':
            enabled.append(LLMProvider.GEMINI)
        
        # If no providers are explicitly enabled, enable all by default
        if not enabled:
            logger.warning("No LLM providers explicitly enabled. Enabling all providers by default.")
            enabled = [LLMProvider.OPENAI, LLMProvider.MISTRAL, LLMProvider.GEMINI]
        
        return enabled
    
    def _get_provider_settings(self) -> Dict[str, Any]:
        """Get settings for each provider."""
        return {
            LLMProvider.OPENAI.value: {
                'api_key': os.getenv('OPENAI_API_KEY'),
                'model': os.getenv('OPENAI_MODEL', 'gpt-4'),
                'temperature': float(os.getenv('OPENAI_TEMPERATURE', '0.1')),
                'max_tokens': int(os.getenv('OPENAI_MAX_TOKENS', '4000'))
            },
            LLMProvider.MISTRAL.value: {
                'api_key': os.getenv('MISTRAL_API_KEY'),
                'model': os.getenv('MISTRAL_MODEL', 'mistral-large-latest'),
                'temperature': float(os.getenv('MISTRAL_TEMPERATURE', '0.1')),
                'max_tokens': int(os.getenv('MISTRAL_MAX_TOKENS', '4000'))
            },
            LLMProvider.GEMINI.value: {
                'api_key': os.getenv('GEMINI_API_KEY'),
                'model': os.getenv('GEMINI_MODEL', 'gemini-1.5-pro'),
                'temperature': float(os.getenv('GEMINI_TEMPERATURE', '0.1')),
                'max_tokens': int(os.getenv('GEMINI_MAX_TOKENS', '4000'))
            }
        }
    
    def is_provider_enabled(self, provider: LLMProvider) -> bool:
        """Check if a specific provider is enabled."""
        return provider in self.enabled_providers
    
    def get_enabled_providers(self) -> List[LLMProvider]:
        """Get list of enabled providers."""
        return self.enabled_providers.copy()
    
    def get_provider_settings(self, provider: LLMProvider) -> Dict[str, Any]:
        """Get settings for a specific provider."""
        return self.provider_settings.get(provider.value, {})
    
    def validate_configuration(self) -> bool:
        """Validate that all enabled providers have required API keys."""
        for provider in self.enabled_providers:
            settings = self.get_provider_settings(provider)
            api_key = settings.get('api_key')
            
            if not api_key:
                logger.error(f"API key missing for {provider.value}")
                return False
            
            logger.info(f"✓ {provider.value} configured with API key")
        
        return True
    
    def get_provider_names(self) -> List[str]:
        """Get list of enabled provider names as strings."""
        return [provider.value for provider in self.enabled_providers]
    
    def print_configuration(self):
        """Print current LLM configuration."""
        print("\n🤖 LLM Configuration:")
        print("=" * 50)
        
        for provider in self.enabled_providers:
            settings = self.get_provider_settings(provider)
            status = "✅ Enabled" if provider in self.enabled_providers else "❌ Disabled"
            api_key_status = "✅ Configured" if settings.get('api_key') else "❌ Missing API Key"
            
            print(f"  {provider.value.upper()}: {status}")
            print(f"    Model: {settings.get('model', 'N/A')}")
            print(f"    API Key: {api_key_status}")
            print(f"    Temperature: {settings.get('temperature', 'N/A')}")
            print()
        
        print(f"Total Enabled Providers: {len(self.enabled_providers)}")
        print("=" * 50)

# Global configuration instance
llm_config = LLMConfig()

def get_enabled_llm_providers() -> List[LLMProvider]:
    """Get list of enabled LLM providers."""
    return llm_config.get_enabled_providers()

def is_llm_enabled(provider: str) -> bool:
    """Check if a specific LLM provider is enabled."""
    try:
        provider_enum = LLMProvider(provider.lower())
        return llm_config.is_provider_enabled(provider_enum)
    except ValueError:
        logger.warning(f"Unknown LLM provider: {provider}")
        return False

def get_llm_settings(provider: str) -> Dict[str, Any]:
    """Get settings for a specific LLM provider."""
    try:
        provider_enum = LLMProvider(provider.lower())
        return llm_config.get_provider_settings(provider_enum)
    except ValueError:
        logger.warning(f"Unknown LLM provider: {provider}")
        return {}

def validate_llm_configuration() -> bool:
    """Validate LLM configuration."""
    return llm_config.validate_configuration()

def print_llm_configuration():
    """Print current LLM configuration."""
    llm_config.print_configuration() 