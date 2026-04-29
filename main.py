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

def print_section(title: str, content):
    print(f"\n=== {title} ===")
    if not content:
        print("None")
        return
    
    if isinstance(content, str):
        print(content)
    elif isinstance(content, list):
        for item in content:
            msg = item.get("message", "Unknown message")
            print(f"- {msg}")

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
            result = engine.evaluate(user_input).to_dict()
            
            print_section("FINAL STATUS", result.get("final_status", "Unknown"))
            print_section("SEVERITY CONTEXT", result.get("severity_context", []))
            print_section("ADVICE", result.get("advice_list", []))
            print_section("EXPLANATION", result.get("reasoning_narrative", ""))
            
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