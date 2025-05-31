import streamlit as st
from agents.classifier_agent import classify_and_route
from agents.email_agent import process_email
from agents.json_agent import process_json
from agents.pdf_agent import process_pdf
from memory.shared_memory import SharedMemory
import uuid
from datetime import datetime
import sqlite3
import threading
import json
import os
import streamlit.components.v1 as components

# ---------- Persistent Log Setup ----------
LOG_PATH = "output_logs/log.jsonl"
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def log_to_file(conversation_id: str, step: str, data: dict):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "conversation_id": conversation_id,
        "step": step,
        "data": data
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(log_entry) + "\n")

# ---------- Thread-Safe Shared Memory ----------
local_storage = threading.local()

def get_db_connection():
    if not hasattr(local_storage, "conn"):
        local_storage.conn = sqlite3.connect(":memory:", check_same_thread=False)
        local_storage.conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            conversation_id TEXT PRIMARY KEY,
            data TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
    return local_storage.conn

class ThreadSafeSharedMemory:
    def __init__(self):
        self.lock = threading.Lock()
        
    def store(self, conversation_id: str, data: dict):
        with self.lock:
            conn = get_db_connection()
            conn.execute(
                "INSERT INTO conversations (conversation_id, data) VALUES (?, ?)",
                (conversation_id, str(data))
            )
            conn.commit()
            log_to_file(conversation_id, "store", data)
    
    def append_to_conversation(self, conversation_id: str, data: dict):
        with self.lock:
            conn = get_db_connection()
            cursor = conn.execute(
                "SELECT data FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            result = cursor.fetchone()
            
            if result:
                existing_data = eval(result[0])
                updated_data = {**existing_data, **data}
                conn.execute(
                    "UPDATE conversations SET data = ? WHERE conversation_id = ?",
                    (str(updated_data), conversation_id)
                )
                log_to_file(conversation_id, "append", data)
            else:
                conn.execute(
                    "INSERT INTO conversations (conversation_id, data) VALUES (?, ?)",
                    (conversation_id, str(data))
                )
                log_to_file(conversation_id, "store", data)
            conn.commit()
    
    def retrieve_conversation(self, conversation_id: str) -> dict:
        with self.lock:
            conn = get_db_connection()
            cursor = conn.execute(
                "SELECT data FROM conversations WHERE conversation_id = ?",
                (conversation_id,)
            )
            result = cursor.fetchone()
            return eval(result[0]) if result else None

# ---------- Display JSON ----------
def display_json(data):
    json_str = json.dumps(data, indent=2)
    html = f"""
    <pre style='
        color: white;
        font-family: monospace;
        white-space: pre;
        background-color: transparent;
        margin: 0;
        padding: 10px;
    '>
    {json_str}
    </pre>
    """
    components.html(html, height=min(800, 200 + len(json_str) // 2), scrolling=True)

# ---------- Main App ----------
memory = ThreadSafeSharedMemory()

st.title("📨 Multi-Agent AI System")

tab1, tab2 = st.tabs(["📁 Upload File", "✍️ Text Input"])

process_file = False
process_text = False

with tab1:
    uploaded_file = st.file_uploader(
        "Upload a file (PDF, JSON, or Email)", 
        type=["pdf", "json", "txt", "eml"],
        key="file_uploader"
    )
    process_file = st.button("Process File", key="process_file")

with tab2:
    input_text = st.text_area(
        "Paste your content directly:",
        height=200,
        placeholder="Paste email text, JSON, or other content here...",
        key="text_input"
    )
    process_text = st.button("Process Text", key="process_text")

if process_file and uploaded_file is not None:
    content_source = uploaded_file
    content_type = "file"
elif process_text and input_text.strip():
    content_source = input_text
    content_type = "text"
else:
    content_source = None

if content_source:
    conversation_id = str(uuid.uuid4())
    timestamp = datetime.now().isoformat()
    
    try:
        if content_type == "file":
            source = f"file:{uploaded_file.name}"
            raw_content = uploaded_file.getvalue()

            if uploaded_file.name.endswith(".pdf"):
                content = raw_content
                classification_input = "[PDF FILE]"
            elif uploaded_file.name.endswith((".txt", ".eml", ".json")):
                content = raw_content.decode("utf-8", errors="ignore")
                classification_input = content
            else:
                raise ValueError("Unsupported file format.")
        else:
            source = "text_input"
            content = input_text
            classification_input = content

        preview = classification_input

        memory.store(
            conversation_id=conversation_id,
            data={
                "source": source,
                "upload_timestamp": timestamp,
                "original_content": preview[:1000] + "..." if len(preview) > 1000 else preview,
                "processing_steps": []
            }
        )
        
        with st.spinner("Classifying content..."):
            classification = classify_and_route(source, classification_input)
        
        memory.append_to_conversation(
            conversation_id=conversation_id,
            data={
                "classification": classification,
                "processing_steps": [f"Classified as {classification['format']} with intent {classification['intent']}"]
            }
        )
        
        with st.expander("🔍 Classification Results", expanded=True):
            display_json(classification)
        
        with st.spinner(f"Processing {classification['format']}..."):
            if classification["format"] == "email":
                result = process_email(content, conversation_id, memory)
            elif classification["format"] == "json":
                result = process_json(content, conversation_id, memory)
            elif classification["format"] == "pdf":
                result = process_pdf(content, conversation_id, memory)
            else:
                raise ValueError("Unsupported format for processing.")
            
            st.subheader("📝 Processing Results")
            display_json(result)
            
            st.subheader("🕒 Processing History")
            history = memory.retrieve_conversation(conversation_id)
            display_json(history)
            
    except Exception as e:
        st.error(f"❌ Error processing content: {str(e)}")
        memory.append_to_conversation(
            conversation_id=conversation_id,
            data={
                "error": str(e),
                "processing_steps": ["Error during processing"]
            }
        )
