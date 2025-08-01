"""
Modular LLM Provider Interface for Medical Document Extractor

This module provides a flexible interface for integrating multiple LLM providers
(OpenAI, Mistral, Gemini) with a common API for rule-based document analysis.
"""

import os
import logging
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)

@dataclass
class LLMResponse:
    """Represents a response from an LLM provider."""
    provider: str
    model: str
    content: str
    confidence: float
    processing_time: float
    tokens_used: Optional[int] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class RuleAnalysisResult:
    """Represents the result of rule-based analysis."""
    rule_id: str
    rule_name: str
    rule_description: str
    decision: str  # PASS, FAIL, WARNING
    confidence: float
    extracted_data: Dict[str, Any]
    additional_info: Dict[str, Any]
    recommendations: List[str]
    processing_time: float
    llm_provider: str
    llm_model: str
    
    def __post_init__(self):
        if self.extracted_data is None:
            self.extracted_data = {}
        if self.additional_info is None:
            self.additional_info = {}
        if self.recommendations is None:
            self.recommendations = []

class LLMProvider(ABC):
    """
    Abstract base class for LLM providers.
    
    This defines the common interface that all LLM providers must implement.
    """
    
    def __init__(self, api_key: str, model: str, **kwargs):
        """
        Initialize the LLM provider.
        
        Args:
            api_key: API key for the provider
            model: Model name to use
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.model = model
        self.config = kwargs
        self._validate_config()
    
    @abstractmethod
    def _validate_config(self):
        """Validate provider-specific configuration."""
        pass
    
    @abstractmethod
    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        """
        Make a request to the LLM provider.
        
        Args:
            prompt: The prompt to send to the LLM
            **kwargs: Additional request parameters
            
        Returns:
            LLMResponse with the provider's response
        """
        pass
    
    def analyze_document(self, 
                        text_content: str,
                        rules: List[Dict[str, Any]],
                        custom_prompt: Optional[str] = None) -> List[RuleAnalysisResult]:
        """
        Analyze document text against specified rules.
        
        Args:
            text_content: The extracted text content to analyze
            rules: List of rules to check against
            custom_prompt: Optional custom prompt template
            
        Returns:
            List of RuleAnalysisResult objects
        """
        results = []
        
        for rule in rules:
            try:
                start_time = time.time()
                
                # Create prompt for this rule
                prompt = self._create_rule_prompt(text_content, rule, custom_prompt)
                
                # Make request to LLM
                response = self._make_request(prompt)
                
                # Parse response into rule result
                rule_result = self._parse_rule_response(response, rule)
                rule_result.processing_time = time.time() - start_time
                
                results.append(rule_result)
                
                logger.info(f"Rule '{rule['name']}' analysis completed: {rule_result.decision}")
                
            except Exception as e:
                logger.error(f"Error analyzing rule '{rule.get('name', 'unknown')}': {e}")
                # Create error result
                error_result = RuleAnalysisResult(
                    rule_id=rule.get('id', 'unknown'),
                    rule_name=rule.get('name', 'Unknown Rule'),
                    rule_description=rule.get('description', ''),
                    decision='FAIL',
                    confidence=0.0,
                    extracted_data={},
                    additional_info={'error': str(e)},
                    recommendations=['Check rule configuration and LLM provider'],
                    processing_time=0.0,
                    llm_provider=self.__class__.__name__,
                    llm_model=self.model
                )
                results.append(error_result)
        
        return results
    
    def _create_rule_prompt(self, 
                           text_content: str, 
                           rule: Dict[str, Any],
                           custom_prompt: Optional[str] = None) -> str:
        """
        Create a prompt for rule analysis.
        
        Args:
            text_content: Document text content
            rule: Rule definition
            custom_prompt: Optional custom prompt template
            
        Returns:
            Formatted prompt string
        """
        if custom_prompt:
            # Use custom prompt template
            return custom_prompt.format(
                text_content=text_content,
                rule_name=rule.get('name', ''),
                rule_description=rule.get('description', ''),
                rule_id=rule.get('id', '')
            )
        
        # Default prompt template
        return f"""
You are a medical document analyst. Analyze the following document text according to this rule:

Rule ID: {rule.get('id', 'unknown')}
Rule Name: {rule.get('name', 'Unknown Rule')}
Rule Description: {rule.get('description', '')}

Document Text:
{text_content}

Please analyze the document and provide your response in the following JSON format:
{{
    "decision": "PASS|FAIL|WARNING",
    "confidence": 0.0-1.0,
    "extracted_data": {{}},
    "additional_info": {{}},
    "recommendations": []
}}

