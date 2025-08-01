import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import json

logger = logging.getLogger(__name__)

class PolicyType(Enum):
    """Enumeration of policy document types."""
    HEALTH_INSURANCE = "health_insurance"
    LIFE_INSURANCE = "life_insurance"
    MASTER_POLICY = "master_policy"
    POLICY_SCHEDULE = "policy_schedule"
    ENDORSEMENT = "endorsement"
    CLAIM_DOCUMENT = "claim_document"
    MEDICAL_REPORT = "medical_report"
    HOSPITAL_BILL = "hospital_bill"
    OTHER = "other"

class DocumentCategory(Enum):
    """Enumeration of document categories."""
    POLICY = "policy"
    CLAIM = "claim"
    MEDICAL = "medical"
    ADMINISTRATIVE = "administrative"

@dataclass
class ClassificationResult:
    """Result of document classification."""
    document_type: PolicyType
    category: DocumentCategory
    confidence_score: float
    extraction_method: str
    policy_version: Optional[str] = None
    policy_number: Optional[str] = None
    classification_details: Dict[str, Any] = None
    recommendations: List[str] = None

class PolicyClassifier:
    """Classifier for policy documents and related files."""
    
    def __init__(self):
        # Policy type keywords and patterns
        self.policy_keywords = {
            PolicyType.HEALTH_INSURANCE: [
                "mediclaim", "health insurance", "health policy", "medical insurance",
                "healthcare", "hospitalization", "critical illness", "disease",
                "room rent", "icu", "co-payment", "sum assured"
            ],
            PolicyType.LIFE_INSURANCE: [
                "life insurance", "life policy", "term life", "whole life",
                "endowment", "death benefit", "maturity benefit", "premium"
            ],
            PolicyType.MASTER_POLICY: [
                "master policy", "master document", "base policy", "policy document",
                "terms and conditions", "policy wordings"
            ],
            PolicyType.POLICY_SCHEDULE: [
                "policy schedule", "schedule", "individual policy", "member details",
                "insured details", "coverage details"
            ],
            PolicyType.ENDORSEMENT: [
                "endorsement", "rider", "add-on", "modification", "amendment",
                "change request", "policy change"
            ],
            PolicyType.CLAIM_DOCUMENT: [
                "claim", "claim form", "claim document", "claim request",
                "hospitalization", "discharge summary", "medical certificate"
            ],
            PolicyType.MEDICAL_REPORT: [
                "medical report", "diagnosis", "prescription", "lab report",
                "test results", "doctor certificate", "medical certificate"
            ],
            PolicyType.HOSPITAL_BILL: [
                "hospital bill", "medical bill", "invoice", "charges",
                "itemized bill", "cost breakdown", "payment receipt"
            ]
        }
        
        # Filename patterns for classification
        self.filename_patterns = {
            PolicyType.HEALTH_INSURANCE: [
                r"mediclaim", r"health.*policy", r"health.*insurance",
                r"medical.*policy", r"healthcare.*policy"
            ],
            PolicyType.LIFE_INSURANCE: [
                r"life.*policy", r"life.*insurance", r"term.*life",
                r"whole.*life", r"endowment.*policy"
            ],
            PolicyType.MASTER_POLICY: [
                r"master.*policy", r"policy.*document", r"terms.*conditions",
                r"policy.*wordings", r"base.*policy"
            ],
            PolicyType.POLICY_SCHEDULE: [
                r"policy.*schedule", r"schedule.*policy", r"individual.*policy",
                r"member.*details", r"insured.*details"
            ],
            PolicyType.ENDORSEMENT: [
                r"endorsement", r"rider", r"add.*on", r"modification",
                r"amendment", r"policy.*change"
            ],
            PolicyType.CLAIM_DOCUMENT: [
                r"claim.*form", r"claim.*document", r"claim.*request",
                r"hospitalization.*claim", r"discharge.*summary"
            ],
            PolicyType.MEDICAL_REPORT: [
                r"medical.*report", r"diagnosis", r"prescription",
                r"lab.*report", r"test.*results", r"doctor.*certificate"
            ],
            PolicyType.HOSPITAL_BILL: [
                r"hospital.*bill", r"medical.*bill", r"invoice",
                r"itemized.*bill", r"cost.*breakdown", r"payment.*receipt"
            ]
        }
        
        # Policy number patterns
        self.policy_number_patterns = [
            r"POL[-\s]?(\d{4}[-\s]?\d{6})",
            r"Policy[-\s]?No[.:\s]?(\d{4}[-\s]?\d{6})",
            r"Policy[-\s]?Number[.:\s]?(\d{4}[-\s]?\d{6})",
            r"(\d{4}[-\s]?\d{6})",
            r"([A-Z]{2,4}\d{6,10})"
        ]
        
        # Version patterns
        self.version_patterns = [
            r"v[.\s]?(\d+\.\d+)",
            r"version[.\s]?(\d+\.\d+)",
            r"ver[.\s]?(\d+\.\d+)",
            r"(\d{4}[-\s]?\d{2}[-\s]?\d{2})",  # Date as version
            r"rev[.\s]?(\d+)",
            r"revision[.\s]?(\d+)"
        ]
    
    def classify_document(self, filename: str, content: str = None, 
                         metadata: Dict[str, Any] = None) -> ClassificationResult:
        """Classify a document based on filename, content, and metadata."""
        try:
            # Initialize classification details
            classification_details = {
                "filename_analysis": {},
                "content_analysis": {},
                "metadata_analysis": {},
                "confidence_factors": {}
            }
            
            # Step 1: Filename-based classification
            filename_result = self._classify_by_filename(filename)
            classification_details["filename_analysis"] = filename_result
            
            # Step 2: Content-based classification (if available)
            content_result = None
            if content:
                content_result = self._classify_by_content(content)
                classification_details["content_analysis"] = content_result
            
            # Step 3: Metadata-based classification (if available)
            metadata_result = None
            if metadata:
                metadata_result = self._classify_by_metadata(metadata)
                classification_details["metadata_analysis"] = metadata_result
            
            # Step 4: Combine results and determine final classification
            final_result = self._combine_classification_results(
                filename_result, content_result, metadata_result
            )
            
            # Step 5: Extract policy information
            policy_number = self._extract_policy_number(filename, content)
            policy_version = self._extract_policy_version(filename, content)
            
            # Step 6: Generate recommendations
            recommendations = self._generate_classification_recommendations(
                final_result, filename_result, content_result, metadata_result
            )
            
            return ClassificationResult(
                document_type=final_result["type"],
                category=final_result["category"],
                confidence_score=final_result["confidence"],
                policy_version=policy_version,
                policy_number=policy_number,
                extraction_method=final_result["method"],
                classification_details=classification_details,
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error classifying document {filename}: {e}")
            return ClassificationResult(
                document_type=PolicyType.OTHER,
                category=DocumentCategory.ADMINISTRATIVE,
                confidence_score=0.0,
                extraction_method="error_fallback",
                recommendations=[f"Classification failed: {str(e)}"]
            )
    
    def _classify_by_filename(self, filename: str) -> Dict[str, Any]:
        """Classify document based on filename patterns."""
        filename_lower = filename.lower()
        results = {}
        
        for policy_type, patterns in self.filename_patterns.items():
            score = 0.0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, filename_lower):
                    score += 1.0
                    matched_patterns.append(pattern)
            
            if score > 0:
                results[policy_type.value] = {
                    "score": score,
                    "matched_patterns": matched_patterns,
                    "confidence": min(score / len(patterns), 1.0)
                }
        
        # Find best match
        best_type = None
        best_score = 0.0
        
        for policy_type, result in results.items():
            if result["score"] > best_score:
                best_score = result["score"]
                best_type = policy_type
        
        return {
            "best_type": best_type,
            "best_score": best_score,
            "all_results": results,
            "method": "filename_pattern_matching"
        }
    
    def _classify_by_content(self, content: str) -> Dict[str, Any]:
        """Classify document based on content analysis."""
        content_lower = content.lower()
        results = {}
        
        for policy_type, keywords in self.policy_keywords.items():
            score = 0.0
            matched_keywords = []
            
            for keyword in keywords:
                if keyword.lower() in content_lower:
                    score += 1.0
                    matched_keywords.append(keyword)
            
            if score > 0:
                results[policy_type.value] = {
                    "score": score,
                    "matched_keywords": matched_keywords,
                    "confidence": min(score / len(keywords), 1.0)
                }
        
        # Find best match
        best_type = None
        best_score = 0.0
        
        for policy_type, result in results.items():
            if result["score"] > best_score:
                best_score = result["score"]
                best_type = policy_type
        
        return {
            "best_type": best_type,
            "best_score": best_score,
            "all_results": results,
            "method": "content_keyword_matching"
        }
    
    def _classify_by_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Classify document based on metadata."""
        results = {}
        
        # Check for policy-related metadata
        if "policy_type" in metadata:
            policy_type = metadata["policy_type"].lower()
            if "health" in policy_type or "medical" in policy_type:
                results[PolicyType.HEALTH_INSURANCE.value] = {
                    "score": 1.0,
                    "confidence": 0.8,
                    "source": "metadata_policy_type"
                }
            elif "life" in policy_type:
                results[PolicyType.LIFE_INSURANCE.value] = {
                    "score": 1.0,
                    "confidence": 0.8,
                    "source": "metadata_policy_type"
                }
        
        # Check for document type metadata
        if "document_type" in metadata:
            doc_type = metadata["document_type"].lower()
            if "master" in doc_type:
                results[PolicyType.MASTER_POLICY.value] = {
                    "score": 1.0,
                    "confidence": 0.9,
                    "source": "metadata_document_type"
                }
            elif "schedule" in doc_type:
                results[PolicyType.POLICY_SCHEDULE.value] = {
                    "score": 1.0,
                    "confidence": 0.9,
                    "source": "metadata_document_type"
                }
            elif "endorsement" in doc_type:
                results[PolicyType.ENDORSEMENT.value] = {
                    "score": 1.0,
                    "confidence": 0.9,
                    "source": "metadata_document_type"
                }
        
        return {
            "best_type": max(results.keys(), key=lambda k: results[k]["score"]) if results else None,
            "best_score": max(results.values(), key=lambda v: v["score"])["score"] if results else 0.0,
            "all_results": results,
            "method": "metadata_analysis"
        }
    
    def _combine_classification_results(self, filename_result: Dict[str, Any],
                                     content_result: Dict[str, Any] = None,
                                     metadata_result: Dict[str, Any] = None) -> Dict[str, Any]:
        """Combine results from different classification methods."""
        results = []
        weights = []
        
        # Add filename result
        if filename_result and filename_result["best_type"]:
            results.append(filename_result["best_type"])
            weights.append(0.3)  # 30% weight for filename
        
        # Add content result
        if content_result and content_result["best_type"]:
            results.append(content_result["best_type"])
            weights.append(0.5)  # 50% weight for content
        
        # Add metadata result
        if metadata_result and metadata_result["best_type"]:
            results.append(metadata_result["best_type"])
            weights.append(0.2)  # 20% weight for metadata
        
        if not results:
            return {
                "type": PolicyType.OTHER,
                "category": DocumentCategory.ADMINISTRATIVE,
                "confidence": 0.0,
                "method": "fallback"
            }
        
        # Count occurrences of each type
        type_counts = {}
        for result in results:
            type_counts[result] = type_counts.get(result, 0) + 1
        
        # Find most common type
        best_type = max(type_counts.keys(), key=lambda k: type_counts[k])
        
        # Calculate confidence based on agreement
        confidence = type_counts[best_type] / len(results)
        
        # Determine category
        category = self._get_category_for_type(best_type)
        
        return {
            "type": PolicyType(best_type),
            "category": category,
            "confidence": confidence,
            "method": "combined_analysis"
        }
    
    def _get_category_for_type(self, policy_type: str) -> DocumentCategory:
        """Get document category for policy type."""
        category_mapping = {
            PolicyType.HEALTH_INSURANCE.value: DocumentCategory.POLICY,
            PolicyType.LIFE_INSURANCE.value: DocumentCategory.POLICY,
            PolicyType.MASTER_POLICY.value: DocumentCategory.POLICY,
            PolicyType.POLICY_SCHEDULE.value: DocumentCategory.POLICY,
            PolicyType.ENDORSEMENT.value: DocumentCategory.POLICY,
            PolicyType.CLAIM_DOCUMENT.value: DocumentCategory.CLAIM,
            PolicyType.MEDICAL_REPORT.value: DocumentCategory.MEDICAL,
            PolicyType.HOSPITAL_BILL.value: DocumentCategory.CLAIM,
            PolicyType.OTHER.value: DocumentCategory.ADMINISTRATIVE
        }
        return category_mapping.get(policy_type, DocumentCategory.ADMINISTRATIVE)
    
    def _extract_policy_number(self, filename: str, content: str = None) -> Optional[str]:
        """Extract policy number from filename or content."""
        # Check filename first
        for pattern in self.policy_number_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Check content if available
        if content:
            for pattern in self.policy_number_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None
    
    def _extract_policy_version(self, filename: str, content: str = None) -> Optional[str]:
        """Extract policy version from filename or content."""
        # Check filename first
        for pattern in self.version_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1)
        
        # Check content if available
        if content:
            for pattern in self.version_patterns:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    return match.group(1)
        
        return None
    
    def _generate_classification_recommendations(self, final_result: Dict[str, Any],
                                              filename_result: Dict[str, Any],
                                              content_result: Dict[str, Any] = None,
                                              metadata_result: Dict[str, Any] = None) -> List[str]:
        """Generate recommendations based on classification results."""
        recommendations = []
        
        # Confidence-based recommendations
        confidence = final_result["confidence"]
        if confidence < 0.5:
            recommendations.append("Low confidence classification - manual review recommended")
        elif confidence < 0.8:
            recommendations.append("Medium confidence classification - consider additional validation")
        else:
            recommendations.append("High confidence classification - proceed with processing")
        
        # Method-specific recommendations
        if filename_result and filename_result["best_score"] > 0:
            recommendations.append(f"Filename analysis suggests: {filename_result['best_type']}")
        
        if content_result and content_result["best_score"] > 0:
            recommendations.append(f"Content analysis suggests: {content_result['best_type']}")
        
        if metadata_result and metadata_result["best_score"] > 0:
            recommendations.append(f"Metadata analysis suggests: {metadata_result['best_type']}")
        
        # Processing recommendations
        policy_type = final_result["type"]
        if policy_type in [PolicyType.HEALTH_INSURANCE, PolicyType.MASTER_POLICY]:
            recommendations.append("Use health insurance extraction pipeline")
        elif policy_type == PolicyType.LIFE_INSURANCE:
            recommendations.append("Use life insurance extraction pipeline")
        elif policy_type == PolicyType.CLAIM_DOCUMENT:
            recommendations.append("Use claim processing pipeline")
        elif policy_type == PolicyType.MEDICAL_REPORT:
            recommendations.append("Use medical document processing pipeline")
        
        return recommendations
    
    def route_to_processor(self, classification_result: ClassificationResult) -> str:
        """Route document to appropriate processor based on classification."""
        routing_map = {
            PolicyType.HEALTH_INSURANCE: "health_policy_processor",
            PolicyType.LIFE_INSURANCE: "life_policy_processor", 
            PolicyType.MASTER_POLICY: "master_policy_processor",
            PolicyType.POLICY_SCHEDULE: "policy_schedule_processor",
            PolicyType.ENDORSEMENT: "endorsement_processor",
            PolicyType.CLAIM_DOCUMENT: "claim_processor",
            PolicyType.MEDICAL_REPORT: "medical_processor",
            PolicyType.HOSPITAL_BILL: "bill_processor",
            PolicyType.OTHER: "general_processor"
        }
        
        return routing_map.get(classification_result.document_type, "general_processor")
    
    def validate_classification(self, classification_result: ClassificationResult) -> bool:
        """Validate classification result."""
        # Check if confidence is acceptable
        if classification_result.confidence_score < 0.3:
            return False
        
        # Check if document type is valid
        if classification_result.document_type == PolicyType.OTHER:
            return False
        
        # Check if category is valid
        if classification_result.category == DocumentCategory.ADMINISTRATIVE:
            return False
        
        return True

def classify_policy_document(filename: str, content: str = None, 
                           metadata: Dict[str, Any] = None) -> ClassificationResult:
    """Convenience function to classify a policy document."""
    classifier = PolicyClassifier()
    return classifier.classify_document(filename, content, metadata) 