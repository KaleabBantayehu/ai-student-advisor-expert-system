from src.inference_engine import InferenceEngine

def main():
    engine = InferenceEngine()

    user_input = {
        "gpa": 3.2,
        "attendance": 85,
        "study_hours": 3,
        "assignment_completion": True
    }

    result = engine.evaluate(user_input)
    print(result.to_dict())

if __name__ == "__main__":
    main()