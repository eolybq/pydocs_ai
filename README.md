# PyDocs AI: Python libraries expert
[![Python](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)](#)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)](#)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)](#)
[![OpenAI](https://custom-icon-badges.demolab.com/badge/ChatGPT-74aa9c?logo=openai&logoColor=white)](https://developers.openai.com/api/docs/models/gpt-4.1-nano)
[![Docker](https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white)](#)
[![Hugging Face](https://img.shields.io/badge/Hugging%20Face-FFD21E?logo=huggingface&logoColor=black)](https://yezdata-pydocs-ai.hf.space)

App is **live** on Hugging Face Spaces:
- **[Frontend](https://yezdata-pydocs-ai.hf.space)**
- **[API](https://yezdata-pydocs-ai-api.hf.space/docs)**

> **Quick Summary:** A full-stack Retrieval-Augmented Generation (RAG) system designed to solve the "hallucination" problem in LLM's responses, written from scratch in Python. It ingests raw HTML documentation, creates semantic embeddings, and grounds LLM responses in factual data from libraries like Pandas, NumPy, and Scikit-learn. This allows the LLM to have the right context when asked a question about Python libraries.

---

## 🔍 Visual Demonstration

https://github.com/user-attachments/assets/b03dc06d-6c45-4e86-af28-07e97c370987

---

## 📊 Project Scope: Accuracy through Context

This project contrasts standard LLM usage with a grounded **RAG (Retrieval-Augmented Generation)** pipeline. By retrieving exact documentation snippets before answering, the system minimizes errors and provides reliable code examples. Users get relevant information from documentation alongside the LLM's output, resulting in more reliable information than plain LLM usage.

## 🏆 Key Capabilities

| Component | Feature | Technology |
| :--- | :--- | :--- |
| **Smart Ingestion** | Context-aware HTML parsing & semantic chunking. | `BeautifulSoup4` |
| **Vector Search** | High-dimensional similarity search (3072 dim). | `pgvector` (Neon.tech) |
| **Inference** | Grounded answers using retrieved context. | `GPT-4.1-nano` |
| **Frontend** | Interactive data-driven chat interface. | `Streamlit` |

### Currently Supported Docs
*   **Data Science:** Pandas, NumPy, Scikit-Learn
*   **Visualization:** Matplotlib, Seaborn
*   **Database:** SQLAlchemy

---

## 🛠️ Engineering Highlights

### 1. Custom Ingestion Pipeline (`scripts/embedd_docs.py`)
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
*   **Infrastructure:** PostgreSQL (Neon.tech - pgvector), Docker, Hugging Face Hub
*   **AI/ML:** OpenAI API (Embeddings & Chat)

---
*Created in collaboration with [SwytDrymz](https://github.com/SwytDrymz)*
