import re
import logging
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of validation for a single field."""
    field_name: str
    value: Any
    is_valid: bool
    confidence_score: float  # 0.0 to 1.0
    validation_messages: List[str]
    suggested_value: Optional[Any] = None

@dataclass
class PolicyValidationReport:
    """Complete validation report for a policy extraction."""
    overall_valid: bool
    overall_confidence: float
    field_results: Dict[str, ValidationResult]
    cross_field_issues: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the validation report to a dictionary for JSON serialization."""
        return {
            "overall_valid": self.overall_valid,
            "overall_confidence": self.overall_confidence,
            "field_results": {
                field_name: {
                    "field_name": result.field_name,
                    "value": result.value,
                    "is_valid": result.is_valid,
                    "confidence_score": result.confidence_score,
                    "validation_messages": result.validation_messages,
                    "suggested_value": result.suggested_value
                }
                for field_name, result in self.field_results.items()
            },
            "cross_field_issues": self.cross_field_issues,
            "recommendations": self.recommendations
        }

class PolicyCappingValidator:
    """Validator for policy capping values extracted from documents."""
    
    def __init__(self):
        self.validation_rules = {
            'base_sum_assured': {
                'type': 'amount',
                'min_value': 10000,
                'max_value': 10000000,
                'required': True,
                'description': 'Base Sum Assured/Base Sum Insured'
            },
            'room_rent_capping': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': True,
                'description': 'Cap on room rent'
            },
            'icu_capping': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': True,
                'description': 'Cap on ICU charges'
            },
            'room_category_capping': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': False,
                'description': 'Cap on room category'
            },
            'medical_practitioners_capping': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': False,
                'description': 'Cap on medical practitioners'
            },
            'treatment_related_to_participation_as_a_non_professional_in_hazardous_or_adventure_sports': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': False,
                'description': 'Cap on hazardous sports treatment'
            },
            'other_expenses_capping': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': False,
                'description': 'Cap on other expenses'
            },
            'modern_treatment_capping': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': False,
                'description': 'Cap on modern treatment'
            },
            'cataract_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 100000,
                'required': False,
                'description': 'Cap on cataract'
            },
            'hernia_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 100000,
                'required': False,
                'description': 'Cap on hernia'
            },
            'joint_replacement_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 500000,
                'required': False,
                'description': 'Cap on joint replacement'
            },
            'any_kind_of_surgery_specific_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 500000,
                'required': False,
                'description': 'Cap on any kind of surgery'
            },
            'treatment_based_capping_dialysis': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 200000,
                'required': False,
                'description': 'Cap on dialysis treatment'
            },
            'treatment_based_capping_chemotherapy': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 500000,
                'required': False,
                'description': 'Cap on chemotherapy treatment'
            },
            'treatment_based_capping_radiotherapy': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 300000,
                'required': False,
                'description': 'Cap on radiotherapy treatment'
            },
            'consumable_and_non_medical_items_capping': {
                'type': 'percentage_or_actuals',
                'min_value': 0,
                'max_value': 100,
                'required': False,
                'description': 'Cap on consumable and non-medical items'
            },
            'maternity_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 200000,
                'required': False,
                'description': 'Cap on maternity'
            },
            'ambulance_charge_capping': {
                'type': 'amount',
                'min_value': 0,
                'max_value': 10000,
                'required': False,
                'description': 'Cap on ambulance charge'
            },
            'daily_cash_benefit': {
                'type': 'amount',
                'min_value': 0,
                'max_value': 5000,
                'required': False,
                'description': 'Daily cash benefit amount'
            },
            'co_payment': {
                'type': 'percentage',
                'min_value': 0,
                'max_value': 50,
                'required': False,
                'description': 'Co-payment percentage'
            },
            'opd_daycare_domiciliary_treatment_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 100000,
                'required': False,
                'description': 'Cap on OPD, Daycare, Domiciliary treatment'
            },
            'pre_post_hospitalization_expenses_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 100000,
                'required': False,
                'description': 'Cap on pre and post hospitalization expenses'
            },
            'diagnostic_tests_and_investigation_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 50000,
                'required': False,
                'description': 'Cap on diagnostic tests and investigation'
            },
            'implants_stents_prosthetics_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 300000,
                'required': False,
                'description': 'Cap on implants, stents, prosthetics'
            },
            'mental_illness_treatment_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 200000,
                'required': False,
                'description': 'Cap on mental illness treatment'
            },
            'organ_donor_expenses_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 500000,
                'required': False,
                'description': 'Cap on organ donor expenses'
            },
            'bariatric_obesity_surgery_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 400000,
                'required': False,
                'description': 'Cap on bariatric, obesity surgery'
            },
            'cancer_treatment_capping_in_specific_plans': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 1000000,
                'required': False,
                'description': 'Cap on cancer treatment in specific plans'
            },
            'internal_congenital_disease_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 300000,
                'required': False,
                'description': 'Cap on internal, congenital disease'
            },
            'ayush_hospitalization_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 100000,
                'required': False,
                'description': 'Cap on AYUSH hospitalization'
            },
            'vaccination_preventive_health_check_up_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 50000,
                'required': False,
                'description': 'Cap on vaccination, preventive health check up'
            },
            'artificial_prostheses_aids_capping': {
                'type': 'amount_or_percentage',
                'min_value': 0,
                'max_value': 100000,
                'required': False,
                'description': 'Cap on artificial prostheses, aids'
            },
            'policy_start_date': {
                'type': 'date',
                'required': False,
                'description': 'Policy start date'
            },
            'policy_end_date': {
                'type': 'date',
                'required': False,
                'description': 'Policy end date'
            },
            'date_of_admission': {
                'type': 'date',
                'required': False,
                'description': 'Date of admission to hospital'
            }
        }
    
    def validate_single_field(self, field_name: str, value: Any) -> ValidationResult:
        """Validate a single field according to its rules."""
        if field_name not in self.validation_rules:
            return ValidationResult(
                field_name=field_name,
                value=value,
                is_valid=True,
                confidence_score=0.5,
                validation_messages=[f"Unknown field '{field_name}' - no validation rules defined"]
            )
        
        rule = self.validation_rules[field_name]
        messages = []
        confidence_score = 1.0
        suggested_value = None
        
        # Check if value is null/empty
        if value is None or value == "" or value == "null":
            if rule['required']:
                messages.append(f"{field_name} is required but was not found")
                confidence_score = 0.0
                is_valid = False
            else:
                messages.append(f"{field_name} is optional and not provided")
                is_valid = True
                confidence_score = 0.8
            return ValidationResult(
                field_name=field_name,
                value=value,
                is_valid=is_valid,
                confidence_score=confidence_score,
                validation_messages=messages,
                suggested_value=suggested_value
            )
        
        # Parse and validate based on type
        if rule['type'] == 'amount':
            result = self._validate_amount(field_name, value, rule)
        elif rule['type'] == 'percentage':
            result = self._validate_percentage(field_name, value, rule)
        elif rule['type'] == 'percentage_or_actuals':
            result = self._validate_percentage_or_actuals(field_name, value, rule)
        elif rule['type'] == 'amount_or_percentage':
            result = self._validate_amount_or_percentage(field_name, value, rule)
        elif rule['type'] == 'date':
            result = self._validate_date(field_name, value, rule)
        else:
            result = ValidationResult(
                field_name=field_name,
                value=value,
                is_valid=True,
                confidence_score=0.5,
                validation_messages=[f"Unknown validation type '{rule['type']}' for {field_name}"]
            )
        
        return result
    
    def _validate_amount(self, field_name: str, value: Any, rule: Dict) -> ValidationResult:
        """Validate amount fields."""
        messages = []
        confidence_score = 1.0
        suggested_value = None
        
        # Try to extract numeric value
        numeric_value = self._extract_numeric_value(value)
        
        if numeric_value is None:
            messages.append(f"Could not extract numeric value from '{value}'")
            confidence_score = 0.3
            is_valid = False
        else:
            if numeric_value < rule['min_value']:
                messages.append(f"Value {numeric_value} is below minimum {rule['min_value']}")
                confidence_score = 0.4
                is_valid = False
            elif numeric_value > rule['max_value']:
                messages.append(f"Value {numeric_value} is above maximum {rule['max_value']}")
                confidence_score = 0.4
                is_valid = False
            else:
                is_valid = True
                confidence_score = 0.9
        
        return ValidationResult(
            field_name=field_name,
            value=value,
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_messages=messages,
            suggested_value=suggested_value
        )
    
    def _validate_percentage(self, field_name: str, value: Any, rule: Dict) -> ValidationResult:
        """Validate percentage fields."""
        messages = []
        confidence_score = 1.0
        suggested_value = None
        
        # Try to extract percentage value
        percentage_value = self._extract_percentage_value(value)
        
        if percentage_value is None:
            messages.append(f"Could not extract percentage value from '{value}'")
            confidence_score = 0.3
            is_valid = False
        else:
            if percentage_value < rule['min_value']:
                messages.append(f"Percentage {percentage_value}% is below minimum {rule['min_value']}%")
                confidence_score = 0.4
                is_valid = False
            elif percentage_value > rule['max_value']:
                messages.append(f"Percentage {percentage_value}% is above maximum {rule['max_value']}%")
                confidence_score = 0.4
                is_valid = False
            else:
                is_valid = True
                confidence_score = 0.9
        
        return ValidationResult(
            field_name=field_name,
            value=value,
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_messages=messages,
            suggested_value=suggested_value
        )
    
    def _validate_percentage_or_actuals(self, field_name: str, value: Any, rule: Dict) -> ValidationResult:
        """Validate fields that can be percentage or 'at actuals'."""
        messages = []
        confidence_score = 1.0
        suggested_value = None
        
        # Check for "at actuals" or similar
        if isinstance(value, str) and any(phrase in value.lower() for phrase in ['at actuals', 'actual', '100%']):
            is_valid = True
            confidence_score = 0.9
            messages.append("Value indicates 'at actuals' (100%)")
        else:
            # Try to extract percentage
            percentage_value = self._extract_percentage_value(value)
            
            if percentage_value is None:
                messages.append(f"Could not extract percentage value from '{value}'")
                confidence_score = 0.3
                is_valid = False
            else:
                if percentage_value < rule['min_value']:
                    messages.append(f"Percentage {percentage_value}% is below minimum {rule['min_value']}%")
                    confidence_score = 0.4
                    is_valid = False
                elif percentage_value > rule['max_value']:
                    messages.append(f"Percentage {percentage_value}% is above maximum {rule['max_value']}%")
                    confidence_score = 0.4
                    is_valid = False
                else:
                    is_valid = True
                    confidence_score = 0.9
        
        return ValidationResult(
            field_name=field_name,
            value=value,
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_messages=messages,
            suggested_value=suggested_value
        )
    
    def _validate_amount_or_percentage(self, field_name: str, value: Any, rule: Dict) -> ValidationResult:
        """Validate fields that can be amount or percentage."""
        messages = []
        confidence_score = 1.0
        suggested_value = None
        
        # Try percentage first
        percentage_value = self._extract_percentage_value(value)
        if percentage_value is not None:
            if percentage_value < rule['min_value']:
                messages.append(f"Percentage {percentage_value}% is below minimum {rule['min_value']}%")
                confidence_score = 0.4
                is_valid = False
            elif percentage_value > rule['max_value']:
                messages.append(f"Percentage {percentage_value}% is above maximum {rule['max_value']}%")
                confidence_score = 0.4
                is_valid = False
            else:
                is_valid = True
                confidence_score = 0.9
        else:
            # Try amount
            numeric_value = self._extract_numeric_value(value)
            if numeric_value is None:
                messages.append(f"Could not extract numeric or percentage value from '{value}'")
                confidence_score = 0.3
                is_valid = False
            else:
                if numeric_value < rule['min_value']:
                    messages.append(f"Amount {numeric_value} is below minimum {rule['min_value']}")
                    confidence_score = 0.4
                    is_valid = False
                elif numeric_value > rule['max_value']:
                    messages.append(f"Amount {numeric_value} is above maximum {rule['max_value']}")
                    confidence_score = 0.4
                    is_valid = False
                else:
                    is_valid = True
                    confidence_score = 0.9
        
        return ValidationResult(
            field_name=field_name,
            value=value,
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_messages=messages,
            suggested_value=suggested_value
        )
    
    def _extract_numeric_value(self, value: Any) -> Optional[float]:
        """Extract numeric value from various formats."""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Remove common currency symbols and commas
            cleaned = re.sub(r'[₹$€£,]', '', value.strip())
            # Extract number
            match = re.search(r'(\d+(?:\.\d+)?)', cleaned)
            if match:
                return float(match.group(1))
        
        return None
    
    def _extract_percentage_value(self, value: Any) -> Optional[float]:
        """Extract percentage value from various formats."""
        if isinstance(value, (int, float)):
            return float(value)
        
        if isinstance(value, str):
            # Look for percentage patterns
            cleaned = value.strip().lower()
            # Remove % symbol and extract number
            match = re.search(r'(\d+(?:\.\d+)?)\s*%', cleaned)
            if match:
                return float(match.group(1))
            # Also check for "percent" or "per cent"
            match = re.search(r'(\d+(?:\.\d+)?)\s*(?:percent|per cent)', cleaned)
            if match:
                return float(match.group(1))
        
        return None
    
    def _validate_date(self, field_name: str, value: Any, rule: Dict) -> ValidationResult:
        """Validate date fields."""
        messages = []
        confidence_score = 1.0
        suggested_value = None
        
        if value is None or value == "null" or value == "":
            messages.append(f"{rule['description']} is optional and not provided")
            confidence_score = 0.8
            is_valid = True
        elif isinstance(value, str):
            # Check for common date formats including both YYYY and YY formats
            date_patterns = [
                r'\d{1,2}/\d{1,2}/\d{4}',  # DD/MM/YYYY or MM/DD/YYYY
                r'\d{1,2}/\d{1,2}/\d{2}',   # DD/MM/YY or MM/DD/YY
                r'\d{1,2}/\d{1}/\d{2}',     # DD/M/YY or MM/D/YY (e.g., 7/5/25)
                r'\d{1}/\d{1,2}/\d{2}',     # D/MM/YY or M/DD/YY (e.g., 7/12/25)
                r'\d{1}/\d{1}/\d{2}',       # D/M/YY or M/D/YY (e.g., 7/5/25)
                r'\d{4}-\d{1,2}-\d{1,2}',  # YYYY-MM-DD
                r'\d{1,2}-\d{1,2}-\d{4}',  # DD-MM-YYYY or MM-DD-YYYY
                r'\d{1,2}-\d{1,2}-\d{2}',  # DD-MM-YY or MM-DD-YY
                r'\d{1,2}-\d{1}-\d{2}',     # DD-M-YY or MM-D-YY
                r'\d{1}-\d{1,2}-\d{2}',     # D-MM-YY or M-DD-YY
                r'\d{1}-\d{1}-\d{2}',       # D-M-YY or M-D-YY
                r'\d{1,2}\.\d{1,2}\.\d{4}',  # DD.MM.YYYY or MM.DD.YYYY
                r'\d{1,2}\.\d{1,2}\.\d{2}',  # DD.MM.YY or MM.DD.YY
                r'\d{1,2}\.\d{1}\.\d{2}',     # DD.M.YY or MM.D.YY
                r'\d{1}\.\d{1,2}\.\d{2}',     # D.MM.YY or M.DD.YY
                r'\d{1}\.\d{1}\.\d{2}',       # D.M.YY or M.D.YY
            ]
            
            is_valid_date = False
            for pattern in date_patterns:
                if re.search(pattern, value):
                    is_valid_date = True
                    break
            
            if is_valid_date:
                is_valid = True
                confidence_score = 0.9
            else:
                messages.append(f"Could not extract valid date format from '{value}'")
                confidence_score = 0.3
                is_valid = False
        else:
            messages.append(f"Date value should be a string, got {type(value)}")
            confidence_score = 0.3
            is_valid = False
        
        return ValidationResult(
            field_name=field_name,
            value=value,
            is_valid=is_valid,
            confidence_score=confidence_score,
            validation_messages=messages,
            suggested_value=suggested_value
        )
    
    def validate_policy_extraction(self, extraction_data: Dict[str, Any]) -> PolicyValidationReport:
        """Validate complete policy extraction data."""
        field_results = {}
        cross_field_issues = []
        recommendations = []
        
        # Validate each field
        for field_name, value in extraction_data.items():
            result = self.validate_single_field(field_name, value)
            field_results[field_name] = result
        
        # Cross-field validation
        cross_field_issues = self._validate_cross_fields(extraction_data, field_results)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(field_results, cross_field_issues)
        
        # Calculate overall metrics
        valid_fields = sum(1 for result in field_results.values() if result.is_valid)
        total_fields = len(field_results)
        overall_valid = valid_fields == total_fields
        overall_confidence = sum(result.confidence_score for result in field_results.values()) / total_fields if total_fields > 0 else 0.0
        
        return PolicyValidationReport(
            overall_valid=overall_valid,
            overall_confidence=overall_confidence,
            field_results=field_results,
            cross_field_issues=cross_field_issues,
            recommendations=recommendations
        )
    
    def _validate_cross_fields(self, extraction_data: Dict[str, Any], field_results: Dict[str, ValidationResult]) -> List[str]:
        """Validate relationships between fields."""
        issues = []
        
        # Check if base sum assured is reasonable compared to other caps
        base_sum = self._extract_numeric_value(extraction_data.get('base_sum_assured'))
        if base_sum:
            # Check if room rent capping makes sense
            room_rent = self._extract_percentage_value(extraction_data.get('room_rent_capping'))
            if room_rent and room_rent > 100:
                issues.append("Room rent capping cannot exceed 100%")
            
            # Check if ICU capping makes sense
            icu_cap = self._extract_percentage_value(extraction_data.get('icu_capping'))
            if icu_cap and icu_cap > 100:
                issues.append("ICU capping cannot exceed 100%")
        
        # Check if co-payment is reasonable
        co_payment = self._extract_percentage_value(extraction_data.get('co_payment'))
        if co_payment and co_payment > 50:
            issues.append("Co-payment should not exceed 50%")
        
        # Check if daily cash benefit is reasonable
        daily_cash = self._extract_numeric_value(extraction_data.get('daily_cash_benefit'))
        if daily_cash and daily_cash > 5000:
            issues.append("Daily cash benefit seems unusually high (>5000)")
        
        return issues
    
    def _generate_recommendations(self, field_results: Dict[str, ValidationResult], cross_field_issues: List[str]) -> List[str]:
        """Generate recommendations based on validation results."""
        recommendations = []
        
        # Count issues by severity
        high_confidence_fields = sum(1 for result in field_results.values() if result.confidence_score >= 0.8)
        low_confidence_fields = sum(1 for result in field_results.values() if result.confidence_score < 0.5)
        
        if low_confidence_fields > 0:
            recommendations.append(f"Review {low_confidence_fields} fields with low confidence scores")
        
        if high_confidence_fields < len(field_results) * 0.7:
            recommendations.append("Overall confidence is low - consider manual review")
        
        if cross_field_issues:
            recommendations.append("Cross-field validation issues detected - review relationships")
        
        # Specific recommendations
        for field_name, result in field_results.items():
            if not result.is_valid and result.validation_messages:
                recommendations.append(f"Fix {field_name}: {result.validation_messages[0]}")
        
        return recommendations

def validate_extraction_result(extraction_data: Dict[str, Any]) -> PolicyValidationReport:
    """Convenience function to validate extraction results."""
    validator = PolicyCappingValidator()
    return validator.validate_policy_extraction(extraction_data) 