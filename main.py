import sys
from src.inference_engine import InferenceEngine

def get_float_input(prompt: str, min_val: float, max_val: float = float('inf')) -> float:
    while True:
        try:
            val = float(input(prompt))
            if min_val <= val <= max_val:
                return val
            if max_val == float('inf'):
                print(f"Error: Value must be at least {min_val}.")
            else:
                print(f"Error: Value must be between {min_val} and {max_val}.")
        except ValueError:
            print("Error: Please enter a valid number.")

def get_bool_input(prompt: str) -> bool:
    while True:
        val = input(prompt).strip().lower()
        if val in ('yes', 'y'):
            return True
        if val in ('no', 'n'):
            return False
        print("Error: Please enter 'yes' or 'no'.")

def get_default_empty_message(title: str) -> str:
    defaults = {
        "FINAL STATUS": "No academic status determined.",
        "RISK LEVEL": "Risk level unavailable.",
        "SEVERITY CONTEXT": "No critical academic risks detected at this time.",
        "ADVICE": "No guidance recommended at this time.",
        "EXPLANATION": "No explanation available.",
    }
    return defaults.get(title, "No data available.")


def print_section(title: str, content, default_msg: str = None):
    print(f"\n=== {title} ===")
    if not content:
        print(default_msg or get_default_empty_message(title))
        return
    
    if isinstance(content, str):
        print(content.strip())
    elif isinstance(content, list):
        for item in content:
            if isinstance(item, dict):
                msg = item.get("message", "Unknown message")
            else:
                msg = str(item)
            print(f"- {msg}")


def format_advice_items(advice_list):
    if not advice_list:
        return []

    actionable_verbs = (
        "prioritize", "maintain", "increase", "improve", "schedule",
        "complete", "investigate", "add", "focus", "seek", "review", "contact",
        "consider", "continue", "keep"
    )

    def normalize_phrase(phrase: str) -> str:
        phrase = phrase.strip().rstrip(".")
        return phrase[0].upper() + phrase[1:] if phrase else phrase

    def is_actionable_phrase(phrase: str) -> bool:
        normalized = phrase.lower().strip()
        return any(normalized.startswith(verb + " ") for verb in actionable_verbs)

    def extract_phrases(raw_text: str) -> list[str]:
        raw_text = raw_text.strip()
        if "—" in raw_text:
            raw_text = raw_text.split("—", 1)[1].strip()
        elif "-" in raw_text and raw_text.index("-") < 20:
            raw_text = raw_text.split("-", 1)[1].strip()

        parts = [part.strip() for part in raw_text.split(";") if part.strip()]
        actionable = [part for part in parts if is_actionable_phrase(part)]
        if actionable:
            return [normalize_phrase(part) + "." for part in actionable]

        if parts:
            selected = [part for part in parts if any(verb in part.lower() for verb in actionable_verbs)]
            if selected:
                return [normalize_phrase(part) + "." for part in selected]
            return [normalize_phrase(parts[-1]) + "."]

        return []

    seen = set()
    concise_advice = []
    for advice in advice_list:
        raw = advice.get("message", "") if isinstance(advice, dict) else str(advice)
        phrases = extract_phrases(raw)
        for phrase in phrases:
            normalized = phrase.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            concise_advice.append(phrase)

    return concise_advice


def calculate_risk_level(result, inputs):
    gpa = inputs.get("gpa", 0.0)
    alerts = result.severity_context or result.alerts or []
    alert_count = len(alerts)

    def describe_alert(alert_message: str) -> str:
        message = alert_message.lower()
        if "attendance" in message:
            return "Low attendance"
        if "assignment" in message:
            return "inconsistent assignment completion"
        if "gpa" in message or "probation" in message:
            return "GPA concerns"
        return alert_message.rstrip(".")

    if gpa < 2.0 or alert_count > 1:
        if gpa < 2.0 and alert_count > 1:
            return (
                "High",
                "GPA below 2.0 combined with multiple critical alerts indicates elevated academic risk."
            )
        if gpa < 2.0:
            return (
                "High",
                "GPA below 2.0 indicates elevated academic risk."
            )
        return (
            "High",
            "Multiple critical alerts indicate elevated academic risk."
        )

    if alert_count == 1 or (2.0 <= gpa < 3.0):
        if alert_count == 1 and gpa >= 3.0:
            alert_desc = describe_alert(alerts[0].get("message", "alert"))
            return (
                "Moderate",
                f"{alert_desc} introduces moderate academic risk despite a strong GPA."
            )

        if alert_count == 1:
            alert_desc = describe_alert(alerts[0].get("message", "alert"))
            reason_parts = [alert_desc]
            if 2.0 <= gpa < 3.0:
                reason_parts.append("GPA in the 2.0–3.0 range")
            return (
                "Moderate",
                f"{', '.join(reason_parts).capitalize()} indicates moderate academic risk."
            )

        return (
            "Moderate",
            "GPA in the 2.0–3.0 range indicates moderate academic risk."
        )

    return (
        "Low",
        "Strong GPA and no critical alerts indicate a lower academic risk profile."
    )


