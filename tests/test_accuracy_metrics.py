#!/usr/bin/env python3
"""
Test script for accuracy metrics system.
"""

import json
import sys
import os
from pathlib import Path

# Add app directory to path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from accuracy_metrics import AccuracyTracker, track_extraction_accuracy

def create_sample_extraction_data():
    """Create sample extraction data for testing."""
    return {
        "openai": {
            "room_rent_capping": "2%",
            "icu_capping": "5%",
            "co_payment": "10%",
            "base_sum_assured": "500000",
            "cataract_capping": "25000",
            "hernia_capping": "30000",
            "joint_replacement_capping": "150000",
            "maternity_capping": "50000",
            "ambulance_charge_capping": "1000",
            "daily_cash_benefit": "2000",
            "modern_treatment_capping": "100%",
            "other_expenses_capping": "5%",
            "medical_practitioners_capping": "100%",
            "room_category_capping": "100%",
            "treatment_hazardous_sports_capping": "0%",
            "dialysis_capping": "50000",
            "chemotherapy_capping": "100000",
            "radiotherapy_capping": "100000",
            "consumable_non_medical_capping": "5%",
            "opd_daycare_domiciliary_capping": "10000",
            "pre_post_hospitalization_capping": "30000",
            "diagnostic_tests_capping": "15000",
            "implants_stents_prosthetics_capping": "100000",
            "mental_illness_treatment_capping": "50000",
            "organ_donor_expenses_capping": "50000",
            "bariatric_obesity_surgery_capping": "150000",
            "cancer_treatment_capping": "200000",
            "internal_congenital_disease_capping": "50000",
            "ayush_hospitalization_capping": "25000",
            "vaccination_preventive_capping": "5000",
            "artificial_prostheses_aids_capping": "25000",
            "processing_time": 25.5
        },
        "mistral": {
            "room_rent_capping": "2%",
            "icu_capping": "5%",
            "co_payment": "10%",
            "base_sum_assured": "500000",
            "cataract_capping": "25000",
            "hernia_capping": "30000",
            "joint_replacement_capping": "150000",
            "maternity_capping": "50000",
            "ambulance_charge_capping": "1000",
            "daily_cash_benefit": "2000",
            "modern_treatment_capping": "100%",
            "other_expenses_capping": "5%",
            "medical_practitioners_capping": "100%",
            "room_category_capping": "100%",
            "treatment_hazardous_sports_capping": "0%",
            "dialysis_capping": "50000",
            "chemotherapy_capping": "100000",
            "radiotherapy_capping": "100000",
            "consumable_non_medical_capping": "5%",
            "opd_daycare_domiciliary_capping": "10000",
            "pre_post_hospitalization_capping": "30000",
            "diagnostic_tests_capping": "15000",
            "implants_stents_prosthetics_capping": "100000",
            "mental_illness_treatment_capping": "50000",
            "organ_donor_expenses_capping": "50000",
            "bariatric_obesity_surgery_capping": "150000",
            "cancer_treatment_capping": "200000",
            "internal_congenital_disease_capping": "50000",
            "ayush_hospitalization_capping": "25000",
            "vaccination_preventive_capping": "5000",
            "artificial_prostheses_aids_capping": "25000",
            "processing_time": 28.2
        },
        "gemini": {
            "room_rent_capping": "2%",
            "icu_capping": "5%",
            "co_payment": "10%",
            "base_sum_assured": "500000",
            "cataract_capping": "25000",
            "hernia_capping": "30000",
            "joint_replacement_capping": "150000",
            "maternity_capping": "50000",
            "ambulance_charge_capping": "1000",
            "daily_cash_benefit": "2000",
            "modern_treatment_capping": "100%",
            "other_expenses_capping": "5%",
            "medical_practitioners_capping": "100%",
            "room_category_capping": "100%",
            "treatment_hazardous_sports_capping": "0%",
            "dialysis_capping": "50000",
            "chemotherapy_capping": "100000",
            "radiotherapy_capping": "100000",
            "consumable_non_medical_capping": "5%",
            "opd_daycare_domiciliary_capping": "10000",
            "pre_post_hospitalization_capping": "30000",
            "diagnostic_tests_capping": "15000",
            "implants_stents_prosthetics_capping": "100000",
            "mental_illness_treatment_capping": "50000",
            "organ_donor_expenses_capping": "50000",
            "bariatric_obesity_surgery_capping": "150000",
            "cancer_treatment_capping": "200000",
            "internal_congenital_disease_capping": "50000",
            "ayush_hospitalization_capping": "25000",
            "vaccination_preventive_capping": "5000",
            "artificial_prostheses_aids_capping": "25000",
            "processing_time": 22.8
        }
    }

