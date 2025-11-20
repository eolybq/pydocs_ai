# RAG documentation ChatBOT
- Project is currently working when runned with local "Qwen 3 embedding 8b"
- In progress is integration with OpenAI embedding and Chat model in order to dockerize whole app and deploy it into live production

This project creates RAG pipeline in python from scratch in order to get relevant documentation answers from LLMs. Project works with python libraries documentation files in HTML which are then parsed and cleaned from HTML tags, split into chunks with same context (context logic is to split HTML page into sections based on headings), converted to embedding vectors and stored in Supabase postgreSQL database. Then based on user query is relevant information from database retrieved and prompted into LLM (currently Gemini). User gets relevant information from documentation with LLM own output and will get more reliable information than with plain LLM usage. 

Project creates multiple API endpoints which implement uploading custom zip file of documentation (then preprocessing, embedding, storing / creating table in DB), converting user query to embedding vector and retrieving relevant content from vector database, prompting it with user query to LLM and outputing response.
- Project also contains frontend GUI which calls this API in form of React app to make using this functionality convenient.

**Now:**  
- Project utilize OpenAI python library API endpoints in order to work with locally runned embedding models in LMStudio and then to prompt relevant RAG retrieval data to GeminiAPI.
- Both of these API are used through OpenAI library.  

**In plan:**  
- Swapping LMStudio models with OpenAI embedding models, swapping Gemini with ChatGPT 5.1 nano
- Turning app into production ready app and dockerizing -> deployment  


Project created in collaboration with my [brother](https://github.com/SwytDrymz)

## Tools used
- Python (SQLAlchemy, OpenAI, FastAPI, BeatifulSoup4)
- PostgreSQL (Supabase - pgvector)
- LMStudio (Qwen 3 text-embedding) / GeminiAPI
- React (Vite)

## Screenshots
[//]: # (TODO pridat screenshot z UI az bude hotovo)
- UI implement still in progress