import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from policy_rules import PolicyRuleReport, RuleResult, RuleDecision, RuleSection

logger = logging.getLogger(__name__)

@dataclass
class PolicyRuleTableRow:
    """Represents a single row in the policy rule validation table."""
    section: str
    rule: str
    criteria: str
    decision_if_fails: str
    document_required: str
    status: str
    actual_decision: str
    reason: str
    deduction_amount: Optional[float] = None
    notes: Optional[str] = None

class PolicyReportGenerator:
    """Generates tabular policy rule validation reports."""
    
    def __init__(self):
        self.rule_definitions = {
            "inception_date": {
                "section": "Policy Validity",
                "rule": "Inception Date",
                "criteria": "Policy must be active on date of admission",
                "decision_if_fails": "Reject",
                "document_required": "Policy Document"
            },
            "portability_clause": {
                "section": "Policy Validity",
                "rule": "Portability Clause",
                "criteria": "Continuity of waiting period must be ensured",
                "decision_if_fails": "Reject",
                "document_required": "Portability Certificate"
            },
            "lapse_check": {
                "section": "Policy Validity",
                "rule": "Lapse Check",
                "criteria": "Policy should not be in grace/lapse",
                "decision_if_fails": "Reject",
                "document_required": "Payment Receipt"
            },
            "room_rent_eligibility": {
                "section": "Policy Limits",
                "rule": "Room Rent Eligibility",
                "criteria": "Room rent within entitled limit",
                "decision_if_fails": "Proportionate Deduction",
                "document_required": "Hospital Bill"
            },
            "icu_capping": {
                "section": "Policy Limits",
                "rule": "ICU Capping",
                "criteria": "ICU charges within cap",
                "decision_if_fails": "Deduct",
                "document_required": "Hospital Bill"
            },
            "co_payment": {
                "section": "Policy Limits",
                "rule": "Co-payment",
                "criteria": "Co-pay % as per policy",
                "decision_if_fails": "Deduct",
                "document_required": "Policy Document"
            },
            "sub_limits": {
                "section": "Policy Limits",
                "rule": "Sub-limits",
                "criteria": "Procedure under cap limit",
                "decision_if_fails": "Cap Limit Applied",
                "document_required": "Policy Document"
            },
            "daycare": {
                "section": "Policy Limits",
                "rule": "Daycare",
                "criteria": "Within IRDA-approved daycare",
                "decision_if_fails": "Reject",
                "document_required": "Discharge Summary"
            },
            "initial_waiting": {
                "section": "Waiting Periods",
                "rule": "Initial Waiting",
                "criteria": "<30 days for non-accident",
                "decision_if_fails": "Reject",
                "document_required": "Policy Document"
            },
            "ped": {
                "section": "Waiting Periods",
                "rule": "PED",
                "criteria": "Declared + waiting period over",
                "decision_if_fails": "Reject",
                "document_required": "Proposal Form"
            },
            "disease_specific": {
                "section": "Waiting Periods",
                "rule": "Disease Specific",
                "criteria": "Condition covered post waiting period",
                "decision_if_fails": "Reject",
                "document_required": "Policy Document"
            },
            "maternity": {
                "section": "Waiting Periods",
                "rule": "Maternity",
                "criteria": "Covered with waiting period",
                "decision_if_fails": "Reject",
                "document_required": "Policy Document"
            },
            "non_medical": {
                "section": "Policy Limits",
                "rule": "Non-Medical",
                "criteria": "IRDA non-payables",
                "decision_if_fails": "Deduct",
                "document_required": "Itemized Bill"
            }
        }
    
    def generate_table_rows(self, policy_rule_report: PolicyRuleReport) -> List[PolicyRuleTableRow]:
        """Convert policy rule validation results into table rows with early termination logic."""
        rows = []
        
        # Define rule processing order for early termination
        rule_order = [
            "inception_date",      # Policy validity - if fails, reject immediately
            "lapse_check",         # Policy validity - if fails, reject immediately
            "daycare",             # Policy limits - if fails, reject immediately
            "room_rent_eligibility", # Policy limits - continue processing
            "icu_capping",         # Policy limits - continue processing
            "co_payment",          # Policy limits - continue processing
            "sub_limits",          # Policy limits - continue processing
            "non_medical",         # Policy limits - continue processing
            "initial_waiting",     # Waiting periods - if fails, reject immediately
            "disease_specific",    # Waiting periods - if fails, reject immediately
            "maternity"            # Waiting periods - if fails, reject immediately
        ]
        
        # Track if we should stop processing due to a REJECT decision
        should_stop_processing = False
        stop_reason = ""
        
        # Process rules in order
        for rule_key in rule_order:
            # Find the corresponding rule result
            rule_result = None
            for rule_name, result in policy_rule_report.rule_results.items():
                if self._get_rule_key(result.rule_name) == rule_key:
                    rule_result = result
                    break
            
            if rule_result and rule_key in self.rule_definitions:
                definition = self.rule_definitions[rule_key]
                
                # Determine status and actual decision
                status = "PASS" if rule_result.decision == RuleDecision.PASS else "FAIL"
                actual_decision = rule_result.decision.value
                
                # Check if this is a REJECT decision that should stop processing
                if rule_result.decision == RuleDecision.REJECT:
                    should_stop_processing = True
                    stop_reason = f"Processing stopped due to {rule_result.rule_name} failure: {rule_result.details}"
                
                # Format deduction amount
                deduction_amount = None
                if rule_result.deduction_amount and rule_result.deduction_amount > 0:
                    deduction_amount = rule_result.deduction_amount
                
                # Create table row
                row = PolicyRuleTableRow(
                    section=definition["section"],
                    rule=definition["rule"],
                    criteria=definition["criteria"],
                    decision_if_fails=definition["decision_if_fails"],
                    document_required=definition["document_required"],
                    status=status,
                    actual_decision=actual_decision,
                    reason=rule_result.details if rule_result.details else "No specific reason provided",
                    deduction_amount=deduction_amount,
                    notes=rule_result.details if rule_result.details else None
                )
                rows.append(row)
                
                # If we should stop processing, add a note and break
                if should_stop_processing:
                    break
        
        # Note: Rules that weren't processed due to early termination are intentionally omitted
        # to avoid cluttering the report with irrelevant information
        
        return rows
    
    def _get_rule_key(self, rule_name: str) -> str:
        """Map rule names to rule keys."""
        rule_mapping = {
            "Inception Date": "inception_date",
            "Portability Clause": "portability_clause",
            "Lapse Check": "lapse_check",
            "Room Rent Eligibility": "room_rent_eligibility",
            "ICU Capping": "icu_capping",
            "Co-payment": "co_payment",
            "Sub-limits": "sub_limits",
            "Daycare": "daycare",
            "Initial Waiting": "initial_waiting",
            "PED": "ped",
            "Disease Specific": "disease_specific",
            "Maternity": "maternity",
            "Non-Medical": "non_medical"
        }
        return rule_mapping.get(rule_name, rule_name.lower().replace(" ", "_"))
    
    def generate_ascii_table(self, rows: List[PolicyRuleTableRow]) -> str:
        """Generate ASCII table format."""
        if not rows:
            return "No policy rule validation results available."
        
        # Define column headers and widths
        headers = ["SECTION", "RULE", "CRITERIA", "DECISION IF FAILS", "DOCUMENT REQUIRED", "STATUS", "ACTUAL DECISION", "REASON"]
        widths = [15, 20, 40, 25, 20, 8, 15, 50]
        
        # Create header row
        header_row = "| " + " | ".join(f"{header:<{width}}" for header, width in zip(headers, widths)) + " |"
        separator = "|" + "|".join("-" * (width + 2) for width in widths) + "|"
        
        # Create data rows
        data_rows = []
        for row in rows:
            # Truncate reason if too long
            reason = row.reason[:47] + "..." if len(row.reason) > 50 else row.reason
            data_row = "| " + " | ".join([
                f"{row.section:<{widths[0]}}",
                f"{row.rule:<{widths[1]}}",
                f"{row.criteria:<{widths[2]}}",
                f"{row.decision_if_fails:<{widths[3]}}",
                f"{row.document_required:<{widths[4]}}",
                f"{row.status:<{widths[5]}}",
                f"{row.actual_decision:<{widths[6]}}",
                f"{reason:<{widths[7]}}"
            ]) + " |"
            data_rows.append(data_row)
        
        # Combine all parts
        table = f"{separator}\n{header_row}\n{separator}\n"
        table += "\n".join(data_rows)
        table += f"\n{separator}"
        
        return table
    
    def generate_markdown_table(self, rows: List[PolicyRuleTableRow]) -> str:
        """Generate markdown table format."""
        if not rows:
            return "No policy rule validation results available."
        
        # Create header
        table = "| SECTION | RULE | CRITERIA | DECISION IF FAILS | DOCUMENT REQUIRED | STATUS | ACTUAL DECISION | REASON |\n"
        table += "|---------|------|----------|-------------------|-------------------|--------|-----------------|--------|\n"
        
        # Create data rows
        for row in rows:
            deduction_info = f" (₹{row.deduction_amount:,.2f})" if row.deduction_amount else ""
            actual_decision = f"{row.actual_decision}{deduction_info}"
            
            # Escape pipe characters in reason
            reason = row.reason.replace("|", "\\|")
            
            table += f"| {row.section} | {row.rule} | {row.criteria} | {row.decision_if_fails} | {row.document_required} | {row.status} | {actual_decision} | {reason} |\n"
        
        return table
    
    def generate_html_table(self, rows: List[PolicyRuleTableRow]) -> str:
        """Generate HTML table format."""
        if not rows:
            return "<p>No policy rule validation results available.</p>"
        
        html = """
        <style>
        .policy-table { border-collapse: collapse; width: 100%; margin: 20px 0; }
        .policy-table th, .policy-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        .policy-table th { background-color: #f2f2f2; font-weight: bold; }
        .policy-table .pass { background-color: #d4edda; }
        .policy-table .fail { background-color: #f8d7da; }
        .policy-table .not-processed { background-color: #fff3cd; }
        .policy-table .deduction { color: #721c24; font-weight: bold; }
        .policy-table .reason { max-width: 300px; word-wrap: break-word; }
        </style>
        <table class="policy-table">
        <thead>
        <tr>
            <th>SECTION</th>
            <th>RULE</th>
            <th>CRITERIA</th>
            <th>DECISION IF FAILS</th>
            <th>DOCUMENT REQUIRED</th>
            <th>STATUS</th>
            <th>ACTUAL DECISION</th>
            <th>REASON</th>
        </tr>
        </thead>
        <tbody>
        """
        
        for row in rows:
            if row.status == "PASS":
                status_class = "pass"
            elif row.status == "NOT PROCESSED":
                status_class = "not-processed"
            else:
                status_class = "fail"
                
            deduction_info = f" (₹{row.deduction_amount:,.2f})" if row.deduction_amount else ""
            actual_decision = f"{row.actual_decision}{deduction_info}"
            
            # Escape HTML characters in reason
            reason = row.reason.replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")
            
            html += f"""
            <tr class="{status_class}">
                <td>{row.section}</td>
                <td>{row.rule}</td>
                <td>{row.criteria}</td>
                <td>{row.decision_if_fails}</td>
                <td>{row.document_required}</td>
                <td>{row.status}</td>
                <td class="deduction">{actual_decision}</td>
                <td class="reason">{reason}</td>
            </tr>
            """
        
        html += "</tbody></table>"
        return html
    
    def generate_text_report(self, rows: List[PolicyRuleTableRow], policy_rule_report: PolicyRuleReport) -> str:
        """Generate simple text format report."""
        if not rows:
            return "No policy rule validation results available."
        
        # Determine status display with appropriate emoji
        status_display = ""
        if policy_rule_report.status == "CLEARED":
            status_display = "✅ CLEARED"
        elif policy_rule_report.status == "CLEARED WITH DEDUCTIONS":
            status_display = "⚠️ CLEARED WITH DEDUCTIONS"
        elif policy_rule_report.status == "REJECTED":
            status_display = "❌ REJECTED"
        else:
            status_display = f"❓ {policy_rule_report.status}"
        
        # Generate text report
        text_report = f"""
POLICY RULE VALIDATION SUMMARY
{'='*50}

Overall Status: {status_display}
Total Deductions: ₹{policy_rule_report.total_deductions:,.2f}

Rule Statistics:
• Total Rules Checked: {len(policy_rule_report.rule_results)}
• Rules Passed: {sum(1 for rule in policy_rule_report.rule_results.values() if rule.decision == RuleDecision.PASS)} ({sum(1 for rule in policy_rule_report.rule_results.values() if rule.decision == RuleDecision.PASS)/len(policy_rule_report.rule_results)*100:.1f}%)
• Rules Failed: {sum(1 for rule in policy_rule_report.rule_results.values() if rule.decision == RuleDecision.REJECT)} ({sum(1 for rule in policy_rule_report.rule_results.values() if rule.decision == RuleDecision.REJECT)/len(policy_rule_report.rule_results)*100:.1f}%)

Key Observations:
"""
        
        if policy_rule_report.recommendations:
            for i, rec in enumerate(policy_rule_report.recommendations[:5], 1):
                text_report += f"• {rec}\n"
        else:
            text_report += "• No specific recommendations available\n"
        
        text_report += f"\nDETAILED RULE RESULTS:\n{'-'*50}\n"
        
        # Group rules by section
        sections = {}
        for row in rows:
            if row.section not in sections:
                sections[row.section] = []
            sections[row.section].append(row)
        
        # Generate section-wise text
        for section_name, section_rules in sections.items():
            text_report += f"\n{section_name.upper()}:\n"
            text_report += "-" * len(section_name) + "\n"
            
            for rule in section_rules:
                status_icon = "✅" if rule.status == "PASS" else "❌"
                deduction_info = f" (₹{rule.deduction_amount:,.2f})" if rule.deduction_amount else ""
                
                text_report += f"{status_icon} {rule.rule}\n"
                text_report += f"   Criteria: {rule.criteria}\n"
                text_report += f"   Decision: {rule.actual_decision}{deduction_info}\n"
                text_report += f"   Reason: {rule.reason}\n"
                text_report += f"   Document Required: {rule.document_required}\n\n"
        
        return text_report
    
    def generate_summary_report(self, policy_rule_report: PolicyRuleReport) -> str:
        """Generate a summary report with key statistics."""
        total_rules = len(policy_rule_report.rule_results)
        passed_rules = sum(1 for rule in policy_rule_report.rule_results.values() if rule.decision == RuleDecision.PASS)
        failed_rules = total_rules - passed_rules
        total_deductions = policy_rule_report.total_deductions
        
        # Determine status display with appropriate emoji
        status_display = ""
        if policy_rule_report.status == "CLEARED":
            status_display = "✅ CLEARED"
        elif policy_rule_report.status == "CLEARED WITH DEDUCTIONS":
            status_display = "⚠️ CLEARED WITH DEDUCTIONS"
        elif policy_rule_report.status == "REJECTED":
            status_display = "❌ REJECTED"
        else:
            status_display = f"❓ {policy_rule_report.status}"
        
        summary = f"""
📋 POLICY RULE VALIDATION SUMMARY
{'='*50}

Overall Status: {status_display}
Total Deductions: ₹{total_deductions:,.2f}

Rule Statistics:
• Total Rules Checked: {total_rules}
• Rules Passed: {passed_rules} ({passed_rules/total_rules*100:.1f}%)
• Rules Failed: {failed_rules} ({failed_rules/total_rules*100:.1f}%)

Key Observations:
"""
        
        if policy_rule_report.recommendations:
            for i, rec in enumerate(policy_rule_report.recommendations[:5], 1):
                summary += f"• {rec}\n"
        else:
            summary += "• No specific recommendations available\n"
        
        return summary
    
    def save_report(self, policy_rule_report: PolicyRuleReport, output_file: str, format_type: str = "markdown"):
        """Save policy rule validation report to file."""
        rows = self.generate_table_rows(policy_rule_report)
        
        if format_type == "text":
            # Generate text format report
            full_report = self.generate_text_report(rows, policy_rule_report)
        elif format_type == "ascii":
            table_content = self.generate_ascii_table(rows)
            summary = self.generate_summary_report(policy_rule_report)
            full_report = summary + "\n\n" + table_content
        elif format_type == "html":
            table_content = self.generate_html_table(rows)
            summary = self.generate_summary_report(policy_rule_report)
            full_report = summary + "\n\n" + table_content
        else:  # markdown
            table_content = self.generate_markdown_table(rows)
            summary = self.generate_summary_report(policy_rule_report)
            full_report = summary + "\n\n" + table_content
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        logger.info(f"Policy rule validation report saved to {output_file}")

def generate_policy_rule_report(policy_rule_report: PolicyRuleReport, output_file: str = None, format_type: str = "markdown") -> str:
    """Generate a policy rule validation report in tabular format."""
    generator = PolicyReportGenerator()
    
    if output_file:
        generator.save_report(policy_rule_report, output_file, format_type)
        return f"Report saved to {output_file}"
    else:
        rows = generator.generate_table_rows(policy_rule_report)
        if format_type == "text":
            return generator.generate_text_report(rows, policy_rule_report)
        else:
            summary = generator.generate_summary_report(policy_rule_report)
            table = generator.generate_markdown_table(rows)
            return summary + "\n\n" + table 