def format_explanation(result, inputs) -> str:
    status_message = result.final_status.get("message", "Unknown status") if result.final_status else "Unknown status"
    gpa = inputs.get("gpa", "N/A")
    attendance = inputs.get("attendance", "N/A")
    assignment_completion = inputs.get("assignment_completion", True)

    if status_message == "Excellent Standing":
        evaluation = f"The student has an excellent GPA of {gpa} and attendance at {attendance}%, which reflects strong academic performance."
    elif status_message == "Good Standing":
        evaluation = f"The student has a good GPA of {gpa} with attendance at {attendance}%, indicating generally solid academic performance."
    elif status_message == "Satisfactory Standing":
        evaluation = f"The student has a satisfactory GPA of {gpa}, but there is room to strengthen performance and attendance at {attendance}%."
    elif status_message == "Academic Probation Warning":
        evaluation = f"The student has a marginal GPA of {gpa} and is showing early warning signs in attendance at {attendance}% ."
    elif status_message == "Academic Probation":
        evaluation = f"The student has a low GPA of {gpa} and attendance at {attendance}%, indicating serious academic risk."
    else:
        evaluation = f"The student has a GPA of {gpa} and attendance at {attendance}%, which places current performance in the {status_message} category."

    key_weakness = None
    if result.severity_context:
        alert = result.severity_context[0].get("message", "").lower()
        if "attendance" in alert:
            key_weakness = "attendance below recommended levels"
        elif "assignment" in alert:
            key_weakness = "incomplete assignment completion"
        elif "gpa" in alert or "probation" in alert:
            key_weakness = "low GPA performance"
        else:
            key_weakness = alert.rstrip(".")
    else:
        if attendance != "N/A" and attendance < 80:
            key_weakness = "attendance below recommended levels"
        elif gpa != "N/A" and gpa < 3.0:
            key_weakness = "GPA below the higher performance range"
        elif not assignment_completion:
            key_weakness = "incomplete assignment completion"

    if key_weakness:
        issue = f"However, the main weakness is {key_weakness}."
        if "attendance" in key_weakness:
            impact = "This can reduce learning consistency and make it harder to maintain strong course performance."
        elif "gpa" in key_weakness:
            impact = "This may limit the student’s ability to stay above academic thresholds."
        else:
            impact = "This may hinder steady progress toward academic goals."
    else:
        issue = "No major weaknesses were identified in the current evaluation."
        impact = "The current performance profile is stable, but it should be maintained carefully."

    if "attendance" in (key_weakness or ""):
        recommendation = "Improving attendance while maintaining study habits is strongly recommended."
    elif "GPA" in (key_weakness or ""):
        recommendation = "Focus on targeted academic support and steady study routines to raise overall performance."
    elif "assignment" in (key_weakness or ""):
        recommendation = "Improve assignment completion consistency and continue regular study habits."
    else:
        recommendation = "Continue current habits while monitoring attendance and assignment completion."

    return " ".join([evaluation, issue, impact, recommendation])


def main():
    print("Welcome to the AI Student Advisor Expert System.")
    engine = InferenceEngine()

    while True:
        print("\n" + "="*40)
        print("        STUDENT EVALUATION")
        print("="*40)
        
        gpa = get_float_input("Enter GPA (0-4): ", 0.0, 4.0)
        attendance = get_float_input("Enter Attendance % (0-100): ", 0.0, 100.0)
        study_hours = get_float_input("Enter Study hours per day (>= 0): ", 0.0)
        assignment_completion = get_bool_input("Assignments completed? (yes/no): ")

        user_input = {
            "gpa": gpa,
            "attendance": attendance,
            "study_hours": study_hours,
            "assignment_completion": assignment_completion
        }

        print("\nAnalyzing data...")
        try:
            result = engine.evaluate(user_input)
            
            risk_level, risk_reason = calculate_risk_level(result, user_input)
            print_section("FINAL STATUS", result.final_status.get("message") if result.final_status else None)
            print_section("RISK LEVEL", risk_level)
            if risk_reason:
                print(f"\nReason: {risk_reason}")
            print_section("SEVERITY CONTEXT", result.severity_context)
            concise_advice = format_advice_items(result.advice_list)
            print_section("ADVICE", concise_advice)
            print_section("EXPLANATION", format_explanation(result, user_input))
            
        except Exception as e:
            print(f"\nError during evaluation: {e}")

        print("\n" + "-"*40)
        run_again = get_bool_input("Evaluate another student? (yes/no): ")
        if not run_again:
            print("Exiting AI Student Advisor. Goodbye!")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram interrupted by user. Exiting.")
        sys.exit(0)