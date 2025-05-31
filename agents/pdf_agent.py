from groq import Groq
import os
import json
import PyPDF2
from io import BytesIO
import re

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def process_pdf(content: str | bytes, conversation_id: str, memory) -> dict:
    """Process PDF content (either binary or text)"""
    try:
        # Handle both string (pasted) and bytes (uploaded) input
        if isinstance(content, str):
            text = content
            is_pasted_text = True
        else:
            with BytesIO(content) as pdf_file:
                reader = PyPDF2.PdfReader(pdf_file)
                text = "\n".join(page.extract_text() for page in reader.pages)
            is_pasted_text = False

        if not text.strip():
            raise ValueError("No extractable content found")

        # Store metadata
        memory.append_to_conversation(
            conversation_id,
            {
                "pdf_text_sample": text[:1000] + "..." if len(text) > 1000 else text,
                "is_pasted_text": is_pasted_text,
                "processing_steps": ["PDF content extracted"]
            }
        )

        # Analyze content
        prompt = f"""
        Analyze this {'pasted text' if is_pasted_text else 'PDF document'}:
        1. Document type (invoice, contract, report, etc.)
        2. Key entities (names, dates, amounts)
        3. Anomalies or special formatting
        
        Return JSON with:
        - document_type: string
        - key_entities: dict
        - anomalies: array
        
        Content:
        {text[:15000]}
        """
        
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        
        result = json.loads(response.choices[0].message.content)
        memory.append_to_conversation(
            conversation_id,
            {
                "agent": "pdf_processor",
                "results": result,
                "processing_steps": ["PDF analysis completed"]
            }
        )
        
        return result

    except Exception as e:
        error_msg = f"PDF processing failed: {str(e)}"
        memory.append_to_conversation(
            conversation_id,
            {
                "agent": "pdf_processor",
                "error": error_msg,
                "processing_steps": ["PDF processing failed"]
            }
        )
        return {"error": error_msg}