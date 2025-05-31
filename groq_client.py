import os
from groq import Groq

# Load API key from environment variable
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set!")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

def classify_intent(text: str) -> str:
    labels = ["Invoice", "RFQ", "Complaint", "Regulation", "Other"]
    
    # Craft a zero-shot classification prompt
    prompt = f"""
    Classify the following text into ONE of these categories: {", ".join(labels)}.
    Return ONLY the label name, nothing else.

    Text: "{text}"
    """
    
    # Call Llama 3 70B via Groq API
    response = client.chat.completions.create(
        model="llama3-70b-8192",  # Groq's official model name for Llama 3 70B
        messages=[
            {"role": "system", "content": "You are a precise text classifier."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.1,  # Low temp for deterministic output
        max_tokens=10,    # Strict output length control
    )
    
    # Extract and validate the predicted label
    predicted_label = response.choices[0].message.content.strip()
    return predicted_label if predicted_label in labels else "Other"