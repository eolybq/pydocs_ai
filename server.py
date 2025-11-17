from openai import OpenAI
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

from services.create_embeddings import convert_embedding, get_embedding
from services.database import search_similar

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # nebo konkrétní originy frontendu
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

load_dotenv()

client = OpenAI(
    api_key=os.getenv("api_key"),
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



# vytvoreni embedding a ulozeni do databaze
# get_embedding("pandas")




# TODO dodělat frontend_dev aby response vypsal jako MD
# a oddelat nadpis stranky
@app.post("/query")
async def main(request: Request):
    data = await request.json()
    user_query = data.get("prompt")

    sim_embeddings = search_similar(convert_embedding(user_query))
    print(sim_embeddings)
    out_data = get_llm_res(user_query, sim_embeddings)
    print(out_data)

    return {"response": out_data.content}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)


