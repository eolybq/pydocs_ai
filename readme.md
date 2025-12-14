# RAG documentation ChatBOT
- App is live at https://docs-rag-chat-bot.onrender.com

**Supported docs:**
- Pandas
- Numpy
- SK-Learn
- Matplotlib / Seaborn
... adding more soon!

This project creates RAG pipeline in python from scratch in order to get relevant documentation answers from LLMs. Project works with python libraries documentation files in HTML which are then parsed and cleaned from HTML tags, split into chunks with same context (context logic is to split HTML page into sections based on headings), converted to embedding vectors and stored in Supabase postgreSQL database. Then based on user query is relevant information from database retrieved and prompted into LLM (currently GPT 5-nano). User gets relevant information from documentation with LLM own output and will get more reliable information than with plain LLM usage. 

Project creates multiple API endpoints which implement uploading custom zip file of documentation (then preprocessing, embedding, storing / creating table in DB), converting user query to embedding vector and retrieving relevant content from vector database, prompting it with user query to LLM and outputing response.
- Project also contains frontend GUI which calls this API in form of React app to make using this functionality convenient.

- Project utilize OpenAI python library API endpoints in order to work with OpenAI embedding model and then to prompt relevant RAG retrieval data to GPT 5-nano.

Project uses docker to be live deployed on render

Project created in collaboration with my [brother](https://github.com/SwytDrymz)

## Tools used
- Python (SQLAlchemy, OpenAI, FastAPI, BeatifulSoup4)
- PostgreSQL (Supabase - pgvector)
- text-embedding-3-large 3072 dim
- React (Vite)

# Screenshots
![Screen1](assets/screen1.png)
![Screen2](assets/screen2.png)