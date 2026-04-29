from inference_engine import InferenceEngine

engine = InferenceEngine()

result = engine.evaluate({
    "gpa": 1.8,
    "attendance": 65,
    "study_hours": 1,
    "assignment_completion": False   # must match the expected field name
})

print(result.to_dict())
