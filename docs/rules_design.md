Optimizing tool selection...

# AI-Based Student Academic Advisor System

## Rule-Based Expert System Design

---

## System Overview

| Input Variable        | Type    | Range/Values    |
| --------------------- | ------- | --------------- |
| GPA                   | Float   | 0.0 – 4.0       |
| Attendance            | Integer | 0 – 100 (%)     |
| Study Hours           | Float   | ≥ 0 (hours/day) |
| Assignment Completion | Boolean | yes / no        |

---

## Rule Categories

### 1. Academic Status Rules (R1–R5)

_Determine the student's current academic standing based on GPA and attendance._

| Rule ID | Condition                                            | Conclusion                                      |
| ------- | ---------------------------------------------------- | ----------------------------------------------- |
| **R1**  | `GPA >= 3.5` AND `Attendance >= 90%`                 | **Academic Status:** Excellent Standing         |
| **R2**  | `GPA >= 3.0` AND `GPA < 3.5` AND `Attendance >= 80%` | **Academic Status:** Good Standing              |
| **R3**  | `GPA >= 2.5` AND `GPA < 3.0`                         | **Academic Status:** Satisfactory Standing      |
| **R4**  | `GPA >= 2.0` AND `GPA < 2.5`                         | **Academic Status:** Academic Probation Warning |
| **R5**  | `GPA < 2.0`                                          | **Academic Status:** Academic Probation         |

---

### 2. Behavioral Advice Rules (R6–R10)

_Provide guidance based on study habits and assignment completion patterns._

| Rule ID | Condition                                                        | Conclusion                                                                                                |
| ------- | ---------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| **R6**  | `Study Hours >= 4` AND `Assignment Completion = yes`             | **Advice:** Consistent Performer — Maintain current habits; consider exploring advanced topics.           |
| **R7**  | `Study Hours >= 4` AND `Assignment Completion = no`              | **Advice:** Needs Motivation — Prioritize completing assignments; seek tutoring for time management.      |
| **R8**  | `Study Hours >= 2` AND `Study Hours < 4` AND `Attendance >= 85%` | **Advice:** Moderate Effort — Increase study time gradually; your attendance is strong.                   |
| **R9**  | `Study Hours < 2` AND `Assignment Completion = yes`              | **Advice:** Efficient Learner — You work smart; consider adding study hours to reach your full potential. |
| **R10** | `Study Hours < 2` AND `Assignment Completion = no`               | **Advice:** At Risk Behavior — Immediate intervention needed; schedule meeting with academic advisor.     |

---

### 3. Critical Condition Rules (R11–R15)

_Identify at-risk students requiring immediate attention._

| Rule ID | Condition                                                            | Conclusion                                                                                                     |
| ------- | -------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- |
| **R11** | `GPA < 2.0` AND `Attendance < 70%`                                   | **Critical Alert:** Severe Academic Distress — Mandatory tutoring and counseling referral.                     |
| **R12** | `GPA < 2.5` AND `Assignment Completion = no`                         | **Critical Alert:** Academic Support Required — Assignment completion is mandatory for course progression.     |
| **R13** | `Attendance < 60%`                                                   | **Critical Alert:** Attendance Intervention — Risk of automatic course failure; contact student immediately.   |
| **R14** | `GPA >= 3.5` AND `Study Hours >= 5` AND `Assignment Completion = no` | **Critical Alert:** Verify Data — High effort but missing assignments; investigate submission issues.          |
| **R15** | `GPA < 1.5`                                                          | **Critical Alert:** Immediate Academic Intervention — High risk of dismissal; emergency support plan required. |

---

### 4. Excellence Recognition Rules (R16–R20)

_Acknowledge and reward outstanding academic performance._

| Rule ID | Condition                                                             | Conclusion                                                                                 |
| ------- | --------------------------------------------------------------------- | ------------------------------------------------------------------------------------------ |
| **R16** | `GPA >= 3.8` AND `Attendance >= 95%` AND `Study Hours >= 3`           | **Recognition:** Dean's List Candidate — Outstanding performance across all metrics.       |
| **R17** | `GPA >= 3.5` AND `Assignment Completion = yes` AND `Study Hours >= 4` | **Recognition:** Honor Roll Eligible — Strong academic performance with consistent effort. |
| **R18** | `GPA >= 4.0`                                                          | **Recognition:** Perfect GPA Achievement — Exceptional academic excellence.                |
| **R19** | `Attendance = 100%` AND `GPA >= 3.0`                                  | **Recognition:** Perfect Attendance — Dedication and commitment recognized.                |
| **R20** | `Study Hours >= 6` AND `GPA >= 3.5`                                   | **Recognition:** Dedicated Scholar — Exceptional dedication to academics.                  |

---

## Inference Engine Logic Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    INPUT COLLECTION                         │
│  GPA | Attendance | Study Hours | Assignment Completion    │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              RULE CATEGORY PRIORITY                         │
│  1. Critical Condition Rules (R11–R15)  ← First            │
│  2. Excellence Recognition Rules (R16–R20)                 │
│  3. Academic Status Rules (R1–R5)                          │
│  4. Behavioral Advice Rules (R6–R10)  ← Last               │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                  RULE EVALUATION                            │
│  • Match conditions against inputs                         │
│  • Fire all applicable rules (not just first match)        │
│  • Aggregate conclusions                                   │
└─────────────────────┬───────────────────────────────────────┘
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 DECISION OUTPUT                             │
│  • Academic Status (one output)                            │
│  • Behavioral Advice (zero or one)                         │
│  • Critical Alerts (zero or more)                          │
│  • Excellence Recognition (zero or more)                   │
│  • Explanation: "Because [condition], we recommend..."     │
└─────────────────────────────────────────────────────────────┘
```

---

## Sample Decision Explanations

| Scenario                                             | Fired Rules                 | Explanation                                                                                                                                                                                                                                                       |
| ---------------------------------------------------- | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GPA=3.9, Attendance=96%, Study=4hrs, Assignments=yes | R1, R16, R17, R18           | "Your GPA of 3.9 combined with 96% attendance and consistent assignment completion qualifies you for the Dean's List and Honor Roll. Because you meet all excellence criteria, you are recognized for outstanding academic performance."                          |
| GPA=1.8, Attendance=65%, Study=1hr, Assignments=no   | R5, R10, R11, R12, R13, R15 | "Your GPA of 1.8 with only 65% attendance and incomplete assignments puts you at severe academic risk. Because multiple critical conditions are met, immediate intervention is required including mandatory tutoring, counseling, and an emergency support plan." |
| GPA=2.7, Attendance=88%, Study=3hrs, Assignments=yes | R3, R8                      | "Your GPA of 2.7 indicates satisfactory standing. Because your study hours are moderate but your attendance is strong, consider gradually increasing study time to improve your academic position."                                                               |

---

## Design Principles Applied

| Principle               | Implementation                                                                   |
| ----------------------- | -------------------------------------------------------------------------------- |
| **Modularity**          | Rules are separated by category; each rule has distinct condition and conclusion |
| **Extensibility**       | New rules can be added to any category without modifying existing logic          |
| **Readability**         | Natural language conditions; clear rule IDs and structured tables                |
| **Explanation**         | Each conclusion includes reasoning context for transparency                      |
| **No Hardcoding**       | All thresholds are parameters; system can be tuned for different institutions    |
| **Combined Conditions** | Rules use AND operators to evaluate multiple inputs realistically                |

---

This rule base provides a production-quality foundation for an expert system that simulates human academic advising reasoning while maintaining transparency in decision-making.
