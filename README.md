# 🐍 PyDocs AI: Python libraries expert
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)](#)
[![OpenAI](https://custom-icon-badges.demolab.com/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](https://developers.openai.com/api/docs/models/gpt-4.1-nano)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](#)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)](https://yezdata-pydocs-ai.hf.space)

> **Stop guessing parameters. Start coding with confidence.** PyDocs AI is a Retrieval-Augmented Generation (RAG) assistant that grounds LLM responses in the *actual* documentation of your favorite Python libraries. No more invented functions, no more deprecated syntax—just accurate, context-aware answers.

## 🚀 Try It Live
Don't just take our word for it. The app is deployed and ready to help you code:
- **[Frontend](https://yezdata-pydocs-ai.hf.space)**
- **[API Docs](https://yezdata-pydocs-ai-api.hf.space/docs)**

---

## 🔍 Visual Demonstration

https://github.com/user-attachments/assets/b03dc06d-6c45-4e86-af28-07e97c370987

---

## 📊 Project Scope: Accuracy through Context

This project contrasts standard LLM usage with a grounded **RAG (Retrieval-Augmented Generation)** pipeline. By retrieving exact documentation snippets before answering, the system minimizes errors and provides reliable code examples. Users get relevant information from documentation alongside the LLM's output, resulting in more reliable information than plain LLM usage.

### 📚 Knowledge Base
Currently indexed and supported libraries:
| Category | Libraries |
| :--- | :--- |
| Data Science | Pandas NumPy Scikit-Learn |
| Visualization | Matplotlib Seaborn |
| Database | SQLAlchemy |

---

## 🛠️ Under the Hood: Why It Works Better
Standard RAG tutorials often just split text by character count, breaking code blocks and losing context. PyDocs AI takes a **structure-first approach**:

### 1. Custom Context-Aware Ingestion Pipeline (`scripts/embedd_docs.py`)
Standard text splitters often break code blocks or separate headers from their content. This project implements a **semantic ingestion engine**:
*   **Context Preservation:** Splits HTML pages based on logical sections (Headings `<h1>`-`<h6>`) rather than arbitrary character counts.
*   **Resiliency:** Implements a checkpoint system (`checkpoints.json`) to handle large datasets and resume interrupted jobs seamlessly.
*   **Batch Processing:** Optimizes OpenAI API usage with batched embedding requests and bulk inserts to PostgreSQL.

### 2. High-Fidelity Embeddings (OpenAI)
The system utilizes OpenAI's **text-embedding-3-large** model for superior semantic understanding.
*   **Why?** The 3072-dimensional vectors provide significantly better nuance for technical terminology compared to smaller models.
*   **Efficiency:** Batched conversion and bulk upserts to PostgreSQL ensure high performance during documentation ingestion.

### 3. RAG Architecture
Instead of relying on a "Black Box" LLM, the system uses a "Glass Box" retrieval method:
1.  **Vectorization:** User queries are converted to embeddings in real-time.
2.  **Similarity Search:** `pgvector` retrieves chunks using Euclidean distance.
3.  **Prompt Injection:** The LLM is forced to use *only* the provided context, ensuring factual accuracy.

### 4. REST API & Cloud Deployment (FastAPI + Docker)
Exposed the core RAG logic via a robust FastAPI backend, ensuring high-performance handling of concurrent user requests.
*   **API Design:** Implemented endpoints for query processing and documentation management.
*   **Containerization:** Both API and Frontend are **Dockerized**, ensuring consistency across different environments.
*   **CI/CD:** Automated deployment to **Hugging Face Spaces** via GitHub Actions.

---

## 💻 Tech Stack
*   **API:** Python 3.12, FastAPI, SQLAlchemy, BeautifulSoup4
*   **Frontend:** Streamlit
*   **Database:** PostgreSQL + pgvector (Neon.tech)
*   **Infrastructure:** Docker, CI/CD to Hugging Face Spaces
*   **AI/ML:** OpenAI API (Embeddings & Chat)

---
*🤝 Collaboration*
Built by [Václav Jež]https://github.com/eolybq & [Vojtěch Jež](https://github.com/SwytDrymz).

Star this repo if you found it useful! ⭐