Focus on the specific rule requirements and provide detailed analysis.
"""
    
    def _parse_rule_response(self, response: LLMResponse, rule: Dict[str, Any]) -> RuleAnalysisResult:
        """
        Parse LLM response into a structured rule analysis result.
        
        Args:
            response: LLM response
            rule: Original rule definition
            
        Returns:
            RuleAnalysisResult object
        """
        try:
            # Try to parse JSON response
            if response.content.strip().startswith('{'):
                parsed = json.loads(response.content)
            else:
                # Fallback: try to extract JSON from text
                import re
                json_match = re.search(r'\{.*\}', response.content, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    raise ValueError("No valid JSON found in response")
            
            return RuleAnalysisResult(
                rule_id=rule.get('id', 'unknown'),
                rule_name=rule.get('name', 'Unknown Rule'),
                rule_description=rule.get('description', ''),
                decision=parsed.get('decision', 'FAIL'),
                confidence=parsed.get('confidence', 0.0),
                extracted_data=parsed.get('extracted_data', {}),
                additional_info=parsed.get('additional_info', {}),
                recommendations=parsed.get('recommendations', []),
                processing_time=response.processing_time,
                llm_provider=response.provider,
                llm_model=response.model
            )
            
        except Exception as e:
            logger.error(f"Error parsing LLM response: {e}")
            # Return error result
            return RuleAnalysisResult(
                rule_id=rule.get('id', 'unknown'),
                rule_name=rule.get('name', 'Unknown Rule'),
                rule_description=rule.get('description', ''),
                decision='FAIL',
                confidence=0.0,
                extracted_data={},
                additional_info={'parsing_error': str(e), 'raw_response': response.content},
                recommendations=['Check LLM response format'],
                processing_time=response.processing_time,
                llm_provider=response.provider,
                llm_model=response.model
            )

class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            import openai
            self.client = openai.OpenAI(api_key=api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Run: pip install openai")
    
    def _validate_config(self):
        """Validate OpenAI configuration."""
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        if not self.model:
            raise ValueError("OpenAI model name is required")
    
    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        """Make request to OpenAI API."""
        start_time = time.time()
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=kwargs.get('temperature', 0.1),
                max_tokens=kwargs.get('max_tokens', 2000),
                **kwargs
            )
            
            content = response.choices[0].message.content
            processing_time = time.time() - start_time
            
            return LLMResponse(
                provider="OpenAI",
                model=self.model,
                content=content,
                confidence=1.0,  # OpenAI doesn't provide confidence scores
                processing_time=processing_time,
                tokens_used=response.usage.total_tokens if response.usage else None,
                metadata={'finish_reason': response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return LLMResponse(
                provider="OpenAI",
                model=self.model,
                content="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

class MistralProvider(LLMProvider):
    """Mistral AI provider implementation."""
    
    def __init__(self, api_key: str, model: str = "mistral-large", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            from mistralai.client import MistralClient
            from mistralai.models.chat_completion import ChatMessage
            self.client = MistralClient(api_key=api_key)
            self.ChatMessage = ChatMessage
        except ImportError:
            raise ImportError("Mistral AI package not installed. Run: pip install mistralai")
    
    def _validate_config(self):
        """Validate Mistral configuration."""
        if not self.api_key:
            raise ValueError("Mistral API key is required")
        if not self.model:
            raise ValueError("Mistral model name is required")
    
    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        """Make request to Mistral API."""
        start_time = time.time()
        
        try:
            response = self.client.chat(
                model=self.model,
                messages=[self.ChatMessage(role="user", content=prompt)],
                temperature=kwargs.get('temperature', 0.1),
                max_tokens=kwargs.get('max_tokens', 2000),
                **kwargs
            )
            
            content = response.choices[0].message.content
            processing_time = time.time() - start_time
            
            return LLMResponse(
                provider="Mistral",
                model=self.model,
                content=content,
                confidence=1.0,  # Mistral doesn't provide confidence scores
                processing_time=processing_time,
                metadata={'finish_reason': response.choices[0].finish_reason}
            )
            
        except Exception as e:
            logger.error(f"Mistral API error: {e}")
            return LLMResponse(
                provider="Mistral",
                model=self.model,
                content="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

class GeminiProvider(LLMProvider):
    """Google Gemini provider implementation."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro", **kwargs):
        super().__init__(api_key, model, **kwargs)
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(model)
        except ImportError:
            raise ImportError("Google Generative AI package not installed. Run: pip install google-generativeai")
    
    def _validate_config(self):
        """Validate Gemini configuration."""
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        if not self.model:
            raise ValueError("Gemini model name is required")
    
    def _make_request(self, prompt: str, **kwargs) -> LLMResponse:
        """Make request to Gemini API."""
        start_time = time.time()
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=kwargs.get('generation_config', None),
                **kwargs
            )
            
            content = response.text
            processing_time = time.time() - start_time
            
            return LLMResponse(
                provider="Gemini",
                model=self.model.model_name,
                content=content,
                confidence=1.0,  # Gemini doesn't provide confidence scores
                processing_time=processing_time,
                metadata={'candidates': len(response.candidates) if response.candidates else 0}
            )
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return LLMResponse(
                provider="Gemini",
                model=self.model.model_name,
                content="",
                confidence=0.0,
                processing_time=time.time() - start_time,
                error_message=str(e)
            )

# Factory function for creating LLM providers
def create_llm_provider(provider_type: str, api_key: str, model: str = None, **kwargs) -> LLMProvider:
    """
    Factory function to create LLM provider instances.
    
    Args:
        provider_type: Type of provider ('openai', 'mistral', 'gemini')
        api_key: API key for the provider
        model: Model name (optional, uses defaults)
        **kwargs: Additional provider-specific configuration
        
    Returns:
        LLMProvider instance
    """
    provider_type = provider_type.lower()
    
    if provider_type == 'openai':
        return OpenAIProvider(api_key, model or "gpt-4", **kwargs)
    elif provider_type == 'mistral':
        return MistralProvider(api_key, model or "mistral-large", **kwargs)
    elif provider_type == 'gemini':
        return GeminiProvider(api_key, model or "gemini-pro", **kwargs)
    else:
        raise ValueError(f"Unsupported provider type: {provider_type}")

# Utility functions for common LLM operations
def get_available_providers() -> List[str]:
    """Get list of available LLM providers."""
    return ['openai', 'mistral', 'gemini']

def validate_provider_config(provider_type: str, api_key: str) -> bool:
    """
    Validate provider configuration.
    
    Args:
        provider_type: Type of provider
        api_key: API key to validate
        
    Returns:
        True if configuration is valid
    """
    try:
        provider = create_llm_provider(provider_type, api_key)
        # Test with a simple prompt
        response = provider._make_request("Hello, this is a test.")
        return response.error_message is None
    except Exception as e:
        logger.error(f"Provider validation failed: {e}")
        return False 