from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from services.create_embeddings import convert_embedding_batch
from services.database import search_similar, get_tables

load_dotenv()

origins = [
    "http://localhost:8000",
    "http://localhost:3000",
    "https://docs-rag-chat-bot.onrender.com",
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def get_llm_res(user_query, sim_embeddings):
    context_str = "\n\n".join(
        f"<chunk>\nmain_title: {c['main_title']}\nchunk_title: {c['chunk_title']}\ncontent: {c['content']}\n</chunk>"
        for c in sim_embeddings
    )

    prompt = f"""
    Please answer the user query based on the following context:

    <context>
    {context_str}
    </context>

    <query>
    {user_query}
    </query>
    """

    # models = client.models.list()
    # for model in models:
    #     print(model.id)

    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {
                "role": "system",
                "content": """
                    Answer in English. You are a professional python RAG assistant. In every prompt you recive relevant data from RAG system (<context>), you use this data to enhance your answer to user message (<user_query>).
                    If <context> doesn't contain anything relevant to QUERY, say : "I cannot answer this based on the provided documentation.".
                    - Answer like a RAG system ChatBot should - with smart information management from <context> .
                    - If the user asks about a concept not explicitly in the docs (like "Time Series"), apply the library's documented API to that concept using your general knowledge.
                    - If there is a conflict between your internal knowledge and the <context>, the <context> ALWAYS wins.
                    Use structured output in Markdown with Headings, Bold, Lists, Tables and Code blocks.
                    Provide exact code examples in blocks if possible.
                """,
            },
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message


@app.get("/get_tables")
def get_all_tables():
    tables = get_tables()
    return tables


@app.post("/query")
def get_response(request: Request):
    data = request.json()
    user_query = data.get("prompt")
    doc_name = data.get("doc_name")

    query_emb = convert_embedding_batch([user_query])[0]
    # TODO vzit return status funkce a poslat vys -> nakonec az userovi  ve forme nejake hlasky
    sim_embeddings = search_similar(query_emb, doc_name).get("results", [])
    # print(sim_embeddings)
    out_data = get_llm_res(user_query, sim_embeddings)
    # print(out_data)

    return {"response": out_data.content}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
