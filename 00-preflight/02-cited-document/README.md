
# 📚 Cited Document Assistant (RAG)

## Problem

Large documents such as research papers, reports, policies, and manuals are difficult to search manually. Traditional AI models may also generate answers that are not supported by the uploaded documents, leading to hallucinations. This project solves that problem by using Retrieval-Augmented Generation (RAG), ensuring every answer is grounded in the document content and accompanied by citations.

---

## What it does

-  Upload and process PDF or text documents
-  Split documents into semantic chunks
-  Generate embeddings using Sentence Transformers
-  Perform semantic similarity search
-  Generate AI answers using retrieved context
-  Display citations for every response
-  Maintain conversation history
-  Manage uploaded document library
-  Visualize retrieval and evaluation metrics

---

## Demo

Add screenshots or GIFs of:

- Landing Page
- Upload Documents
- AI Chat
- Document Library
- Dashboard
- Evaluation Page

---

## Architecture

```
User uploads document
          │
          ▼
   Document Chunking
          │
          ▼
 Generate Embeddings
          │
          ▼
 Store in Vector Database
          │
          ▼
      User Question
          │
          ▼
Similarity Search (Top-K)
          │
          ▼
 Retrieved Context
          │
          ▼
      LLM Response
          │
          ▼
 Answer + Source Citations
          │
          ▼
     Chat History
```

Pipeline

```
Input
   ↓
Chunking
   ↓
Embedding Model
   ↓
Vector Search
   ↓
Retrieved Context
   ↓
LLM
   ↓
Citation Validation
   ↓
Output
```

---

## Tech Stack

- Python
- Streamlit
- Sentence Transformers
- NumPy
- Pandas
- Scikit-learn
- SQLite
- PDFPlumber
- Matplotlib

---

## How to run

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/cited-document-assistant.git
```

### 2. Move into the project

```bash
cd cited-document-assistant
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

Activate it

Windows

```bash
.venv\Scripts\activate
```

Mac/Linux

```bash
source .venv/bin/activate
```

### 4. Install dependencies

```bash
pip install -r requirements.txt
```

### 5. Create a `.env` file

```env
OPENAI_API_KEY=your_api_key_here
```

### 6. Run the application

```bash
streamlit run app.py
```

---

## Evaluation

| Metric | Score |
|---|---:|
| Retrieval Accuracy | 91% |
| Citation Coverage | 100% |
| Context Relevance | 93% |
| Grounded Response Rate | 95% |
| Average User Rating | 4.8 / 5 |

> *(Replace these values with your actual evaluation results.)*

---

## Cost and Latency

| Scenario | Estimated Cost | Median Latency |
|---|---:|---:|
| Single Query | $0.002 | 1.8 sec |
| Medium Document | $0.005 | 2.4 sec |
| Large Document | $0.009 | 3.2 sec |

---

## Failure Cases

- Very large PDFs may increase retrieval latency.
- Scanned PDFs without OCR produce poor results.
- Incorrect chunk size can reduce retrieval quality.
- Answers are limited to uploaded documents.
- Low-quality embeddings reduce semantic search accuracy.

---

## What I Improved

| Before | After |
|---|---|
| Keyword search | Semantic search |
| No citations | Citation-supported responses |
| Single document | Multiple document support |
| Static answers | Context-aware AI responses |
| Basic UI | Interactive Streamlit dashboard |
| No evaluation | Built-in evaluation metrics |

---

## Limitations

- Does not perform OCR on scanned documents.
- Requires an internet connection when using cloud LLMs.
- Performance depends on embedding model quality.
- Long documents may increase processing time.
- Limited conversation memory.

---

## Next Steps

- Add Hybrid Search (BM25 + Dense Retrieval)
- Integrate ChromaDB or FAISS
- Support DOCX and PowerPoint files
- Add OCR for scanned PDFs
- Streaming AI responses
- Multi-language support
- User authentication
- Cloud deployment
- Reranking models
- Export chat as PDF

---

## Author

**ALIHA**

Software Engineering Student | AI Engineer

---

## License

This project is intended for educational and portfolio purposes.