def create_sample_ground_truth():
    """Create sample ground truth data."""
    return {
        "room_rent_capping": "2%",
        "icu_capping": "5%",
        "co_payment": "10%",
        "base_sum_assured": "500000",
        "cataract_capping": "25000",
        "hernia_capping": "30000",
        "joint_replacement_capping": "150000",
        "maternity_capping": "50000",
        "ambulance_charge_capping": "1000",
        "daily_cash_benefit": "2000",
        "modern_treatment_capping": "100%",
        "other_expenses_capping": "5%",
        "medical_practitioners_capping": "100%",
        "room_category_capping": "100%",
        "treatment_hazardous_sports_capping": "0%",
        "dialysis_capping": "50000",
        "chemotherapy_capping": "100000",
        "radiotherapy_capping": "100000",
        "consumable_non_medical_capping": "5%",
        "opd_daycare_domiciliary_capping": "10000",
        "pre_post_hospitalization_capping": "30000",
        "diagnostic_tests_capping": "15000",
        "implants_stents_prosthetics_capping": "100000",
        "mental_illness_treatment_capping": "50000",
        "organ_donor_expenses_capping": "50000",
        "bariatric_obesity_surgery_capping": "150000",
        "cancer_treatment_capping": "200000",
        "internal_congenital_disease_capping": "50000",
        "ayush_hospitalization_capping": "25000",
        "vaccination_preventive_capping": "5000",
        "artificial_prostheses_aids_capping": "25000"
    }

def test_accuracy_tracker():
    """Test the accuracy tracker functionality."""
    print("🧪 Testing Accuracy Metrics System")
    print("=" * 50)
    
    # Create sample data
    extraction_data = create_sample_extraction_data()
    ground_truth = create_sample_ground_truth()
    
    # Test accuracy tracking
    print("\n1. Testing accuracy comparison...")
    accuracy_report = track_extraction_accuracy(extraction_data, ground_truth, "test_extraction")
    
    print(f"✅ Accuracy report generated")
    print(f"   Best Model: {accuracy_report.overall_best_model}")
    print(f"   Overall Accuracy: {accuracy_report.overall_accuracy:.1f}%")
    
    # Print detailed results
    print("\n2. Model Comparison:")
    for model_name, model_accuracy in accuracy_report.model_comparison.items():
        print(f"   {model_name.upper()}:")
        print(f"     Accuracy: {model_accuracy.accuracy_percentage:.1f}%")
        print(f"     Confidence: {model_accuracy.average_confidence:.2f}")
        print(f"     Processing Time: {model_accuracy.processing_time:.1f}s")
        print(f"     Errors: {model_accuracy.error_count}")
    
    # Print recommendations
    print("\n3. Recommendations:")
    for i, recommendation in enumerate(accuracy_report.recommendations, 1):
        print(f"   {i}. {recommendation}")
    
    # Test field-level analysis
    print("\n4. Field Performance Analysis:")
    for field_name, performance in accuracy_report.field_performance.items():
        if any(perf.get("accuracy", 0) < 100 for perf in performance.values()):
            print(f"   ⚠️  {field_name}: Some models had issues")
        else:
            print(f"   ✅ {field_name}: All models accurate")
    
    # Save report
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    report_file = output_dir / "test_accuracy_report.json"
    tracker = AccuracyTracker()
    tracker.save_accuracy_report(accuracy_report, str(report_file))
    print(f"\n📄 Accuracy report saved to: {report_file}")
    
    return accuracy_report

