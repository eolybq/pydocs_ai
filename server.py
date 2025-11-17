from openai import OpenAI
from dotenv import load_dotenv
import os

from services.create_embeddings import convert_embedding, get_embedding
from services.database import search_similar

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
user_query = input("Ask something:")
sim_embeddings = search_similar(convert_embedding(user_query))
print(sim_embeddings)

print(get_llm_res(user_query, sim_embeddings))


