# RAG documentation ChatBOT
- ! This project aims to be runned locally (hosting isn't in plan) - in order to use locally runned open-source models with free usage  

This project creates RAG pipeline in python from scratch in order to get relevant documentation answers from LLMs. Project works with python libraries documentation files in HTML which are then parsed and cleaned from HTML tags, split into chunks with same context (context logic is to split HTML page into sections based on headings), converted to embedding vectors and stored in Supabase postgreSQL database. Then based on user query is relevant information from database retrieved and prompted into LLM (currently Gemini). User gets relevant information from documentation with LLM own output and will get more reliable information than with plain LLM usage. 

Project creates API endpoint which when called, convert user query to embedding vector and retrieves relevant content from vector database, prompts it with user query to LLM and outputs response.
- Project also contains frontend GUI which calls this API in form of react app to make using this functionality convenient.

Project utilize OpenAI python library api endpoints in order to work with locally runned embedding models in LMStudio and then to prompt relevant RAG retrieval data to GeminiAPI. Both of these API are used through OpenAI library.  


## Tools used
- Python (SQLAlchemy, OpenAI, FastAPI, BeatifulSoup4)
- PostgreSQL (Supabase - pgvector)
- LMStudio (Qwen 3 text-embedding) / GeminiAPI
- React (Vite), HTML

## Screenshots
[//]: # (TODO pridat screenshot z UI az bude hotovo)
- UI implement still in progress