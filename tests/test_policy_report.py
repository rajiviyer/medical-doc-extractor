#!/usr/bin/env python3
import sys
import os
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "app"))

from policy_report_generator import generate_policy_rule_report
from policy_rules import PolicyRuleReport, RuleResult, RuleDecision, RuleSection

def create_sample_policy_rule_report():
    """Create a sample policy rule report for testing."""
    
    # Create sample rule results
    rule_results = [
        RuleResult(
            rule_name="Inception Date",
            decision=RuleDecision.PASS,
            reasoning="Policy is active on admission date",
            deduction_amount=0.0
        ),
        RuleResult(
            rule_name="Lapse Check",
            decision=RuleDecision.PASS,
            reasoning="Policy is not in grace/lapse period",
            deduction_amount=0.0
        ),
        RuleResult(
            rule_name="Room Rent Eligibility",
            decision=RuleDecision.FAIL,
            reasoning="Room rent exceeds entitled limit by 20%",
            deduction_amount=5000.0
        ),
        RuleResult(
            rule_name="ICU Capping",
            decision=RuleDecision.FAIL,
            reasoning="ICU charges exceed cap by 15%",
            deduction_amount=3000.0
        ),
        RuleResult(
            rule_name="Co-payment",
            decision=RuleDecision.FAIL,
            reasoning="Co-payment of 10% applied",
            deduction_amount=2500.0
        ),
        RuleResult(
            rule_name="Initial Waiting",
            decision=RuleDecision.PASS,
            reasoning="Waiting period satisfied",
            deduction_amount=0.0
        ),
        RuleResult(
            rule_name="Disease Specific",
            decision=RuleDecision.FAIL,
            reasoning="Disease waiting period not satisfied",
            deduction_amount=0.0
        ),
        RuleResult(
            rule_name="Non-Medical",
            decision=RuleDecision.FAIL,
            reasoning="Non-medical items deducted",
            deduction_amount=1500.0
        )
    ]
    
    # Create policy rule report
    report = PolicyRuleReport(
        overall_valid=False,
        risk_level="High",
        total_deductions=12000.0,
        rule_results=rule_results,
        recommendations=[
            "Policy not active on admission date - claim may be rejected",
            "Room rent deduction: ₹5,000",
            "ICU capping deduction: ₹3,000",
            "Co-payment deduction: ₹2,500",
            "Disease waiting period not satisfied",
            "Non-medical items deduction: ₹1,500"
        ]
    )
    
    return report

def test_markdown_report():
    """Test markdown report generation."""
    print("🧪 Testing Markdown Report Generation")
    
    report = create_sample_policy_rule_report()
    markdown_report = generate_policy_rule_report(report, format_type="markdown")
    
    print("📄 Generated Markdown Report:")
    print("=" * 60)
    print(markdown_report)
    print("=" * 60)
    
    # Save to file
    os.makedirs("output", exist_ok=True)
    with open("output/sample_policy_rule_report.md", "w", encoding="utf-8") as f:
        f.write(markdown_report)
    print("✅ Markdown report saved to output/sample_policy_rule_report.md")

def test_html_report():
    """Test HTML report generation."""
    print("\n🧪 Testing HTML Report Generation")
    
    report = create_sample_policy_rule_report()
    generate_policy_rule_report(report, "output/sample_policy_rule_report.html", format_type="html")
    
    print("✅ HTML report saved to output/sample_policy_rule_report.html")
    print("📝 You can open the HTML file in a browser for better viewing")

def test_ascii_report():
    """Test ASCII report generation."""
    print("\n🧪 Testing ASCII Report Generation")
    
    from policy_report_generator import PolicyReportGenerator
    
    report = create_sample_policy_rule_report()
    generator = PolicyReportGenerator()
    rows = generator.generate_table_rows(report)
    ascii_table = generator.generate_ascii_table(rows)
    
    print("📄 Generated ASCII Table:")
    print("=" * 80)
    print(ascii_table)
    print("=" * 80)

def main():
    """Run all policy report tests."""
    print("🚀 Starting Policy Rule Report Generation Tests")
    
    try:
        test_markdown_report()
        test_html_report()
        test_ascii_report()
        
        print("\n✅ All policy report generation tests completed successfully!")
        print("\n📊 Generated Reports:")
        print("  • output/sample_policy_rule_report.md (Markdown)")
        print("  • output/sample_policy_rule_report.html (HTML)")
        print("\n💡 You can view the HTML report in a browser for the best formatting")
        
        return 0
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 