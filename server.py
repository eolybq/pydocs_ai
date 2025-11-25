from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, Request, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import zipfile
import os

from services.create_embeddings import convert_embedding_batch, get_embedding
from services.database import search_similar, create_table, get_tables

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
    api_key=os.getenv("api_key"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

UPLOAD_DIR = "tmp"


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


def run_embedding_pipeline(doc_name):
    get_embedding(doc_name)


@app.get("/get_tables")
async def get_all_tables():
    tables = get_tables()
    return tables

# Unzip a nahrani zip souboru a prevod na embedding
@app.post("/create_em_db")
async def create_em_db(background: BackgroundTasks, file: UploadFile = File(...)):
    """
    uložit ZIP do tmp složky
    rozbalit ZIP
    projít všechny HTML soubory → get_chunks_list
    uložit do DB přes save_bulk_embeddings
    """
    print("Filename:", file.filename)
    print("Content type:", file.content_type)

    # zajistí, že složka existuje
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    doc_name = file.filename.rsplit(".", 1)[0]

    extract_dir = os.path.join(UPLOAD_DIR, doc_name)
    os.makedirs(extract_dir, exist_ok=True)

    # rozbalení ZIPu přímo z in-memory streamu
    with zipfile.ZipFile(file.file) as zip_ref:
        zip_ref.extractall(extract_dir)

    # vytvoreni prislusne db v schema rag_docs
    create_table(doc_name)

    # vytvoreni embedding a ulozeni do databaze
    # TODO zjistit zdali funguje a spravne - api nedostava runtime error
    background.add_task(run_embedding_pipeline, doc_name)

    return {
        "status": "ok",
        "extracted_to": extract_dir,
        "file_count": len(os.listdir(extract_dir))
    }


# TODO dodělat dynamický výběr dokumentace -  vybrat asi v UI? nebo nekde v kodu

@app.post("/query")
async def get_response(request: Request):
    data = await request.json()
    user_query = data.get("prompt")
    doc_name = data.get("doc_name")
# TODO zkontrtolovat zdali funguje s novou convert embedding_batch funcki misto conver embedding - umele prevadim na list a pak beru prvni prvek
    query_emb = convert_embedding_batch([user_query])[0]
    # TODO vzit return status funkce a poslat vys -> nakonec az userovi  ve forme nejake hlasky
    sim_embeddings = search_similar(query_emb, doc_name).results
    print(sim_embeddings)
    out_data = get_llm_res(user_query, sim_embeddings)
    print(out_data)

    return {"response": out_data.content}


if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)


