# 🧠 Multi-Agent AI Document Classifier & Processor

This is a Streamlit-based multi-agent AI system that classifies incoming documents (PDF, JSON, EML, or plain text) and routes them to specialized agents for processing. It uses Groq’s LLaMA 3 (70B) for classification and analysis.

---

## 📂 Folder Structure

```

multi_agent_app
├── app.py
├── agents
│   ├── classifier_agent.py
│   ├── email_agent.py
│   ├── json_agent.py
│   └── pdf_agent.py
├── memory
│   └── shared_memory.py
├── sample_inputs
│   ├── sample.json
│   ├── sample.eml
│   └── sample.pdf
├── output_logs
│   └── log.jsonl
├── requirements.txt
└── README.md

````

---

## 🚀 Features

- **File uploads**: Supports `.pdf`, `.json`, `.eml`, `.txt`
- **Text classification**: Determines format and intent
- **Routing**: Forwards input to the appropriate agent
- **Agents**:
  - 📧 Email Agent
  - 📄 PDF Agent
  - 🧾 JSON Agent
- **Shared memory**: Stores conversation history using SQLite (thread-safe)
- **LLM backend**: Uses Groq’s LLaMA 3 (70B) via `groq` API

---

## 📸 Screenshots

### 📁 File Upload & Classification
![image](https://github.com/user-attachments/assets/0abba617-cc59-4f94-a9b9-875b418d9255)


### 🧾 PDF Analysis Output
![image](https://github.com/user-attachments/assets/13c417f6-60bd-42b6-b80b-f90a2ab7aa4b)
![image](https://github.com/user-attachments/assets/fde6b104-5e34-4e43-81d1-166c8ddff6bb)

---

## 📎 Sample Inputs

Samples provided in the `sample_inputs/` folder:

- `sample.pdf` – An invoice-style document
- `sample.json` – JSON API request sample
- `sample.eml` – A plain-text email message

You can upload these directly in the Streamlit interface to test functionality.

---

## 🧪 Sample Output Logs

Logs are written to the `output_logs/` directory for debug or review. For example:

```json
{"timestamp": "2025-06-01T01:57:11.898802", "conversation_id": "13fe32a3-c552-4576-8796-00467272c97a", "step": "store", "data": {"source": "file:sample.pdf", "upload_timestamp": "2025-06-01T01:57:11.897803", "original_content": "[PDF FILE]", "processing_steps": []}}
{"timestamp": "2025-06-01T01:57:12.218592", "conversation_id": "13fe32a3-c552-4576-8796-00467272c97a", "step": "append", "data": {"classification": {"format": "pdf", "intent": "Other", "source": "file:sample.pdf"}, "processing_steps": ["Classified as pdf with intent Other"]}}
{"timestamp": "2025-06-01T01:57:12.228576", "conversation_id": "13fe32a3-c552-4576-8796-00467272c97a", "step": "append", "data": {"pdf_text_sample": "INVOICE\n \n#INV-2024-1001\n \nDate:\n \n2024-05-20\n \nDue\n \nDate:\n \n2024-06-20\n \nFrom:\n \nSupplier\n \nInc.\n \nTo:\n \nAcme\n \nCorp.\n \nITEMS:\n \n-\n \nWidget\n \nA:\n \n50\n \nunits\n \n@\n \n$12.00\n \n-\n \nWidget\n \nB:\n \n30\n \nunits\n \n@\n \n$8.50\n \nTOTAL:\n \n$855.00\n \n ", "is_pasted_text": false, "processing_steps": ["PDF content extracted"]}}
{"timestamp": "2025-06-01T01:57:12.824038", "conversation_id": "13fe32a3-c552-4576-8796-00467272c97a", "step": "append", "data": {"agent": "pdf_processor", "results": {"document_type": "invoice", "key_entities": {"invoice_number": "#INV-2024-1001", "date": "2024-05-20", "due_date": "2024-06-20", "supplier": "Supplier Inc.", "buyer": "Acme Corp.", "items": [{"item": "Widget A", "quantity": 50, "unit_price": 12.0}, {"item": "Widget B", "quantity": 30, "unit_price": 8.5}], "total": 855.0}, "anomalies": []}, "processing_steps": ["PDF analysis completed"]}}

````

---

## 🛠️ Setup Instructions

1. **Clone the repo**

   ```bash
   git clone https://github.com/yourusername/multi-agent-ai-docs.git
   cd multi-agent-ai-docs
   ```

2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Set your Groq API key**

   ```bash
   export GROQ_API_KEY=your_key_here
   ```

4. **Run the Streamlit app**

   ```bash
   streamlit run app.py
   ```

---

## ✅ Requirements

* Python 3.9+
* Groq Python SDK (`groq`)
* Streamlit
* PyPDF2
* SQLite (default)

See `requirements.txt` for full list.

---

## 🧠 Model Used

* **LLM**: [Groq's LLaMA 3 70B](https://groq.com/)
* **Response Format**: Structured JSON via `response_format={"type": "json_object"}`

---

### 📝 You Should Also Include

#### `requirements.txt`
```txt
streamlit
groq
PyPDF2
pygments
````
