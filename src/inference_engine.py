"""
Inference Engine for AI-Based Student Academic Advisor System

This module provides a generic rule evaluation engine that:
- Imports rules from knowledge_base.py
- Evaluates conditions dynamically (no hardcoded logic)
- Supports min/max numeric checks and exact matches
- Aggregates decisions by category
- Provides human-readable explanations

Architecture:
- ConditionEvaluator: Evaluates individual conditions
- RuleEvaluator: Evaluates complete rules against inputs
- DecisionAggregator: Aggregates fired rules into final output
- InferenceEngine: Main orchestrator
"""

from typing import Any, Callable, Optional
from dataclasses import dataclass, field
from .knowledge_base import RULES, CATEGORY_PRIORITY


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class ConditionResult:
    """Result of evaluating a single condition."""
    field_name: str
    expected: dict
    actual_value: Any
    passed: bool
    reason: str = ""


@dataclass
class RuleFired:
    """Record of a rule that has been triggered."""
    rule_id: str
    category: str
    name: str
    output: dict
    priority: int
    conditions_met: list[ConditionResult]
    explanation: str


@dataclass
class InferenceResult:
    """
    Final result from the inference engine.
    
    New structure with hierarchical reasoning:
    - final_status: Single academic status from status rules (highest priority wins)
    - severity_context: Context from critical rules (additive, doesn't replace status)
    - advice_list: Behavioral advice from advice rules
    - alerts: Critical condition alerts
    - recognitions: Excellence recognitions
    - reasoning_narrative: Human-readable explanation combining all fired rules
    """
    final_status: Optional[dict] = None
    severity_context: list[dict] = field(default_factory=list)
    advice_list: list[dict] = field(default_factory=list)
    alerts: list[dict] = field(default_factory=list)
    recognitions: list[dict] = field(default_factory=list)
    reasoning_narrative: str = ""
    fired_rules: list[RuleFired] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert result to dictionary for serialization."""
        return {
            "final_status": self.final_status.get("message", "Unknown") if self.final_status else "Unknown",
            "severity_context": [
                {
                    "rule_id": s.get("rule_id", ""),
                    "message": s.get("message", ""),
                    "reason": s.get("reason", "")
                }
                for s in self.severity_context
            ],
            "advice_list": self.advice_list,
            "alerts": self.alerts,
            "recognitions": self.recognitions,
            "reasoning_narrative": self.reasoning_narrative
        }


# =============================================================================
# CONDITION EVALUATOR
# =============================================================================

class ConditionEvaluator:
    """
    Generic condition evaluator that handles:
    - min/max range checks (numeric)
    - exact value matches (any type)
    - boolean conditions
    """
    
    @staticmethod
    def evaluate(field_name: str, condition: dict, input_value: Any) -> ConditionResult:
        """
        Evaluate a single condition against an input value.
        
        Args:
            field_name: Name of the field being evaluated
            condition: Condition specification (e.g., {"min": 3.5} or True)
            input_value: The actual value to evaluate
            
        Returns:
            ConditionResult with pass/fail status and reason
        """
        # Handle exact match (boolean, numeric, etc.)
        if not isinstance(condition, dict):
            passed = (input_value == condition)
            reason = f"{field_name} is {input_value}" + (" (matches)" if passed else f" (expected {condition})")
            return ConditionResult(
                field_name=field_name,
                expected=condition,
                actual_value=input_value,
                passed=passed,
                reason=reason
            )
        
        # Handle min/max range checks
        checks_passed = []
        reasons = []
        
        if "min" in condition:
            passed = input_value >= condition["min"]
            checks_passed.append(passed)
            reasons.append(f"{field_name} >= {condition['min']}")
        
        if "max" in condition:
            passed = input_value <= condition["max"]
            checks_passed.append(passed)
            reasons.append(f"{field_name} <= {condition['max']}")
        
        # All checks must pass (AND logic)
        all_passed = all(checks_passed)
        reason = "; ".join(reasons) + (": PASSED" if all_passed else ": FAILED")
        
        return ConditionResult(
            field_name=field_name,
            expected=condition,
            actual_value=input_value,
            passed=all_passed,
            reason=reason
        )


# =============================================================================
# RULE EVALUATOR
# =============================================================================

class RuleEvaluator:
    """
    Evaluates complete rules against input data.
    All conditions in a rule must be TRUE for the rule to fire.
    """
    
    def __init__(self):
        self.condition_evaluator = ConditionEvaluator()
    
    def evaluate_rule(self, rule: dict, inputs: dict) -> tuple[bool, list[ConditionResult]]:
        """
        Evaluate all conditions in a rule against the input data.
        
        Args:
            rule: Rule dictionary with 'conditions' key
            inputs: Dictionary of input field names to values
            
        Returns:
            Tuple of (all_conditions_passed, list of ConditionResults)
        """
        conditions = rule.get("conditions", {})
        results = []
        
        for field_name, condition in conditions.items():
            if field_name not in inputs:
                # Field not provided - condition fails
                results.append(ConditionResult(
                    field_name=field_name,
                    expected=condition,
                    actual_value=None,
                    passed=False,
                    reason=f"{field_name} not provided in inputs"
                ))
                continue
            
            input_value = inputs[field_name]
            result = self.condition_evaluator.evaluate(field_name, condition, input_value)
            results.append(result)
        
        # Rule fires only if ALL conditions pass
        all_passed = all(r.passed for r in results)
        return all_passed, results


# =============================================================================
# DECISION AGGREGATOR
# =============================================================================

class DecisionAggregator:
    """
    Aggregates fired rules into structured output.
    Handles priority resolution and category-specific logic.
    """
    
    # Priority order (higher = more important)
    CATEGORY_PRIORITY_ORDER = {
        "Critical Condition": 5,
        "Excellence Recognition": 4,
        "Academic Status": 3,
        "Behavioral Advice": 2
    }
    
    def __init__(self):
        self.rule_evaluator = RuleEvaluator()
    
    def aggregate(self, rules: list[dict], inputs: dict) -> InferenceResult:
        """
        Evaluate all rules and aggregate results with hierarchical reasoning.
        
        New behavior:
        - Classify rules by type (Status/Critical/Advice/Recognition)
        - Final status: Only ONE from status rules using priority
        - Critical rules add severity context, don't replace status
        - Generate human-readable reasoning narrative
        
        Args:
            rules: List of rule dictionaries
            inputs: Input data dictionary
            
        Returns:
            InferenceResult with categorized outputs and reasoning narrative
        """
        result = InferenceResult()
        
        # Track fired rules by category for narrative generation
        status_rules_fired = []
        critical_rules_fired = []
        advice_rules_fired = []
        recognition_rules_fired = []
        
        # Sort rules by priority (higher first)
        sorted_rules = sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)
        
        # Evaluate each rule
        for rule in sorted_rules:
            fired, condition_results = self.rule_evaluator.evaluate_rule(rule, inputs)
            
            if fired:
                rule_fired = self._create_rule_fired(rule, condition_results)
                result.fired_rules.append(rule_fired)
                
                # Categorize and track
                self._categorize_output(rule, result, condition_results)
                
                # Track for narrative generation
                category = rule["category"]
                if category == "Academic Status":
                    status_rules_fired.append(rule_fired)
                elif category == "Critical Condition":
                    critical_rules_fired.append(rule_fired)
                elif category == "Behavioral Advice":
                    advice_rules_fired.append(rule_fired)
                elif category == "Excellence Recognition":
                    recognition_rules_fired.append(rule_fired)
        
        # Resolve final status - only ONE from status rules (highest priority wins)
        result.final_status = self._resolve_academic_status(status_rules_fired)

        primary_issue = self._detect_primary_issue(critical_rules_fired, inputs)
        result.advice_list = self._align_advice_with_primary_issue(
            result.advice_list,
            primary_issue,
            inputs
        )
        
        # Generate human-readable reasoning narrative
        result.reasoning_narrative = self._generate_reasoning_narrative(
            status_rules_fired,
            critical_rules_fired,
            advice_rules_fired,
            recognition_rules_fired,
            inputs,
            primary_issue
        )
        
        return result
    
    def _create_rule_fired(self, rule: dict, condition_results: list[ConditionResult]) -> RuleFired:
        """Create a RuleFired record."""
        return RuleFired(
            rule_id=rule["id"],
            category=rule["category"],
            name=rule["name"],
            output=rule["output"],
            priority=rule.get("priority", 0),
            conditions_met=condition_results,
            explanation=rule["output"].get("explanation", "")
        )
    
    def _build_firing_reason(self, condition_results: list[ConditionResult]) -> str:
        """Build human-readable reason for why rule fired."""
        passed = [r for r in condition_results if r.passed]
        return "; ".join([r.reason for r in passed])
    
    def _categorize_output(self, rule: dict, result: InferenceResult, condition_results: list[ConditionResult]):
        """
        Categorize rule output into appropriate list.
        
        New behavior:
        - Critical rules go to severity_context (additive, doesn't replace status)
        - Status rules handled separately for conflict resolution
        - Advice/Recognition rules go to their respective lists
        """
        output_type = rule["output"].get("type", "")
        category = rule["category"]
        
        # Build firing reason from condition results
        firing_reason = self._build_firing_reason(condition_results)
        
        output_entry = {
            "rule_id": rule["id"],
            "name": rule["name"],
            "message": rule["output"].get("message", ""),
            "explanation": rule["output"].get("explanation", ""),
            "reason": firing_reason
        }
        
        if output_type == "Academic Status":
            # Handled separately for conflict resolution
            pass
        elif category == "Critical Condition":
            # Critical rules add to severity_context (doesn't replace status)
            result.severity_context.append(output_entry)
            result.alerts.append(output_entry)  # Keep in alerts too for backward compat
        elif output_type == "Advice":
            result.advice_list.append(output_entry)
        elif output_type == "Recognition":
            result.recognitions.append(output_entry)
    
    def _resolve_academic_status(self, status_rules: list[RuleFired]) -> Optional[dict]:
        """
        Resolve academic status when multiple status rules fire.
        Use highest priority (higher number = higher priority in our system).
        Returns only ONE status.
        """
        if not status_rules:
            # Gracefully fallback if no standard status rule matched.
            return {
                "rule_id": "R0",
                "name": "Needs Attention",
                "message": "Needs Attention",
                "explanation": "The student does not fully meet criteria for defined academic categories and requires closer evaluation.",
                "priority": 1
            }
        
        # Sort by priority (higher number = higher priority)
        status_rules.sort(key=lambda r: r.priority, reverse=True)
        
        best = status_rules[0]
        return {
            "rule_id": best.rule_id,
            "name": best.name,
            "message": best.output.get("message", ""),
            "explanation": best.output.get("explanation", ""),
            "priority": best.priority
        }

    def _detect_primary_issue(self, critical_rules: list[RuleFired], inputs: dict) -> Optional[str]:
        """Identify the highest-priority issue that advice should address first."""
        if not critical_rules:
            attendance = inputs.get("attendance", 100)
            if attendance < 80:
                return "attendance"
            if not inputs.get("assignment_completion", True):
                return "assignment"
            if inputs.get("gpa", 0.0) < 3.0:
                return "gpa"
            return None

        issue_priority = {
            "attendance": 3,
            "assignment": 2,
            "gpa": 1,
        }
        detected_issues = []

        for rule in critical_rules:
            searchable_text = " ".join([
                rule.name,
                rule.output.get("message", ""),
                rule.output.get("explanation", ""),
                rule.explanation,
                " ".join(condition.field_name for condition in rule.conditions_met),
            ]).lower()

            for issue, priority in issue_priority.items():
                if issue in searchable_text:
                    detected_issues.append((rule.priority, priority, issue))

        if not detected_issues:
            return None

        detected_issues.sort(reverse=True)
        return detected_issues[0][2]

    def _align_advice_with_primary_issue(
        self,
        advice_list: list[dict],
        primary_issue: Optional[str],
        inputs: dict
    ) -> list[dict]:
        """Make displayed advice match the highest-priority detected issue."""
        if primary_issue == "attendance":
            attendance = inputs.get("attendance", 0)
            return [{
                "rule_id": "aligned_attendance_advice",
                "name": "Attendance Improvement",
                "message": (
                    f"Improve class attendance from {attendance}% to at least 80% "
                    "to ensure consistent learning, while maintaining your current study habits."
                ),
                "explanation": "Attendance is the highest-priority detected issue, so advice prioritizes attendance improvement.",
                "reason": "Advice aligned with the primary attendance issue."
            }]

        return advice_list
    
    def _generate_reasoning_narrative(
        self,
        status_rules: list[RuleFired],
        critical_rules: list[RuleFired],
        advice_rules: list[RuleFired],
        recognition_rules: list[RuleFired],
        inputs: dict,
        primary_issue: Optional[str] = None
    ) -> str:
        """
        Generate a clear, structured explanation of the student's academic situation.

        Structure:
        1. Academic evaluation (GPA and attendance assessment)
        2. Main issue (primary concern or strength)
        3. Impact (consequences or implications)
        4. Recommendation (specific actionable advice)
        """
        gpa = inputs.get('gpa', 0.0)
        attendance = inputs.get('attendance', 100)
        assignment_completion = inputs.get('assignment_completion', True)

        # Determine academic status
        status_message = "Unknown"
        if status_rules:
            status_rules.sort(key=lambda r: r.priority, reverse=True)
            status_message = status_rules[0].output.get('message', 'Unknown')

        # Build structured explanation
        explanation_parts = []

        # 1. Academic Evaluation
        if gpa >= 3.5 and attendance >= 90:
            evaluation = f"The student has an excellent GPA of {gpa} and attendance at {attendance}%, indicating strong academic performance."
        elif gpa >= 3.0 and attendance >= 80:
            evaluation = f"The student has a good GPA of {gpa} with attendance at {attendance}%, showing solid academic performance."
        elif gpa >= 2.5:
            evaluation = f"The student has a satisfactory GPA of {gpa}, but there is room for improvement in academic performance."
        elif gpa >= 2.0:
            evaluation = f"The student has a marginal GPA of {gpa}, indicating early warning signs that require attention."
        else:
            evaluation = f"The student has a low GPA of {gpa}, indicating serious academic risk requiring immediate intervention."

        explanation_parts.append(evaluation)

        # 2. Main Issue & 3. Impact
        issues_and_impacts = []

        if critical_rules:
            critical_issues = []
            for rule in critical_rules:
                msg = rule.output.get("message", "")
                if "attendance" in msg.lower():
                    critical_issues.append(f"attendance at {attendance}% is below the recommended level")
                elif "assignment" in msg.lower():
                    critical_issues.append("incomplete assignment completion")
                elif "gpa" in msg.lower() or "probation" in msg.lower():
                    critical_issues.append(f"GPA of {gpa} indicates academic probation level")

            if critical_issues:
                if primary_issue == "attendance":
                    other_issues = [
                        issue for issue in critical_issues
                        if "attendance" not in issue.lower()
                    ]
                    main_issue = f"However, the main issue is attendance at {attendance}%, which is below the recommended level."
                    if other_issues:
                        main_issue += f" Additional concerns include {', and '.join(other_issues)}."
                else:
                    main_issue = f"However, {', and '.join(critical_issues)}."
                impact = "This may affect learning consistency and academic progress."
                issues_and_impacts.extend([main_issue, impact])

        elif primary_issue == "attendance":
            main_issue = f"However, the main issue is attendance at {attendance}%, which is below the recommended level."
            impact = "This may affect learning consistency and academic progress."
            issues_and_impacts.extend([main_issue, impact])

        elif recognition_rules and not critical_rules:
            # Only show recognition if there are no critical issues
            recognition_parts = []
            for rule in recognition_rules:
                msg = rule.output.get("message", "")
                if " — " in msg:
                    # Extract just the main recognition title
                    title = msg.split(" — ")[0]
                    recognition_parts.append(title.lower())
            
            if recognition_parts:
                main_issue = f"Additionally, {', '.join(recognition_parts)}."
                issues_and_impacts.append(main_issue)

        # 4. Recommendation
        recommendations = []

        if primary_issue == "attendance":
            recommendations.append(
                f"Improve class attendance from {attendance}% to at least 80% to ensure consistent learning, while maintaining current study habits."
            )
        elif advice_rules:
            # Take only the most relevant advice (highest priority)
            advice_rules.sort(key=lambda r: r.priority, reverse=True)
            best_advice = advice_rules[0].output.get("message", "")
            if best_advice:
                recommendations.append(best_advice)

        if not recommendations and critical_rules:
            if gpa < 2.0:
                recommendations.append("Immediate academic intervention is required, including tutoring and counseling.")
            elif attendance < 80:
                recommendations.append("Focus on improving attendance and maintaining consistent study habits.")
            elif not assignment_completion:
                recommendations.append("Complete all assignments and establish better time management practices.")

        # Combine all parts
        final_parts = [evaluation]

        if issues_and_impacts:
            final_parts.extend(issues_and_impacts)

        if recommendations:
            rec_text = recommendations[0]
            final_parts.append(f"This places the student in the '{status_message}' category. {rec_text}")
        else:
            final_parts.append(f"This places the student in the '{status_message}' category.")

        return " ".join(final_parts)


# =============================================================================
# INFERENCE ENGINE (MAIN ORCHESTRATOR)
# =============================================================================

class InferenceEngine:
    """
    Main inference engine that orchestrates rule evaluation.
    
    Usage:
        engine = InferenceEngine()
        result = engine.evaluate({
            "gpa": 3.8,
            "attendance": 95,
            "study_hours": 4,
            "assignment_completion": True
        })
        print(result.to_dict())
    """
    
    def __init__(self, rules: Optional[list[dict]] = None):
        """
        Initialize the inference engine.
        
        Args:
            rules: Optional custom rules list. If None, uses RULES from knowledge_base.
        """
        self.rules = rules if rules is not None else RULES
        self.aggregator = DecisionAggregator()
    
    def evaluate(self, inputs: dict) -> InferenceResult:
        """
        Evaluate inputs against all rules and return structured result.
        
        Args:
            inputs: Dictionary with keys: gpa, attendance, study_hours, assignment_completion
            
        Returns:
            InferenceResult with categorized outputs and explanations
        """
        # Validate inputs
        self._validate_inputs(inputs)
        
        # Aggregate decisions
        result = self.aggregator.aggregate(self.rules, inputs)
        
        return result
    
    def _validate_inputs(self, inputs: dict):
        """Validate that required inputs are present."""
        required_fields = ["gpa", "attendance", "study_hours", "assignment_completion"]
        missing = [f for f in required_fields if f not in inputs]
        
        if missing:
            raise ValueError(f"Missing required input fields: {missing}")
    
    def get_rule_by_id(self, rule_id: str) -> Optional[dict]:
        """Get a specific rule by ID."""
        for rule in self.rules:
            if rule["id"] == rule_id:
                return rule
        return None
    
    def list_categories(self) -> list[str]:
        """List all rule categories."""
        return list(set(rule["category"] for rule in self.rules))
    
    def list_rules_by_category(self, category: str) -> list[dict]:
        """List all rules in a specific category."""
        return [r for r in self.rules if r["category"] == category]


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def evaluate_student(
    gpa: float,
    attendance: int,
    study_hours: float,
    assignment_completion: bool
) -> dict:
    """
    Convenience function to evaluate a student.
    
    Args:
        gpa: Grade Point Average (0.0 - 4.0)
        attendance: Attendance percentage (0 - 100)
        study_hours: Study hours per day
        assignment_completion: Whether assignments are completed
        
    Returns:
        Dictionary with evaluation results
    """
    engine = InferenceEngine()
    inputs = {
        "gpa": gpa,
        "attendance": attendance,
        "study_hours": study_hours,
        "assignment_completion": assignment_completion
    }
    result = engine.evaluate(inputs)
    return result.to_dict()


# =============================================================================
# MAIN ENTRY POINT (for testing)
# =============================================================================

if __name__ == "__main__":
    # Example usage
    print("=" * 60)
    print("INFERENCE ENGINE TEST")
    print("=" * 60)
    
    # Test case 1: Excellent student
    print("\n--- Test Case 1: High Performer ---")
    result = evaluate_student(
        gpa=3.9,
        attendance=96,
        study_hours=4,
        assignment_completion=True
    )
    print(f"Status: {result['final_status']}")
    print(f"Severity Context: {result['severity_context']}")
    print(f"Recognitions: {result['recognitions']}")
    print(f"Alerts: {result['alerts']}")
    print(f"Explanation: {result['reasoning_narrative'].encode('ascii', 'replace').decode('ascii')}")
    
    # Test case 2: At-risk student
    print("\n--- Test Case 2: At-Risk Student ---")
    result = evaluate_student(
        gpa=1.8,
        attendance=65,
        study_hours=1,
        assignment_completion=False
    )
    print(f"Status: {result['final_status']}")
    print(f"Severity Context: {result['severity_context']}")
    print(f"Alerts: {result['alerts']}")
    print(f"Advice: {result['advice_list']}")
    print(f"Explanation: {result['reasoning_narrative'].encode('ascii', 'replace').decode('ascii')}")
    
    # Test case 3: Moderate student
    print("\n--- Test Case 3: Moderate Student ---")
    result = evaluate_student(
        gpa=2.7,
        attendance=88,
        study_hours=3,
        assignment_completion=True
    )
    print(f"Status: {result['final_status']}")
    print(f"Severity Context: {result['severity_context']}")
    print(f"Advice: {result['advice_list']}")
    print(f"Explanation: {result['reasoning_narrative'].encode('ascii', 'replace').decode('ascii')}")
