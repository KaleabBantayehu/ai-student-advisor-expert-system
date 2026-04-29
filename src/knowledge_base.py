"""
Knowledge Base for AI-Based Student Academic Advisor System

This module contains the complete rule set in a machine-readable format.
Each rule is represented as a dictionary with:
- id: Unique rule identifier
- category: Rule category for organization
- conditions: Structured conditions (programmatically evaluatable)
- output: The conclusion/action for the rule
- priority: Execution priority (higher = evaluated first)
"""

# =============================================================================
# RULE KNOWLEDGE BASE
# =============================================================================

RULES = [
    # -------------------------------------------------------------------------
    # 1. ACADEMIC STATUS RULES (R1–R5)
    # Determine the student's current academic standing based on GPA and attendance
    # -------------------------------------------------------------------------
    
    {
        "id": "R1",
        "category": "Academic Status",
        "name": "Excellent Standing",
        "conditions": {
            "gpa": {"min": 3.5},
            "attendance": {"min": 90}
        },
        "output": {
            "type": "Academic Status",
            "message": "Excellent Standing",
            "explanation": "GPA is 3.5 or higher with attendance at 90% or above indicates excellent academic standing."
        },
        "priority": 3
    },
    
    {
        "id": "R2",
        "category": "Academic Status",
        "name": "Good Standing",
        "conditions": {
            "gpa": {"min": 3.0, "max": 3.5},
            "attendance": {"min": 80}
        },
        "output": {
            "type": "Academic Status",
            "message": "Good Standing",
            "explanation": "GPA between 3.0 and 3.5 with at least 80% attendance indicates good academic standing."
        },
        "priority": 3
    },
    
    {
        "id": "R3",
        "category": "Academic Status",
        "name": "Satisfactory Standing",
        "conditions": {
            "gpa": {"min": 2.5, "max": 3.0}
        },
        "output": {
            "type": "Academic Status",
            "message": "Satisfactory Standing",
            "explanation": "GPA between 2.5 and 3.0 indicates satisfactory but improvable academic standing."
        },
        "priority": 3
    },
    
    {
        "id": "R4",
        "category": "Academic Status",
        "name": "Academic Probation Warning",
        "conditions": {
            "gpa": {"min": 2.0, "max": 2.5}
        },
        "output": {
            "type": "Academic Status",
            "message": "Academic Probation Warning",
            "explanation": "GPA between 2.0 and 2.5 places the student on academic probation warning."
        },
        "priority": 3
    },
    
    {
        "id": "R5",
        "category": "Academic Status",
        "name": "Academic Probation",
        "conditions": {
            "gpa": {"max": 2.0}
        },
        "output": {
            "type": "Academic Status",
            "message": "Academic Probation",
            "explanation": "GPA below 2.0 places the student on academic probation requiring immediate intervention."
        },
        "priority": 3
    },
    
    # -------------------------------------------------------------------------
    # 2. BEHAVIORAL ADVICE RULES (R6–R10)
    # Provide guidance based on study habits and assignment completion patterns
    # -------------------------------------------------------------------------
    
    {
        "id": "R6",
        "category": "Behavioral Advice",
        "name": "Consistent Performer",
        "conditions": {
            "study_hours": {"min": 4},
            "assignment_completion": True
        },
        "output": {
            "type": "Advice",
            "message": "Consistent Performer — Maintain current habits; consider exploring advanced topics.",
            "explanation": "High study hours (4+) combined with completed assignments indicates consistent performance habits."
        },
        "priority": 2
    },
    
    {
        "id": "R7",
        "category": "Behavioral Advice",
        "name": "Needs Motivation",
        "conditions": {
            "study_hours": {"min": 4},
            "assignment_completion": False
        },
        "output": {
            "type": "Advice",
            "message": "Needs Motivation — Prioritize completing assignments; seek tutoring for time management.",
            "explanation": "Despite high study hours, incomplete assignments suggest motivation or submission issues."
        },
        "priority": 2
    },
    
    {
        "id": "R8",
        "category": "Behavioral Advice",
        "name": "Moderate Effort",
        "conditions": {
            "study_hours": {"min": 2, "max": 4},
            "attendance": {"min": 85}
        },
        "output": {
            "type": "Advice",
            "message": "Moderate Effort — Increase study time gradually; your attendance is strong.",
            "explanation": "Moderate study hours (2-4) with strong attendance indicate room for improvement in study intensity."
        },
        "priority": 2
    },
    
    {
        "id": "R9",
        "category": "Behavioral Advice",
        "name": "Efficient Learner",
        "conditions": {
            "study_hours": {"max": 2},
            "assignment_completion": True
        },
        "output": {
            "type": "Advice",
            "message": "Efficient Learner — You work smart; consider adding study hours to reach your full potential.",
            "explanation": "Low study hours but completed assignments suggest efficient learning strategies."
        },
        "priority": 2
    },
    
    {
        "id": "R10",
        "category": "Behavioral Advice",
        "name": "At Risk Behavior",
        "conditions": {
            "study_hours": {"max": 2},
            "assignment_completion": False
        },
        "output": {
            "type": "Advice",
            "message": "At Risk Behavior — Immediate intervention needed; schedule meeting with academic advisor.",
            "explanation": "Low study hours and incomplete assignments indicate at-risk academic behavior requiring immediate attention."
        },
        "priority": 2
    },
    
    # -------------------------------------------------------------------------
    # 3. CRITICAL CONDITION RULES (R11–R15)
    # Identify at-risk students requiring immediate attention
    # -------------------------------------------------------------------------
    
    {
        "id": "R11",
        "category": "Critical Condition",
        "name": "Severe Academic Distress",
        "conditions": {
            "gpa": {"max": 2.0},
            "attendance": {"max": 70}
        },
        "output": {
            "type": "Critical Alert",
            "message": "Severe Academic Distress — Mandatory tutoring and counseling referral.",
            "explanation": "GPA below 2.0 combined with attendance below 70% indicates severe academic distress requiring immediate intervention."
        },
        "priority": 5
    },
    
    {
        "id": "R12",
        "category": "Critical Condition",
        "name": "Academic Support Required",
        "conditions": {
            "gpa": {"max": 2.5},
            "assignment_completion": False
        },
        "output": {
            "type": "Critical Alert",
            "message": "Academic Support Required — Assignment completion is mandatory for course progression.",
            "explanation": "GPA below 2.5 with incomplete assignments indicates critical academic support needs."
        },
        "priority": 5
    },
    
    {
        "id": "R13",
        "category": "Critical Condition",
        "name": "Attendance Intervention",
        "conditions": {
            "attendance": {"max": 60}
        },
        "output": {
            "type": "Critical Alert",
            "message": "Attendance Intervention — Risk of automatic course failure; contact student immediately.",
            "explanation": "Attendance below 60% puts the student at risk of automatic course failure per attendance policy."
        },
        "priority": 5
    },
    
    {
        "id": "R14",
        "category": "Critical Condition",
        "name": "Verify Data",
        "conditions": {
            "gpa": {"min": 3.5},
            "study_hours": {"min": 5},
            "assignment_completion": False
        },
        "output": {
            "type": "Critical Alert",
            "message": "Verify Data — High effort but missing assignments; investigate submission issues.",
            "explanation": "High GPA and study hours with incomplete assignments suggests possible submission system issues."
        },
        "priority": 5
    },
    
    {
        "id": "R15",
        "category": "Critical Condition",
        "name": "Immediate Academic Intervention",
        "conditions": {
            "gpa": {"max": 1.5}
        },
        "output": {
            "type": "Critical Alert",
            "message": "Immediate Academic Intervention — High risk of dismissal; emergency support plan required.",
            "explanation": "GPA below 1.5 indicates extremely high risk of academic dismissal requiring emergency intervention."
        },
        "priority": 5
    },
    
    # -------------------------------------------------------------------------
    # 4. EXCELLENCE RECOGNITION RULES (R16–R20)
    # Acknowledge and reward outstanding academic performance
    # -------------------------------------------------------------------------
    
    {
        "id": "R16",
        "category": "Excellence Recognition",
        "name": "Dean's List Candidate",
        "conditions": {
            "gpa": {"min": 3.8},
            "attendance": {"min": 95},
            "study_hours": {"min": 3}
        },
        "output": {
            "type": "Recognition",
            "message": "Dean's List Candidate — Outstanding performance across all metrics.",
            "explanation": "GPA 3.8+, 95%+ attendance, and 3+ study hours qualifies the student for Dean's List consideration."
        },
        "priority": 4
    },
    
    {
        "id": "R17",
        "category": "Excellence Recognition",
        "name": "Honor Roll Eligible",
        "conditions": {
            "gpa": {"min": 3.5},
            "assignment_completion": True,
            "study_hours": {"min": 4}
        },
        "output": {
            "type": "Recognition",
            "message": "Honor Roll Eligible — Strong academic performance with consistent effort.",
            "explanation": "GPA 3.5+, completed assignments, and 4+ study hours qualifies for Honor Roll."
        },
        "priority": 4
    },
    
    {
        "id": "R18",
        "category": "Excellence Recognition",
        "name": "Perfect GPA Achievement",
        "conditions": {
            "gpa": {"min": 4.0}
        },
        "output": {
            "type": "Recognition",
            "message": "Perfect GPA Achievement — Exceptional academic excellence.",
            "explanation": "Achieving a perfect 4.0 GPA represents the highest level of academic excellence."
        },
        "priority": 4
    },
    
    {
        "id": "R19",
        "category": "Excellence Recognition",
        "name": "Perfect Attendance",
        "conditions": {
            "attendance": 100,
            "gpa": {"min": 3.0}
        },
        "output": {
            "type": "Recognition",
            "message": "Perfect Attendance — Dedication and commitment recognized.",
            "explanation": "100% attendance with GPA 3.0+ demonstrates exceptional dedication and commitment."
        },
        "priority": 4
    },
    
    {
        "id": "R20",
        "category": "Excellence Recognition",
        "name": "Dedicated Scholar",
        "conditions": {
            "study_hours": {"min": 6},
            "gpa": {"min": 3.5}
        },
        "output": {
            "type": "Recognition",
            "message": "Dedicated Scholar — Exceptional dedication to academics.",
            "explanation": "6+ study hours daily with GPA 3.5+ demonstrates exceptional dedication to academic success."
        },
        "priority": 4
    },
]


