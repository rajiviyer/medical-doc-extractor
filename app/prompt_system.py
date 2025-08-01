"""
Custom Prompt System for LLM Providers

This module provides a flexible prompt system that supports:
- Custom prompts for different LLM providers (OpenAI, Mistral, Gemini)
- Use case specific prompts (medical document analysis, policy review, etc.)
- Template-based prompt generation with variable substitution
- Prompt versioning and management
- Integration with the configuration system
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from app.llm_config import LLMConfigurationManager

logger = logging.getLogger(__name__)

class PromptType(Enum):
    """Types of prompts supported by the system."""
    MEDICAL_DOCUMENT_ANALYSIS = "medical_document_analysis"
    POLICY_REVIEW = "policy_review"
    RULE_CHECKING = "rule_checking"
    TEXT_SUMMARIZATION = "text_summarization"
    ENTITY_EXTRACTION = "entity_extraction"
    CLASSIFICATION = "classification"
    CUSTOM = "custom"

class ProviderType(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    MISTRAL = "mistral"
    GEMINI = "gemini"

@dataclass
class PromptTemplate:
    """Template for a custom prompt."""
    name: str
    prompt_type: PromptType
    provider: ProviderType
    template: str
    variables: List[str]
    description: str
    version: str = "1.0"
    created_at: str = None
    updated_at: str = None
    is_active: bool = True
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at

@dataclass
class PromptContext:
    """Context for prompt generation."""
    text_content: str
    document_type: Optional[str] = None
    rules: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    custom_variables: Optional[Dict[str, Any]] = None

@dataclass
class GeneratedPrompt:
    """Generated prompt with metadata."""
    template_name: str
    provider: str
    prompt_type: str
    final_prompt: str
    variables_used: Dict[str, Any]
    generation_time: float
    version: str

class PromptManager:
    """
    Manages custom prompts for different LLM providers and use cases.
    """
    
    def __init__(self, config_manager: Optional[LLMConfigurationManager] = None):
        """
        Initialize the prompt manager.
        
        Args:
            config_manager: LLM configuration manager for provider integration
        """
        self.config_manager = config_manager
        self.templates: Dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default prompt templates for common use cases."""
        
        # Medical Document Analysis Templates
        self.add_template(PromptTemplate(
            name="medical_document_analysis_openai",
            prompt_type=PromptType.MEDICAL_DOCUMENT_ANALYSIS,
            provider=ProviderType.OPENAI,
            template="""You are a medical document analysis expert. Analyze the following medical document and extract key information.

Document Content:
{text_content}

Please provide:
1. Document type and classification
2. Key medical entities (patient info, diagnoses, treatments, medications)
3. Important dates and timelines
4. Any critical findings or recommendations
5. Confidence level in your analysis

Format your response as JSON with the following structure:
{{
    "document_type": "string",
    "entities": {{
        "patient_info": {{}},
        "diagnoses": [],
        "treatments": [],
        "medications": []
    }},
    "timeline": {{
        "dates": [],
        "events": []
    }},
    "findings": [],
    "confidence": "high|medium|low"
}}""",
            variables=["text_content"],
            description="OpenAI template for medical document analysis"
        ))
        
        self.add_template(PromptTemplate(
            name="medical_document_analysis_mistral",
            prompt_type=PromptType.MEDICAL_DOCUMENT_ANALYSIS,
            provider=ProviderType.MISTRAL,
            template="""<s>[INST] You are a medical document analysis expert. Analyze the following medical document and extract key information.

Document Content:
{text_content}

Please provide:
1. Document type and classification
2. Key medical entities (patient info, diagnoses, treatments, medications)
3. Important dates and timelines
4. Any critical findings or recommendations
5. Confidence level in your analysis

Format your response as JSON with the following structure:
{{
    "document_type": "string",
    "entities": {{
        "patient_info": {{}},
        "diagnoses": [],
        "treatments": [],
        "medications": []
    }},
    "timeline": {{
        "dates": [],
        "events": []
    }},
    "findings": [],
    "confidence": "high|medium|low"
}} [/INST]""",
            variables=["text_content"],
            description="Mistral template for medical document analysis"
        ))
        
        # Policy Review Templates
        self.add_template(PromptTemplate(
            name="policy_review_openai",
            prompt_type=PromptType.POLICY_REVIEW,
            provider=ProviderType.OPENAI,
            template="""You are a policy review expert. Analyze the following policy document and provide a comprehensive review.

Policy Content:
{text_content}

Please provide:
1. Policy type and scope
2. Key terms and conditions
3. Coverage details and limitations
4. Important dates and deadlines
5. Compliance requirements
6. Risk assessment

Format your response as JSON with the following structure:
{{
    "policy_type": "string",
    "scope": "string",
    "terms_conditions": [],
    "coverage": {{
        "included": [],
        "excluded": [],
        "limitations": []
    }},
    "timeline": {{
        "effective_date": "string",
        "expiry_date": "string",
        "deadlines": []
    }},
    "compliance": [],
    "risk_assessment": "low|medium|high"
}}""",
            variables=["text_content"],
            description="OpenAI template for policy review"
        ))
        
        # Rule Checking Templates
        self.add_template(PromptTemplate(
            name="rule_checking_openai",
            prompt_type=PromptType.RULE_CHECKING,
            provider=ProviderType.OPENAI,
            template="""You are a rule compliance expert. Check the following document against the specified rules.

Document Content:
{text_content}

Rules to Check:
{rules}

For each rule, provide:
1. Rule ID and description
2. Compliance status (compliant/non-compliant/uncertain)
3. Evidence from the document
4. Confidence level
5. Recommendations if non-compliant

Format your response as JSON with the following structure:
{{
    "rule_analysis": [
        {{
            "rule_id": "string",
            "rule_description": "string",
            "status": "compliant|non-compliant|uncertain",
            "evidence": "string",
            "confidence": "high|medium|low",
            "recommendations": []
        }}
    ],
    "overall_compliance": "compliant|non-compliant|partial",
    "critical_issues": []
}}""",
            variables=["text_content", "rules"],
            description="OpenAI template for rule checking"
        ))
        
        # Text Summarization Templates
        self.add_template(PromptTemplate(
            name="text_summarization_openai",
            prompt_type=PromptType.TEXT_SUMMARIZATION,
            provider=ProviderType.OPENAI,
            template="""Summarize the following document in a clear and concise manner.

Document Content:
{text_content}

Please provide:
1. Executive summary (2-3 sentences)
2. Key points (bullet points)
3. Important details
4. Action items (if any)

Format your response as JSON with the following structure:
{{
    "executive_summary": "string",
    "key_points": [],
    "important_details": [],
    "action_items": [],
    "summary_length": "short|medium|long"
}}""",
            variables=["text_content"],
            description="OpenAI template for text summarization"
        ))
        
        # Entity Extraction Templates
        self.add_template(PromptTemplate(
            name="entity_extraction_openai",
            prompt_type=PromptType.ENTITY_EXTRACTION,
            provider=ProviderType.OPENAI,
            template="""Extract specific entities from the following document.

Document Content:
{text_content}

Entity Types to Extract:
{entity_types}

Please extract and categorize all entities found in the document.

Format your response as JSON with the following structure:
{{
    "entities": {{
        "entity_type": [
            {{
                "text": "string",
                "confidence": "high|medium|low",
                "position": "string"
            }}
        ]
    }},
    "extraction_confidence": "high|medium|low"
}}""",
            variables=["text_content", "entity_types"],
            description="OpenAI template for entity extraction"
        ))
    
    def add_template(self, template: PromptTemplate):
        """Add a new prompt template."""
        template_key = f"{template.provider.value}_{template.name}"
        self.templates[template_key] = template
        logger.info(f"Added prompt template: {template_key}")
    
    def get_template(self, name: str, provider: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name and provider."""
        template_key = f"{provider}_{name}"
        return self.templates.get(template_key)
    
    def list_templates(self, provider: Optional[str] = None, prompt_type: Optional[PromptType] = None) -> List[PromptTemplate]:
        """List available templates with optional filtering."""
        templates = []
        
        for template in self.templates.values():
            if provider and template.provider.value != provider:
                continue
            if prompt_type and template.prompt_type != prompt_type:
                continue
            templates.append(template)
        
        return templates
    
    def generate_prompt(self, template_name: str, provider: str, context: PromptContext, 
                       custom_variables: Optional[Dict[str, Any]] = None) -> GeneratedPrompt:
        """
        Generate a prompt from a template with context.
        
        Args:
            template_name: Name of the template to use
            provider: LLM provider name
            context: Context for prompt generation
            custom_variables: Additional variables for template
            
        Returns:
            GeneratedPrompt object
        """
        import time
        start_time = time.time()
        
        # Get template
        template = self.get_template(template_name, provider)
        if not template:
            raise ValueError(f"Template not found: {template_name} for provider {provider}")
        
        # Prepare variables
        variables = {
            'text_content': context.text_content,
            'document_type': context.document_type or 'unknown',
            'metadata': context.metadata or {},
        }
        
        # Add custom variables
        if custom_variables:
            variables.update(custom_variables)
        
        # Add rules if present
        if context.rules:
            variables['rules'] = json.dumps(context.rules, indent=2)
        
        # Generate final prompt
        final_prompt = template.template
        
        # Replace variables in template
        for var_name, var_value in variables.items():
            placeholder = f"{{{var_name}}}"
            if placeholder in final_prompt:
                if isinstance(var_value, (dict, list)):
                    final_prompt = final_prompt.replace(placeholder, json.dumps(var_value, indent=2))
                else:
                    final_prompt = final_prompt.replace(placeholder, str(var_value))
        
        generation_time = time.time() - start_time
        
        return GeneratedPrompt(
            template_name=template_name,
            provider=provider,
            prompt_type=template.prompt_type.value,
            final_prompt=final_prompt,
            variables_used=variables,
            generation_time=generation_time,
            version=template.version
        )
    
    def create_custom_template(self, name: str, prompt_type: PromptType, provider: ProviderType,
                             template: str, variables: List[str], description: str) -> PromptTemplate:
        """Create a custom prompt template."""
        custom_template = PromptTemplate(
            name=name,
            prompt_type=prompt_type,
            provider=provider,
            template=template,
            variables=variables,
            description=description
        )
        
        self.add_template(custom_template)
        return custom_template
    
    def update_template(self, name: str, provider: str, **kwargs) -> bool:
        """Update an existing template."""
        template = self.get_template(name, provider)
        if not template:
            return False
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(template, field):
                setattr(template, field, value)
        
        template.updated_at = datetime.now().isoformat()
        return True
    
    def delete_template(self, name: str, provider: str) -> bool:
        """Delete a template."""
        template_key = f"{provider}_{name}"
        if template_key in self.templates:
            del self.templates[template_key]
            logger.info(f"Deleted template: {template_key}")
            return True
        return False
    
    def export_templates(self, file_path: str):
        """Export templates to JSON file."""
        # Convert templates to serializable format
        templates_data = []
        for template in self.templates.values():
            template_dict = asdict(template)
            # Convert enums to strings for JSON serialization
            template_dict['prompt_type'] = template.prompt_type.value
            template_dict['provider'] = template.provider.value
            templates_data.append(template_dict)
        
        export_data = {
            'templates': templates_data,
            'exported_at': datetime.now().isoformat(),
            'version': '1.0'
        }
        
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        logger.info(f"Exported templates to: {file_path}")
    
    def import_templates(self, file_path: str):
        """Import templates from JSON file."""
        with open(file_path, 'r') as f:
            import_data = json.load(f)
        
        for template_data in import_data.get('templates', []):
            # Convert string enums back to enum objects
            template_data['prompt_type'] = PromptType(template_data['prompt_type'])
            template_data['provider'] = ProviderType(template_data['provider'])
            
            template = PromptTemplate(**template_data)
            self.add_template(template)
        
        logger.info(f"Imported templates from: {file_path}")

class PromptSystem:
    """
    High-level prompt system that integrates with LLM configuration.
    """
    
    def __init__(self, config_manager: LLMConfigurationManager):
        """
        Initialize the prompt system.
        
        Args:
            config_manager: LLM configuration manager
        """
        self.config_manager = config_manager
        self.prompt_manager = PromptManager(config_manager)
    
    def analyze_document(self, text_content: str, prompt_type: PromptType, 
                        provider: Optional[str] = None, **kwargs) -> GeneratedPrompt:
        """
        Analyze a document using the specified prompt type.
        
        Args:
            text_content: Document text content
            prompt_type: Type of analysis to perform
            provider: LLM provider (uses default if None)
            **kwargs: Additional context variables
            
        Returns:
            GeneratedPrompt object
        """
        if provider is None:
            provider = self.config_manager.config_manager.default_provider
        
        # Find appropriate template
        templates = self.prompt_manager.list_templates(provider, prompt_type)
        if not templates:
            raise ValueError(f"No template found for {prompt_type.value} and provider {provider}")
        
        # Use the first available template
        template = templates[0]
        
        # Create context
        context = PromptContext(
            text_content=text_content,
            **kwargs
        )
        
        # Generate prompt
        return self.prompt_manager.generate_prompt(
            template.name,
            provider,
            context
        )
    
    def check_rules(self, text_content: str, rules: List[Dict[str, Any]], 
                   provider: Optional[str] = None) -> GeneratedPrompt:
        """
        Check document against rules.
        
        Args:
            text_content: Document text content
            rules: List of rules to check
            provider: LLM provider (uses default if None)
            
        Returns:
            GeneratedPrompt object
        """
        context = PromptContext(
            text_content=text_content,
            rules=rules
        )
        
        return self.prompt_manager.generate_prompt(
            "rule_checking_openai",  # Default template name
            provider or self.config_manager.config_manager.default_provider,
            context
        )
    
    def get_available_prompts(self, provider: Optional[str] = None) -> Dict[str, List[str]]:
        """Get available prompts by type for a provider."""
        if provider is None:
            provider = self.config_manager.config_manager.default_provider
        
        templates = self.prompt_manager.list_templates(provider)
        
        result = {}
        for template in templates:
            prompt_type = template.prompt_type.value
            if prompt_type not in result:
                result[prompt_type] = []
            result[prompt_type].append(template.name)
        
        return result

# Utility functions

def create_prompt_system(config_manager: LLMConfigurationManager) -> PromptSystem:
    """Create a prompt system instance."""
    return PromptSystem(config_manager)

def create_prompt_manager() -> PromptManager:
    """Create a prompt manager instance."""
    return PromptManager() 