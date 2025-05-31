from groq import Groq
import os
import json
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_email(content: str, conversation_id: str, memory) -> dict:
    """Process email content with improved entity extraction"""
    try:
        # Pre-process email content
        clean_content = re.sub(r'\n{3,}', '\n\n', content.strip())
        
        prompt = f"""
        Extract structured information from this email:
        {{
            "Sender": {{
                "name": "extracted from signature or from address",
                "email": "from address"
            }},
            "Recipient": "to address",
            "Subject": "email subject",
            "KeyDates": ["list of important dates"],
            "Urgency": "low/medium/high",
            "ActionItems": ["list of requested actions"],
            "Entities": {{
                "Products": ["mentioned products"],
                "Quantities": ["mentioned quantities"],
                "Companies": ["mentioned organizations"]
            }}
        }}

        Email Content:
        {clean_content[:10000]}

        Return ONLY valid JSON. Do not include any commentary or markdown formatting.
        """
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a precise email parsing assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Standardize output format
        standardized = {
            "Sender": result.get("Sender", {}),
            "Recipient": result.get("Recipient", ""),
            "Subject": result.get("Subject", ""),
            "KeyDates": result.get("KeyDates", []),
            "Urgency": result.get("Urgency", "medium").lower(),
            "ActionItems": result.get("ActionItems", []),
            "Entities": result.get("Entities", {})
        }
        
        memory.append_to_conversation(
            conversation_id,
            {
                "agent": "email_processor",
                "results": standardized,
                "processing_steps": ["Email processed successfully"]
            }
        )
        
        return standardized

    except Exception as e:
        error_msg = f"Email processing failed: {str(e)}"
        memory.append_to_conversation(
            conversation_id,
            {
                "agent": "email_processor",
                "error": error_msg,
                "processing_steps": ["Email processing failed"]
            }
        )
        return {"error": error_msg}