# =============================================================================
# RULE CATEGORIES AND PRIORITY MAPPING
# =============================================================================

CATEGORY_PRIORITY = {
    "Critical Condition": 5,      # Highest priority - evaluated first
    "Excellence Recognition": 4,  # Recognition after critical checks
    "Academic Status": 3,         # Core status determination
    "Behavioral Advice": 2,       # Guidance after status determined
}


# =============================================================================
# CONDITION OPERATORS
# =============================================================================

OPERATORS = {
    ">=": lambda a, b: a >= b,
    "<=": lambda a, b: a <= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    ">":  lambda a, b: a > b,
    "<":  lambda a, b: a < b,
}


# =============================================================================
# INPUT SCHEMA
# =============================================================================

INPUT_SCHEMA = {
    "gpa": {
        "type": "float",
        "range": (0.0, 4.0),
        "description": "Grade Point Average (0.0 - 4.0)"
    },
    "attendance": {
        "type": "integer",
        "range": (0, 100),
        "description": "Attendance percentage (0 - 100%)"
    },
    "study_hours": {
        "type": "float",
        "range": (0.0, 24.0),
        "description": "Study hours per day"
    },
    "assignment_completion": {
        "type": "boolean",
        "values": [True, False],
        "description": "Assignment completion status (yes/no)"
    },
}


# =============================================================================
# RULE LOOKUP HELPERS
# =============================================================================

def get_rules_by_category(category: str) -> list:
    """Return all rules in a specific category."""
    return [rule for rule in RULES if rule["category"] == category]


def get_rules_by_priority(priority: int) -> list:
    """Return all rules with a specific priority level."""
    return [rule for rule in RULES if rule["priority"] == priority]


def get_rule_by_id(rule_id: str) -> dict:
    """Return a specific rule by its ID."""
    for rule in RULES:
        if rule["id"] == rule_id:
            return rule
    return None


def get_all_categories() -> list:
    """Return all unique rule categories."""
    return list(set(rule["category"] for rule in RULES))


# =============================================================================
# METADATA
# =============================================================================

__version__ = "1.0.0"
__author__ = "AI Systems Design Team"
__description__ = "Knowledge Base for AI-Based Student Academic Advisor System"
__total_rules__ = len(RULES)