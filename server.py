from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os

from services.create_embeddings import convert_embedding_batch
from services.database import search_similar, get_tables

load_dotenv()
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # nebo konkrétní originy frontendu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI(
    api_key=os.getenv("CHAT_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)



def get_llm_res(user_query, sim_embeddings):
    context_str = "\n\n".join(
        f"<chunk>\nmain_title: {c['main_title']}\nchunk_title: {c['chunk_title']}\ncontent: {c['content']}\n</chunk>"
        for c in sim_embeddings
    )

    prompt = f"""
        Use ONLY the following context to answer the question.
        If something is not in the context, say "I don't know, this topic doesnt't appear in documentation.".

        CONTEXT:
        {context_str}

        QUESTION:
        {user_query}
    """

    # models = client.models.list()
    # for model in models:
    #     print(model.id)

    response = client.chat.completions.create(
        model="gemini-2.5-flash",
        messages=[
            {"role": "system", "content": "Answer in English. You are a professional assitant. In every prompt you recive relevant data from RAG system, you use this data to enhance your answer."},
            {
                "role": "user",
                "content": prompt
            }
        ],
    )

    return response.choices[0].message



# TODO dodělat dynamický výběr dokumentace -  vybrat asi v UI? nebo nekde v kodu
@app.get("/get_tables")
async def get_all_tables():
    tables = get_tables()
    return tables


@app.post("/query")
async def get_response(request: Request):
    data = await request.json()
    user_query = data.get("prompt")
    doc_name = data.get("doc_name")
    # NOTE Mozna napsat na tvrdo idk
    embedd_model = data.get("embedd_model")

# TODO zkontrtolovat zdali funguje s novou convert embedding_batch funcki misto conver embedding - umele prevadim na list a pak beru prvni prvek
    query_emb = convert_embedding_batch([user_query], embedd_model=embedd_model)[0]
    # TODO vzit return status funkce a poslat vys -> nakonec az userovi  ve forme nejake hlasky
    sim_embeddings = search_similar(query_emb, doc_name).results
    print(sim_embeddings)
    out_data = get_llm_res(user_query, sim_embeddings)
    print(out_data)

    return {"response": out_data.content}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)


