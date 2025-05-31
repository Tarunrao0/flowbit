# Multi-Agent AI System

A document processing system that classifies and routes PDFs, JSON files, and emails to specialized agents for intelligent processing. Built with modular agents, shared memory, and Groq-powered LLM classification.

![image](https://github.com/user-attachments/assets/956d9f33-c966-4b2d-9484-9e799f3730b9)


---

## Features

### Automatic Classification
- Detects document format: **PDF / JSON / Email**
- Identifies document **intent**: Invoice, RFQ, Complaint, Regulation, etc.

### Specialized Agents
- **PDF Agent**: Extracts and processes text from PDF documents
- **JSON Agent**: Validates JSON schema, flags missing fields
- **Email Agent**: Parses sender, subject, body, and urgency from email content

### Shared Memory (SQLite)
- Stores sender, document type, timestamp, and extracted fields
- Thread-aware memory for chaining and context tracing
- Accessible to all agents for context-sharing

---

## Tech Stack

| Component     | Tech                     |
|---------------|--------------------------|
| **Backend**   | Python 3.9+              |
| **LLM**       | Groq / LLaMA3-70B        |
| **Web UI**    | Streamlit                |
| **PDF Parser**| PyMuPDF / PyPDF2         |
| **Memory**    | SQLite (via `sqlite3`)   |
| **Classification** | Transformers pipeline (Groq API) |

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/yourusername/multi-agent-ai-system.git
   cd multi-agent-ai-system

2. **Create Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Requirements**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**
   Create a `.env` file:

   ```env
   GROQ_API_KEY=your_groq_api_key
   ```

---

## Sample Inputs

### Email

Upload a `.txt` file like:

```
From: supplier@example.com
Subject: Request for Quotation

Please quote for 1,000 units of Widget A.
```

### JSON

Upload a `.json` like:

```json
{
  "id": "INV-1001",
  "type": "Invoice",
  "amount": 2500
}
```

### PDF

Upload a PDF with plain text content (e.g. invoice or regulation text).

---

## Run the App

Start the Streamlit frontend:

```bash
streamlit run streamlit_app.py
```

---

## Project Structure

```
multi-agent-ai-system/
├── agents/
│   ├── classifier_agent.py
│   ├── email_agent.py
│   ├── json_agent.py
│   └── pdf_agent.py
├── memory/
│   └── memory_store.py
├── utils/
│   └── file_utils.py
├── config.py
├── groq_client.py
├── main.py
├── streamlit_app.py
├── requirements.txt
└── .env
```

---

## How It Works

1. **User uploads a file** in the Streamlit app.
2. The **Classifier Agent** detects format + intent.
3. The file is **routed to the relevant agent**:

   * PDF Agent
   * JSON Agent
   * Email Agent
4. Agent processes content and stores results in shared SQLite memory.
5. Final output is shown in the UI and available via memory lookup.
