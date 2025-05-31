from agents.classifier_agent import classify_and_route
import uuid

def run_pipeline(file_name: str, content: str):
    thread_id = str(uuid.uuid4())
    format_type, intent, result = classify_and_route(file_name, content, thread_id)
    return {
        "thread_id": thread_id,
        "format": format_type,
        "intent": intent,
        "result": result
    }
