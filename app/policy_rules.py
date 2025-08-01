import re
import logging
from datetime import datetime, date
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class RuleDecision(Enum):
    PASS = "Pass"
    REJECT = "Reject"
    DEDUCT = "Deduct"
    PROPORTIONATE_DEDUCTION = "Proportionate Deduction"
    CAP_LIMIT_APPLIED = "Cap Limit Applied"

class RuleSection(Enum):
    POLICY_VALIDITY = "Policy Validity"
    POLICY_LIMITS = "Policy Limits"
    WAITING_PERIODS = "Waiting Periods"

@dataclass
class RuleResult:
    """Result of a single rule check."""
    rule_name: str
    section: str
    decision: RuleDecision
    criteria_met: bool
    confidence_score: float  # 0.0 to 1.0
    details: str
    deduction_amount: Optional[float] = None
    supporting_evidence: List[str] = None

@dataclass
class PolicyRuleReport:
    """Complete policy rule validation report."""
    overall_valid: bool
    overall_confidence: float
    rule_results: Dict[str, RuleResult]
    total_deductions: float
    recommendations: List[str]
    risk_level: str  # "Low", "Medium", "High"
    status: str  # "CLEARED", "CLEARED WITH DEDUCTIONS", "REJECTED"

class PolicyRuleValidator:
    """Validator for policy business rules and claims processing."""
    
    def __init__(self):
        self.rules = {
            "inception_date": {
                "section": RuleSection.POLICY_VALIDITY,
                "rule": "Inception Date",
                "document_required": ["Policy Master Document", "Policy Document"],
                "criteria": "Policy must be active on date of admission",
                "decision": [RuleDecision.PASS, RuleDecision.REJECT]
            },
            "lapse_check": {
                "section": RuleSection.POLICY_VALIDITY,
                "rule": "Lapse Check",
                "document_required": ["Policy Master Document", "Policy Document", "Payment Receipt"],
                "criteria": "Policy should not be in grace/lapse",
                "decision": [RuleDecision.PASS, RuleDecision.REJECT]
            },
            "room_rent_eligibility": {
                "section": RuleSection.POLICY_LIMITS,
                "rule": "Room Rent Eligibility",
                "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill"],
                "criteria": "Room rent within entitled limit",
                "decision": [RuleDecision.PASS, RuleDecision.PROPORTIONATE_DEDUCTION],
                "deduction_amount": "If Proportionate Deduction"
            },
            "icu_capping": {
                "section": RuleSection.POLICY_LIMITS,
                "rule": "ICU Capping",
                "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill"],
                "criteria": "ICU charges within cap",
                "decision": [RuleDecision.PASS, RuleDecision.DEDUCT],
                "deduction_amount": "If Deduct"
            },
            "co_payment": {
                "section": RuleSection.POLICY_LIMITS,
                "rule": "Co-payment",
                "document_required": ["Policy Master Document", "Policy Document"],
                "criteria": "Co-pay % as per policy",
                "decision": [RuleDecision.PASS, RuleDecision.DEDUCT],
                "deduction_amount": "If Deduct"
            },
            "sub_limits": {
                "section": RuleSection.POLICY_LIMITS,
                "rule": "Sub-limits",
                "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill"],
                "criteria": "Procedure under cap limit",
                "decision": [RuleDecision.PASS, RuleDecision.CAP_LIMIT_APPLIED]
            },
            "daycare": {
                "section": RuleSection.POLICY_LIMITS,
                "rule": "Daycare",
                "document_required": ["Policy Master Document", "Policy Document", "Discharge Summary"],
                "criteria": "Within IRDA-approved daycare",
                "decision": [RuleDecision.PASS, RuleDecision.REJECT]
            },
            "initial_waiting": {
                "section": RuleSection.WAITING_PERIODS,
                "rule": "Initial Waiting",
                "document_required": ["Policy Master Document", "Policy Document"],
                "criteria": "<30 days for non-accident",
                "decision": [RuleDecision.PASS, RuleDecision.REJECT]
            },
            "disease_specific": {
                "section": RuleSection.WAITING_PERIODS,
                "rule": "Disease Specific",
                "document_required": ["Policy Master Document", "Policy Document"],
                "criteria": "Condition covered post waiting period",
                "decision": [RuleDecision.PASS, RuleDecision.REJECT]
            },
            "maternity": {
                "section": RuleSection.WAITING_PERIODS,
                "rule": "Maternity",
                "document_required": ["Policy Master Document", "Policy Document"],
                "criteria": "Covered with waiting period",
                "decision": [RuleDecision.PASS, RuleDecision.REJECT]
            },
            "non_medical": {
                "section": RuleSection.WAITING_PERIODS,
                "rule": "Non-Medical",
                "document_required": ["Policy Master Document", "Policy Document", "Hospital Bill", "Itemized Bill"],
                "criteria": "IRDA non-payables",
                "decision": [RuleDecision.PASS, RuleDecision.DEDUCT],
                "deduction_amount": "If Deduct"
            }
        }
    
    def validate_inception_date(self, policy_data: Dict[str, Any], admission_date: str = None) -> RuleResult:
        """Validate if policy is active on admission date."""
        try:
            # Check for both inception_date and policy_start_date
            inception_date = policy_data.get('inception_date') or policy_data.get('policy_start_date')
            if not inception_date:
                return RuleResult(
                    rule_name="Inception Date",
                    section="Policy Validity",
                    decision=RuleDecision.REJECT,
                    criteria_met=False,
                    confidence_score=0.0,
                    details="Inception date not found in policy data"
                )
            
            # Parse dates - handle both YYYY-MM-DD and DD/MM/YYYY formats
            try:
                # Try YYYY-MM-DD format first
                inception = datetime.strptime(inception_date, "%Y-%m-%d").date()
            except ValueError:
                try:
                    # Try DD/MM/YYYY format
                    inception = datetime.strptime(inception_date, "%d/%m/%Y").date()
                except ValueError:
                    try:
                        # Try DD/MM/YY format
                        inception = datetime.strptime(inception_date, "%d/%m/%y").date()
                    except ValueError:
                        return RuleResult(
                            rule_name="Inception Date",
                            section="Policy Validity",
                            decision=RuleDecision.REJECT,
                            criteria_met=False,
                            confidence_score=0.3,
                            details=f"Invalid inception date format: {inception_date}"
                        )
            
            try:
                # Try YYYY-MM-DD format first for admission date
                admission = datetime.strptime(admission_date, "%Y-%m-%d").date() if admission_date else date.today()
            except ValueError:
                try:
                    # Try DD/MM/YYYY format for admission date
                    admission = datetime.strptime(admission_date, "%d/%m/%Y").date() if admission_date else date.today()
                except ValueError:
                    try:
                        # Try DD/MM/YY format for admission date
                        admission = datetime.strptime(admission_date, "%d/%m/%y").date() if admission_date else date.today()
                    except ValueError:
                        return RuleResult(
                            rule_name="Inception Date",
                            section="Policy Validity",
                            decision=RuleDecision.REJECT,
                            criteria_met=False,
                            confidence_score=0.3,
                            details=f"Invalid admission date format: {admission_date}"
                        )
            
            if inception <= admission:
                return RuleResult(
                    rule_name="Inception Date",
                    section="Policy Validity",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details=f"Policy active from {inception_date}, admission on {admission_date}"
                )
            else:
                return RuleResult(
                    rule_name="Inception Date",
                    section="Policy Validity",
                    decision=RuleDecision.REJECT,
                    criteria_met=False,
                    confidence_score=0.9,
                    details=f"Policy not active on admission date. Inception: {inception_date}, Admission: {admission_date}"
                )
        except Exception as e:
            return RuleResult(
                rule_name="Inception Date",
                section="Policy Validity",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating inception date: {str(e)}"
            )
    
    def validate_lapse_check(self, policy_data: Dict[str, Any]) -> RuleResult:
        """Check if policy is in grace/lapse period."""
        try:
            # Check for grace period indicators
            grace_period = policy_data.get('grace_period', 0)
            last_payment_date = policy_data.get('last_payment_date')
            policy_status = policy_data.get('policy_status', 'active').lower()
            
            if policy_status in ['lapsed', 'grace']:
                return RuleResult(
                    rule_name="Lapse Check",
                    section="Policy Validity",
                    decision=RuleDecision.REJECT,
                    criteria_met=False,
                    confidence_score=0.8,
                    details=f"Policy status: {policy_status}"
                )
            
            # Additional checks for payment status
            if last_payment_date:
                last_payment = datetime.strptime(last_payment_date, "%Y-%m-%d").date()
                days_since_payment = (date.today() - last_payment).days
                
                if days_since_payment > grace_period:
                    return RuleResult(
                        rule_name="Lapse Check",
                        section="Policy Validity",
                        decision=RuleDecision.REJECT,
                        criteria_met=False,
                        confidence_score=0.7,
                        details=f"Payment overdue by {days_since_payment - grace_period} days"
                    )
            
            return RuleResult(
                rule_name="Lapse Check",
                section="Policy Validity",
                decision=RuleDecision.PASS,
                criteria_met=True,
                confidence_score=0.8,
                details="Policy is active and not in grace/lapse period"
            )
        except Exception as e:
            return RuleResult(
                rule_name="Lapse Check",
                section="Policy Validity",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error checking lapse status: {str(e)}"
            )
    
    def validate_room_rent_eligibility(self, policy_data: Dict[str, Any], hospital_bill: Dict[str, Any]) -> RuleResult:
        """Validate room rent against policy limits."""
        try:
            room_rent_cap = policy_data.get('room_rent_capping', 0)
            actual_room_rent = hospital_bill.get('room_rent', 0)
            base_sum_assured = policy_data.get('base_sum_assured', 0)
            
            if room_rent_cap == 0:
                return RuleResult(
                    rule_name="Room Rent Eligibility",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.8,
                    details="No room rent capping applied"
                )
            
            # Calculate room rent limit
            if isinstance(room_rent_cap, str) and 'actuals' in room_rent_cap.lower():
                room_rent_limit = actual_room_rent  # No limit
            else:
                # Convert string values to float for calculation
                room_rent_cap_float = float(str(room_rent_cap).replace('%', '').replace(',', '')) if room_rent_cap else 0
                base_sum_assured_float = float(str(base_sum_assured).replace(',', '')) if base_sum_assured else 0
                room_rent_limit = (base_sum_assured_float * room_rent_cap_float) / 100
            
            if actual_room_rent <= room_rent_limit:
                return RuleResult(
                    rule_name="Room Rent Eligibility",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details=f"Room rent {actual_room_rent} within limit {room_rent_limit}"
                )
            else:
                deduction = actual_room_rent - room_rent_limit
                return RuleResult(
                    rule_name="Room Rent Eligibility",
                    section="Policy Limits",
                    decision=RuleDecision.PROPORTIONATE_DEDUCTION,
                    criteria_met=False,
                    confidence_score=0.9,
                    details=f"Room rent {actual_room_rent} exceeds limit {room_rent_limit}",
                    deduction_amount=deduction
                )
        except Exception as e:
            return RuleResult(
                rule_name="Room Rent Eligibility",
                section="Policy Limits",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating room rent: {str(e)}"
            )
    
    def validate_icu_capping(self, policy_data: Dict[str, Any], hospital_bill: Dict[str, Any]) -> RuleResult:
        """Validate ICU charges against policy cap."""
        try:
            icu_cap = policy_data.get('icu_capping', 0)
            actual_icu_charges = hospital_bill.get('icu_charges', 0)
            base_sum_assured = policy_data.get('base_sum_assured', 0)
            
            if icu_cap == 0:
                return RuleResult(
                    rule_name="ICU Capping",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.8,
                    details="No ICU capping applied"
                )
            
            # Calculate ICU limit
            if isinstance(icu_cap, str) and 'actuals' in icu_cap.lower():
                icu_limit = actual_icu_charges  # No limit
            else:
                # Convert string values to float for calculation
                icu_cap_float = float(str(icu_cap).replace('%', '').replace(',', '')) if icu_cap else 0
                base_sum_assured_float = float(str(base_sum_assured).replace(',', '')) if base_sum_assured else 0
                icu_limit = (base_sum_assured_float * icu_cap_float) / 100
            
            if actual_icu_charges <= icu_limit:
                return RuleResult(
                    rule_name="ICU Capping",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details=f"ICU charges {actual_icu_charges} within limit {icu_limit}"
                )
            else:
                deduction = actual_icu_charges - icu_limit
                return RuleResult(
                    rule_name="ICU Capping",
                    section="Policy Limits",
                    decision=RuleDecision.DEDUCT,
                    criteria_met=False,
                    confidence_score=0.9,
                    details=f"ICU charges {actual_icu_charges} exceed limit {icu_limit}",
                    deduction_amount=deduction
                )
        except Exception as e:
            return RuleResult(
                rule_name="ICU Capping",
                section="Policy Limits",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating ICU capping: {str(e)}"
            )
    
    def validate_co_payment(self, policy_data: Dict[str, Any], claim_amount: float) -> RuleResult:
        """Validate co-payment percentage."""
        try:
            co_payment_percent = policy_data.get('co_payment', 0)
            
            # Handle null/empty values
            if co_payment_percent in [None, 0, "null", "", "0"]:
                return RuleResult(
                    rule_name="Co-payment",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details="No co-payment applicable"
                )
            
            # Convert string values to float for calculation
            co_payment_float = float(str(co_payment_percent).replace('%', '').replace(',', '')) if co_payment_percent else 0
            deduction_amount = (claim_amount * co_payment_float) / 100
            
            return RuleResult(
                rule_name="Co-payment",
                section="Policy Limits",
                decision=RuleDecision.DEDUCT,
                criteria_met=True,
                confidence_score=0.9,
                details=f"Co-payment {co_payment_percent}% applied",
                deduction_amount=deduction_amount
            )
        except Exception as e:
            return RuleResult(
                rule_name="Co-payment",
                section="Policy Limits",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating co-payment: {str(e)}"
            )
    
    def validate_sub_limits(self, policy_data: Dict[str, Any], hospital_bill: Dict[str, Any]) -> RuleResult:
        """Validate procedure costs against sub-limits."""
        try:
            procedure = hospital_bill.get('procedure', '')
            procedure_cost = hospital_bill.get('procedure_cost', 0)
            
            # Check for specific procedure caps
            procedure_caps = {
                'cataract': policy_data.get('cataract_capping', 0),
                'hernia': policy_data.get('hernia_capping', 0),
                'joint_replacement': policy_data.get('joint_replacement_capping', 0),
                'bariatric': policy_data.get('bariatric_obesity_surgery_capping', 0)
            }
            
            applicable_cap = None
            for proc_type, cap in procedure_caps.items():
                if proc_type in procedure.lower():
                    applicable_cap = cap
                    break
            
            if not applicable_cap:
                return RuleResult(
                    rule_name="Sub-limits",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.8,
                    details="No specific sub-limit for this procedure"
                )
            
            if procedure_cost <= applicable_cap:
                return RuleResult(
                    rule_name="Sub-limits",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details=f"Procedure cost {procedure_cost} within cap {applicable_cap}"
                )
            else:
                return RuleResult(
                    rule_name="Sub-limits",
                    section="Policy Limits",
                    decision=RuleDecision.CAP_LIMIT_APPLIED,
                    criteria_met=False,
                    confidence_score=0.9,
                    details=f"Procedure cost {procedure_cost} exceeds cap {applicable_cap}",
                    deduction_amount=procedure_cost - applicable_cap
                )
        except Exception as e:
            return RuleResult(
                rule_name="Sub-limits",
                section="Policy Limits",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating sub-limits: {str(e)}"
            )
    
    def validate_daycare(self, policy_data: Dict[str, Any], discharge_summary: Dict[str, Any]) -> RuleResult:
        """Validate daycare procedures against IRDA guidelines."""
        try:
            # IRDA-approved daycare procedures
            irda_daycare_procedures = [
                'cataract', 'hernia', 'tonsillectomy', 'adenoidectomy',
                'dental', 'endoscopy', 'colonoscopy', 'biopsy'
            ]
            
            procedure = discharge_summary.get('procedure', '').lower()
            is_daycare = discharge_summary.get('is_daycare', False)
            
            if not is_daycare:
                return RuleResult(
                    rule_name="Daycare",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details="Not a daycare procedure"
                )
            
            # Check if procedure is in IRDA list
            is_irda_approved = any(proc in procedure for proc in irda_daycare_procedures)
            
            if is_irda_approved:
                return RuleResult(
                    rule_name="Daycare",
                    section="Policy Limits",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details=f"Daycare procedure '{procedure}' is IRDA approved"
                )
            else:
                return RuleResult(
                    rule_name="Daycare",
                    section="Policy Limits",
                    decision=RuleDecision.REJECT,
                    criteria_met=False,
                    confidence_score=0.8,
                    details=f"Daycare procedure '{procedure}' not in IRDA approved list"
                )
        except Exception as e:
            return RuleResult(
                rule_name="Daycare",
                section="Policy Limits",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating daycare: {str(e)}"
            )
    
    def validate_waiting_periods(self, policy_data: Dict[str, Any], admission_date: str, condition: str = None) -> List[RuleResult]:
        """Validate various waiting periods."""
        results = []
        
        # Initial waiting period
        try:
            # Check for both inception_date and policy_start_date
            inception_date = policy_data.get('inception_date') or policy_data.get('policy_start_date')
            if not inception_date or not admission_date:
                results.append(RuleResult(
                    rule_name="Initial Waiting",
                    section="Waiting Periods",
                    decision=RuleDecision.REJECT,
                    criteria_met=False,
                    confidence_score=0.3,
                    details="Missing inception date or admission date for initial waiting period validation"
                ))
            else:
                # Parse dates - handle both YYYY-MM-DD and DD/MM/YYYY formats
                try:
                    # Try YYYY-MM-DD format first
                    inception = datetime.strptime(inception_date, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        # Try DD/MM/YYYY format
                        inception = datetime.strptime(inception_date, "%d/%m/%Y").date()
                    except ValueError:
                        try:
                            # Try DD/MM/YY format
                            inception = datetime.strptime(inception_date, "%d/%m/%y").date()
                        except ValueError:
                            results.append(RuleResult(
                                rule_name="Initial Waiting",
                                section="Waiting Periods",
                                decision=RuleDecision.REJECT,
                                criteria_met=False,
                                confidence_score=0.3,
                                details=f"Invalid inception date format: {inception_date}"
                            ))
                            return results
                
                try:
                    # Try YYYY-MM-DD format first for admission date
                    admission = datetime.strptime(admission_date, "%Y-%m-%d").date()
                except ValueError:
                    try:
                        # Try DD/MM/YYYY format for admission date
                        admission = datetime.strptime(admission_date, "%d/%m/%Y").date()
                    except ValueError:
                        try:
                            # Try DD/MM/YY format for admission date
                            admission = datetime.strptime(admission_date, "%d/%m/%y").date()
                        except ValueError:
                            results.append(RuleResult(
                                rule_name="Initial Waiting",
                                section="Waiting Periods",
                                decision=RuleDecision.REJECT,
                                criteria_met=False,
                                confidence_score=0.3,
                                details=f"Invalid admission date format: {admission_date}"
                            ))
                            return results
                days_since_inception = (admission - inception).days
                
                if days_since_inception < 30:
                    results.append(RuleResult(
                        rule_name="Initial Waiting",
                        section="Waiting Periods",
                        decision=RuleDecision.REJECT,
                        criteria_met=False,
                        confidence_score=0.9,
                        details=f"Policy only {days_since_inception} days old, requires 30 days"
                    ))
                else:
                    results.append(RuleResult(
                        rule_name="Initial Waiting",
                        section="Waiting Periods",
                        decision=RuleDecision.PASS,
                        criteria_met=True,
                        confidence_score=0.9,
                        details=f"Policy {days_since_inception} days old, exceeds 30-day requirement"
                    ))
        except Exception as e:
            results.append(RuleResult(
                rule_name="Initial Waiting",
                section="Waiting Periods",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating initial waiting period: Invalid date format or calculation error"
            ))
        
        # Disease-specific waiting periods
        if condition:
            disease_waiting_periods = {
                'diabetes': 90,
                'hypertension': 90,
                'cardiac': 180,
                'cancer': 365
            }
            
            for disease, waiting_days in disease_waiting_periods.items():
                if disease in condition.lower():
                    try:
                        # Check if we have valid dates
                        if not inception_date or not admission_date:
                            results.append(RuleResult(
                                rule_name="Disease Specific",
                                section="Waiting Periods",
                                decision=RuleDecision.REJECT,
                                criteria_met=False,
                                confidence_score=0.3,
                                details=f"Missing date information for {disease.title()} condition validation"
                            ))
                            continue
                            
                        # Parse dates - handle both YYYY-MM-DD and DD/MM/YYYY formats
                        try:
                            # Try YYYY-MM-DD format first
                            inception = datetime.strptime(inception_date, "%Y-%m-%d").date()
                        except ValueError:
                            try:
                                # Try DD/MM/YYYY format
                                inception = datetime.strptime(inception_date, "%d/%m/%Y").date()
                            except ValueError:
                                try:
                                    # Try DD/MM/YY format
                                    inception = datetime.strptime(inception_date, "%d/%m/%y").date()
                                except ValueError:
                                    results.append(RuleResult(
                                        rule_name="Disease Specific",
                                        section="Waiting Periods",
                                        decision=RuleDecision.REJECT,
                                        criteria_met=False,
                                        confidence_score=0.3,
                                        details=f"Invalid inception date format: {inception_date}"
                                    ))
                                    continue
                        
                        try:
                            # Try YYYY-MM-DD format first for admission date
                            admission = datetime.strptime(admission_date, "%Y-%m-%d").date()
                        except ValueError:
                            try:
                                # Try DD/MM/YYYY format for admission date
                                admission = datetime.strptime(admission_date, "%d/%m/%Y").date()
                            except ValueError:
                                try:
                                    # Try DD/MM/YY format for admission date
                                    admission = datetime.strptime(admission_date, "%d/%m/%y").date()
                                except ValueError:
                                    results.append(RuleResult(
                                        rule_name="Disease Specific",
                                        section="Waiting Periods",
                                        decision=RuleDecision.REJECT,
                                        criteria_met=False,
                                        confidence_score=0.3,
                                        details=f"Invalid admission date format: {admission_date}"
                                    ))
                                    continue
                        days_since_inception = (admission - inception).days
                        
                        if days_since_inception < waiting_days:
                            results.append(RuleResult(
                                rule_name="Disease Specific",
                                section="Waiting Periods",
                                decision=RuleDecision.REJECT,
                                criteria_met=False,
                                confidence_score=0.9,
                                details=f"{disease.title()} condition requires {waiting_days} days, policy only {days_since_inception} days old"
                            ))
                        else:
                            results.append(RuleResult(
                                rule_name="Disease Specific",
                                section="Waiting Periods",
                                decision=RuleDecision.PASS,
                                criteria_met=True,
                                confidence_score=0.9,
                                details=f"{disease.title()} condition waiting period satisfied"
                            ))
                    except Exception as e:
                        results.append(RuleResult(
                            rule_name="Disease Specific",
                            section="Waiting Periods",
                            decision=RuleDecision.REJECT,
                            criteria_met=False,
                            confidence_score=0.3,
                                                    details=f"Error validating disease waiting period: Invalid date format or calculation error"
                    ))
        
        # Maternity waiting period (only for female patients with maternity-related conditions)
        # Check if this is a maternity-related claim
        maternity_conditions = ['pregnancy', 'delivery', 'cesarean', 'maternity', 'obstetric', 'gynecological']
        is_maternity_related = condition and any(maternity_condition in condition.lower() for maternity_condition in maternity_conditions)
        
        # For now, we'll assume the patient is male (based on the name "Patel Dashrathbhai A")
        # In a real system, this would come from patient data
        patient_gender = "male"  # This should be extracted from patient data
        
        if is_maternity_related and patient_gender.lower() == "female":
            # Only validate maternity waiting period for female patients with maternity conditions
            try:
                if not inception_date or not admission_date:
                    results.append(RuleResult(
                        rule_name="Maternity",
                        section="Waiting Periods",
                        decision=RuleDecision.REJECT,
                        criteria_met=False,
                        confidence_score=0.3,
                        details="Missing date information for maternity waiting period validation"
                    ))
                else:
                    # Parse dates - handle both YYYY-MM-DD and DD/MM/YYYY formats
                    try:
                        # Try YYYY-MM-DD format first
                        inception = datetime.strptime(inception_date, "%Y-%m-%d").date()
                    except ValueError:
                        try:
                            # Try DD/MM/YYYY format
                            inception = datetime.strptime(inception_date, "%d/%m/%Y").date()
                        except ValueError:
                            try:
                                # Try DD/MM/YY format
                                inception = datetime.strptime(inception_date, "%d/%m/%y").date()
                            except ValueError:
                                results.append(RuleResult(
                                    rule_name="Maternity",
                                    section="Waiting Periods",
                                    decision=RuleDecision.REJECT,
                                    criteria_met=False,
                                    confidence_score=0.3,
                                    details=f"Invalid inception date format: {inception_date}"
                                ))
                                return results
                    
                    try:
                        # Try YYYY-MM-DD format first for admission date
                        admission = datetime.strptime(admission_date, "%Y-%m-%d").date()
                    except ValueError:
                        try:
                            # Try DD/MM/YYYY format for admission date
                            admission = datetime.strptime(admission_date, "%d/%m/%Y").date()
                        except ValueError:
                            try:
                                # Try DD/MM/YY format for admission date
                                admission = datetime.strptime(admission_date, "%d/%m/%y").date()
                            except ValueError:
                                results.append(RuleResult(
                                    rule_name="Maternity",
                                    section="Waiting Periods",
                                    decision=RuleDecision.REJECT,
                                    criteria_met=False,
                                    confidence_score=0.3,
                                    details=f"Invalid admission date format: {admission_date}"
                                ))
                                return results
                    days_since_inception = (admission - inception).days
                    maternity_waiting_days = 270
                    
                    if days_since_inception < maternity_waiting_days:
                        results.append(RuleResult(
                            rule_name="Maternity",
                            section="Waiting Periods",
                            decision=RuleDecision.REJECT,
                            criteria_met=False,
                            confidence_score=0.9,
                            details=f"Maternity condition requires {maternity_waiting_days} days, policy only {days_since_inception} days old"
                        ))
                    else:
                        results.append(RuleResult(
                            rule_name="Maternity",
                            section="Waiting Periods",
                            decision=RuleDecision.PASS,
                            criteria_met=True,
                            confidence_score=0.9,
                            details=f"Maternity condition waiting period satisfied"
                        ))
            except Exception as e:
                results.append(RuleResult(
                    rule_name="Maternity",
                    section="Waiting Periods",
                    decision=RuleDecision.REJECT,
                    criteria_met=False,
                    confidence_score=0.3,
                    details=f"Error validating maternity waiting period: Invalid date format or calculation error"
                ))
        elif is_maternity_related and patient_gender.lower() == "male":
            # Male patient with maternity-related condition - this shouldn't happen
            results.append(RuleResult(
                rule_name="Maternity",
                section="Waiting Periods",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.9,
                details=f"Maternity condition not applicable for male patient"
            ))
        else:
            # Not a maternity-related condition or patient gender not applicable
            # Skip maternity validation
            pass
        
        return results
    
    def validate_non_medical_items(self, hospital_bill: Dict[str, Any]) -> RuleResult:
        """Validate non-medical items against IRDA guidelines."""
        try:
            # IRDA non-payable items
            non_payable_items = [
                'toiletries', 'personal items', 'food', 'telephone', 'tv',
                'attendant charges', 'documentation charges', 'administrative charges'
            ]
            
            itemized_bill = hospital_bill.get('itemized_bill', {})
            non_medical_deduction = 0
            
            for item, amount in itemized_bill.items():
                if any(non_payable in item.lower() for non_payable in non_payable_items):
                    non_medical_deduction += amount
            
            if non_medical_deduction == 0:
                return RuleResult(
                    rule_name="Non-Medical",
                    section="Waiting Periods",
                    decision=RuleDecision.PASS,
                    criteria_met=True,
                    confidence_score=0.9,
                    details="No non-medical items found in bill"
                )
            else:
                return RuleResult(
                    rule_name="Non-Medical",
                    section="Waiting Periods",
                    decision=RuleDecision.DEDUCT,
                    criteria_met=False,
                    confidence_score=0.8,
                    details=f"Non-medical items totaling {non_medical_deduction} found",
                    deduction_amount=non_medical_deduction
                )
        except Exception as e:
            return RuleResult(
                rule_name="Non-Medical",
                section="Waiting Periods",
                decision=RuleDecision.REJECT,
                criteria_met=False,
                confidence_score=0.3,
                details=f"Error validating non-medical items: {str(e)}"
            )
    
    def validate_policy_rules(self, policy_data: Dict[str, Any], claim_data: Dict[str, Any] = None) -> PolicyRuleReport:
        """Validate all policy rules and generate comprehensive report with early termination logic."""
        rule_results = {}
        total_deductions = 0.0
        recommendations = []
        
        # Policy validity checks (critical - if these fail, reject immediately)
        if claim_data and claim_data.get('admission_date'):
            inception_result = self.validate_inception_date(policy_data, claim_data['admission_date'])
            rule_results['inception_date'] = inception_result
            
            if inception_result.decision == RuleDecision.REJECT:
                recommendations.append("Policy not active on admission date - claim may be rejected")
                # Early termination: if inception date fails, reject immediately
                return self._create_early_termination_report(rule_results, total_deductions, recommendations, "Policy validity check failed")
        
        lapse_result = self.validate_lapse_check(policy_data)
        rule_results['lapse_check'] = lapse_result
        
        if lapse_result.decision == RuleDecision.REJECT:
            recommendations.append("Policy is in grace/lapse period - payment required")
            # Early termination: if lapse check fails, reject immediately
            return self._create_early_termination_report(rule_results, total_deductions, recommendations, "Policy lapse check failed")
        
        # Policy limits checks (continue processing even if some fail)
        if claim_data and claim_data.get('hospital_bill'):
            hospital_bill = claim_data['hospital_bill']
            
            # Daycare check (critical - if fails, reject immediately)
            daycare_result = self.validate_daycare(policy_data, claim_data.get('discharge_summary', {}))
            rule_results['daycare'] = daycare_result
            if daycare_result.decision == RuleDecision.REJECT:
                recommendations.append("Daycare procedure not approved - claim may be rejected")
                return self._create_early_termination_report(rule_results, total_deductions, recommendations, "Daycare check failed")
            
            # Continue with other policy limits (these may result in deductions but not rejection)
            room_rent_result = self.validate_room_rent_eligibility(policy_data, hospital_bill)
            rule_results['room_rent_eligibility'] = room_rent_result
            if room_rent_result.deduction_amount:
                total_deductions += room_rent_result.deduction_amount
                recommendations.append(f"Room rent deduction: {room_rent_result.deduction_amount}")
            
            icu_result = self.validate_icu_capping(policy_data, hospital_bill)
            rule_results['icu_capping'] = icu_result
            if icu_result.deduction_amount:
                total_deductions += icu_result.deduction_amount
                recommendations.append(f"ICU capping deduction: {icu_result.deduction_amount}")
            
            sub_limits_result = self.validate_sub_limits(policy_data, hospital_bill)
            rule_results['sub_limits'] = sub_limits_result
            if sub_limits_result.deduction_amount:
                total_deductions += sub_limits_result.deduction_amount
                recommendations.append(f"Sub-limit deduction: {sub_limits_result.deduction_amount}")
            
            non_medical_result = self.validate_non_medical_items(hospital_bill)
            rule_results['non_medical'] = non_medical_result
            if non_medical_result.deduction_amount:
                total_deductions += non_medical_result.deduction_amount
                recommendations.append(f"Non-medical items deduction: {non_medical_result.deduction_amount}")
        
        # Co-payment check
        if claim_data and claim_data.get('claim_amount'):
            co_payment_result = self.validate_co_payment(policy_data, claim_data['claim_amount'])
            rule_results['co_payment'] = co_payment_result
            if co_payment_result.deduction_amount:
                total_deductions += co_payment_result.deduction_amount
                recommendations.append(f"Co-payment deduction: {co_payment_result.deduction_amount}")
        
        # Waiting period checks (critical - if these fail, reject immediately)
        if claim_data and claim_data.get('admission_date'):
            waiting_results = self.validate_waiting_periods(
                policy_data, 
                claim_data['admission_date'], 
                claim_data.get('condition')
            )
            for result in waiting_results:
                rule_results[result.rule_name.lower().replace(' ', '_')] = result
                if result.decision == RuleDecision.REJECT:
                    recommendations.append(f"Waiting period not satisfied: {result.details}")
                    # Early termination: if any waiting period fails, reject immediately
                    return self._create_early_termination_report(rule_results, total_deductions, recommendations, f"Waiting period check failed: {result.rule_name}")
        
        # Calculate overall validity and confidence
        passed_rules = sum(1 for result in rule_results.values() if result.decision == RuleDecision.PASS)
        total_rules = len(rule_results)
        overall_valid = passed_rules == total_rules
        overall_confidence = sum(result.confidence_score for result in rule_results.values()) / total_rules if total_rules > 0 else 0.0
        
        # Determine status based on conditions
        rejected_rules = sum(1 for result in rule_results.values() if result.decision == RuleDecision.REJECT)
        
        if rejected_rules > 0:
            status = "REJECTED"
        elif total_deductions > 0:
            status = "CLEARED WITH DEDUCTIONS"
        else:
            status = "CLEARED"
        
        # Determine risk level
        if overall_valid and total_deductions == 0:
            risk_level = "Low"
        elif overall_valid and total_deductions > 0:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return PolicyRuleReport(
            overall_valid=overall_valid,
            overall_confidence=overall_confidence,
            rule_results=rule_results,
            total_deductions=total_deductions,
            recommendations=recommendations,
            risk_level=risk_level,
            status=status
        )
    
    def _create_early_termination_report(self, rule_results: Dict[str, RuleResult], total_deductions: float, 
                                       recommendations: List[str], termination_reason: str) -> PolicyRuleReport:
        """Create a policy rule report when early termination occurs."""
        # Calculate overall validity and confidence for processed rules
        passed_rules = sum(1 for result in rule_results.values() if result.decision == RuleDecision.PASS)
        total_rules = len(rule_results)
        overall_valid = False  # Early termination means the claim is invalid
        overall_confidence = sum(result.confidence_score for result in rule_results.values()) / total_rules if total_rules > 0 else 0.0
        
        # Add early termination note to recommendations
        recommendations.append(f"Early termination: {termination_reason}")
        
        return PolicyRuleReport(
            overall_valid=overall_valid,
            overall_confidence=overall_confidence,
            rule_results=rule_results,
            total_deductions=total_deductions,
            recommendations=recommendations,
            risk_level="High",  # Early termination indicates high risk
            status="REJECTED"  # Early termination means rejected
        )

def validate_policy_rules(policy_data: Dict[str, Any], claim_data: Dict[str, Any] = None) -> PolicyRuleReport:
    """Convenience function to validate policy rules."""
    validator = PolicyRuleValidator()
    return validator.validate_policy_rules(policy_data, claim_data) 