def test_error_scenarios():
    """Test accuracy tracking with error scenarios."""
    print("\n🧪 Testing Error Scenarios")
    print("=" * 50)
    
    # Create data with errors
    error_extraction_data = {
        "openai": {
            "room_rent_capping": "150%",  # Out of range
            "icu_capping": "5%",
            "co_payment": "60%",  # Out of range
            "base_sum_assured": "500000",
            "cataract_capping": "25000",
            "hernia_capping": "30000",
            "joint_replacement_capping": "150000",
            "maternity_capping": "50000",
            "ambulance_charge_capping": "1000",
            "daily_cash_benefit": "2000",
            "modern_treatment_capping": "100%",
            "other_expenses_capping": "5%",
            "medical_practitioners_capping": "100%",
            "room_category_capping": "100%",
            "treatment_hazardous_sports_capping": "0%",
            "dialysis_capping": "50000",
            "chemotherapy_capping": "100000",
            "radiotherapy_capping": "100000",
            "consumable_non_medical_capping": "5%",
            "opd_daycare_domiciliary_capping": "10000",
            "pre_post_hospitalization_capping": "30000",
            "diagnostic_tests_capping": "15000",
            "implants_stents_prosthetics_capping": "100000",
            "mental_illness_treatment_capping": "50000",
            "organ_donor_expenses_capping": "50000",
            "bariatric_obesity_surgery_capping": "150000",
            "cancer_treatment_capping": "200000",
            "internal_congenital_disease_capping": "50000",
            "ayush_hospitalization_capping": "25000",
            "vaccination_preventive_capping": "5000",
            "artificial_prostheses_aids_capping": "25000",
            "processing_time": 25.5
        }
    }
    
    ground_truth = create_sample_ground_truth()
    
    # Test error tracking
    tracker = AccuracyTracker()
    model_accuracy = tracker.calculate_model_accuracy(
        "openai", error_extraction_data["openai"], ground_truth, 25.5
    )
    
    print(f"✅ Error scenario test completed")
    print(f"   Accuracy: {model_accuracy.accuracy_percentage:.1f}%")
    print(f"   Errors: {model_accuracy.error_count}")
    
    # Check specific field errors
    for field_accuracy in model_accuracy.field_accuracies:
        if not field_accuracy.is_correct:
            print(f"   ❌ {field_accuracy.field_name}: {field_accuracy.error_type}")
    
    return model_accuracy

def test_ground_truth_loading():
    """Test loading ground truth from file."""
    print("\n🧪 Testing Ground Truth Loading")
    print("=" * 50)
    
    tracker = AccuracyTracker()
    
    # Test loading from file
    ground_truth_file = "data/ground_truth_sample.json"
    if os.path.exists(ground_truth_file):
        ground_truth_data = tracker.load_ground_truth(ground_truth_file)
        if ground_truth_data:
            print(f"✅ Ground truth loaded from {ground_truth_file}")
            print(f"   Policy ID: {ground_truth_data.get('policy_id', 'N/A')}")
            print(f"   Policy Name: {ground_truth_data.get('policy_name', 'N/A')}")
            print(f"   Fields: {len(ground_truth_data.get('ground_truth_values', {}))}")
        else:
            print(f"❌ Failed to load ground truth from {ground_truth_file}")
    else:
        print(f"⚠️  Ground truth file not found: {ground_truth_file}")

def main():
    """Run all accuracy metrics tests."""
    print("🚀 Starting Accuracy Metrics System Tests")
    print("=" * 60)
    
    try:
        # Test basic functionality
        accuracy_report = test_accuracy_tracker()
        
        # Test error scenarios
        error_model = test_error_scenarios()
        
        # Test ground truth loading
        test_ground_truth_loading()
        
        print("\n✅ All accuracy metrics tests completed successfully!")
        print(f"📊 Best model accuracy: {accuracy_report.overall_accuracy:.1f}%")
        print(f"📊 Error model accuracy: {error_model.accuracy_percentage:.1f}%")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 