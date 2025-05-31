from groq import Groq
import os
import re
import json

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def classify_and_route(source: str, content: str) -> dict:
    """Classify content with improved JSON detection"""
    # First check if content is valid document JSON
    if is_document_json(content):
        return {
            "format": "json",
            "intent": detect_json_intent(content),
            "source": source
        }
    
    # Then check for PDF-like structure
    if is_pdf_like_content(content):
        return {
            "format": "pdf",
            "intent": detect_pdf_intent(content),
            "source": source
        }
    
    # Default to normal classification
    return normal_classification(source, content)

def is_document_json(content: str) -> bool:
    """Check if content is valid JSON and resembles a document"""
    try:
        data = json.loads(content)
        # Only consider it JSON format if it has document-like structure
        document_keys = {'id', 'type', 'date', 'items', 'from', 'to', 'subject'}
        if isinstance(data, dict) and any(key in data for key in document_keys):
            return True
        return False
    except ValueError:
        return False

def detect_json_intent(content: str) -> str:
    """Determine intent of JSON content"""
    data = json.loads(content)
    
    # Check for invoice patterns
    invoice_patterns = [r'invoice', r'total', r'amount', r'due_date']
    if any(re.search(pattern, str(data), re.IGNORECASE) for pattern in invoice_patterns):
        return "Invoice"
    
    # Check for RFQ patterns
    rfq_patterns = [r'rfq', r'request for quotation', r'items', r'quote']
    if any(re.search(pattern, str(data), re.IGNORECASE) for pattern in rfq_patterns):
        return "RFQ"
    
    return "Other"

def detect_pdf_intent(content: str) -> str:
    """Detect intent of PDF-like content"""
    # Check for invoice patterns
    invoice_keywords = ['invoice', 'total', 'subtotal', 'amount due', 'balance']
    if any(keyword.lower() in content.lower() for keyword in invoice_keywords):
        return "Invoice"
    
    # Check for RFQ patterns
    rfq_keywords = ['rfq', 'request for quote', 'quotation', 'pricing']
    if any(keyword.lower() in content.lower() for keyword in rfq_keywords):
        return "RFQ"
    
    return "Other"

def is_pdf_like_content(content: str) -> bool:
    """Check for PDF structure without matching JSON"""
    if is_document_json(content):
        return False
        
    pdf_patterns = [
        r"^\s*[A-Z0-9\-_]+\s+#\d+",  # Document numbers
        r"\b\d+\s+units?\s+@\s+\$\d+\.?\d*",  # Line items
        r"\b(?:total|subtotal|amount due)\s*:\s*\$\d+\.?\d*",  # Monetary amounts
        r"\bpage\s+\d+\s+of\s+\d+\b",  # Pagination
        r"\b(?:invoice|receipt|contract|agreement)\b"  # Document types
    ]
    return any(re.search(pattern, content, re.IGNORECASE) for pattern in pdf_patterns)

def normal_classification(source: str, content: str) -> dict:
    """Standard LLM classification with error handling"""
    try:
        format_prompt = f"""Classify this content's format (respond ONLY with one word):
        Options: pdf, json, email, text
        Content: {content[:2000]}"""
        
        intent_prompt = f"""Classify this content's intent (respond ONLY with one word):
        Options: Invoice, RFQ, Complaint, Regulation, Other
        Content: {content[:2000]}"""
        
        format_response = get_llm_classification(format_prompt).lower()
        intent_response = get_llm_classification(intent_prompt)
        
        # Validate responses
        valid_formats = {'pdf', 'json', 'email', 'text'}
        valid_intents = {'Invoice', 'RFQ', 'Complaint', 'Regulation', 'Other'}
        
        format_response = format_response if format_response in valid_formats else 'text'
        intent_response = intent_response if intent_response in valid_intents else 'Other'
        
        return {
            "format": format_response,
            "intent": intent_response,
            "source": source
        }
    except Exception as e:
        # Fallback to safe defaults if classification fails
        return {
            "format": "text",
            "intent": "Other",
            "source": source
        }

def get_llm_classification(prompt: str) -> str:
    """Get single-word classification from LLM with error handling"""
    try:
        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
            max_tokens=10,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "Other"