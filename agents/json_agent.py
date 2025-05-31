from groq import Groq
import os
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_json(content: str, conversation_id: str, memory) -> dict:
    """Process JSON content with robust validation"""
    try:
        # First validate basic JSON structure
        data = json.loads(content)
        
        prompt = f"""
        Analyze this JSON document:
        {{
            "validation": {{
                "missing_fields": ["list of expected but missing fields"],
                "anomalies": ["list of data anomalies"]
            }},
            "enhancements": {{
                "suggested_fields": ["list of recommended additional fields"],
                "normalization": ["suggested data formatting improvements"]
            }}
        }}

        JSON Content:
        {content}

        Rules:
        1. For invoices: expect 'id', 'type', 'amount', 'currency', 'date', 'due_date'
        2. For RFQs: expect 'items', 'delivery_date', 'payment_terms'
        3. Return empty arrays if nothing is missing/anomalous

        Return ONLY valid JSON. Do not include commentary or markdown formatting.
        """
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a precise JSON validator."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        result = {
            "original": data,
            "validation": analysis.get("validation", {}),
            "enhancements": analysis.get("enhancements", {})
        }
        
        memory.append_to_conversation(
            conversation_id,
            {
                "agent": "json_processor",
                "results": result,
                "processing_steps": ["JSON processed successfully"]
            }
        )
        
        return result

    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON: {str(e)}"
        memory.append_to_conversation(
            conversation_id,
            {
                "agent": "json_processor",
                "error": error_msg,
                "processing_steps": ["JSON validation failed"]
            }
        )
        return {"error": error_msg}
    except Exception as e:
        error_msg = f"JSON processing failed: {str(e)}"
        memory.append_to_conversation(
            conversation_id,
            {
                "agent": "json_processor",
                "error": error_msg,
                "processing_steps": ["JSON processing failed"]
            }
        )
        return {"error": error_msg}