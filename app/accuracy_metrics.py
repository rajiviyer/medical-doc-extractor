import json
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import statistics
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class FieldAccuracy:
    """Accuracy metrics for a single field."""
    field_name: str
    extracted_value: Any
    expected_value: Any
    is_correct: bool
    confidence_score: float
    extraction_method: str
    error_type: Optional[str] = None
    similarity_score: Optional[float] = None

@dataclass
class ModelAccuracy:
    """Accuracy metrics for a single LLM model."""
    model_name: str
    total_fields: int
    correct_fields: int
    accuracy_percentage: float
    average_confidence: float
    field_accuracies: List[FieldAccuracy]
    processing_time: float
    error_count: int

@dataclass
class AccuracyReport:
    """Complete accuracy report for all models."""
    timestamp: datetime
    test_name: str
    model_comparison: Dict[str, ModelAccuracy]
    overall_best_model: str
    overall_accuracy: float
    confidence_distribution: Dict[str, List[float]]
    field_performance: Dict[str, Dict[str, float]]
    recommendations: List[str]

class AccuracyTracker:
    """Tracks and analyzes extraction accuracy across different LLM models."""
    
    def __init__(self):
        self.accuracy_history = []
        self.ground_truth_data = {}
        self.field_definitions = {
            "room_rent_capping": {"type": "percentage", "range": (0, 100)},
            "icu_capping": {"type": "percentage", "range": (0, 100)},
            "co_payment": {"type": "percentage", "range": (0, 50)},
            "base_sum_assured": {"type": "currency", "range": (10000, 10000000)},
            "cataract_capping": {"type": "currency", "range": (0, 100000)},
            "hernia_capping": {"type": "currency", "range": (0, 100000)},
            "joint_replacement_capping": {"type": "currency", "range": (0, 500000)},
            "maternity_capping": {"type": "currency", "range": (0, 200000)},
            "ambulance_charge_capping": {"type": "currency", "range": (0, 5000)},
            "daily_cash_benefit": {"type": "currency", "range": (0, 5000)},
            "modern_treatment_capping": {"type": "percentage", "range": (0, 100)},
            "other_expenses_capping": {"type": "percentage", "range": (0, 100)},
            "medical_practitioners_capping": {"type": "percentage", "range": (0, 100)},
            "room_category_capping": {"type": "percentage", "range": (0, 100)},
            "treatment_hazardous_sports_capping": {"type": "percentage", "range": (0, 100)},
            "dialysis_capping": {"type": "currency", "range": (0, 100000)},
            "chemotherapy_capping": {"type": "currency", "range": (0, 200000)},
            "radiotherapy_capping": {"type": "currency", "range": (0, 200000)},
            "consumable_non_medical_capping": {"type": "percentage", "range": (0, 100)},
            "opd_daycare_domiciliary_capping": {"type": "currency", "range": (0, 50000)},
            "pre_post_hospitalization_capping": {"type": "currency", "range": (0, 100000)},
            "diagnostic_tests_capping": {"type": "currency", "range": (0, 50000)},
            "implants_stents_prosthetics_capping": {"type": "currency", "range": (0, 200000)},
            "mental_illness_treatment_capping": {"type": "currency", "range": (0, 100000)},
            "organ_donor_expenses_capping": {"type": "currency", "range": (0, 100000)},
            "bariatric_obesity_surgery_capping": {"type": "currency", "range": (0, 300000)},
            "cancer_treatment_capping": {"type": "currency", "range": (0, 500000)},
            "internal_congenital_disease_capping": {"type": "currency", "range": (0, 100000)},
            "ayush_hospitalization_capping": {"type": "currency", "range": (0, 50000)},
            "vaccination_preventive_capping": {"type": "currency", "range": (0, 10000)},
            "artificial_prostheses_aids_capping": {"type": "currency", "range": (0, 50000)}
        }
    
    def load_ground_truth(self, ground_truth_file: str) -> Dict[str, Any]:
        """Load ground truth data from JSON file."""
        try:
            with open(ground_truth_file, 'r', encoding='utf-8') as f:
                self.ground_truth_data = json.load(f)
            logger.info(f"Loaded ground truth data from {ground_truth_file}")
            return self.ground_truth_data
        except Exception as e:
            logger.error(f"Failed to load ground truth data: {e}")
            return {}
    
    def calculate_field_accuracy(self, field_name: str, extracted_value: Any, 
                               expected_value: Any, confidence_score: float, 
                               extraction_method: str) -> FieldAccuracy:
        """Calculate accuracy for a single field."""
        try:
            # Normalize values for comparison
            extracted_normalized = self._normalize_value(extracted_value)
            expected_normalized = self._normalize_value(expected_value)
            
            # Check if values are correct
            is_correct = self._compare_values(extracted_normalized, expected_normalized)
            
            # Calculate similarity score
            similarity_score = self._calculate_similarity(extracted_normalized, expected_normalized)
            
            # Determine error type if incorrect
            error_type = None
            if not is_correct:
                error_type = self._classify_error(extracted_normalized, expected_normalized, field_name)
            
            return FieldAccuracy(
                field_name=field_name,
                extracted_value=extracted_value,
                expected_value=expected_value,
                is_correct=is_correct,
                confidence_score=confidence_score,
                extraction_method=extraction_method,
                error_type=error_type,
                similarity_score=similarity_score
            )
        except Exception as e:
            logger.error(f"Error calculating field accuracy for {field_name}: {e}")
            return FieldAccuracy(
                field_name=field_name,
                extracted_value=extracted_value,
                expected_value=expected_value,
                is_correct=False,
                confidence_score=confidence_score,
                extraction_method=extraction_method,
                error_type="calculation_error"
            )
    
    def _normalize_value(self, value: Any) -> Any:
        """Normalize value for comparison."""
        if value is None:
            return None
        
        if isinstance(value, str):
            # Remove common prefixes/suffixes
            value = value.lower().strip()
            value = value.replace('rs.', '').replace('rs', '').replace('₹', '')
            value = value.replace('%', '').replace('percent', '').replace('per cent', '')
            value = value.replace('at actuals', '100').replace('actuals', '100')
            value = value.replace('not applicable', '0').replace('na', '0')
            value = value.replace('unlimited', '999999')
            
            # Try to convert to number
            try:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            except ValueError:
                return value
        
        return value
    
    def _compare_values(self, extracted: Any, expected: Any) -> bool:
        """Compare normalized values for accuracy."""
        if extracted is None and expected is None:
            return True
        if extracted is None or expected is None:
            return False
        
        # Exact match for numbers
        if isinstance(extracted, (int, float)) and isinstance(expected, (int, float)):
            return abs(extracted - expected) < 0.01
        
        # String comparison
        if isinstance(extracted, str) and isinstance(expected, str):
            return extracted.lower() == expected.lower()
        
        # Mixed types
        return str(extracted).lower() == str(expected).lower()
    
    def _calculate_similarity(self, extracted: Any, expected: Any) -> float:
        """Calculate similarity score between values."""
        if extracted is None or expected is None:
            return 0.0
        
        if isinstance(extracted, (int, float)) and isinstance(expected, (int, float)):
            if expected == 0:
                return 1.0 if extracted == 0 else 0.0
            return max(0, 1 - abs(extracted - expected) / abs(expected))
        
        if isinstance(extracted, str) and isinstance(expected, str):
            # Simple string similarity
            if extracted == expected:
                return 1.0
            if extracted in expected or expected in extracted:
                return 0.8
            return 0.0
        
        return 0.0
    
    def _classify_error(self, extracted: Any, expected: Any, field_name: str) -> str:
        """Classify the type of error."""
        if extracted is None:
            return "missing_extraction"
        
        if expected is None:
            return "no_ground_truth"
        
        # Check for range errors
        field_def = self.field_definitions.get(field_name, {})
        if field_def.get("type") == "percentage":
            if isinstance(extracted, (int, float)) and (extracted < 0 or extracted > 100):
                return "out_of_range"
        elif field_def.get("type") == "currency":
            if isinstance(extracted, (int, float)) and extracted < 0:
                return "negative_value"
        
        # Check for format errors
        if isinstance(extracted, str) and isinstance(expected, (int, float)):
            return "format_error"
        
        return "value_mismatch"
    
    def calculate_model_accuracy(self, model_name: str, extracted_data: Dict[str, Any], 
                               ground_truth: Dict[str, Any], processing_time: float) -> ModelAccuracy:
        """Calculate accuracy metrics for a single model."""
        field_accuracies = []
        correct_fields = 0
        total_confidence = 0.0
        error_count = 0
        
        for field_name in self.field_definitions.keys():
            extracted_value = extracted_data.get(field_name)
            expected_value = ground_truth.get(field_name)
            confidence_score = extracted_data.get(f"{field_name}_confidence", 0.5)
            
            field_accuracy = self.calculate_field_accuracy(
                field_name, extracted_value, expected_value, 
                confidence_score, model_name
            )
            
            field_accuracies.append(field_accuracy)
            
            if field_accuracy.is_correct:
                correct_fields += 1
            else:
                error_count += 1
            
            total_confidence += confidence_score
        
        total_fields = len(field_accuracies)
        accuracy_percentage = (correct_fields / total_fields * 100) if total_fields > 0 else 0
        average_confidence = total_confidence / total_fields if total_fields > 0 else 0
        
        return ModelAccuracy(
            model_name=model_name,
            total_fields=total_fields,
            correct_fields=correct_fields,
            accuracy_percentage=accuracy_percentage,
            average_confidence=average_confidence,
            field_accuracies=field_accuracies,
            processing_time=processing_time,
            error_count=error_count
        )
    
    def compare_models(self, model_results: Dict[str, Dict[str, Any]], 
                      ground_truth: Dict[str, Any], test_name: str = "policy_extraction_test") -> AccuracyReport:
        """Compare accuracy across multiple models."""
        model_accuracies = {}
        confidence_distribution = {}
        field_performance = {}
        
        # Calculate accuracy for each model
        for model_name, extracted_data in model_results.items():
            processing_time = extracted_data.get("processing_time", 0)
            model_accuracy = self.calculate_model_accuracy(
                model_name, extracted_data, ground_truth, processing_time
            )
            model_accuracies[model_name] = model_accuracy
            
            # Collect confidence scores
            confidence_distribution[model_name] = [
                field.confidence_score for field in model_accuracy.field_accuracies
            ]
        
        # Find best model
        best_model = max(model_accuracies.keys(), 
                        key=lambda x: model_accuracies[x].accuracy_percentage)
        overall_accuracy = model_accuracies[best_model].accuracy_percentage
        
        # Calculate field-level performance
        field_performance = self._calculate_field_performance(model_accuracies)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(model_accuracies, field_performance)
        
        return AccuracyReport(
            timestamp=datetime.now(),
            test_name=test_name,
            model_comparison=model_accuracies,
            overall_best_model=best_model,
            overall_accuracy=overall_accuracy,
            confidence_distribution=confidence_distribution,
            field_performance=field_performance,
            recommendations=recommendations
        )
    
    def _calculate_field_performance(self, model_accuracies: Dict[str, ModelAccuracy]) -> Dict[str, Dict[str, float]]:
        """Calculate performance metrics for each field across models."""
        field_performance = {}
        
        for field_name in self.field_definitions.keys():
            field_performance[field_name] = {}
            
            for model_name, model_accuracy in model_accuracies.items():
                field_accuracy = next(
                    (fa for fa in model_accuracy.field_accuracies if fa.field_name == field_name),
                    None
                )
                
                if field_accuracy:
                    field_performance[field_name][model_name] = {
                        "accuracy": 100.0 if field_accuracy.is_correct else 0.0,
                        "confidence": field_accuracy.confidence_score,
                        "similarity": field_accuracy.similarity_score or 0.0
                    }
        
        return field_performance
    
    def _generate_recommendations(self, model_accuracies: Dict[str, ModelAccuracy], 
                                field_performance: Dict[str, Dict[str, float]]) -> List[str]:
        """Generate recommendations based on accuracy analysis."""
        recommendations = []
        
        # Model performance recommendations
        best_model = max(model_accuracies.keys(), 
                        key=lambda x: model_accuracies[x].accuracy_percentage)
        worst_model = min(model_accuracies.keys(), 
                         key=lambda x: model_accuracies[x].accuracy_percentage)
        
        best_accuracy = model_accuracies[best_model].accuracy_percentage
        worst_accuracy = model_accuracies[worst_model].accuracy_percentage
        
        if best_accuracy > 90:
            recommendations.append(f"Excellent performance: {best_model} achieved {best_accuracy:.1f}% accuracy")
        elif best_accuracy > 80:
            recommendations.append(f"Good performance: {best_model} achieved {best_accuracy:.1f}% accuracy")
        else:
            recommendations.append(f"Needs improvement: Best model {best_model} only achieved {best_accuracy:.1f}% accuracy")
        
        if worst_accuracy < 70:
            recommendations.append(f"Consider optimizing {worst_model}: Only {worst_accuracy:.1f}% accuracy")
        
        # Field-specific recommendations
        problematic_fields = []
        for field_name, performance in field_performance.items():
            avg_accuracy = statistics.mean([
                perf.get("accuracy", 0) for perf in performance.values()
            ])
            if avg_accuracy < 70:
                problematic_fields.append(field_name)
        
        if problematic_fields:
            recommendations.append(f"Focus on improving extraction for: {', '.join(problematic_fields[:5])}")
        
        # Confidence recommendations
        for model_name, model_accuracy in model_accuracies.items():
            if model_accuracy.average_confidence < 0.6:
                recommendations.append(f"Low confidence for {model_name}: {model_accuracy.average_confidence:.2f}")
        
        return recommendations
    
    def save_accuracy_report(self, report: AccuracyReport, output_file: str):
        """Save accuracy report to JSON file."""
        try:
            report_data = {
                "timestamp": report.timestamp.isoformat(),
                "test_name": report.test_name,
                "overall_best_model": report.overall_best_model,
                "overall_accuracy": report.overall_accuracy,
                "model_comparison": {
                    model_name: {
                        "total_fields": ma.total_fields,
                        "correct_fields": ma.correct_fields,
                        "accuracy_percentage": ma.accuracy_percentage,
                        "average_confidence": ma.average_confidence,
                        "processing_time": ma.processing_time,
                        "error_count": ma.error_count,
                        "field_accuracies": [
                            {
                                "field_name": fa.field_name,
                                "extracted_value": fa.extracted_value,
                                "expected_value": fa.expected_value,
                                "is_correct": fa.is_correct,
                                "confidence_score": fa.confidence_score,
                                "error_type": fa.error_type,
                                "similarity_score": fa.similarity_score
                            }
                            for fa in ma.field_accuracies
                        ]
                    }
                    for model_name, ma in report.model_comparison.items()
                },
                "confidence_distribution": report.confidence_distribution,
                "field_performance": report.field_performance,
                "recommendations": report.recommendations
            }
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Accuracy report saved to {output_file}")
            
        except Exception as e:
            logger.error(f"Failed to save accuracy report: {e}")
    
    def load_accuracy_report(self, report_file: str) -> Optional[AccuracyReport]:
        """Load accuracy report from JSON file."""
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct the report object
            model_accuracies = {}
            for model_name, model_data in data["model_comparison"].items():
                field_accuracies = [
                    FieldAccuracy(
                        field_name=fa["field_name"],
                        extracted_value=fa["extracted_value"],
                        expected_value=fa["expected_value"],
                        is_correct=fa["is_correct"],
                        confidence_score=fa["confidence_score"],
                        extraction_method=model_name,
                        error_type=fa.get("error_type"),
                        similarity_score=fa.get("similarity_score")
                    )
                    for fa in model_data["field_accuracies"]
                ]
                
                model_accuracies[model_name] = ModelAccuracy(
                    model_name=model_name,
                    total_fields=model_data["total_fields"],
                    correct_fields=model_data["correct_fields"],
                    accuracy_percentage=model_data["accuracy_percentage"],
                    average_confidence=model_data["average_confidence"],
                    field_accuracies=field_accuracies,
                    processing_time=model_data["processing_time"],
                    error_count=model_data["error_count"]
                )
            
            return AccuracyReport(
                timestamp=datetime.fromisoformat(data["timestamp"]),
                test_name=data["test_name"],
                model_comparison=model_accuracies,
                overall_best_model=data["overall_best_model"],
                overall_accuracy=data["overall_accuracy"],
                confidence_distribution=data["confidence_distribution"],
                field_performance=data["field_performance"],
                recommendations=data["recommendations"]
            )
            
        except Exception as e:
            logger.error(f"Failed to load accuracy report: {e}")
            return None

def track_extraction_accuracy(extracted_data: Dict[str, Any], ground_truth: Dict[str, Any], 
                            test_name: str = "policy_extraction") -> AccuracyReport:
    """Convenience function to track extraction accuracy."""
    tracker = AccuracyTracker()
    return tracker.compare_models(extracted_data, ground_truth, test_name) 