import json
import mimetypes

def detect_format(file_name: str, content: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_name)
    if mime_type == 'application/pdf':
        return 'PDF'
    try:
        json.loads(content)
        return 'JSON'
    except json.JSONDecodeError:
        pass
    if "From:" in content and "Subject:" in content:
        return 'Email'
    return 'Unknown'
